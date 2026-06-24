from app.agent_kernel.contracts.agent import AgentContract
from app.agent_kernel.contracts.result import AgentTaskResult
from app.agent_kernel.contracts.task import AgentTask
from app.agent_kernel.runtime.context import AgentContext


class AgentRunner:
    async def run(
        self,
        agent: AgentContract,
        task: AgentTask,
        context: AgentContext,
    ) -> AgentTaskResult:
        return await agent.run(task, context)
