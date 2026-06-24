from typing import Protocol

from app.agent_kernel.contracts.result import AgentTaskResult
from app.agent_kernel.contracts.task import AgentTask
from app.agent_kernel.runtime.context import AgentContext


class AgentContract(Protocol):
    key: str
    version: str

    async def run(self, task: AgentTask, context: AgentContext) -> AgentTaskResult:
        """执行单个智能体任务，并返回结构化结果。"""
