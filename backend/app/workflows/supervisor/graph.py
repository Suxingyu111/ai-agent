from app.workflows.supervisor.state import SupervisorWorkflowState


def create_supervisor_graph_placeholder() -> type[SupervisorWorkflowState]:
    return SupervisorWorkflowState
