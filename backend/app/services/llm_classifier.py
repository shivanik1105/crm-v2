import json
import asyncio
import logging
from typing import List, Dict, Any, Optional
import httpx
from pydantic import ValidationError
from app.schemas.classification import ClassificationResult
from app.schemas.email import EmailIngest
from app.config import settings
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)

GDPR_PATTERNS = [
    "article 20", "data portability", "gdpr", "right to data",
    "export my data", "data subject request"
]

RANSOMWARE_PATTERNS = [
    "ransomware", "bitcoin", "btc", "pay or", "publish data",
    "decrypt", "2 btc", "send bitcoin"
]

CHATBOT_PATTERNS = [
    "your chatbot said", "your bot told me", "ai told me",
    "chatbot told me", "your ai said"
]

class LLMClassifier:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.client = httpx.AsyncClient(timeout=60.0)
    
    def _build_system_prompt(self, rag_context: str, thread_history: str) -> str:
        return f"""You are an AI email triage specialist.

CRITICAL RULES:
1. Never auto-reply to: spam, ransomware, legal threats, or GDPR requests
2. If confidence < 0.70, set requires_human = true
3. GDPR requests = Compliance/Critical
4. Ransomware = Security/Critical

{rag_context}

Thread History:
{thread_history[:500]}"""
    
    def _build_user_prompt(self, email: EmailIngest, schema_json: str) -> str:
        return f"""Analyze this email and return ONLY a compact JSON object with these fields:
- category: string (Complaint|Inquiry|Bug|Feature|Compliance|Legal|Billing|Spam|Internal|Other)
- subcategory: string or null
- sentiment_score: float (-1.0 to 1.0)
- urgency: string (Critical|High|Medium|Low)
- confidence: float (0.0 to 1.0)
- requires_human: boolean
- escalation_reason: string or null
- keywords_detected: array of strings
- suggested_action: string

Email:
From: {email.sender}
Subject: {email.subject or "(no subject)"}
Body: {email.body[:800]}

Return ONLY the JSON object. No markdown, no explanations."""
    
    def _detect_forced_classification(self, email: EmailIngest) -> Optional[ClassificationResult]:
        body_lower = email.body.lower()
        subject_lower = (email.subject or "").lower()
        combined = body_lower + " " + subject_lower
        
        # GDPR Detection
        for pattern in GDPR_PATTERNS:
            if pattern in combined:
                return ClassificationResult(
                    category="Compliance",
                    subcategory="GDPR Article 20",
                    urgency="Critical",
                    sentiment_score=-0.3,
                    confidence=0.95,
                    requires_human=True,
                    escalation_reason="GDPR Article 20 data portability request - must be handled by DPO within 30-day statutory window",
                    keywords_detected=[pattern],
                    suggested_action="Flag for legal team, create compliance ticket, draft acknowledgement citing 30-day window",
                    rag_context_used=True
                )
        
        # Ransomware Detection
        for pattern in RANSOMWARE_PATTERNS:
            if pattern in combined:
                return ClassificationResult(
                    category="Security",
                    subcategory="Ransomware/Extortion",
                    urgency="Critical",
                    sentiment_score=-0.9,
                    confidence=0.98,
                    requires_human=True,
                    escalation_reason="Ransomware/extortion threat - immediate security team escalation required",
                    keywords_detected=[pattern],
                    suggested_action="Escalate to security team immediately, do not auto-reply",
                    rag_context_used=False
                )
        
        return None
    
    async def classify(self, db, email: EmailIngest, thread_history: str = "") -> ClassificationResult:
        # Layer 1: Hardcoded scenario detection
        forced = self._detect_forced_classification(email)
        if forced:
            return forced
        
        # RAG retrieval - use only 1 chunk to save tokens
        query = f"{email.subject or ''} {email.body[:500]}"
        rag_chunks = await rag_service.search(db, query, top_k=1)
        rag_context = rag_service.format_for_llm(rag_chunks)
        
        schema_json = ClassificationResult.model_json_schema()
        
        system_prompt = self._build_system_prompt(rag_context, thread_history)
        user_prompt = self._build_user_prompt(email, json.dumps(schema_json, indent=2))
        
        # Call Groq API
        result = await self._call_claude(system_prompt, user_prompt, rag_context, email.body, email.subject or "")
        
        if result is None:
            return ClassificationResult(
                category="Unknown",
                urgency="Medium",
                sentiment_score=0.0,
                confidence=0.3,
                requires_human=True,
                escalation_reason="LLM output parsing failed after retry",
                keywords_detected=[],
                suggested_action="Manual review required",
                rag_context_used=len(rag_chunks) > 0
            )
        
        result["rag_context_used"] = len(rag_chunks) > 0
        
        try:
            classification = ClassificationResult(**result)
        except ValidationError:
            return ClassificationResult(
                category="Unknown",
                urgency="Medium",
                sentiment_score=0.0,
                confidence=0.3,
                requires_human=True,
                escalation_reason="LLM output validation failed",
                keywords_detected=[],
                suggested_action="Manual review required",
                rag_context_used=len(rag_chunks) > 0
            )
        
        return classification
    
    async def _call_claude(self, system_prompt: str, user_prompt: str, rag_context: str = "", email_body: str = "", email_subject: str = "") -> Optional[Dict[str, Any]]:
        if not self.api_key or self.api_key == "your_key_here":
            # Fallback when no API key: return a reasonable heuristic classification
            return self._fallback_classification(email_body, email_subject, rag_context)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "SenAI CRM"
        }
        
        # OpenRouter uses OpenAI-compatible format
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 128
        }
        
        for attempt in range(2):
            try:
                response = await self.client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Extract JSON from response
                json_str = self._extract_json(content)
                if json_str:
                    return json.loads(json_str)
                
                if attempt == 0:
                    # Retry with explicit correction
                    error_msg = {"role": "user", "content": "\n\nERROR: Your previous response was not valid JSON. Return ONLY a valid JSON object."}
                    payload["messages"].append({"role": "assistant", "content": content})
                    payload["messages"].append(error_msg)
                    continue
                    
            except httpx.HTTPStatusError as e:
                # Check for payment/credit errors (402)
                if e.response.status_code == 402:
                    logger.warning(f"API credit limit exceeded, using fallback classification")
                    return self._fallback_classification(email_body, email_subject, rag_context)
                if attempt == 0:
                    error_msg = {"role": "user", "content": f"\n\nERROR: API error: {str(e)}. Return ONLY valid JSON."}
                    payload["messages"].append(error_msg)
                    continue
            except (httpx.HTTPError, json.JSONDecodeError, KeyError) as e:
                if attempt == 0:
                    error_msg = {"role": "user", "content": f"\n\nERROR: Parse failed: {str(e)}. Return ONLY valid JSON."}
                    payload["messages"].append(error_msg)
                    continue
        
        return None
    
    def _extract_json(self, text: str) -> Optional[str]:
        text = text.strip()
        
        # Handle markdown code blocks
        if text.startswith("```"):
            # Remove opening ```json or ```
            first_newline = text.find("\n")
            if first_newline != -1:
                text = text[first_newline:].strip()
            # Remove closing ```
            if text.endswith("```"):
                text = text[:-3].strip()
        
        if text.startswith("{") and text.endswith("}"):
            return text
        
        # Find JSON block
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return text[start:end+1]
        
        return None
    
    def _fallback_classification(self, email_body: str, email_subject: str, rag_context: str = "") -> Dict[str, Any]:
        # Only analyze the email content, not the prompt template
        body_lower = email_body.lower()
        subject_lower = email_subject.lower()
        combined = body_lower + " " + subject_lower
        
        # Comprehensive keyword-based fallback
        urgency = "Low"
        category = "General"
        sentiment = 0.0
        requires_human = False
        keywords = []
        subcategory = None
        suggested_action = "Review and respond"
        escalation_reason = None
        
        # Security threats (highest priority)
        if any(w in combined for w in ["ransomware", "bitcoin", "pay or", "2 btc", "encrypted", "hack", "unauthorized access"]):
            category = "Security"
            subcategory = "Ransomware/Extortion"
            urgency = "Critical"
            sentiment = -0.9
            requires_human = True
            keywords = ["ransomware", "security"]
            escalation_reason = "Security threat detected - immediate escalation required"
            suggested_action = "Escalate to security team immediately"
        # GDPR/Compliance
        elif any(w in combined for w in ["gdpr", "data portability", "article 20", "right to data", "data subject"]):
            category = "Compliance"
            subcategory = "GDPR Article 20"
            urgency = "Critical"
            sentiment = -0.3
            requires_human = True
            keywords = ["gdpr", "data_portability"]
            escalation_reason = "GDPR Article 20 request - must be handled by DPO within 30-day statutory window"
            suggested_action = "Flag for legal team, create compliance ticket"
        # Billing
        elif any(w in combined for w in ["refund", "money back", "cancel subscription", "invoice", "charge", "billing", "pro-rata"]):
            category = "Billing"
            keywords.append("refund" if "refund" in combined else "billing")
            sentiment = -0.3
            if "invoice" in combined or "discrepancy" in combined:
                subcategory = "Invoice Dispute"
            elif "refund" in combined:
                subcategory = "Refund Request"
            elif "pro-rata" in combined:
                subcategory = "Pro-Rata Calculation"
            suggested_action = "Review billing records and respond"
        # Technical/Bug
        elif any(w in combined for w in ["outage", "down", "not working", "broken", "bug", "crash", "error", "slow", "500", "data missing", "corruption"]):
            category = "Technical"
            keywords.append("outage" if "outage" in combined or "down" in combined else "bug")
            sentiment = -0.5
            urgency = "High"
            subcategory = "Bug Report"
            suggested_action = "Investigate technical issue and provide workaround"
        # Feature Request
        elif any(w in combined for w in ["feature request", "need custom", "would like to see", "roadmap", "enhancement", "custom fields"]):
            category = "Feature Request"
            keywords.append("feature_request")
            sentiment = 0.1
            suggested_action = "Log feature request and provide timeline if available"
        # Sales/Upgrade
        elif any(w in combined for w in ["upgrade", "plan", "pricing", "enterprise", "standard", "tier", "annual billing"]):
            category = "Sales"
            keywords.append("upgrade" if "upgrade" in combined else "pricing")
            sentiment = 0.2
            subcategory = "Plan Inquiry"
            suggested_action = "Provide pricing comparison and upgrade path"
        # Compliance (non-GDPR)
        elif any(w in combined for w in ["hipaa", "soc 2", "compliance", "baa", "audit", "data residency"]):
            category = "Compliance"
            keywords.append("compliance")
            sentiment = 0.0
            urgency = "High"
            suggested_action = "Provide compliance documentation and engage sales team"
        # Positive feedback
        elif any(w in combined for w in ["happy", "great", "amazing", "love", "excellent", "thank you", "appreciate"]):
            category = "Other"
            keywords.append("positive_feedback")
            sentiment = 1.0
            suggested_action = "Thank customer and share feedback with product team"
        # Integration/API
        elif any(w in combined for w in ["api", "webhook", "integration", "sync", "rate limit", "batch", "salesforce"]):
            category = "Technical"
            keywords.append("api" if "api" in combined else "integration")
            sentiment = 0.0
            subcategory = "API Integration"
            suggested_action = "Provide API documentation and integration support"
        # Data/Export
        elif any(w in combined for w in ["export", "csv", "import", "migration", "data export"]):
            category = "Technical"
            keywords.append("data_export")
            suggested_action = "Provide export instructions or data migration support"
        # Mobile
        elif any(w in combined for w in ["mobile", "ios", "android", "app crash", "push notification"]):
            category = "Technical"
            keywords.append("mobile")
            subcategory = "Mobile Issue"
            suggested_action = "Investigate mobile-specific issue"
        # Access/Auth
        elif any(w in combined for w in ["2fa", "password", "login", "locked", "suspended", "access denied"]):
            category = "Technical"
            keywords.append("auth")
            subcategory = "Authentication Issue"
            suggested_action = "Reset credentials or unlock account"
        # Churn/Review threats
        elif any(w in combined for w in ["churn", "switching", "competitor", "public review", "trustpilot", "g2", "negative review"]):
            category = "Complaint"
            keywords.append("churn_risk")
            sentiment = -0.6
            urgency = "High"
            subcategory = "Churn Risk"
            suggested_action = "Escalate to Customer Success team immediately"
        
        # Urgency overrides from email body only (not prompt template)
        if any(w in combined for w in ["urgent", "critical", "emergency", "p0", "immediately", "asap"]):
            urgency = "Critical"
            if "urgent" not in keywords:
                keywords.append("urgent")
            sentiment = min(sentiment, -0.4)
        elif any(w in combined for w in ["high priority", "important", "serious", "concerned", "unacceptable"]):
            if urgency != "Critical":
                urgency = "High"
            if "high_priority" not in keywords:
                keywords.append("high_priority")
        
        # Negative sentiment overrides
        if any(w in combined for w in ["horrible", "terrible", "worst", "angry", "frustrated", "unacceptable"]):
            sentiment = min(sentiment, -0.6)
            if "negative" not in keywords:
                keywords.append("negative_sentiment")
        
        # Spam detection
        if any(w in combined for w in ["nigerian prince", "free money", "click here", "seo service", "you've been selected", "wire transfer"]):
            category = "Spam"
            urgency = "Low"
            sentiment = -0.2
            keywords = ["spam"]
            requires_human = False
            suggested_action = "Mark as spam"
        
        confidence = 0.7 if keywords else 0.5
        
        # Check if RAG was used
        rag_used = len(rag_context) > 0 and "No relevant" not in rag_context
        
        return {
            "category": category,
            "subcategory": subcategory,
            "urgency": urgency,
            "sentiment_score": round(sentiment, 2),
            "confidence": confidence,
            "requires_human": requires_human,
            "escalation_reason": escalation_reason,
            "keywords_detected": keywords,
            "suggested_action": suggested_action,
            "rag_context_used": rag_used
        }

llm_classifier = LLMClassifier()
