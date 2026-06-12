from sqlalchemy import Column, Integer, String, DateTime, Text, Index, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Thread(Base):
    __tablename__ = "threads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_email = Column(String(255), nullable=False, index=True)
    contact_id = Column(String(36), ForeignKey("contacts.id"), nullable=True)
    subject = Column(Text, nullable=True)
    category = Column(String(100), default="General")
    status = Column(String(50), default="Open")
    last_updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime, server_default=func.now())

    contact = relationship("Contact", back_populates="threads", lazy="selectin")
    emails = relationship("Email", back_populates="thread", order_by="Email.timestamp", lazy="selectin")

    __table_args__ = (
        Index("idx_threads_sender_updated", "sender_email", "last_updated_at"),
    )
