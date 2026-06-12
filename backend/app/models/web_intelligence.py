from sqlalchemy import Column, String, DateTime, Text, func, JSON
from app.database import Base
import uuid

class WebIntelligenceCache(Base):
    __tablename__ = "web_intelligence_cache"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String(2048), nullable=False, index=True)
    url_hash = Column(String(64), nullable=False, unique=True)
    content_summary = Column(Text, nullable=True)
    raw_data = Column(JSON, default=dict)
    cached_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
