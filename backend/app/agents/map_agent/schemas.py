from pydantic import BaseModel


class MapTaskInput(BaseModel):
    query: str


class MapTaskResult(BaseModel):
    locations: list[str]
