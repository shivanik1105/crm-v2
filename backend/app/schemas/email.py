from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, field_validator

class EmailIngest(BaseModel):
    message_id: str = Field(..., min_length=1, max_length=255)
    sender: EmailStr
    recipient: EmailStr
    subject: Optional[str] = Field(default="", max_length=1000)
    body: str = Field(..., max_length=10000)
    timestamp: datetime
    headers: Optional[Dict[str, str]] = Field(default_factory=dict)

    @field_validator('body', mode='before')
    @classmethod
    def truncate_body(cls, v: Any) -> Any:
        if isinstance(v, str) and len(v) > 10000:
            return v[:10000]
        return v

class EmailIngestResponse(BaseModel):
    job_id: str
    status: str
    message: str
    existing: bool = False
    email_id: Optional[str] = None

class EmailOut(BaseModel):
    id: str
    message_id: str
    sender: str
    recipient: str
    subject: Optional[str]
    body: str
    body_truncated: bool
    timestamp: datetime
    category: str
    sentiment_score: float
    urgency: str
    confidence: float
    requires_human: bool
    status: str
    raw_entities: Dict[str, Any]
    classification_result: Dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}

class ThreadOut(BaseModel):
    id: str
    sender_email: str
    subject: Optional[str]
    category: str
    status: str
    last_updated_at: datetime
    created_at: datetime
    emails: List[EmailOut]

    model_config = {"from_attributes": True}

class DraftUpdate(BaseModel):
    draft_body: str

class DraftOut(BaseModel):
    id: str
    email_id: str
    draft_body: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
