from typing import Literal

from pydantic import BaseModel, Field


class MemoryCandidate(BaseModel):
    type: str
    content: str
    confidence: float = Field(ge=0, le=1)
    requires_user_consent: bool = True


class LoveMasterModelOutput(BaseModel):
    reply: str = Field(description="给用户展示的自然语言回复。")
    memory_candidates: list[MemoryCandidate] = Field(
        default_factory=list,
        description="可写入会话记忆的候选信息。",
    )
    safety_flags: list[str] = Field(
        default_factory=list,
        description="模型认为本轮命中的安全风险标签。",
    )
    relationship_stage: str | None = Field(
        default=None,
        description="用户当前关系阶段，例如暧昧期、热恋期、冲突期、分手后等。",
    )
    needs_clarification: bool = Field(
        default=False,
        description="是否需要用户补充关键信息。",
    )
    suggested_next_questions: list[str] = Field(
        default_factory=list,
        description="建议继续追问用户的问题。",
    )


class LoveReportOutput(BaseModel):
    report_title: str = Field(description="恋爱报告标题。")
    relationship_stage: Literal[
        "初识期",
        "暧昧期",
        "热恋期",
        "稳定期",
        "冲突期",
        "冷淡期",
        "分手后",
        "不确定",
    ] = Field(description="基于当前对话判断的关系阶段。")
    user_goal: str = Field(description="用户本轮最想达成的关系目标。")
    situation_summary: str = Field(description="基于已知信息总结的当前局面。")
    positive_signals: list[str] = Field(default_factory=list, description="关系中的积极信号。")
    risk_signals: list[str] = Field(default_factory=list, description="关系中的风险信号。")
    emotional_needs: list[str] = Field(default_factory=list, description="用户表达出的情感需求。")
    next_steps: list[str] = Field(default_factory=list, description="建议用户接下来采取的行动。")
    communication_script: str = Field(description="可直接参考的低压力沟通话术。")
    questions_to_clarify: list[str] = Field(
        default_factory=list,
        description="为了继续分析需要用户补充的问题。",
    )
    memory_candidates: list[MemoryCandidate] = Field(
        default_factory=list,
        description="可写入会话记忆的候选信息。",
    )
    safety_flags: list[str] = Field(default_factory=list, description="报告生成命中的安全风险标签。")
    confidence: float = Field(ge=0, le=1, description="报告判断的置信度。")
