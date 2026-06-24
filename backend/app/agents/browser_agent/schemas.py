from pydantic import BaseModel


class BrowserTaskInput(BaseModel):
    url: str


class BrowserTaskResult(BaseModel):
    title: str | None = None
    observations: list[str]
