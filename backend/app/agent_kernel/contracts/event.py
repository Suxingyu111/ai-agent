from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AgentEvent(BaseModel):
    event_type: str
    run_id: str
    task_id: str | None = None
    agent_instance_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
