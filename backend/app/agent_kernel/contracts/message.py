from typing import Literal

from pydantic import BaseModel


class AgentMessage(BaseModel):
    role: Literal["system", "user", "assistant", "tool"]
    content: str
