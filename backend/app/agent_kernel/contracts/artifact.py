from pydantic import BaseModel


class ArtifactRef(BaseModel):
    artifact_id: str
    name: str
    content_type: str
    url: str | None = None
