from pydantic import BaseModel


class ReviewerTaskInput(BaseModel):
    content: str


class ReviewerTaskResult(BaseModel):
    passed: bool
    issues: list[str]
