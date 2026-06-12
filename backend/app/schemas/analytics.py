from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class SentimentPoint(BaseModel):
    timestamp: datetime
    sentiment_score: float
    email_id: str

class SentimentTrendResponse(BaseModel):
    sender: str
    points: List[SentimentPoint]
    moving_average: float
    trend_direction: str  # improving, stable, deteriorating
    alert_triggered: bool

class CategoryDistributionItem(BaseModel):
    category: str
    count: int
    percentage: float

class CategoryDistributionResponse(BaseModel):
    distribution: List[CategoryDistributionItem]
    total: int

class AtRiskAccount(BaseModel):
    sender: str
    churn_risk_score: float
    account_value: float
    unresolved_threads: int
    last_email_date: datetime
    sentiment_trend: str

class AtRiskPanelResponse(BaseModel):
    accounts: List[AtRiskAccount]
    total_at_risk: int

class AgentPerformanceMetrics(BaseModel):
    auto_reply_rate: float
    escalation_rate: float
    avg_confidence: float
    avg_tools_used: float
    total_processed: int
    total_escalated: int

class ResponseTimeHeatmapItem(BaseModel):
    hour: int
    day: str
    avg_response_minutes: float
    email_count: int

class AnalyticsDashboardResponse(BaseModel):
    sentiment_trends: List[SentimentTrendResponse]
    category_distribution: CategoryDistributionResponse
    at_risk_accounts: AtRiskPanelResponse
    agent_performance: AgentPerformanceMetrics
    response_time_heatmap: List[ResponseTimeHeatmapItem]
