"""Initial CivicLens schema.

Revision ID: 20261020_0001
Revises:
Create Date: 2026-10-20

Creates the Phase 3 tables from the SQLAlchemy metadata so the database matches
the models, plus the complaint reference sequence. Downgrade drops that schema.
Do not run the downgrade against a database you need to keep.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op
from app.models import Base

revision: str = "20261020_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

ENUM_NAMES = (
    "audit_action",
    "complaint_priority",
    "complaint_status",
    "notification_type",
    "suggestion_origin",
    "user_role",
)


def upgrade() -> None:
    op.execute(sa.text("CREATE SEQUENCE IF NOT EXISTS complaint_reference_seq"))
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
    op.execute(sa.text("DROP SEQUENCE IF EXISTS complaint_reference_seq"))
    for enum_name in ENUM_NAMES:
        op.execute(sa.text(f"DROP TYPE IF EXISTS {enum_name}"))
