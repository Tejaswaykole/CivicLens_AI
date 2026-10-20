"""PostgreSQL behavior. Skipped unless TEST_DATABASE_URL names a _test database."""

import secrets
import uuid
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError

from app.core.passwords import hash_password
from app.domain.enums import (
    AuditAction,
    ComplaintPriority,
    ComplaintStatus,
    NotificationType,
    SuggestionOrigin,
    UserRole,
)
from app.models import Base
from app.models.assignment import ComplaintAssignment
from app.models.complaint import Complaint
from app.models.department import Department
from app.models.human_review import HumanReview
from app.models.model_prediction import ModelPrediction
from app.models.notification import Notification
from app.models.user import User

pytestmark = pytest.mark.postgres


def _department(db, code: str, *, sla: int = 24) -> Department:
    department = Department(
        code=code,
        name=f"{code} Development Agency",
        description="Development department",
        nodal_officer_name="Dev Nodal",
        contact_email=f"{code.lower()}@example.com",
        sla_target_hours=sla,
        is_active=True,
    )
    db.add(department)
    db.flush()
    return department


_PASSWORDS: dict[uuid.UUID, str] = {}


def _user(db, role: UserRole, *, department: Department | None = None, active: bool = True) -> User:
    password = secrets.token_urlsafe(18)
    user = User(
        display_name=f"Dev {role.value}",
        email=f"{role.value}.{uuid.uuid4().hex[:8]}@example.com",
        role=role,
        is_active=active,
        email_verified=True,
        department_id=department.id if department else None,
        password_hash=hash_password(password),
        ward_or_zone="Development ward",
    )
    db.add(user)
    db.flush()
    _PASSWORDS[user.id] = password
    return user


def _auth(client, user: User) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user.email, "password": _PASSWORDS[user.id]},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]
    assert "password" not in response.json()
    return {"Authorization": f"Bearer {token}"}


def _complaint_body(
    citizen: User,
    department: Department,
    title: str = "Dark residential street",
) -> dict:
    return {
        "citizen_id": str(citizen.id),
        "title": title,
        "description": "Four consecutive lights have been dark for several nights.",
        "category": "Street Lighting",
        "location_address": "Lane 7 near the development park",
        "ward_zone": "Development ward",
        "requested_department_id": str(department.id),
    }


def test_migration_matches_models_and_revision(migrated_engine) -> None:
    from alembic.config import Config
    from alembic.runtime.migration import MigrationContext
    from alembic.script import ScriptDirectory

    inspector = inspect(migrated_engine)
    tables = set(inspector.get_table_names())
    assert set(Base.metadata.tables) <= tables
    for name, table in Base.metadata.tables.items():
        columns = {column["name"] for column in inspector.get_columns(name)}
        assert columns == {column.name for column in table.columns}, name

    with migrated_engine.connect() as connection:
        sequence = connection.execute(
            text("SELECT to_regclass('public.complaint_reference_seq')")
        ).scalar_one()
        assert sequence is not None
        context = MigrationContext.configure(connection)
        backend_root = Path(__file__).resolve().parents[1]
        config = Config(str(backend_root / "alembic.ini"))
        config.set_main_option("script_location", str(backend_root / "alembic"))
        head = ScriptDirectory.from_config(config).get_current_head()
        assert context.get_current_revision() == head

    indexes = {index["name"] for index in inspector.get_indexes("complaint_assignments")}
    assert "uq_complaint_assignments_one_current" in indexes
    foreign_keys = inspector.get_foreign_keys("complaint_status_history")
    assert foreign_keys
    for foreign_key in foreign_keys:
        ondelete = foreign_key.get("options", {}).get("ondelete", foreign_key.get("ondelete"))
        assert ondelete == "RESTRICT"


def test_health_checks_the_database(client) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "ok"
    assert body["authenticated"] is False


def test_user_response_omits_password_hash(client, db_session) -> None:
    user = _user(db_session, UserRole.citizen)
    response = client.get(f"/api/v1/users/{user.id}", headers=_auth(client, user))
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == user.email
    assert body["avatar_initials"]
    assert "password_hash" not in body
    assert "$argon2" not in response.text


def test_complaint_lifecycle_history_assignment_and_audit(client, db_session) -> None:
    department = _department(db_session, f"P{uuid.uuid4().hex[:6].upper()}")
    other = _department(db_session, f"Q{uuid.uuid4().hex[:6].upper()}", sla=12)
    citizen = _user(db_session, UserRole.citizen)
    officer = _user(db_session, UserRole.department_officer, department=department)
    reviewer = _user(db_session, UserRole.grievance_officer)
    admin = _user(db_session, UserRole.system_admin)
    citizen_headers = _auth(client, citizen)
    reviewer_headers = _auth(client, reviewer)
    admin_headers = _auth(client, admin)

    created = client.post(
        "/api/v1/complaints",
        json=_complaint_body(citizen, department),
        headers=citizen_headers,
    )
    assert created.status_code == 201, created.text
    complaint = created.json()
    assert complaint["status"] == "submitted"
    assert complaint["predictions"] == []
    assert complaint["confirmed_priority"] is None
    assert complaint["public_reference"].startswith("DEL-")
    assert len(complaint["public_reference"]) == 15
    assert complaint["status_history"][0]["previous_status"] is None
    assert complaint["status_history"][0]["actor_verified"] is True
    assert complaint["requested_department"]["id"] == str(department.id)
    assert complaint["department"] is None

    missing = client.get(f"/api/v1/complaints/{uuid.uuid4()}", headers=citizen_headers)
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "not_found"

    blocked = client.patch(
        f"/api/v1/complaints/{complaint['id']}/status",
        json={"status": "resolved", "note": "This jump is not allowed."},
        headers=admin_headers,
    )
    assert blocked.status_code == 409
    assert blocked.json()["error"]["code"] == "invalid_status_transition"

    too_early = client.post(
        f"/api/v1/complaints/{complaint['id']}/assignments",
        json={"department_id": str(department.id)},
        headers=reviewer_headers,
    )
    assert too_early.status_code == 409

    triaged = client.patch(
        f"/api/v1/complaints/{complaint['id']}/status",
        json={
            "status": "triaged",
            "note": "Queued for a department.",
            "actor_user_id": str(reviewer.id),
            "actor_label": "unverified label",
        },
        headers=reviewer_headers,
    )
    assert triaged.status_code == 200, triaged.text
    assert triaged.json()["status"] == "triaged"
    assert len(triaged.json()["status_history"]) == 2
    assert triaged.json()["status_history"][-1]["actor_verified"] is True

    wrong_officer = _user(db_session, UserRole.citizen)
    rejected_officer = client.post(
        f"/api/v1/complaints/{complaint['id']}/assignments",
        json={"department_id": str(department.id), "assigned_officer_id": str(wrong_officer.id)},
        headers=reviewer_headers,
    )
    assert rejected_officer.status_code == 409

    assigned = client.post(
        f"/api/v1/complaints/{complaint['id']}/assignments",
        json={
            "department_id": str(department.id),
            "assigned_officer_id": str(officer.id),
            "assigned_crew_unit": "Development unit",
            "note": "First assignment.",
            "actor_user_id": str(reviewer.id),
        },
        headers=reviewer_headers,
    )
    assert assigned.status_code == 201, assigned.text
    assert assigned.json()["is_current"] is True
    assert assigned.json()["complaint_status"] == "assigned"

    reassigned = client.post(
        f"/api/v1/complaints/{complaint['id']}/assignments",
        json={"department_id": str(other.id), "note": "Moved to another agency."},
        headers=reviewer_headers,
    )
    assert reassigned.status_code == 201, reassigned.text
    detail = client.get(f"/api/v1/complaints/{complaint['id']}", headers=reviewer_headers)
    assert detail.status_code == 200
    assignments = detail.json()["assignments"]
    assert len(assignments) == 2
    assert sum(item["is_current"] for item in assignments) == 1
    assert detail.json()["department"]["id"] == str(other.id)
    assert detail.json()["resolution_due_at"] is not None

    audit = client.get(
        "/api/v1/audit-logs",
        params={"entity_id": complaint["id"], "page_size": 20},
        headers=admin_headers,
    )
    assert audit.status_code == 200
    actions = {item["action"] for item in audit.json()["items"]}
    assert {"COMPLAINT_CREATED", "STATUS_CHANGE", "ASSIGNMENT_CREATED"} <= actions
    assert all(item["actor_verified"] is True for item in audit.json()["items"])

    notices = client.get(
        "/api/v1/notifications",
        params={"recipient_role": "grievance_officer", "page_size": 100},
        headers=reviewer_headers,
    )
    assert notices.status_code == 200
    match = next(
        item for item in notices.json()["items"] if complaint["public_reference"] in item["title"]
    )
    marked = client.patch(
        f"/api/v1/notifications/{match['id']}/read",
        headers=reviewer_headers,
    )
    assert marked.status_code == 200
    assert marked.json()["is_read"] is True
    again = client.patch(
        f"/api/v1/notifications/{match['id']}/read",
        headers=reviewer_headers,
    )
    assert again.json()["is_read"] is True


def test_pagination_and_filters(client, db_session) -> None:
    department = _department(db_session, f"F{uuid.uuid4().hex[:6].upper()}")
    citizen = _user(db_session, UserRole.citizen)
    admin = _user(db_session, UserRole.system_admin)
    citizen_headers = _auth(client, citizen)
    admin_headers = _auth(client, admin)
    for index in range(3):
        response = client.post(
            "/api/v1/complaints",
            json=_complaint_body(citizen, department, title=f"Development pothole {index} report"),
            headers=citizen_headers,
        )
        assert response.status_code == 201, response.text

    page = client.get(
        "/api/v1/complaints",
        params={"citizen_id": str(citizen.id), "page": 1, "page_size": 2},
        headers=citizen_headers,
    )
    assert page.status_code == 200
    body = page.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert body["page"] == 1

    filtered = client.get(
        "/api/v1/complaints",
        params={
            "citizen_id": str(citizen.id),
            "status": "submitted",
            "category": "Street Lighting",
        },
        headers=citizen_headers,
    )
    assert filtered.json()["total"] == 3

    users = client.get(
        "/api/v1/users",
        params={"role": "citizen", "q": citizen.email},
        headers=admin_headers,
    )
    assert users.status_code == 200
    assert users.json()["total"] == 1
    assert "password_hash" not in users.text

    departments = client.get(
        "/api/v1/departments",
        params={"q": department.code},
        headers=citizen_headers,
    )
    assert departments.status_code == 200
    assert departments.json()["total"] == 1
    assert departments.json()["items"][0]["active_cases_count"] == 0


def test_human_review_rules_and_audit(client, db_session) -> None:
    department = _department(db_session, f"R{uuid.uuid4().hex[:6].upper()}")
    citizen = _user(db_session, UserRole.citizen)
    reviewer = _user(db_session, UserRole.grievance_officer)
    admin = _user(db_session, UserRole.system_admin)
    citizen_headers = _auth(client, citizen)
    reviewer_headers = _auth(client, reviewer)
    admin_headers = _auth(client, admin)
    created = client.post(
        "/api/v1/complaints",
        json=_complaint_body(citizen, department),
        headers=citizen_headers,
    )
    complaint_id = created.json()["id"]

    missing_reason = client.post(
        f"/api/v1/complaints/{complaint_id}/reviews",
        json={
            "reviewer_user_id": str(reviewer.id),
            "suggested_priority": "low",
            "confirmed_priority": "critical",
            "justification": "short",
        },
        headers=reviewer_headers,
    )
    assert missing_reason.status_code == 422

    unknown_reviewer = client.post(
        f"/api/v1/complaints/{complaint_id}/reviews",
        json={
            "reviewer_user_id": str(uuid.uuid4()),
            "suggested_priority": "high",
            "confirmed_priority": "high",
        },
        headers=reviewer_headers,
    )
    assert unknown_reviewer.status_code == 403

    prediction = ModelPrediction(
        complaint_id=uuid.UUID(complaint_id),
        model_identifier="not-a-production-model",
        model_version="test-fixture",
        suggested_priority=ComplaintPriority.high,
        confidence=None,
        explanation={"source": "test fixture"},
    )
    db_session.add(prediction)
    db_session.commit()

    mismatch = client.post(
        f"/api/v1/complaints/{complaint_id}/reviews",
        json={
            "reviewer_user_id": str(reviewer.id),
            "suggested_priority": "low",
            "confirmed_priority": "low",
        },
        headers=reviewer_headers,
    )
    assert mismatch.status_code == 409
    assert mismatch.json()["error"]["code"] == "suggestion_mismatch"

    override = client.post(
        f"/api/v1/complaints/{complaint_id}/reviews",
        json={
            "reviewer_user_id": str(reviewer.id),
            "confirmed_priority": "critical",
            "justification": "The stored suggestion does not match the reported hazard.",
        },
        headers=reviewer_headers,
    )
    assert override.status_code == 201, override.text
    body = override.json()
    assert body["suggestion_origin"] == SuggestionOrigin.stored_prediction.value
    assert body["suggested_priority"] == "high"
    assert body["confirmed_priority"] == "critical"
    assert body["complaint_status"] == ComplaintStatus.triaged.value

    detail = client.get(f"/api/v1/complaints/{complaint_id}", headers=reviewer_headers)
    assert detail.json()["confirmed_priority"] == "critical"
    assert detail.json()["predictions"][0]["confidence"] is None
    assert detail.json()["predictions"][0]["explanation"] == {"source": "test fixture"}

    audit = client.get(
        "/api/v1/audit-logs",
        params={"entity_id": complaint_id, "action": AuditAction.HITL_OVERRIDE.value},
        headers=admin_headers,
    )
    assert audit.json()["total"] == 1
    metadata = audit.json()["items"][0]["event_metadata"]
    assert "description" not in metadata
    assert metadata["public_reference"] == detail.json()["public_reference"]


def test_database_constraints(db_session) -> None:
    user = _user(db_session, UserRole.citizen)
    duplicate = User(
        display_name="Dev duplicate",
        email=user.email,
        role=UserRole.citizen,
        is_active=True,
    )
    db_session.add(duplicate)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    user = _user(db_session, UserRole.citizen)
    complaint = Complaint(
        public_reference="NOT-A-REFERENCE",
        citizen_id=user.id,
        title="Broken footpath",
        description="The footpath has been broken for several days.",
        category="Road Infrastructure",
        location_address="Development lane",
        status=ComplaintStatus.submitted,
    )
    db_session.add(complaint)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    user = _user(db_session, UserRole.citizen)
    complaint = Complaint(
        public_reference="DEL-2026-000001",
        citizen_id=user.id,
        title="Broken footpath",
        description="The footpath has been broken for several days.",
        category="Not a frontend category",
        location_address="Development lane",
        status=ComplaintStatus.submitted,
    )
    db_session.add(complaint)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    department = _department(db_session, f"G{uuid.uuid4().hex[:6].upper()}")
    user = _user(db_session, UserRole.citizen)
    complaint = Complaint(
        public_reference=f"DEL-2026-{uuid.uuid4().int % 1_000_000:06d}",
        citizen_id=user.id,
        title="Broken footpath",
        description="The footpath has been broken for several days.",
        category="Road Infrastructure",
        location_address="Development lane",
        status=ComplaintStatus.submitted,
    )
    db_session.add(complaint)
    db_session.flush()
    first = ComplaintAssignment(
        complaint_id=complaint.id,
        department_id=department.id,
        is_current=True,
    )
    second = ComplaintAssignment(
        complaint_id=complaint.id,
        department_id=department.id,
        is_current=True,
    )
    db_session.add_all([first, second])
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    department = _department(db_session, f"H{uuid.uuid4().hex[:6].upper()}")
    user = _user(db_session, UserRole.citizen)
    reviewer = _user(db_session, UserRole.grievance_officer)
    complaint = Complaint(
        public_reference=f"DEL-2026-{uuid.uuid4().int % 1_000_000:06d}",
        citizen_id=user.id,
        title="Broken footpath",
        description="The footpath has been broken for several days.",
        category="Road Infrastructure",
        location_address="Development lane",
        status=ComplaintStatus.submitted,
    )
    db_session.add(complaint)
    db_session.flush()
    review = HumanReview(
        complaint_id=complaint.id,
        reviewer_user_id=reviewer.id,
        suggested_priority=ComplaintPriority.low,
        confirmed_priority=ComplaintPriority.critical,
        suggestion_origin=SuggestionOrigin.client_supplied,
        justification="short",
    )
    db_session.add(review)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    department = _department(db_session, f"I{uuid.uuid4().hex[:6].upper()}")
    user = _user(db_session, UserRole.citizen)
    complaint = Complaint(
        public_reference=f"DEL-2026-{uuid.uuid4().int % 1_000_000:06d}",
        citizen_id=user.id,
        title="Broken footpath",
        description="The footpath has been broken for several days.",
        category="Road Infrastructure",
        location_address="Development lane",
        status=ComplaintStatus.submitted,
    )
    db_session.add(complaint)
    db_session.flush()
    prediction = ModelPrediction(
        complaint_id=complaint.id,
        model_identifier="constraint-fixture",
        model_version="0",
        confidence=Decimal("1.5000"),
    )
    db_session.add(prediction)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()

    notice = Notification(
        notification_type=NotificationType.info,
        title="No recipient",
        message="This row should be rejected.",
    )
    db_session.add(notice)
    with pytest.raises(IntegrityError):
        db_session.flush()
    db_session.rollback()
