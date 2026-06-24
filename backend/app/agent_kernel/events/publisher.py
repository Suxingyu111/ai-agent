from app.agent_kernel.contracts.event import AgentEvent
from app.agent_kernel.events.bus import InMemoryEventBus


class EventPublisher:
    def __init__(self, bus: InMemoryEventBus) -> None:
        self._bus = bus

    def publish(self, event: AgentEvent) -> None:
        self._bus.publish(event)
