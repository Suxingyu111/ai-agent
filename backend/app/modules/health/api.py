from fastapi import APIRouter, Request

from app.modules.health.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.app_env,
        api_prefix=settings.api_v1_prefix,
    )
