"""Read-only department queries. Case counts are calculated, not stored."""

import uuid

from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.repositories.departments import get_department_with_counts, list_departments
from app.schemas.common import Page, PageParams
from app.schemas.department import DepartmentRead
from app.schemas.mappers import department_to_read


def list_agencies(
    db: Session,
    params: PageParams,
    *,
    is_active: bool | None,
    query: str | None,
) -> Page[DepartmentRead]:
    rows, total = list_departments(db, params, is_active=is_active, query=query)
    return Page(
        items=[
            department_to_read(department, active_cases_count=active, resolved_count=resolved)
            for department, active, resolved in rows
        ],
        page=params.page,
        page_size=params.page_size,
        total=total,
    )


def get_agency(db: Session, department_id: uuid.UUID) -> DepartmentRead:
    row = get_department_with_counts(db, department_id)
    if row is None:
        raise AppError("not_found", "Department not found.", 404)
    department, active, resolved = row
    return department_to_read(department, active_cases_count=active, resolved_count=resolved)
