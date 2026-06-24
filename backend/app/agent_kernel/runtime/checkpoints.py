from pydantic import BaseModel


class CheckpointRef(BaseModel):
    run_id: str
    checkpoint_id: str
