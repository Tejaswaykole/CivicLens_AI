"""Write and list audit events without storing complaint bodies or secrets."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.domain.enums import AuditAction
from app.models.audit_log import AuditLog
from app.repositories.audit_logs import list_audit_logs
from app.schemas.audit import AuditLogRead
from app.schemas.common import Page, PageParams
from app.schemas.mappers import audit_to_read


def record_audit(
    db: Session,
    *,
    action: AuditAction,
    entity_type: str,
    entity_id: uuid.UUID,
    summary: str,
    actor_user_id: uuid.UUID | None = None,
    event_metadata: dict[str, Any] | None = None,
) -> None:
    cleaned = " ".join(summary.split())
    if len(cleaned) > 300:
        cleaned = cleaned[:297] + "..."
    db.add(
        AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            summary=cleaned,
            actor_user_id=actor_user_id,
            event_metadata=event_metadata,
        )
    )


def list_entries(
    db: Session,
    params: PageParams,
    *,
    action: AuditAction | None = None,
    entity_type: str | None = None,
    entity_id: uuid.UUID | None = None,
    actor_user_id: uuid.UUID | None = None,
    query: str | None = None,
    created_from: datetime | None = None,
    created_to: datetime | None = None,
) -> Page[AuditLogRead]:
    rows, total = list_audit_logs(
        db,
        params,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        query=query,
        created_from=created_from,
        created_to=created_to,
    )
    return Page(
        items=[audit_to_read(row) for row in rows],
        page=params.page,
        page_size=params.page_size,
        total=total,
    )
