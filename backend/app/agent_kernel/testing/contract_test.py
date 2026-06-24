from app.agent_kernel.contracts.result import AgentTaskResult


def assert_successful_result(result: AgentTaskResult) -> None:
    assert result.status == "succeeded"
