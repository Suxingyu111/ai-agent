from collections.abc import Callable

from app.agent_kernel.contracts.event import AgentEvent


class InMemoryEventBus:
    def __init__(self) -> None:
        self._subscribers: list[Callable[[AgentEvent], None]] = []

    def subscribe(self, subscriber: Callable[[AgentEvent], None]) -> None:
        self._subscribers.append(subscriber)

    def publish(self, event: AgentEvent) -> None:
        for subscriber in self._subscribers:
            subscriber(event)
