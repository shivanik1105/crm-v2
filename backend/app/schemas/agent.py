from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class RAGChunkDetail(BaseModel):
    """Details about a retrieved knowledge base chunk"""
    source: str
    heading: str
    content: str
    similarity_score: float
    chunk_index: int

class AgentThoughtStep(BaseModel):
    """Individual step in agent reasoning process"""
    step_number: int
    thought: str = Field(..., description="What the agent is thinking")
    action: str = Field(..., description="What action the agent is taking")
    observation: str = Field(..., description="What the agent observed from the action")
    next_step: str = Field(..., description="What the agent plans to do next")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentReasoningTrace(BaseModel):
    """Complete reasoning trace for an email processing"""
    email_id: str
    scenario_detected: Optional[str] = None
    scenario_confidence: float = 0.0
    rag_chunks_retrieved: List[RAGChunkDetail] = Field(default_factory=list)
    reasoning_steps: List[AgentThoughtStep] = Field(default_factory=list)
    final_decision: str
    decision_rationale: str
    escalation_triggered: bool = False
    processing_time_ms: float = 0.0

class SpecialScenarioAlert(BaseModel):
    """Alert for special scenario detection"""
    scenario_type: str = Field(..., description="GDPR | Ransomware | Churn | Outage")
    severity: str = Field(..., pattern="^(Critical|High|Medium)$")
    email_id: str
    sender: str
    subject: str
    detection_reason: str
    recommended_action: str
    escalation_path: str
    sla_deadline: Optional[str] = None
    auto_response_blocked: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EmailDetailWithReasoning(BaseModel):
    """Extended email details with AI reasoning"""
    id: str
    message_id: str
    sender: str
    subject: Optional[str]
    body: str
    timestamp: datetime
    category: str
    urgency: str
    sentiment_score: float
    confidence: float
    requires_human: bool
    status: str
    classification_result: Dict[str, Any]
    reasoning_trace: Optional[AgentReasoningTrace] = None
    rag_context: List[RAGChunkDetail] = Field(default_factory=list)

class AgentStep(BaseModel):
    step_number: int
    thought: str
    action: str
    action_input: Optional[Dict[str, Any]] = None
    observation: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AgentTrace(BaseModel):
    email_id: str
    classification: Dict[str, Any]
    steps: List[AgentStep]
    final_recommendation: str
    draft_reply: Optional[str] = None
    escalate: bool
    escalation_brief: Optional[str] = None
    tools_used: List[str]
    completed_at: datetime = Field(default_factory=datetime.utcnow)
    dry_run: bool
