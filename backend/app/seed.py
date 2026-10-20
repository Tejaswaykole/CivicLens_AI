"""Optional development seed.

Run explicitly with `python -m app.seed` from the backend directory.
Startup never calls this module. It refuses to run when APP_ENV=production.

The rows are fictional development records. They use the department codes,
names, descriptions, and SLA hours from the frontend mock data, with example.com
contacts instead of the mock personal names and government addresses.
No complaints, predictions, or metrics are created. Password hashes are left null.
"""

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_engine
from app.domain.enums import UserRole
from app.models.department import Department
from app.models.user import User

DEPARTMENTS: tuple[dict, ...] = (
    {
        "code": "PWD",
        "name": "Public Works Department (PWD)",
        "description": "Roads, flyovers, storm-water drains and arterial civic assets.",
        "nodal_officer_name": "Dev Nodal PWD",
        "contact_email": "pwd.nodal@example.com",
        "sla_target_hours": 48,
    },
    {
        "code": "DJB",
        "name": "Delhi Jal Board (DJB)",
        "description": "Potable water supply, sewer pipeline leaks, and contamination triage.",
        "nodal_officer_name": "Dev Nodal DJB",
        "contact_email": "djb.nodal@example.com",
        "sla_target_hours": 24,
    },
    {
        "code": "MCD",
        "name": "Municipal Corporation (MCD)",
        "description": "Solid waste management, sanitation, street sweeping, and parks.",
        "nodal_officer_name": "Dev Nodal MCD",
        "contact_email": "mcd.nodal@example.com",
        "sla_target_hours": 36,
    },
    {
        "code": "BSES",
        "name": "Power Distribution (DISCOM)",
        "description": "Faulty streetlights, transformer sparking, and low-hanging cables.",
        "nodal_officer_name": "Dev Nodal BSES",
        "contact_email": "bses.nodal@example.com",
        "sla_target_hours": 12,
    },
)

USERS: tuple[dict, ...] = (
    {
        "email": "dev.admin@example.com",
        "display_name": "Dev System Admin",
        "role": UserRole.system_admin,
        "designation": "Development system administrator",
        "ward_or_zone": "Development zone",
        "department_code": None,
    },
    {
        "email": "dev.triage@example.com",
        "display_name": "Dev Grievance Officer",
        "role": UserRole.grievance_officer,
        "designation": "Development triage officer",
        "ward_or_zone": "Development zone",
        "department_code": None,
    },
    {
        "email": "dev.field.pwd@example.com",
        "display_name": "Dev Department Officer",
        "role": UserRole.department_officer,
        "designation": "Development field officer",
        "ward_or_zone": "Development zone",
        "department_code": "PWD",
    },
    {
        "email": "dev.citizen@example.com",
        "display_name": "Dev Citizen",
        "role": UserRole.citizen,
        "designation": None,
        "ward_or_zone": "Development ward",
        "department_code": None,
    },
)


def _upsert_department(session: Session, spec: dict) -> str:
    department = session.scalar(select(Department).where(Department.code == spec["code"]))
    created = department is None
    if department is None:
        department = Department(is_active=True, **spec)
        session.add(department)
    else:
        for key, value in spec.items():
            setattr(department, key, value)
        department.is_active = True
    return "created" if created else "updated"


def _upsert_user(session: Session, spec: dict, departments: dict[str, Department]) -> str:
    email = spec["email"].lower()
    user = session.scalar(select(User).where(User.email == email))
    department_id = None
    if spec["department_code"] is not None:
        department_id = departments[spec["department_code"]].id
    created = user is None
    if user is None:
        user = User(
            email=email,
            display_name=spec["display_name"],
            role=spec["role"],
            designation=spec["designation"],
            ward_or_zone=spec["ward_or_zone"],
            department_id=department_id,
            is_active=True,
            password_hash=None,
        )
        session.add(user)
    else:
        user.display_name = spec["display_name"]
        user.role = spec["role"]
        user.designation = spec["designation"]
        user.ward_or_zone = spec["ward_or_zone"]
        user.department_id = department_id
        user.is_active = True
    return "created" if created else "updated"


def seed(session: Session) -> dict[str, int]:
    counts = {
        "departments_created": 0,
        "departments_updated": 0,
        "users_created": 0,
        "users_updated": 0,
    }
    departments: dict[str, Department] = {}
    for spec in DEPARTMENTS:
        action = _upsert_department(session, spec)
        counts[f"departments_{action}"] += 1
        session.flush()
        department = session.scalar(select(Department).where(Department.code == spec["code"]))
        if department is None:
            raise RuntimeError(f"Department {spec['code']} was not saved.")
        departments[spec["code"]] = department
    for spec in USERS:
        action = _upsert_user(session, spec, departments)
        counts[f"users_{action}"] += 1
    session.flush()
    return counts


def main() -> None:
    settings = get_settings()
    if settings.app_env == "production":
        raise SystemExit("Refusing to seed when APP_ENV=production.")
    if settings.database_url is None:
        raise SystemExit(
            "DATABASE_URL is not configured. Copy backend/.env.example to backend/.env first."
        )
    engine = get_engine()
    if engine is None:
        raise SystemExit("Database engine is not available.")
    try:
        with Session(engine) as session:
            counts = seed(session)
            session.commit()
    except SQLAlchemyError as exc:
        raise SystemExit(
            f"Seed failed ({type(exc).__name__}) for {settings.database_target_label()}."
        ) from None
    print("Development seed completed. No passwords or model predictions were written.")
    for key, value in counts.items():
        print(f"{key}={value}")


if __name__ == "__main__":
    main()
