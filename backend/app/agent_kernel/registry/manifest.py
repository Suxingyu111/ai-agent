from pydantic import BaseModel, Field


class AgentManifest(BaseModel):
    key: str
    version: str
    display_name: str
    description: str
    responsibility: str
    allowed_tools: list[str] = Field(default_factory=list)
    memory_namespace: str
    max_iterations: int = 6
    max_runtime_seconds: int = 180
