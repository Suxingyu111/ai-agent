from pydantic import BaseModel


class SupervisorTaskInput(BaseModel):
    goal: str


class SupervisorTaskResult(BaseModel):
    selected_agent_keys: list[str]
