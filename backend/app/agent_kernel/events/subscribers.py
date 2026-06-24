from app.agent_kernel.contracts.event import AgentEvent


def noop_subscriber(event: AgentEvent) -> None:
    _ = event
