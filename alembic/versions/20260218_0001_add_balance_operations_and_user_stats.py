"""Add balance_operations and user stats fields

Revision ID: 20260218_0001
Revises: 20260208_0200_002_add_user_social_models
Create Date: 2026-02-18
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260218_0001"
down_revision = "20260208_0200_002_add_user_social_models"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("current_win_streak", sa.Integer(), server_default="0", nullable=False))
    op.add_column("users", sa.Column("best_win_streak", sa.Integer(), server_default="0", nullable=False))
    op.add_column("users", sa.Column("biggest_win_ton", sa.Numeric(18, 9), server_default="0", nullable=False))

    op.create_table(
        "balance_operations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("operation_id", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("op_type", sa.Enum("bet", "payout", "refund", "deposit", "withdraw", name="operationtype"), nullable=False),
        sa.Column("status", sa.Enum("pending", "applied", "failed", name="operationstatus"), nullable=False),
        sa.Column("amount_ton", sa.Numeric(18, 9), server_default="0", nullable=False),
        sa.Column("amount_stars", sa.Integer(), server_default="0", nullable=False),
        sa.Column("request_hash", sa.String(length=64), nullable=True),
        sa.Column("response_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_balance_operations_operation_id", "balance_operations", ["operation_id"], unique=True)
    op.create_index("ix_balance_operations_user_id", "balance_operations", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_balance_operations_user_id", table_name="balance_operations")
    op.drop_index("ix_balance_operations_operation_id", table_name="balance_operations")
    op.drop_table("balance_operations")

    op.drop_column("users", "biggest_win_ton")
    op.drop_column("users", "best_win_streak")
    op.drop_column("users", "current_win_streak")

    op.execute("DROP TYPE IF EXISTS operationtype")
    op.execute("DROP TYPE IF EXISTS operationstatus")
