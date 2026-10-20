"""Password, token, and authorization checks."""

import base64
import json
import secrets
import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, clear_settings_cache
from app.core.database import get_db, reset_engine
from app.core.passwords import hash_password, verify_password
from app.core.rate_limit import reset_rate_limits
from app.core.tokens import TokenError, create_access_token, read_access_token_subject
from app.domain.enums import NotificationType, UserRole
from app.main import app, create_app
from app.models.notification import Notification
from app.models.user import User
from app.services.audit import _public_metadata
from tests.test_postgres import _PASSWORDS, _auth, _complaint_body, _department, _user


def _unsigned_token(user_id: uuid.UUID) -> str:
    def encode(value: dict) -> str:
        raw = json.dumps(value, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()

    header = encode({"alg": "none", "typ": "JWT"})
    payload = encode({"sub": str(user_id), "exp": 9999999999})
    return f"{header}.{payload}."


def test_password_hash_verifies_only_the_original_password() -> None:
    password = secrets.token_urlsafe(18)
    stored = hash_password(password)
    assert stored != password
    assert stored.startswith("$argon2id$")
    assert verify_password(password, stored) is True
    assert verify_password(secrets.token_urlsafe(18), stored) is False
    assert verify_password(password, None) is False


def test_short_password_is_not_hashed() -> None:
    with pytest.raises(ValueError):
        hash_password("short-pass")


def test_access_token_round_trip_and_expiry(monkeypatch) -> None:
    secret = secrets.token_urlsafe(48)
    monkeypatch.setenv("JWT_SECRET", secret)
    monkeypatch.setenv("APP_ENV", "test")
    clear_settings_cache()
    user_id = uuid.uuid4()
    settings = Settings(jwt_secret=secret, app_env="test")
    token, expires_in = create_access_token(user_id, settings)
    assert expires_in == 30 * 60
    assert read_access_token_subject(token, settings) == user_id

    expired = jwt.encode(
        {
            "sub": str(user_id),
            "iat": datetime.now(UTC) - timedelta(hours=2),
            "exp": datetime.now(UTC) - timedelta(hours=1),
        },
        secret,
        algorithm="HS256",
    )
    with pytest.raises(TokenError):
        read_access_token_subject(expired, settings)
    tampered = token[:-4] + ("aaaa" if not token.endswith("aaaa") else "bbbb")
    with pytest.raises(TokenError):
        read_access_token_subject(tampered, settings)
    unsigned = _unsigned_token(user_id)
    with pytest.raises(TokenError):
        read_access_token_subject(unsigned, settings)
    clear_settings_cache()


def test_invalid_bearer_token_returns_401(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET", secrets.token_urlsafe(48))
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("APP_ENV", "test")
    clear_settings_cache()
    reset_engine()

    def unused_db():
        yield None

    app.dependency_overrides[get_db] = unused_db
    client = TestClient(app)
    response = client.get("/api/v1/users", headers={"Authorization": "Bearer not-a-jwt"})
    app.dependency_overrides.clear()
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token"
    clear_settings_cache()
    reset_engine()


def test_auth_is_unavailable_when_the_secret_is_missing(monkeypatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("APP_ENV", "development")
    clear_settings_cache()
    reset_engine()

    def unused_db():
        yield None

    app.dependency_overrides[get_db] = unused_db
    client = TestClient(app)
    response = client.get(
        "/api/v1/departments",
        headers={"Authorization": "Bearer not-a-jwt"},
    )
    app.dependency_overrides.clear()
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "auth_not_configured"
    clear_settings_cache()
    reset_engine()


@pytest.mark.postgres
def test_registration_login_and_duplicate_email(client) -> None:
    password = secrets.token_urlsafe(18)
    email = f"citizen.{uuid.uuid4().hex[:8]}@example.com"
    created = client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "Dev Citizen",
            "email": email,
            "password": password,
            "ward_or_zone": "Development ward",
        },
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["token_type"] == "bearer"
    assert "password" not in body
    headers = {"Authorization": f"Bearer {body['access_token']}"}
    profile = client.get("/api/v1/auth/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["role"] == "citizen"
    assert profile.json()["email"] == email
    assert "password_hash" not in profile.json()

    duplicate = client.post(
        "/api/v1/auth/register",
        json={"display_name": "Dev Citizen", "email": email.upper(), "password": password},
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["error"]["code"] == "duplicate_email"

    escalated = client.post(
        "/api/v1/auth/register",
        json={
            "display_name": "Dev Citizen",
            "email": f"other.{uuid.uuid4().hex[:8]}@example.com",
            "password": password,
            "role": "system_admin",
        },
    )
    assert escalated.status_code == 422

    wrong = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": secrets.token_urlsafe(18)},
    )
    assert wrong.status_code == 401
    assert wrong.json()["error"]["code"] == "invalid_credentials"
    missing = client.post(
        "/api/v1/auth/login",
        json={"email": f"missing.{uuid.uuid4().hex[:8]}@example.com", "password": password},
    )
    assert missing.status_code == 401
    assert missing.json()["error"]["message"] == wrong.json()["error"]["message"]


@pytest.mark.postgres
def test_role_rules_and_audit(client, db_session) -> None:
    department = _department(db_session, f"A{uuid.uuid4().hex[:6].upper()}")
    other = _department(db_session, f"B{uuid.uuid4().hex[:6].upper()}")
    citizen = _user(db_session, UserRole.citizen)
    other_citizen = _user(db_session, UserRole.citizen)
    officer = _user(db_session, UserRole.department_officer, department=department)
    reviewer = _user(db_session, UserRole.grievance_officer)
    admin = _user(db_session, UserRole.system_admin)
    citizen_headers = _auth(client, citizen)
    officer_headers = _auth(client, officer)
    reviewer_headers = _auth(client, reviewer)
    admin_headers = _auth(client, admin)

    stolen = client.post(
        "/api/v1/complaints",
        json=_complaint_body(other_citizen, department),
        headers=citizen_headers,
    )
    assert stolen.status_code == 403

    own = client.post(
        "/api/v1/complaints",
        json=_complaint_body(citizen, department),
        headers=citizen_headers,
    )
    assert own.status_code == 201, own.text
    complaint_id = own.json()["id"]

    hidden = client.get(f"/api/v1/complaints/{complaint_id}", headers=officer_headers)
    assert hidden.status_code == 404
    listed = client.get(
        "/api/v1/complaints",
        params={"citizen_id": str(other_citizen.id)},
        headers=citizen_headers,
    )
    assert listed.status_code == 403
    citizen_audit = client.get("/api/v1/audit-logs", headers=citizen_headers)
    assert citizen_audit.status_code == 403
    citizen_users = client.get("/api/v1/users", headers=citizen_headers)
    assert citizen_users.status_code == 403
    reviewer_citizens = client.get(
        "/api/v1/users",
        params={"role": "citizen"},
        headers=reviewer_headers,
    )
    assert reviewer_citizens.status_code == 403
    officer_citizens = client.get(
        "/api/v1/users",
        params={"role": "citizen"},
        headers=officer_headers,
    )
    assert officer_citizens.status_code == 403

    triaged = client.patch(
        f"/api/v1/complaints/{complaint_id}/status",
        json={"status": "triaged", "note": "Accepted for assignment."},
        headers=reviewer_headers,
    )
    assert triaged.status_code == 200, triaged.text
    field_jump = client.patch(
        f"/api/v1/complaints/{complaint_id}/status",
        json={"status": "in_progress", "note": "Triage cannot skip assignment."},
        headers=reviewer_headers,
    )
    assert field_jump.status_code == 403

    assigned = client.post(
        f"/api/v1/complaints/{complaint_id}/assignments",
        json={"department_id": str(department.id), "assigned_officer_id": str(officer.id)},
        headers=reviewer_headers,
    )
    assert assigned.status_code == 201, assigned.text
    moved = client.post(
        f"/api/v1/complaints/{complaint_id}/assignments",
        json={"department_id": str(other.id)},
        headers=officer_headers,
    )
    assert moved.status_code == 403
    visible = client.get(f"/api/v1/complaints/{complaint_id}", headers=officer_headers)
    assert visible.status_code == 200

    progress = client.patch(
        f"/api/v1/complaints/{complaint_id}/status",
        json={"status": "in_progress", "note": "Crew is on site."},
        headers=officer_headers,
    )
    assert progress.status_code == 200, progress.text
    officer_reject = client.patch(
        f"/api/v1/complaints/{complaint_id}/status",
        json={"status": "rejected", "note": "Field officers cannot reject."},
        headers=officer_headers,
    )
    assert officer_reject.status_code == 403
    officer_review = client.post(
        f"/api/v1/complaints/{complaint_id}/reviews",
        json={
            "reviewer_user_id": str(officer.id),
            "confirmed_priority": "medium",
        },
        headers=officer_headers,
    )
    assert officer_review.status_code == 403

    spoofed = client.patch(
        f"/api/v1/complaints/{complaint_id}/status",
        json={
            "status": "resolved",
            "note": "Pretending to be the administrator.",
            "actor_user_id": str(admin.id),
        },
        headers=officer_headers,
    )
    assert spoofed.status_code == 403

    staff = client.post(
        "/api/v1/users",
        json={
            "display_name": "Dev New Officer",
            "email": f"field.{uuid.uuid4().hex[:8]}@example.com",
            "password": secrets.token_urlsafe(18),
            "role": "department_officer",
            "department_id": str(department.id),
        },
        headers=reviewer_headers,
    )
    assert staff.status_code == 403
    staff = client.post(
        "/api/v1/users",
        json={
            "display_name": "Dev New Officer",
            "email": f"field.{uuid.uuid4().hex[:8]}@example.com",
            "password": secrets.token_urlsafe(18),
            "role": "department_officer",
            "department_id": str(department.id),
        },
        headers=admin_headers,
    )
    assert staff.status_code == 201, staff.text
    assert "password" not in staff.text
    self_demotion = client.patch(
        f"/api/v1/users/{admin.id}",
        json={"role": "citizen"},
        headers=admin_headers,
    )
    assert self_demotion.status_code == 403

    audit = client.get(
        "/api/v1/audit-logs",
        params={"entity_type": "user", "action": "ACCOUNT_CREATED"},
        headers=admin_headers,
    )
    assert audit.status_code == 200
    assert audit.json()["total"] >= 1
    metadata = audit.json()["items"][0]["event_metadata"]
    assert "password" not in metadata
    assert "email" not in metadata

    foreign_notice = Notification(
        recipient_user_id=other_citizen.id,
        notification_type=NotificationType.info,
        title="Private notice",
        message="This belongs to another citizen.",
    )
    db_session.add(foreign_notice)
    db_session.flush()
    denied = client.patch(
        f"/api/v1/notifications/{foreign_notice.id}/read",
        headers=citizen_headers,
    )
    assert denied.status_code == 404


@pytest.mark.postgres
def test_inactive_user_token_is_rejected(client, db_session) -> None:
    user = _user(db_session, UserRole.citizen)
    headers = _auth(client, user)
    stored = db_session.get(User, user.id)
    assert stored is not None
    stored.is_active = False
    db_session.flush()
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "inactive_account"


@pytest.mark.postgres
def test_expired_token_is_rejected(client, db_session) -> None:
    user = _user(db_session, UserRole.citizen)
    secret = Settings().jwt_secret
    assert secret is not None
    expired = jwt.encode(
        {
            "sub": str(user.id),
            "iat": datetime.now(UTC) - timedelta(hours=2),
            "exp": datetime.now(UTC) - timedelta(minutes=5),
        },
        secret,
        algorithm="HS256",
    )
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token"


def test_audit_metadata_drops_secrets_and_nested_objects() -> None:
    cleaned = _public_metadata(
        {
            "role": "citizen",
            "password": "secret-value",
            "nested": {"token": "abc"},
            "fields": ["email_verified"],
            "note": "bearer eyJhbGciOiJIUzI1NiJ9",
            "count": 2,
            "flag": False,
        }
    )
    assert cleaned == {
        "role": "citizen",
        "fields": ["email_verified"],
        "count": 2,
        "flag": False,
    }


def test_login_and_register_rate_limits(monkeypatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("API_HOST", "127.0.0.1")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setenv("JWT_SECRET", "")
    monkeypatch.setenv("AUTH_LOGIN_RATE_LIMIT", "2/minute")
    monkeypatch.setenv("AUTH_REGISTER_RATE_LIMIT", "2/minute")
    clear_settings_cache()
    reset_engine()
    reset_rate_limits()
    client = TestClient(app)
    login_body = {"email": "person@example.com", "password": "not-the-account-password"}
    login_statuses = [
        client.post("/api/v1/auth/login", json=login_body).status_code for _ in range(2)
    ]
    blocked_login = client.post("/api/v1/auth/login", json=login_body)
    assert 429 not in login_statuses
    assert blocked_login.status_code == 429
    assert blocked_login.json()["error"]["code"] == "rate_limited"
    assert "not-the-account-password" not in blocked_login.text

    reset_rate_limits()
    register_body = {
        "display_name": "Dev Citizen",
        "email": "person@example.com",
        "password": "not-the-account-password",
    }
    register_statuses = [
        client.post("/api/v1/auth/register", json=register_body).status_code for _ in range(2)
    ]
    blocked_register = client.post("/api/v1/auth/register", json=register_body)
    assert 429 not in register_statuses
    assert blocked_register.status_code == 429
    assert "not-the-account-password" not in blocked_register.text
    reset_rate_limits()
    clear_settings_cache()
    reset_engine()


def test_production_hides_api_docs_unless_explicitly_enabled(monkeypatch) -> None:
    secret = secrets.token_urlsafe(48)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("API_HOST", "127.0.0.1")
    monkeypatch.setenv("EMAIL_VERIFICATION_DEBUG", "false")
    monkeypatch.setenv("ENABLE_API_DOCS", "false")
    monkeypatch.setenv("JWT_SECRET", secret)
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:secret@localhost:5432/civiclens")
    clear_settings_cache()
    hidden = create_app()
    assert hidden.docs_url is None
    assert hidden.redoc_url is None
    assert hidden.openapi_url is None

    monkeypatch.setenv("ENABLE_API_DOCS", "true")
    clear_settings_cache()
    shown = create_app()
    assert shown.docs_url == "/docs"
    assert shown.redoc_url == "/redoc"
    assert shown.openapi_url == "/openapi.json"
    clear_settings_cache()


@pytest.mark.postgres
def test_citizen_cannot_see_or_change_another_citizens_complaint(client, db_session) -> None:
    department = _department(db_session, f"C{uuid.uuid4().hex[:6].upper()}")
    owner = _user(db_session, UserRole.citizen)
    other = _user(db_session, UserRole.citizen)
    created = client.post(
        "/api/v1/complaints",
        json=_complaint_body(owner, department),
        headers=_auth(client, owner),
    )
    assert created.status_code == 201, created.text
    complaint_id = created.json()["id"]
    headers = _auth(client, other)
    hidden = client.get(f"/api/v1/complaints/{complaint_id}", headers=headers)
    assert hidden.status_code == 404
    assert hidden.json()["error"]["message"] == "Complaint not found."
    status_change = client.patch(
        f"/api/v1/complaints/{complaint_id}/status",
        json={"status": "rejected", "note": "This caller cannot see the complaint."},
        headers=headers,
    )
    assert status_change.status_code == 404
    review = client.post(
        f"/api/v1/complaints/{complaint_id}/reviews",
        json={"reviewer_user_id": str(other.id), "confirmed_priority": "low"},
        headers=headers,
    )
    assert review.status_code == 404
    assert review.json()["error"]["message"] == hidden.json()["error"]["message"]


@pytest.mark.postgres
def test_department_officer_cannot_modify_another_department(client, db_session) -> None:
    home = _department(db_session, f"D{uuid.uuid4().hex[:6].upper()}")
    other = _department(db_session, f"E{uuid.uuid4().hex[:6].upper()}")
    citizen = _user(db_session, UserRole.citizen)
    reviewer = _user(db_session, UserRole.grievance_officer)
    officer = _user(db_session, UserRole.department_officer, department=other)
    created = client.post(
        "/api/v1/complaints",
        json=_complaint_body(citizen, home),
        headers=_auth(client, citizen),
    )
    complaint_id = created.json()["id"]
    reviewer_headers = _auth(client, reviewer)
    triaged = client.patch(
        f"/api/v1/complaints/{complaint_id}/status",
        json={"status": "triaged", "note": "Ready for the home department."},
        headers=reviewer_headers,
    )
    assert triaged.status_code == 200, triaged.text
    assigned = client.post(
        f"/api/v1/complaints/{complaint_id}/assignments",
        json={"department_id": str(home.id)},
        headers=reviewer_headers,
    )
    assert assigned.status_code == 201, assigned.text
    outside = client.patch(
        f"/api/v1/complaints/{complaint_id}/status",
        json={"status": "in_progress", "note": "This officer is in another department."},
        headers=_auth(client, officer),
    )
    assert outside.status_code == 404
    assert outside.json()["error"]["message"] == "Complaint not found."


@pytest.mark.postgres
def test_inactive_account_cannot_log_in(client, db_session) -> None:
    user = _user(db_session, UserRole.citizen)
    stored = db_session.get(User, user.id)
    assert stored is not None
    stored.is_active = False
    db_session.flush()
    inactive = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": _PASSWORDS[user.id]},
    )
    missing = client.post(
        "/api/v1/auth/login",
        json={
            "email": f"missing.{uuid.uuid4().hex[:8]}@example.com",
            "password": _PASSWORDS[user.id],
        },
    )
    assert inactive.status_code == 401
    assert inactive.json()["error"]["code"] == "invalid_credentials"
    assert inactive.json()["error"]["message"] == missing.json()["error"]["message"]


@pytest.mark.postgres
def test_role_change_applies_to_the_existing_token(client, db_session) -> None:
    department = _department(db_session, f"F{uuid.uuid4().hex[:6].upper()}")
    citizen = _user(db_session, UserRole.citizen)
    officer = _user(db_session, UserRole.department_officer, department=department)
    reviewer = _user(db_session, UserRole.grievance_officer)
    admin = _user(db_session, UserRole.system_admin)
    created = client.post(
        "/api/v1/complaints",
        json=_complaint_body(citizen, department),
        headers=_auth(client, citizen),
    )
    complaint_id = created.json()["id"]
    reviewer_headers = _auth(client, reviewer)
    client.patch(
        f"/api/v1/complaints/{complaint_id}/status",
        json={"status": "triaged", "note": "Ready for field work."},
        headers=reviewer_headers,
    )
    client.post(
        f"/api/v1/complaints/{complaint_id}/assignments",
        json={"department_id": str(department.id), "assigned_officer_id": str(officer.id)},
        headers=reviewer_headers,
    )
    officer_headers = _auth(client, officer)
    progress = client.patch(
        f"/api/v1/complaints/{complaint_id}/status",
        json={"status": "in_progress", "note": "The assigned officer started work."},
        headers=officer_headers,
    )
    assert progress.status_code == 200, progress.text
    changed = client.patch(
        f"/api/v1/users/{officer.id}",
        json={"role": "citizen", "clear_department": True},
        headers=_auth(client, admin),
    )
    assert changed.status_code == 200, changed.text
    profile = client.get("/api/v1/auth/me", headers=officer_headers)
    assert profile.json()["role"] == "citizen"
    denied = client.patch(
        f"/api/v1/complaints/{complaint_id}/status",
        json={"status": "resolved", "note": "The old role must not still apply."},
        headers=officer_headers,
    )
    assert denied.status_code == 404


@pytest.mark.postgres
def test_unverified_citizen_cannot_submit_a_complaint(client, db_session) -> None:
    department = _department(db_session, f"V{uuid.uuid4().hex[:6].upper()}")
    password = secrets.token_urlsafe(18)
    email = f"new.{uuid.uuid4().hex[:8]}@example.com"
    created = client.post(
        "/api/v1/auth/register",
        json={"display_name": "Dev Citizen", "email": email, "password": password},
    )
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["dev_verification_token"]
    assert "password" not in body
    headers = {"Authorization": f"Bearer {body['access_token']}"}
    profile = client.get("/api/v1/auth/me", headers=headers)
    assert profile.json()["email_verified"] is False
    complaint = _complaint_body(type("Citizen", (), {"id": profile.json()["id"]})(), department)
    denied = client.post("/api/v1/complaints", json=complaint, headers=headers)
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "email_unverified"
    verified = client.post(
        "/api/v1/auth/verify-email",
        json={"token": body["dev_verification_token"]},
    )
    assert verified.status_code == 200, verified.text
    assert verified.json()["dev_verification_token"] is None
    allowed = client.post("/api/v1/complaints", json=complaint, headers=headers)
    assert allowed.status_code == 201, allowed.text
