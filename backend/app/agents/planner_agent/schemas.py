from pydantic import BaseModel


class PlannerTaskInput(BaseModel):
    goal: str


class PlannerTaskResult(BaseModel):
    steps: list[str]
