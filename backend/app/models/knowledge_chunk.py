from sqlalchemy import Column, Integer, String, DateTime, Text, Index, func, JSON
from app.database import Base
import uuid

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(255), nullable=False)
    heading = Column(String(500), nullable=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=False)  # Stored as JSON string for SQLite compat
    meta = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("idx_knowledge_source_chunk", "source", "chunk_index", unique=True),
    )
