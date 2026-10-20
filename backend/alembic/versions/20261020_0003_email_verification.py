"""Add email verification state.

Revision ID: 20261020_0003
Revises: 20261020_0002
Create Date: 2026-10-20

Adds email verification columns. Existing accounts are marked verified so
current citizens can still submit complaints. New registrations set the flag
in application code.

Downgrade drops only these columns. Do not run it against a database you need
to keep.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261020_0003"
down_revision: str | Sequence[str] | None = "20261020_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _columns() -> set[str]:
    return {column["name"] for column in sa.inspect(op.get_bind()).get_columns("users")}


def upgrade() -> None:
    columns = _columns()
    if "email_verified" not in columns:
        op.add_column("users", sa.Column("email_verified", sa.Boolean(), nullable=True))
        op.execute(sa.text("UPDATE users SET email_verified = true WHERE email_verified IS NULL"))
        op.alter_column(
            "users",
            "email_verified",
            nullable=False,
            server_default=sa.false(),
        )
    if "email_verification_token_hash" not in columns:
        op.add_column(
            "users",
            sa.Column("email_verification_token_hash", sa.String(length=64), nullable=True),
        )
    if "email_verification_expires_at" not in columns:
        op.add_column(
            "users",
            sa.Column("email_verification_expires_at", sa.DateTime(timezone=True), nullable=True),
        )
    indexes = {index["name"] for index in sa.inspect(op.get_bind()).get_indexes("users")}
    if "ix_users_email_verification_token_hash" not in indexes:
        op.create_index(
            "ix_users_email_verification_token_hash",
            "users",
            ["email_verification_token_hash"],
        )


def downgrade() -> None:
    indexes = {index["name"] for index in sa.inspect(op.get_bind()).get_indexes("users")}
    if "ix_users_email_verification_token_hash" in indexes:
        op.drop_index("ix_users_email_verification_token_hash", table_name="users")
    columns = _columns()
    for name in (
        "email_verification_expires_at",
        "email_verification_token_hash",
        "email_verified",
    ):
        if name in columns:
            op.drop_column("users", name)
