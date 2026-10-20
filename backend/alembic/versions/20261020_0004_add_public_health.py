"""Add Public Health category constraint.

Revision ID: 20261020_0004
Revises: 20261020_0003
Create Date: 2026-10-20

Expands the known_category check constraint on the complaints table to accept
all six canonical CivicLens categories:
- Road Infrastructure
- Water & Sewage
- Electrical Hazard
- Sanitation & Solid Waste
- Street Lighting
- Public Health

Downgrade safety:
Downgrade safely verifies whether any complaints currently hold category
'Public Health'. If such records exist, downgrade is aborted to prevent data
corruption or constraint violations. If no Public Health complaints exist,
the original five-category constraint is restored.
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20261020_0004"
down_revision: str | Sequence[str] | None = "20261020_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SIX_CATEGORIES_CONSTRAINT = (
    "category IN ('Road Infrastructure', 'Water & Sewage', 'Electrical Hazard', "
    "'Sanitation & Solid Waste', 'Street Lighting', 'Public Health')"
)

FIVE_CATEGORIES_CONSTRAINT = (
    "category IN ('Road Infrastructure', 'Water & Sewage', 'Electrical Hazard', "
    "'Sanitation & Solid Waste', 'Street Lighting')"
)


def upgrade() -> None:
    # Drop the existing five-category check constraint
    op.drop_constraint("known_category", "complaints", type_="check")
    # Add the six-category check constraint
    op.create_check_constraint(
        "known_category",
        "complaints",
        SIX_CATEGORIES_CONSTRAINT,
    )


def downgrade() -> None:
    bind = op.get_bind()
    has_ph = bind.execute(
        sa.text("SELECT 1 FROM complaints WHERE category = 'Public Health' LIMIT 1")
    ).scalar()
    if has_ph:
        raise RuntimeError(
            "Cannot downgrade migration 20261020_0004: 'Public Health' complaints exist in the database. "
            "Resolve, reassign, or archive these records before removing the category."
        )
    op.drop_constraint("known_category", "complaints", type_="check")
    op.create_check_constraint(
        "known_category",
        "complaints",
        FIVE_CATEGORIES_CONSTRAINT,
    )
