import json
from typing import Any

from langchain.chat_models import init_chat_model
from pydantic import ValidationError

from app.agent_kernel.contracts.model import ChatModelClient, StructuredModelT, StructuredOutputError
from app.agent_kernel.guardrails.contracts import GuardrailContext, GuardrailDecision
from app.agent_kernel.guardrails.pipeline import GuardrailPipeline, build_default_guardrail_pipeline
from app.core.config import Settings


class LangChainChatModelClient(ChatModelClient):
    def __init__(
        self,
        settings: Settings,
        guardrail_pipeline: GuardrailPipeline | None = None,
    ) -> None:
        if not settings.llm_api_key:
            raise ValueError("LLM_API_KEY 不能为空，请先在 backend/.env 中配置大模型密钥。")

        kwargs: dict[str, Any] = {
            "model": settings.llm_model,
            "model_provider": "openai",
            "api_key": settings.llm_api_key,
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens,
            "timeout": settings.llm_timeout_seconds,
            "max_retries": settings.llm_max_retries,
        }
        if settings.llm_base_url:
            kwargs["base_url"] = settings.llm_base_url

        self._model = init_chat_model(**kwargs)
        self._guardrails = guardrail_pipeline or build_default_guardrail_pipeline()

    async def generate(self, messages: list[dict[str, str]]) -> str:
        return self._filter_output(await self._generate_text(messages))

    async def generate_structured(
        self,
        messages: list[dict[str, str]],
        schema: type[StructuredModelT],
    ) -> StructuredModelT:
        try:
            return await self._generate_structured_with_provider(messages, schema)
        except Exception as exc:
            if not self._is_structured_output_unavailable(exc):
                raise
            return await self._generate_structured_with_json_fallback(messages, schema)

    async def _generate_text(self, messages: list[dict[str, str]]) -> str:
        response = await self._model.ainvoke(messages)
        content = response.content
        if isinstance(content, str):
            return content
        return str(content)

    async def _generate_structured_with_provider(
        self,
        messages: list[dict[str, str]],
        schema: type[StructuredModelT],
    ) -> StructuredModelT:
        structured_model = self._model.with_structured_output(schema)
        response = await structured_model.ainvoke(messages)
        try:
            structured = response if isinstance(response, schema) else schema.model_validate(response)
        except ValidationError as exc:
            raise StructuredOutputError(f"模型输出不符合结构化 schema：{exc}") from exc
        return self._filter_structured_output(structured)

    async def _generate_structured_with_json_fallback(
        self,
        messages: list[dict[str, str]],
        schema: type[StructuredModelT],
    ) -> StructuredModelT:
        fallback_messages = [
            *messages,
            {
                "role": "system",
                "content": (
                    "当前模型服务不支持原生结构化输出。请只输出一个合法 JSON 对象，"
                    "不要使用 Markdown，不要包裹代码块，不要输出解释性文字。\n"
                    "JSON 必须符合以下 JSON Schema：\n"
                    f"{json.dumps(schema.model_json_schema(), ensure_ascii=False)}"
                ),
            },
        ]
        content = await self._generate_text(fallback_messages)
        try:
            payload = self._loads_json_object(content)
        except ValueError as exc:
            raise StructuredOutputError(str(exc)) from exc
        try:
            structured = schema.model_validate(payload)
        except ValidationError as exc:
            raise StructuredOutputError(f"模型输出不符合结构化 schema：{exc}") from exc
        return self._filter_structured_output(structured)

    def _loads_json_object(self, content: str) -> dict[str, Any]:
        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            payload = self._loads_embedded_json_object(content)

        if not isinstance(payload, dict):
            raise ValueError("模型结构化输出必须是 JSON 对象。")
        return payload

    def _loads_embedded_json_object(self, content: str) -> dict[str, Any]:
        decoder = json.JSONDecoder()
        for index, char in enumerate(content):
            if char != "{":
                continue
            try:
                payload, _ = decoder.raw_decode(content[index:])
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                return payload
        raise ValueError("模型未返回可解析的 JSON 对象。")

    def _is_structured_output_unavailable(self, exc: Exception) -> bool:
        message = str(exc).lower()
        return "response_format" in message and (
            "unavailable" in message
            or "unsupported" in message
            or "not support" in message
            or "does not support" in message
            or "invalid_request_error" in message
        )

    def _filter_output(self, content: str) -> str:
        result = self._guardrails.inspect(
            content,
            GuardrailContext(
                tenant_id="default",
                project_id="default",
                user_id=None,
                agent_key="model_client",
                run_id="model-call",
                conversation_id=None,
                direction="output",
                safety_profile="default",
            ),
        )
        if result.decision == GuardrailDecision.BLOCK:
            return result.user_message or "模型输出存在安全风险，已被拦截。"
        if result.decision in {GuardrailDecision.REDACT, GuardrailDecision.REWRITE}:
            return result.sanitized_content or ""
        return content

    def _filter_structured_output(self, output: StructuredModelT) -> StructuredModelT:
        updates: dict[str, Any] = {}
        for field_name in output.__class__.model_fields:
            value = getattr(output, field_name)
            if isinstance(value, str):
                updates[field_name] = self._filter_output(value)

        if not updates:
            return output
        return output.model_copy(update=updates)
