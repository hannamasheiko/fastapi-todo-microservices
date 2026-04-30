"""rename completion rate to percent

Revision ID: 05ee11c5f594
Revises: 7a65dd8af0ee
Create Date: 2026-04-30 12:23:25.193090

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "05ee11c5f594"
down_revision: Union[str, Sequence[str], None] = "7a65dd8af0ee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1. Rename the existing column.
    # This preserves the physical column position in PostgreSQL.
    op.alter_column(
        "user_analytics",
        "completion_rate",
        new_column_name="completion_rate_percent",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )

    # 2. Change the renamed column type from Integer to Float.
    op.alter_column(
        "user_analytics",
        "completion_rate_percent",
        existing_type=sa.Integer(),
        type_=sa.Float(),
        existing_nullable=False,
        postgresql_using="completion_rate_percent::double precision",
    )


def downgrade() -> None:
    """Downgrade schema."""

    # 1. Change the column type back from Float to Integer.
    op.alter_column(
        "user_analytics",
        "completion_rate_percent",
        existing_type=sa.Float(),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="completion_rate_percent::integer",
    )

    # 2. Rename the column back.
    op.alter_column(
        "user_analytics",
        "completion_rate_percent",
        new_column_name="completion_rate",
        existing_type=sa.Integer(),
        existing_nullable=False,
    )