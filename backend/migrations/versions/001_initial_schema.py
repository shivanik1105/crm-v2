"""Initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector
import uuid

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # contacts
    op.create_table(
        'contacts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('tier', sa.String(50), default="Starter", nullable=False),
        sa.Column('account_value', sa.Float, default=0.0),
        sa.Column('vip_status', sa.Boolean, default=False),
        sa.Column('churn_risk_score', sa.Float, default=0.0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # threads
    op.create_table(
        'threads',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('sender_email', sa.String(255), nullable=False, index=True),
        sa.Column('contact_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('contacts.id'), nullable=True),
        sa.Column('subject', sa.Text, nullable=True),
        sa.Column('category', sa.String(100), default="General"),
        sa.Column('status', sa.String(50), default="Open"),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_threads_sender_updated', 'threads', ['sender_email', 'last_updated_at'])

    # emails
    op.create_table(
        'emails',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('message_id', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('thread_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('threads.id'), nullable=False),
        sa.Column('sender', sa.String(255), nullable=False, index=True),
        sa.Column('recipient', sa.String(255), nullable=False),
        sa.Column('subject', sa.Text, nullable=True),
        sa.Column('body', sa.Text, nullable=False),
        sa.Column('body_truncated', sa.Boolean, default=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column('category', sa.String(100), default="General"),
        sa.Column('sentiment_score', sa.Float, default=0.0),
        sa.Column('urgency', sa.String(50), default="Low"),
        sa.Column('confidence', sa.Float, default=0.0),
        sa.Column('requires_human', sa.Boolean, default=False),
        sa.Column('status', sa.String(50), default="New"),
        sa.Column('raw_entities', postgresql.JSONB, default=dict),
        sa.Column('classification_result', postgresql.JSONB, default=dict),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_emails_sender_timestamp', 'emails', ['sender', 'timestamp'])

    # actions
    op.create_table(
        'actions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('emails.id'), nullable=False),
        sa.Column('action_type', sa.String(100), nullable=False),
        sa.Column('status', sa.String(50), default="Pending"),
        sa.Column('assigned_to', sa.String(255), nullable=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('agent_reasoning_log', postgresql.JSONB, default=list),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
    )

    # knowledge_chunks
    op.create_table(
        'knowledge_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('source', sa.String(255), nullable=False),
        sa.Column('heading', sa.String(500), nullable=True),
        sa.Column('chunk_index', sa.Integer, nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('embedding', Vector(384), nullable=False),
        sa.Column('metadata', postgresql.JSONB, default=dict),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_knowledge_source_chunk', 'knowledge_chunks', ['source', 'chunk_index'], unique=True)

    # web_intelligence_cache
    op.create_table(
        'web_intelligence_cache',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('url', sa.String(2048), nullable=False, index=True),
        sa.Column('url_hash', sa.String(64), nullable=False, unique=True),
        sa.Column('content_summary', sa.Text, nullable=True),
        sa.Column('raw_data', postgresql.JSONB, default=dict),
        sa.Column('cached_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )

    # audit_logs
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('entity_type', sa.String(100), nullable=False, index=True),
        sa.Column('entity_id', sa.String(255), nullable=False, index=True),
        sa.Column('action', sa.String(100), nullable=False),
        sa.Column('actor', sa.String(255), nullable=True),
        sa.Column('diff', postgresql.JSONB, default=dict),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('ip_address', sa.String(100), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('web_intelligence_cache')
    op.drop_table('knowledge_chunks')
    op.drop_table('actions')
    op.drop_table('emails')
    op.drop_table('threads')
    op.drop_table('contacts')
    op.execute("DROP EXTENSION IF EXISTS vector")
