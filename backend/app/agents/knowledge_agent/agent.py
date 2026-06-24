from app.agent_kernel.contracts.result import AgentTaskResult
from app.agent_kernel.contracts.task import AgentTask
from app.agent_kernel.runtime.context import AgentContext


class KnowledgeAgent:
    key = "knowledge_agent"
    version = "0.1.0"

    async def run(self, task: AgentTask, context: AgentContext) -> AgentTaskResult:
        return AgentTaskResult(
            status="succeeded",
            summary="知识库智能体已接收任务，后续将接入 RAG 检索服务。",
            data={"task_id": task.task_id, "knowledge_scope_ids": context.knowledge_scope_ids},
        )
