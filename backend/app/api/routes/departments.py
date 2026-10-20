"""Department reads."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import pagination_params
from app.core.database import get_db
from app.schemas.common import Page, PageParams
from app.schemas.department import DepartmentRead
from app.services import departments as department_service

router = APIRouter(prefix="/departments", tags=["departments"])


@router.get("", response_model=Page[DepartmentRead])
def list_departments(
    is_active: bool | None = None,
    q: str | None = Query(default=None, max_length=200),
    params: PageParams = Depends(pagination_params),
    db: Session = Depends(get_db),
) -> Page[DepartmentRead]:
    return department_service.list_agencies(db, params, is_active=is_active, query=q)


@router.get("/{department_id}", response_model=DepartmentRead)
def get_department(department_id: uuid.UUID, db: Session = Depends(get_db)) -> DepartmentRead:
    return department_service.get_agency(db, department_id)
