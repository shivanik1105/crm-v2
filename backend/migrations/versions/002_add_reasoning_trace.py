"""add reasoning trace and rag chunks

Revision ID: 002_add_reasoning_trace
Revises: 001_initial_schema
Create Date: 2024-01-15 10:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_reasoning_trace'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add reasoning_trace column to emails table
    op.add_column('emails', sa.Column('reasoning_trace', postgresql.JSONB(), nullable=True))
    
    # Add rag_chunks column to emails table  
    op.add_column('emails', sa.Column('rag_chunks', postgresql.JSONB(), nullable=True))
    
    # Set default values for existing rows
    op.execute("UPDATE emails SET reasoning_trace = '{}' WHERE reasoning_trace IS NULL")
    op.execute("UPDATE emails SET rag_chunks = '[]' WHERE rag_chunks IS NULL")


def downgrade() -> None:
    op.drop_column('emails', 'rag_chunks')
    op.drop_column('emails', 'reasoning_trace')
