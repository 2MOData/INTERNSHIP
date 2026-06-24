"""create source pages table

Revision ID: 9a2c0b7d4f6e
Revises: e51ec8388673
Create Date: 2026-06-24 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9a2c0b7d4f6e"
down_revision: Union[str, Sequence[str], None] = "e51ec8388673"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "source_pages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["sources.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("source_id", "page_number"),
    )
    op.create_index(
        op.f("ix_source_pages_source_id"),
        "source_pages",
        ["source_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_source_pages_source_id"), table_name="source_pages")
    op.drop_table("source_pages")