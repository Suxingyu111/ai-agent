from app.agent_kernel.contracts.result import AgentTaskResult
from app.agent_kernel.contracts.task import AgentTask
from app.agent_kernel.runtime.context import AgentContext


class MapAgent:
    key = "map_agent"
    version = "0.1.0"

    async def run(self, task: AgentTask, context: AgentContext) -> AgentTaskResult:
        return AgentTaskResult(
            status="succeeded",
            summary="地图智能体已接收任务，后续将接入地图服务工具。",
            data={"task_id": task.task_id, "allowed_tools": context.allowed_tool_ids},
        )
