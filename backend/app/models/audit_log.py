from sqlalchemy import Column, String, DateTime, func, JSON
from app.database import Base
import uuid

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String(100), nullable=False, index=True)
    entity_id = Column(String(255), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    actor = Column(String(255), nullable=True)
    diff = Column(JSON, default=dict)
    timestamp = Column(DateTime, server_default=func.now())
    ip_address = Column(String(100), nullable=True)
    user_agent = Column(String(500), nullable=True)
