from pydantic import BaseModel


class KnowledgeTaskInput(BaseModel):
    query: str
    knowledge_base_ids: list[str]


class KnowledgeTaskResult(BaseModel):
    evidence: list[str]
