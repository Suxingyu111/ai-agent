from pydantic import BaseModel


class MemoryScope(BaseModel):
    namespace: str
    tenant_id: str
    project_id: str
    agent_key: str | None = None
