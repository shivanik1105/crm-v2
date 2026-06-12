from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, Index, ForeignKey, func, JSON
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Email(Base):
    __tablename__ = "emails"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(255), unique=True, nullable=False, index=True)
    thread_id = Column(String(36), ForeignKey("threads.id"), nullable=False)
    sender = Column(String(255), nullable=False, index=True)
    recipient = Column(String(255), nullable=False)
    subject = Column(Text, nullable=True)
    body = Column(Text, nullable=False)
    body_truncated = Column(Boolean, default=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    category = Column(String(100), default="General")
    sentiment_score = Column(Float, default=0.0)
    urgency = Column(String(50), default="Low")
    confidence = Column(Float, default=0.0)
    requires_human = Column(Boolean, default=False)
    status = Column(String(50), default="New")
    raw_entities = Column(JSON, default=dict)
    classification_result = Column(JSON, default=dict)
    reasoning_trace = Column(JSON, default=dict)
    rag_chunks = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())

    thread = relationship("Thread", back_populates="emails", lazy="selectin")
    actions = relationship("Action", back_populates="email", lazy="selectin")

    __table_args__ = (
        Index("idx_emails_sender_timestamp", "sender", "timestamp"),
    )
