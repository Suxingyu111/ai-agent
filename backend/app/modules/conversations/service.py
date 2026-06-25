from dataclasses import dataclass, field
from uuid import uuid4

from fastapi import HTTPException, status

from app.agent_kernel.contracts.model import ChatModelClient
from app.agent_kernel.contracts.task import AgentTask
from app.agent_kernel.guardrails.contracts import GuardrailContext, GuardrailDecision, GuardrailFinding
from app.agent_kernel.guardrails.pipeline import GuardrailPipeline, build_default_guardrail_pipeline
from app.agent_kernel.runtime.context import AgentContext
from app.agents.love_master_agent.agent import LoveMasterAgent
from app.agents.love_master_agent.memory import MEMORY_NAMESPACE
from app.db.session import SessionFactory, create_db_and_tables, create_session_factory
from app.modules.conversations.repository import ConversationRepository
from app.modules.conversations.schemas import (
    ConversationCreateRequest,
    ConversationCreateResponse,
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationMessageOut,
    ConversationMessagesResponse,
    LoveReportCreateRequest,
    LoveReportCreateResponse,
    MessageCreateRequest,
    MessageCreateResponse,
)


@dataclass
class ConversationRecord:
    conversation_id: str
    thread_id: str
    agent_key: str
    title: str
    memory_namespace: str
    memory_summary: str = ""
    messages: list[ConversationMessageOut] = field(default_factory=list)


class ConversationService:
    def __init__(
        self,
        model_client: ChatModelClient | None = None,
        guardrail_pipeline: GuardrailPipeline | None = None,
        session_factory: SessionFactory | None = None,
    ) -> None:
        if session_factory is None:
            session_factory = create_session_factory("sqlite+pysqlite:///:memory:")
            create_db_and_tables(session_factory)
        self._repository = ConversationRepository(session_factory)
        self._love_master_agent = LoveMasterAgent(model_client=model_client)
        self._guardrails = guardrail_pipeline or build_default_guardrail_pipeline()

    def create_conversation(
        self, payload: ConversationCreateRequest
    ) -> ConversationCreateResponse:
        if payload.agent_key != LoveMasterAgent.key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="当前仅支持 love_master_agent 会话。",
            )

        record = self._repository.create_conversation(
            agent_key=payload.agent_key,
            title=payload.title or "恋爱咨询",
            memory_namespace=MEMORY_NAMESPACE,
        )
        return self._conversation_response(
            ConversationRecord(
                conversation_id=record.conversation_id,
                thread_id=record.thread_id,
                agent_key=record.agent_key,
                title=record.title,
                memory_namespace=record.memory_namespace,
                memory_summary=record.memory_summary,
                messages=[],
            )
        )

    async def create_message(
        self,
        conversation_id: str,
        payload: MessageCreateRequest,
    ) -> MessageCreateResponse:
        record = self._get_record(conversation_id)
        input_context = self._guardrail_context(record, "input")
        input_result = self._guardrails.inspect(payload.content, input_context)
        user_content = input_result.sanitized_content or payload.content
        input_flags = self._finding_categories(input_result.findings)
        user_message = ConversationMessageOut(
            message_id=f"msg_{uuid4().hex}",
            role="user",
            content=user_content,
            safety_flags=input_flags,
        )
        record.messages.append(user_message)
        self._repository.add_message(record.conversation_id, user_message)

        if input_result.decision == GuardrailDecision.BLOCK:
            assistant_message = ConversationMessageOut(
                message_id=f"msg_{uuid4().hex}",
                role="assistant",
                content=input_result.user_message or "这个请求可能涉及安全风险，我不能按这个方向继续。",
                safety_flags=input_flags,
            )
            record.messages.append(assistant_message)
            self._repository.add_message(record.conversation_id, assistant_message)
            return MessageCreateResponse(
                conversation_id=record.conversation_id,
                user_message=user_message,
                assistant_message=assistant_message,
                memory_summary=record.memory_summary,
                safety_flags=input_flags,
            )

        result = await self._love_master_agent.run(
            AgentTask(
                task_id=f"task_{uuid4().hex}",
                run_id=f"run_{uuid4().hex}",
                agent_key=record.agent_key,
                instruction="用户需要恋爱沟通建议",
                input_data={
                    "messages": [message.model_dump() for message in record.messages],
                    "memory_summary": record.memory_summary,
                },
            ),
            AgentContext(
                tenant_id="default",
                project_id="default",
                run_id=f"run_{uuid4().hex}",
                agent_instance_id=record.thread_id,
                agent_key=record.agent_key,
                agent_version=LoveMasterAgent.version,
                memory_namespace=record.memory_namespace,
            ),
        )

        safety_flags = result.data.get("safety_flags", [])
        output_result = self._guardrails.inspect(
            result.data["reply"],
            self._guardrail_context(record, "output"),
        )
        assistant_content = result.data["reply"]
        output_flags = self._finding_categories(output_result.findings)
        if output_result.decision == GuardrailDecision.BLOCK:
            assistant_content = output_result.user_message or (
                "模型输出可能涉及安全或隐私风险，我不能按这个方向继续。"
            )
            safety_flags = [*safety_flags, *output_flags]
        elif output_result.decision in {GuardrailDecision.REDACT, GuardrailDecision.REWRITE}:
            assistant_content = output_result.sanitized_content or ""
            safety_flags = [*safety_flags, *output_flags]

        safety_flags = list(dict.fromkeys(safety_flags))
        assistant_message = ConversationMessageOut(
            message_id=f"msg_{uuid4().hex}",
            role="assistant",
            content=assistant_content,
            safety_flags=safety_flags,
        )
        record.messages.append(assistant_message)
        self._repository.add_message(record.conversation_id, assistant_message)
        self._merge_memory_candidates(record, result.data.get("memory_candidates", []))

        return MessageCreateResponse(
            conversation_id=record.conversation_id,
            user_message=user_message,
            assistant_message=assistant_message,
            memory_summary=record.memory_summary,
            safety_flags=safety_flags,
        )

    def list_messages(self, conversation_id: str) -> ConversationMessagesResponse:
        record = self._get_record(conversation_id)
        return ConversationMessagesResponse(
            conversation_id=record.conversation_id,
            memory_summary=record.memory_summary,
            messages=record.messages,
        )

    def get_conversation(self, conversation_id: str) -> ConversationDetailResponse:
        return self._conversation_detail_response(self._get_record(conversation_id))

    def list_conversations(self) -> ConversationListResponse:
        conversations = [
            self._conversation_detail_response(
                ConversationRecord(
                    conversation_id=conversation.conversation_id,
                    thread_id=conversation.thread_id,
                    agent_key=conversation.agent_key,
                    title=conversation.title,
                    memory_namespace=conversation.memory_namespace,
                    memory_summary=conversation.memory_summary,
                    messages=[],
                )
            )
            for conversation in self._repository.list_conversations()
        ]
        return ConversationListResponse(conversations=conversations)

    async def create_love_report(
        self,
        conversation_id: str,
        payload: LoveReportCreateRequest,
    ) -> LoveReportCreateResponse:
        record = self._get_record(conversation_id)
        if not record.messages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="请先发送至少一条消息，再生成恋爱报告。",
            )

        preference_text = "\n".join(
            item
            for item in [
                f"分析重点：{payload.focus}" if payload.focus else "",
                f"表达风格：{payload.style}" if payload.style else "",
            ]
            if item
        )
        if preference_text:
            input_result = self._guardrails.inspect(
                preference_text,
                self._guardrail_context(record, "input"),
            )
            if input_result.decision == GuardrailDecision.BLOCK:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=input_result.user_message or "报告偏好包含安全风险。",
                )

        report = await self._love_master_agent.generate_report(
            messages=[message.model_dump() for message in record.messages],
            memory_summary=record.memory_summary,
            focus=payload.focus,
            style=payload.style,
        )
        safety_flags = list(report.safety_flags)
        output_result = self._guardrails.inspect(
            "\n".join([report.communication_script, *report.next_steps]),
            self._guardrail_context(record, "output"),
        )
        output_flags = self._finding_categories(output_result.findings)
        if output_result.decision == GuardrailDecision.BLOCK:
            report = report.model_copy(
                update={
                    "communication_script": output_result.user_message
                    or "报告中的沟通话术存在安全风险，已被替换。",
                    "next_steps": ["先暂停高风险行动，改用尊重边界的直接沟通。"],
                }
            )
            safety_flags = [*safety_flags, *output_flags]
        elif output_result.decision in {GuardrailDecision.REDACT, GuardrailDecision.REWRITE}:
            report = report.model_copy(
                update={
                    "communication_script": output_result.sanitized_content
                    or report.communication_script,
                }
            )
            safety_flags = [*safety_flags, *output_flags]

        safety_flags = list(dict.fromkeys(safety_flags))
        report = report.model_copy(update={"safety_flags": safety_flags})
        self._merge_memory_candidates(
            record,
            [candidate.model_dump() for candidate in report.memory_candidates],
        )
        self._repository.add_love_report(
            conversation_id=record.conversation_id,
            report=report.model_dump(),
            safety_flags=safety_flags,
        )
        return LoveReportCreateResponse(
            conversation_id=record.conversation_id,
            report=report,
            memory_summary=record.memory_summary,
            safety_flags=safety_flags,
        )

    def _get_record(self, conversation_id: str) -> ConversationRecord:
        conversation = self._repository.get_conversation(conversation_id)
        if conversation is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="会话不存在。",
            )
        return ConversationRecord(
            conversation_id=conversation.conversation_id,
            thread_id=conversation.thread_id,
            agent_key=conversation.agent_key,
            title=conversation.title,
            memory_namespace=conversation.memory_namespace,
            memory_summary=conversation.memory_summary,
            messages=self._repository.list_messages(conversation.conversation_id),
        )

    def _conversation_response(self, record: ConversationRecord) -> ConversationCreateResponse:
        return ConversationCreateResponse(
            conversation_id=record.conversation_id,
            thread_id=record.thread_id,
            agent_key=record.agent_key,
            title=record.title,
            memory_namespace=record.memory_namespace,
        )

    def _conversation_detail_response(
        self,
        record: ConversationRecord,
    ) -> ConversationDetailResponse:
        return ConversationDetailResponse(
            conversation_id=record.conversation_id,
            thread_id=record.thread_id,
            agent_key=record.agent_key,
            title=record.title,
            memory_namespace=record.memory_namespace,
            memory_summary=record.memory_summary,
        )

    def _merge_memory_candidates(
        self,
        record: ConversationRecord,
        memory_candidates: list[dict[str, object]],
    ) -> None:
        for candidate in memory_candidates:
            content = str(candidate.get("content") or "")
            if content and content not in record.memory_summary:
                record.memory_summary = (
                    f"{record.memory_summary}\n{content}".strip()
                    if record.memory_summary
                    else content
                )
                self._repository.update_memory_summary(
                    record.conversation_id,
                    record.memory_summary,
                )
                self._repository.add_memory_candidate(
                    conversation_id=record.conversation_id,
                    agent_key=record.agent_key,
                    namespace=record.memory_namespace,
                    memory_type=str(candidate.get("type") or "unknown"),
                    content=content,
                    confidence=float(candidate.get("confidence") or 0),
                    requires_user_consent=bool(candidate.get("requires_user_consent", True)),
                )

    def _guardrail_context(
        self,
        record: ConversationRecord,
        direction: str,
    ) -> GuardrailContext:
        return GuardrailContext(
            tenant_id="default",
            project_id="default",
            user_id=None,
            agent_key=record.agent_key,
            run_id=record.thread_id,
            conversation_id=record.conversation_id,
            direction=direction,  # type: ignore[arg-type]
            safety_profile="emotional_support",
        )

    def _finding_categories(self, findings: list[GuardrailFinding]) -> list[str]:
        return list(dict.fromkeys(finding.category for finding in findings))
