"""Department reads."""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, pagination_params
from app.core.database import get_db
from app.models.user import User
from app.schemas.common import Page, PageParams
from app.schemas.department import DepartmentRead
from app.services import departments as department_service

router = APIRouter(
    prefix="/departments",
    tags=["departments"],
    dependencies=[Depends(get_current_user)],
)


@router.get("", response_model=Page[DepartmentRead])
def list_departments(
    is_active: bool | None = None,
    q: str | None = Query(default=None, max_length=200),
    params: PageParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Page[DepartmentRead]:
    return department_service.list_agencies(db, params, is_active=is_active, query=q)


@router.get("/{department_id}", response_model=DepartmentRead)
def get_department(
    department_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DepartmentRead:
    return department_service.get_agency(db, department_id)
