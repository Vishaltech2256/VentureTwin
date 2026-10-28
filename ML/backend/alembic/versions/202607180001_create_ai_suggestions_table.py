"""create ai suggestions table

Revision ID: 202607180001
Revises: 202607140001
Create Date: 2026-07-18 00:01:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "202607180001"
down_revision = "202607140001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ai_suggestions",
        sa.Column("suggestion_id", sa.Integer(), nullable=False),
        sa.Column("startup_id", sa.Integer(), nullable=False),
        sa.Column("prediction_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=10), nullable=False),
        sa.Column("category", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "priority IN ('HIGH', 'MEDIUM', 'LOW')",
            name="ck_ai_suggestions_priority",
        ),
        sa.CheckConstraint(
            "category IN ('Finance', 'Marketing', 'Operations', 'Hiring', "
            "'Growth', 'Investment')",
            name="ck_ai_suggestions_category",
        ),
        sa.ForeignKeyConstraint(
            ["startup_id"],
            ["startup_profiles.startup_id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["prediction_id"],
            ["predictions.prediction_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("suggestion_id"),
    )
    op.create_index(
        op.f("ix_ai_suggestions_suggestion_id"),
        "ai_suggestions",
        ["suggestion_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_suggestions_startup_id"),
        "ai_suggestions",
        ["startup_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_ai_suggestions_prediction_id"),
        "ai_suggestions",
        ["prediction_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_ai_suggestions_prediction_id"), table_name="ai_suggestions")
    op.drop_index(op.f("ix_ai_suggestions_startup_id"), table_name="ai_suggestions")
    op.drop_index(op.f("ix_ai_suggestions_suggestion_id"), table_name="ai_suggestions")
    op.drop_table("ai_suggestions")
