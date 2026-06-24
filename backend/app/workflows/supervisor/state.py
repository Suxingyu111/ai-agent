from typing import Any

from pydantic import BaseModel, Field


class SupervisorWorkflowState(BaseModel):
    run_id: str
    goal: str
    selected_agent_keys: list[str] = Field(default_factory=list)
    results: dict[str, Any] = Field(default_factory=dict)
