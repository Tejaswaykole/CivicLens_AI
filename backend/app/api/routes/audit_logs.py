"""Audit reads. Unprotected in Phase 3, and not a cryptographic ledger."""

import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import pagination_params
from app.core.database import get_db
from app.domain.enums import AuditAction
from app.schemas.audit import AuditLogRead
from app.schemas.common import Page, PageParams
from app.services import audit as audit_service

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=Page[AuditLogRead])
def list_audit_logs(
    action: AuditAction | None = None,
    entity_type: str | None = Query(default=None, max_length=64),
    entity_id: uuid.UUID | None = None,
    actor_user_id: uuid.UUID | None = None,
    q: str | None = Query(default=None, max_length=200),
    created_from: datetime | None = None,
    created_to: datetime | None = None,
    params: PageParams = Depends(pagination_params),
    db: Session = Depends(get_db),
) -> Page[AuditLogRead]:
    """List audit events. This endpoint is not authenticated."""
    return audit_service.list_entries(
        db,
        params,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        query=q,
        created_from=created_from,
        created_to=created_to,
    )
