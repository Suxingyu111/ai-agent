from typing import Any, Literal

from pydantic import BaseModel, Field

from app.agent_kernel.contracts.artifact import ArtifactRef
from app.agent_kernel.contracts.event import AgentEvent


class Citation(BaseModel):
    source: str
    title: str | None = None
    url: str | None = None


class AgentTaskResult(BaseModel):
    status: Literal["succeeded", "failed", "needs_approval", "needs_clarification"]
    summary: str
    data: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[ArtifactRef] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    events: list[AgentEvent] = Field(default_factory=list)
    next_suggested_tasks: list["AgentTask"] = Field(default_factory=list)


from app.agent_kernel.contracts.task import AgentTask  # noqa: E402

AgentTaskResult.model_rebuild()
