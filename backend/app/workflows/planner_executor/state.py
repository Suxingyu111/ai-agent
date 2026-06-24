from pydantic import BaseModel, Field


class PlannerExecutorState(BaseModel):
    run_id: str
    goal: str
    steps: list[str] = Field(default_factory=list)
