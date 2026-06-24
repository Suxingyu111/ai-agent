from pydantic import BaseModel


class CancellationToken(BaseModel):
    run_id: str
    cancelled: bool = False
