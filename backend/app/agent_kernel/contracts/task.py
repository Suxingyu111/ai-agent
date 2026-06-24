from typing import Any

from pydantic import BaseModel, Field


class AgentTask(BaseModel):
    task_id: str
    run_id: str
    agent_key: str
    instruction: str
    input_data: dict[str, Any] = Field(default_factory=dict)
