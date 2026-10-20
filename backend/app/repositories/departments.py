"""Department queries and complaint counts."""

import uuid

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.domain.enums import OPEN_COMPLAINT_STATUSES, ComplaintStatus
from app.models.complaint import Complaint
from app.models.department import Department
from app.repositories.query import contains_pattern
from app.schemas.common import PageParams


def _count_subquery(*criteria):
    return (
        select(func.count(Complaint.id))
        .where(Complaint.department_id == Department.id, *criteria)
        .scalar_subquery()
    )


def get_department(db: Session, department_id: uuid.UUID) -> Department | None:
    return db.get(Department, department_id)


def get_department_with_counts(
    db: Session,
    department_id: uuid.UUID,
) -> tuple[Department, int, int] | None:
    active_count = _count_subquery(Complaint.status.in_(OPEN_COMPLAINT_STATUSES))
    resolved_count = _count_subquery(Complaint.status == ComplaintStatus.resolved)
    row = db.execute(
        select(
            Department,
            active_count.label("active_cases_count"),
            resolved_count.label("resolved_count"),
        ).where(Department.id == department_id)
    ).one_or_none()
    if row is None:
        return None
    return row[0], int(row[1]), int(row[2])


def list_departments(
    db: Session,
    params: PageParams,
    *,
    is_active: bool | None,
    query: str | None,
) -> tuple[list[tuple[Department, int, int]], int]:
    criteria = []
    if is_active is not None:
        criteria.append(Department.is_active == is_active)
    if query:
        pattern = contains_pattern(query.strip())
        criteria.append(
            or_(
                Department.name.ilike(pattern, escape="\\"),
                Department.code.ilike(pattern, escape="\\"),
            )
        )
    active_count = _count_subquery(Complaint.status.in_(OPEN_COMPLAINT_STATUSES))
    resolved_count = _count_subquery(Complaint.status == ComplaintStatus.resolved)
    stmt = select(
        Department,
        active_count.label("active_cases_count"),
        resolved_count.label("resolved_count"),
    ).where(*criteria)
    total = db.scalar(select(func.count()).select_from(Department).where(*criteria)) or 0
    rows = db.execute(
        stmt.order_by(Department.name.asc()).offset(params.offset).limit(params.page_size)
    ).all()
    return [(row[0], int(row[1]), int(row[2])) for row in rows], int(total)
