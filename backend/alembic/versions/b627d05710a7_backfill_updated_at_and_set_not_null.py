"""backfill_updated_at_and_set_not_null

Backfills NULL updated_at values with created_at, adds a server default of
NOW(), and sets the column NOT NULL so the API never returns a null datetime.

Revision ID: b627d05710a7
Revises: 5992edda0113
Create Date: 2026-06-21 19:27:37.833928
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b627d05710a7'
down_revision: Union[str, None] = '5992edda0113'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Fill any NULLs left from the previous migration with the row's created_at.
    op.execute("UPDATE products SET updated_at = created_at WHERE updated_at IS NULL")

    # Now safe to enforce NOT NULL and add a server-side default.
    op.alter_column(
        "products",
        "updated_at",
        nullable=False,
        server_default=sa.text("NOW()"),
    )


def downgrade() -> None:
    op.alter_column(
        "products",
        "updated_at",
        nullable=True,
        server_default=None,
    )
