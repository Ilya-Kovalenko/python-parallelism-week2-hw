"""add preparing booking status

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-28 15:52:07.851125
"""

from typing import Sequence, Union

from alembic import op


revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE booking_status ADD VALUE IF NOT EXISTS 'preparing'")
    op.alter_column("bookings", "status", server_default="preparing")


def downgrade() -> None:
    op.alter_column("bookings", "status", server_default="pending_payment")
