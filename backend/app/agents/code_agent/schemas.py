from pydantic import BaseModel


class CodeTaskInput(BaseModel):
    instruction: str
    language: str | None = None


class CodeTaskResult(BaseModel):
    summary: str
    files_changed: list[str]
