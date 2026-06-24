from pydantic import BaseModel, Field


class PipelineState(BaseModel):
    run_id: str
    node_keys: list[str] = Field(default_factory=list)
