"""add server defaults to timestamp columns

Revision ID: 45e2b959268f
Revises: f283316eb809
Create Date: 2026-04-23 18:10:41.551189

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '45e2b959268f'
down_revision: Union[str, Sequence[str], None] = "f283316eb809"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=True,
    )
    op.alter_column(
        "todo_items",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=True,
    )
    op.alter_column(
        "todo_items",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=sa.text("now()"),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "todo_items",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        existing_nullable=True,
    )
    op.alter_column(
        "todo_items",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "updated_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        existing_nullable=True,
    )
    op.alter_column(
        "users",
        "created_at",
        existing_type=sa.DateTime(timezone=True),
        server_default=None,
        existing_nullable=True,
    )