from pydantic import BaseModel


class FileTaskInput(BaseModel):
    path: str
    action: str


class FileTaskResult(BaseModel):
    path: str
    changed: bool
