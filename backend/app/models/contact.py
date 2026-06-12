from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, Index, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=True)
    tier = Column(String(50), default="Starter", nullable=False)
    account_value = Column(Float, default=0.0)
    vip_status = Column(Boolean, default=False)
    churn_risk_score = Column(Float, default=0.0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    threads = relationship("Thread", back_populates="contact", lazy="selectin")
