from collections.abc import AsyncIterator

from app.agent_kernel.contracts.event import AgentEvent


async def empty_event_stream() -> AsyncIterator[AgentEvent]:
    if False:
        yield AgentEvent(event_type="noop", run_id="noop")
