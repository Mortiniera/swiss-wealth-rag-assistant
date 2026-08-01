"""add FTS tsvector column on knowledge_chunks

Revision ID: 0003_knowledge_fts
Revises: 0002_pgvector_knowledge
Create Date: 2026-07-31

"""

from typing import Sequence, Union

from alembic import op

revision: str = "0003_knowledge_fts"
down_revision: Union[str, Sequence[str], None] = "0002_pgvector_knowledge"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add generated english tsvector + GIN index for chunk FTS."""
    op.execute(
        """
        ALTER TABLE knowledge_chunks
        ADD COLUMN content_tsv tsvector
        GENERATED ALWAYS AS (to_tsvector('english', coalesce(content, ''))) STORED
        """
    )
    op.execute(
        """
        CREATE INDEX ix_knowledge_chunks_content_tsv
        ON knowledge_chunks
        USING GIN (content_tsv)
        """
    )


def downgrade() -> None:
    """Remove FTS index and generated content_tsv column."""
    op.execute("DROP INDEX IF EXISTS ix_knowledge_chunks_content_tsv")
    op.execute("ALTER TABLE knowledge_chunks DROP COLUMN IF EXISTS content_tsv")
