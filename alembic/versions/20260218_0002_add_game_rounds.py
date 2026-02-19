"""Add game_rounds table

Revision ID: 20260218_0002
Revises: 20260218_0001_add_balance_operations_and_user_stats
Create Date: 2026-02-18
"""
from alembic import op
import sqlalchemy as sa


revision = "20260218_0002"
down_revision = "20260218_0001_add_balance_operations_and_user_stats"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "game_rounds",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("game_type", sa.String(length=32), nullable=False),
        sa.Column("round_id", sa.String(length=64), nullable=False),
        sa.Column("server_seed_hash", sa.String(length=128), nullable=False),
        sa.Column("server_seed", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_game_rounds_round_id", "game_rounds", ["round_id"], unique=True)
    op.create_index("ix_game_rounds_game_type", "game_rounds", ["game_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_game_rounds_game_type", table_name="game_rounds")
    op.drop_index("ix_game_rounds_round_id", table_name="game_rounds")
    op.drop_table("game_rounds")
