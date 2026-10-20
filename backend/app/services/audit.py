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

_SECRET_KEYS = ("password", "token", "secret", "authorization", "jwt", "credential")
_MAX_TEXT = 300


def _sensitive_text(value: str) -> bool:
    lowered = value.lower()
    if lowered.startswith("bearer ") or lowered.startswith("eyj"):
        return True
    return any(marker in lowered for marker in ("password=", "token=", "secret=", "jwt="))


def _scalar(value: Any) -> Any:
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    if isinstance(value, str):
        if _sensitive_text(value):
            return None
        return value[:_MAX_TEXT]
    return None


def _public_metadata(event_metadata: dict[str, Any] | None) -> dict[str, Any] | None:
    """Keep scalar audit fields. Nested objects and secret-like values are dropped."""
    if not isinstance(event_metadata, dict):
        return None
    cleaned: dict[str, Any] = {}
    for key, value in event_metadata.items():
        if not isinstance(key, str) or any(marker in key.lower() for marker in _SECRET_KEYS):
            continue
        if isinstance(value, list | tuple):
            items = []
            for item in value:
                if isinstance(item, dict | list | tuple):
                    items = None
                    break
                scalar = _scalar(item)
                if item is not None and scalar is None:
                    items = None
                    break
                items.append(scalar)
            if items:
                cleaned[key] = items
            continue
        if isinstance(value, dict):
            continue
        scalar = _scalar(value)
        if value is not None and scalar is None:
            continue
        if scalar is not None or value is None:
            cleaned[key] = scalar
    return cleaned or None


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
            event_metadata=_public_metadata(event_metadata),
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
