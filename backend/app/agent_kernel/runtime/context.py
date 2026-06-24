from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    tenant_id: str
    project_id: str
    run_id: str
    agent_instance_id: str
    agent_key: str
    agent_version: str
    memory_namespace: str
    allowed_tool_ids: list[str] = Field(default_factory=list)
    knowledge_scope_ids: list[str] = Field(default_factory=list)
    trace_id: str | None = None
