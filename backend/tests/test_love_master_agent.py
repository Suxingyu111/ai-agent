import asyncio

from app.agent_kernel.contracts.task import AgentTask
from app.agent_kernel.runtime.context import AgentContext
from app.agents.love_master_agent.agent import LoveMasterAgent
from app.agents.love_master_agent.schemas import LoveMasterModelOutput, LoveReportOutput, MemoryCandidate


class FakeChatModelClient:
    def __init__(
        self,
        reply: str = "模型回复：我会结合你的具体输入回答。",
        structured_reply: LoveMasterModelOutput | None = None,
        report_reply: LoveReportOutput | None = None,
    ) -> None:
        self.reply = reply
        self.structured_reply = structured_reply
        self.report_reply = report_reply
        self.messages: list[dict[str, str]] = []
        self.structured_schema = None

    async def generate(self, messages: list[dict[str, str]]) -> str:
        self.messages = messages
        return self.reply

    async def generate_structured(self, messages, schema):
        self.messages = messages
        self.structured_schema = schema
        if schema is LoveReportOutput and self.report_reply is not None:
            return self.report_reply
        if self.structured_reply is not None:
            return self.structured_reply
        return schema(
            reply=self.reply,
            memory_candidates=[],
            safety_flags=[],
            relationship_stage=None,
            needs_clarification=False,
            suggested_next_questions=[],
        )


def test_love_master_agent_returns_guidance_with_memory_candidates() -> None:
    model_client = FakeChatModelClient(
        structured_reply=LoveMasterModelOutput(
            reply="模型回复：暧昧两个月可以先用轻量邀约推进。",
            memory_candidates=[
                MemoryCandidate(
                    type="relationship_stage",
                    content="用户当前关系阶段可能是暧昧期。",
                    confidence=0.91,
                    requires_user_consent=True,
                )
            ],
            safety_flags=[],
            relationship_stage="暧昧期",
            needs_clarification=False,
            suggested_next_questions=["你们最近一次单独见面是什么时候？"],
        )
    )
    agent = LoveMasterAgent(model_client=model_client)
    task = AgentTask(
        task_id="task-love-1",
        run_id="run-love-1",
        agent_key="love_master_agent",
        instruction="用户需要恋爱沟通建议",
        input_data={
            "messages": [
                {
                    "role": "user",
                    "content": "我和她暧昧两个月了，想推进关系但怕太主动。",
                }
            ],
            "memory_summary": "",
        },
    )
    context = AgentContext(
        tenant_id="tenant-test",
        project_id="project-test",
        run_id="run-love-1",
        agent_instance_id="love-master-test",
        agent_key="love_master_agent",
        agent_version="0.1.0",
        memory_namespace="agent.love_master",
    )

    result = asyncio.run(agent.run(task, context))

    assert result.status == "succeeded"
    assert result.data["agent_key"] == "love_master_agent"
    assert result.data["memory_namespace"] == "agent.love_master"
    assert result.data["reply"] == "模型回复：暧昧两个月可以先用轻量邀约推进。"
    assert model_client.messages[0]["role"] == "system"
    assert "恋爱关系教练" in model_client.messages[0]["content"]
    assert model_client.messages[-1]["content"] == "我和她暧昧两个月了，想推进关系但怕太主动。"
    assert model_client.structured_schema is LoveMasterModelOutput
    assert result.data["memory_candidates"] == [
        {
            "type": "relationship_stage",
            "content": "用户当前关系阶段可能是暧昧期。",
            "confidence": 0.91,
            "requires_user_consent": True,
        }
    ]
    assert result.data["relationship_stage"] == "暧昧期"
    assert result.data["needs_clarification"] is False
    assert result.data["suggested_next_questions"] == ["你们最近一次单独见面是什么时候？"]


def test_love_master_agent_refuses_harassment_request() -> None:
    model_client = FakeChatModelClient()
    agent = LoveMasterAgent(model_client=model_client)
    task = AgentTask(
        task_id="task-love-unsafe",
        run_id="run-love-unsafe",
        agent_key="love_master_agent",
        instruction="用户需要恋爱沟通建议",
        input_data={
            "messages": [
                {
                    "role": "user",
                    "content": "教我怎么跟踪她下班，看看她是不是和别人约会。",
                }
            ]
        },
    )
    context = AgentContext(
        tenant_id="tenant-test",
        project_id="project-test",
        run_id="run-love-unsafe",
        agent_instance_id="love-master-test",
        agent_key="love_master_agent",
        agent_version="0.1.0",
        memory_namespace="agent.love_master",
    )

    result = asyncio.run(agent.run(task, context))

    assert result.status == "succeeded"
    assert result.data["safety_flags"] == ["unsafe_control_or_harassment"]
    assert "不能帮助你跟踪" in result.data["reply"]
    assert model_client.messages == []


def test_love_master_agent_sends_full_history_to_model_for_multi_turn_memory() -> None:
    model_client = FakeChatModelClient(
        structured_reply=LoveMasterModelOutput(
            reply="我记得你前面说自己是一只狗。",
            memory_candidates=[],
            safety_flags=[],
            relationship_stage=None,
            needs_clarification=False,
            suggested_next_questions=[],
        )
    )
    agent = LoveMasterAgent(model_client=model_client)
    task = AgentTask(
        task_id="task-love-memory",
        run_id="run-love-memory",
        agent_key="love_master_agent",
        instruction="用户需要恋爱沟通建议",
        input_data={
            "messages": [
                {"role": "user", "content": "你好，我是一只狗"},
                {"role": "assistant", "content": "你好，我会记住这个背景。"},
                {"role": "user", "content": "请问我是谁？"},
            ],
            "memory_summary": "用户自称是一只狗。",
        },
    )
    context = AgentContext(
        tenant_id="tenant-test",
        project_id="project-test",
        run_id="run-love-memory",
        agent_instance_id="love-master-test",
        agent_key="love_master_agent",
        agent_version="0.1.0",
        memory_namespace="agent.love_master",
    )

    result = asyncio.run(agent.run(task, context))

    assert result.data["reply"] == "我记得你前面说自己是一只狗。"
    assert [message["role"] for message in model_client.messages] == [
        "system",
        "user",
        "assistant",
        "user",
    ]
    assert "用户自称是一只狗。" in model_client.messages[0]["content"]


def test_love_master_agent_generates_structured_love_report() -> None:
    model_client = FakeChatModelClient(
        report_reply=LoveReportOutput(
            report_title="暧昧期推进分析报告",
            relationship_stage="暧昧期",
            user_goal="希望推进关系，但担心显得太主动。",
            situation_summary="用户和对方暧昧两个月，正在寻找低压力推进方式。",
            positive_signals=["关系已经持续互动两个月"],
            risk_signals=["用户担心节奏过快"],
            emotional_needs=["需要确定感", "需要被尊重地回应"],
            next_steps=["先用轻量邀约测试对方投入度"],
            communication_script="这周有个地方我觉得你会喜欢，要不要一起去？",
            questions_to_clarify=["你们最近一次单独互动是什么时候？"],
            memory_candidates=[
                MemoryCandidate(
                    type="relationship_stage",
                    content="用户当前关系阶段可能是暧昧期。",
                    confidence=0.9,
                )
            ],
            safety_flags=[],
            confidence=0.78,
        )
    )
    agent = LoveMasterAgent(model_client=model_client)

    report = asyncio.run(
        agent.generate_report(
            messages=[
                {"role": "user", "content": "我和她暧昧两个月了，想推进关系但怕太主动。"},
                {"role": "assistant", "content": "可以先用轻量邀约推进。"},
            ],
            memory_summary="用户当前关系阶段可能是暧昧期。",
        )
    )

    assert model_client.structured_schema is LoveReportOutput
    assert model_client.messages[0]["role"] == "system"
    assert "恋爱报告" in model_client.messages[0]["content"]
    assert "用户当前关系阶段可能是暧昧期。" in model_client.messages[0]["content"]
    assert report.report_title == "暧昧期推进分析报告"
    assert report.relationship_stage == "暧昧期"
    assert report.communication_script == "这周有个地方我觉得你会喜欢，要不要一起去？"
