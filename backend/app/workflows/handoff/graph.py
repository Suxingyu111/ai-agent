from app.workflows.handoff.state import HandoffState


def create_handoff_graph_placeholder() -> type[HandoffState]:
    return HandoffState
