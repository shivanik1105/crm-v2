from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, func, JSON
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Action(Base):
    __tablename__ = "actions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email_id = Column(String(36), ForeignKey("emails.id"), nullable=False)
    action_type = Column(String(100), nullable=False)
    status = Column(String(50), default="Pending")
    assigned_to = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    agent_reasoning_log = Column(JSON, default=list)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    email = relationship("Email", back_populates="actions", lazy="selectin")
