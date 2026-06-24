from pydantic import BaseModel


class PdfTaskInput(BaseModel):
    title: str
    html: str


class PdfTaskResult(BaseModel):
    artifact_id: str
