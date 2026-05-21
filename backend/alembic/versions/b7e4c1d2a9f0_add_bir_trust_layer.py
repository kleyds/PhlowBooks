"""add bir trust layer

Revision ID: b7e4c1d2a9f0
Revises: f43a9d2b7c10
Create Date: 2026-05-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7e4c1d2a9f0"
down_revision: Union[str, None] = "f43a9d2b7c10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("receipt_data", schema=None) as batch_op:
        batch_op.add_column(sa.Column("atp_number", sa.String(length=100), nullable=True))

    op.create_table(
        "receipt_audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("receipt_id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("field_name", sa.String(length=120), nullable=False),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"]),
        sa.ForeignKeyConstraint(["receipt_id"], ["receipts.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("receipt_audit_logs", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_receipt_audit_logs_client_id"), ["client_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_receipt_audit_logs_id"), ["id"], unique=False)
        batch_op.create_index(batch_op.f("ix_receipt_audit_logs_receipt_id"), ["receipt_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_receipt_audit_logs_user_id"), ["user_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("receipt_audit_logs", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_receipt_audit_logs_user_id"))
        batch_op.drop_index(batch_op.f("ix_receipt_audit_logs_receipt_id"))
        batch_op.drop_index(batch_op.f("ix_receipt_audit_logs_id"))
        batch_op.drop_index(batch_op.f("ix_receipt_audit_logs_client_id"))
    op.drop_table("receipt_audit_logs")

    with op.batch_alter_table("receipt_data", schema=None) as batch_op:
        batch_op.drop_column("atp_number")
