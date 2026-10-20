"""Audit log responses. Entries are operational records, not cryptographic proofs."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.domain.enums import AuditAction, UserRole


class AuditActor(BaseModel):
    id: uuid.UUID
    display_name: str
    role: UserRole


class AuditLogRead(BaseModel):
    id: uuid.UUID
    action: AuditAction
    entity_type: str
    entity_id: uuid.UUID
    summary: str
    event_metadata: dict[str, Any] | None
    actor: AuditActor | None
    actor_verified: bool = False
    created_at: datetime
