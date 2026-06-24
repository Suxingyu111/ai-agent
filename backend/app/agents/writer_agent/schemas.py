from pydantic import BaseModel


class WriterTaskInput(BaseModel):
    materials: list[str]


class WriterTaskResult(BaseModel):
    content: str
