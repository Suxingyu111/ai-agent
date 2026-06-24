from pydantic import BaseModel


class ResearchTaskInput(BaseModel):
    question: str


class ResearchTaskResult(BaseModel):
    findings: list[str]
    sources: list[str]
