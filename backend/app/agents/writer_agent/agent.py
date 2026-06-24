from app.agent_kernel.contracts.result import AgentTaskResult
from app.agent_kernel.contracts.task import AgentTask
from app.agent_kernel.runtime.context import AgentContext


class WriterAgent:
    key = "writer_agent"
    version = "0.1.0"

    async def run(self, task: AgentTask, context: AgentContext) -> AgentTaskResult:
        return AgentTaskResult(
            status="succeeded",
            summary="写作智能体已接收任务，后续将接入结构化写作逻辑。",
            data={"task_id": task.task_id, "agent_key": context.agent_key},
        )
