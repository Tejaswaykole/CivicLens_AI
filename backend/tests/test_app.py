"""Application startup checks that do not connect to a database."""

from fastapi.testclient import TestClient

from app.core.config import clear_settings_cache
from app.core.database import get_db, reset_engine
from app.main import app
from app.models import Base

EXPECTED_PATHS = {
    "/api/v1/health",
    "/api/v1/auth/register",
    "/api/v1/auth/login",
    "/api/v1/auth/verify-email",
    "/api/v1/auth/verification",
    "/api/v1/auth/me",
    "/api/v1/users",
    "/api/v1/users/{user_id}",
    "/api/v1/departments",
    "/api/v1/departments/{department_id}",
    "/api/v1/complaints",
    "/api/v1/complaints/{complaint_id}",
    "/api/v1/complaints/{complaint_id}/status",
    "/api/v1/complaints/{complaint_id}/assignments",
    "/api/v1/complaints/{complaint_id}/reviews",
    "/api/v1/audit-logs",
    "/api/v1/notifications",
    "/api/v1/notifications/{notification_id}/read",
}


def test_metadata_contains_the_phase3_tables() -> None:
    assert set(Base.metadata.tables) == {
        "departments",
        "users",
        "complaints",
        "complaint_assignments",
        "complaint_status_history",
        "model_predictions",
        "human_reviews",
        "audit_logs",
        "notifications",
    }
    assert "password_hash" in Base.metadata.tables["users"].columns


def test_openapi_lists_phase3_routes_and_hides_secrets(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "")
    clear_settings_cache()
    reset_engine()
    client = TestClient(app)
    response = client.get("/openapi.json")
    assert response.status_code == 200
    document = response.json()
    assert EXPECTED_PATHS <= set(document["paths"])
    assert "/api/v1/predictions" not in document["paths"]
    user_properties = document["components"]["schemas"]["UserRead"]["properties"]
    assert "password_hash" not in user_properties
    assert "password" not in user_properties
    clear_settings_cache()
    reset_engine()


def test_missing_token_is_rejected_before_the_database(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("JWT_SECRET", "")
    clear_settings_cache()
    reset_engine()

    used = {"database": False}

    def unused_db():
        used["database"] = True
        yield None

    app.dependency_overrides[get_db] = unused_db
    client = TestClient(app)
    response = client.get("/api/v1/complaints")
    app.dependency_overrides.clear()
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "not_authenticated"
    assert used["database"] is False
    clear_settings_cache()
    reset_engine()


def test_health_reports_database_not_configured(monkeypatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "")
    clear_settings_cache()
    reset_engine()
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["database"] == "not_configured"
    assert body["authenticated"] is False
    clear_settings_cache()
    reset_engine()
