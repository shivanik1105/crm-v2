from typing import Optional, List
from pydantic import BaseModel, Field

class RAGChunkInfo(BaseModel):
    """Information about a retrieved RAG chunk"""
    source: str
    heading: str
    content: str
    similarity_score: float
    chunk_index: int

class ClassificationResult(BaseModel):
    category: str = Field(..., description="Primary classification category")
    subcategory: Optional[str] = Field(default=None)
    urgency: str = Field(..., pattern="^(Low|Medium|High|Critical)$")
    sentiment_score: float = Field(..., ge=-1.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    requires_human: bool = Field(default=False)
    escalation_reason: Optional[str] = Field(default=None)
    keywords_detected: List[str] = Field(default_factory=list)
    suggested_action: Optional[str] = Field(default=None)
    rag_context_used: bool = Field(default=False)
    rag_chunks: List[RAGChunkInfo] = Field(default_factory=list)
    scenario_detected: Optional[str] = Field(default=None)

    model_config = {
        "json_schema_extra": {
            "example": {
                "category": "Billing",
                "subcategory": "Refund Request",
                "urgency": "High",
                "sentiment_score": -0.6,
                "confidence": 0.85,
                "requires_human": False,
                "escalation_reason": None,
                "keywords_detected": ["refund", "cancel"],
                "suggested_action": "Check account history and apply retention credit",
                "rag_context_used": True,
                "rag_chunks": [],
                "scenario_detected": None
            }
        }
    }
