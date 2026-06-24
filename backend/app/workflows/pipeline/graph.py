from app.workflows.pipeline.state import PipelineState


def create_pipeline_graph_placeholder() -> type[PipelineState]:
    return PipelineState
