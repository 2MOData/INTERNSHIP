"""create source chunk embeddings table

Revision ID: fc0bba620147
Revises: f3a4b5c6d7e8
Create Date: 2026-07-02 03:10:14.968587

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc0bba620147'
down_revision: Union[str, Sequence[str], None] = 'f3a4b5c6d7e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "source_chunk_embeddings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("chunk_id", sa.Uuid(), nullable=False),
        sa.Column("embedding_model", sa.String(length=100), nullable=False),
        sa.Column("embedding_dimensions", sa.Integer(), nullable=False),
        sa.Column("embedding", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["chunk_id"],
            ["source_chunks.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("chunk_id"),
    )
    op.create_index(
        op.f("ix_source_chunk_embeddings_chunk_id"),
        "source_chunk_embeddings",
        ["chunk_id"],
        unique=False,
    )

    op.execute(
        "ALTER TABLE source_chunk_embeddings "
        "ALTER COLUMN embedding TYPE vector(1536) "
        "USING embedding::vector"
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_source_chunk_embeddings_chunk_id"),
        table_name="source_chunk_embeddings",
    )
    op.drop_table("source_chunk_embeddings")