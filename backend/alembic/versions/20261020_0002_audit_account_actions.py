"""Add account audit actions.

Revision ID: 20261020_0002
Revises: 20261020_0001
Create Date: 2026-10-20

Adds ACCOUNT_CREATED, ROLE_CHANGED, and ACCOUNT_UPDATED to the audit_action
enum. Fresh databases already receive these labels from the models. This
migration adds them only when an existing database is missing a label.

Downgrade is a no-op. PostgreSQL cannot remove one enum label without
recreating the type and rewriting every column that uses it.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261020_0002"
down_revision: str | Sequence[str] | None = "20261020_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

NEW_LABELS = ("ACCOUNT_CREATED", "ROLE_CHANGED", "ACCOUNT_UPDATED")


def upgrade() -> None:
    for label in NEW_LABELS:
        with op.get_context().autocommit_block():
            op.execute(
                sa.text(
                    f"""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1
                            FROM pg_enum
                            WHERE enumlabel = '{label}'
                              AND enumtypid = 'audit_action'::regtype
                        ) THEN
                            ALTER TYPE audit_action ADD VALUE '{label}';
                        END IF;
                    END $$;
                    """
                )
            )


def downgrade() -> None:
    pass
