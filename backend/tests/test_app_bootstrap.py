from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


def test_health_endpoint_returns_application_status() -> None:
    app = create_app(settings=Settings(APP_ENV="test"))
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app_name": "AI 多智能体平台",
        "environment": "test",
        "api_prefix": "/api/v1",
    }
