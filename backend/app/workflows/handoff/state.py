from pydantic import BaseModel


class HandoffState(BaseModel):
    run_id: str
    from_agent_key: str
    to_agent_key: str
