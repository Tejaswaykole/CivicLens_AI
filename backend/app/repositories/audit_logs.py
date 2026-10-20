"""Audit log queries."""

import uuid
from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.domain.enums import AuditAction
from app.models.audit_log import AuditLog
from app.models.user import User
from app.repositories.query import contains_pattern
from app.schemas.common import PageParams


def list_audit_logs(
    db: Session,
    params: PageParams,
    *,
    action: AuditAction | None,
    entity_type: str | None,
    entity_id: uuid.UUID | None,
    actor_user_id: uuid.UUID | None,
    query: str | None,
    created_from: datetime | None,
    created_to: datetime | None,
) -> tuple[list[AuditLog], int]:
    criteria = []
    if action is not None:
        criteria.append(AuditLog.action == action)
    if entity_type:
        criteria.append(AuditLog.entity_type == entity_type)
    if entity_id is not None:
        criteria.append(AuditLog.entity_id == entity_id)
    if actor_user_id is not None:
        criteria.append(AuditLog.actor_user_id == actor_user_id)
    if created_from is not None:
        criteria.append(AuditLog.created_at >= created_from)
    if created_to is not None:
        criteria.append(AuditLog.created_at <= created_to)
    if query:
        pattern = contains_pattern(query.strip())
        criteria.append(
            or_(
                AuditLog.summary.ilike(pattern, escape="\\"),
                AuditLog.actor.has(User.display_name.ilike(pattern, escape="\\")),
            )
        )
    stmt = select(AuditLog).options(joinedload(AuditLog.actor)).where(*criteria)
    total = db.scalar(select(func.count()).select_from(AuditLog).where(*criteria)) or 0
    rows = db.scalars(
        stmt.order_by(AuditLog.created_at.desc()).offset(params.offset).limit(params.page_size)
    ).unique()
    return list(rows), int(total)
