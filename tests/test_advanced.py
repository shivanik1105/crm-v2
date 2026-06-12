import pytest
import os
import sys
import json
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.schemas.email import EmailIngest
from app.schemas.classification import ClassificationResult
from app.schemas.agent import AgentTrace, AgentStep
from app.services.heuristic_filter import heuristic_filter
from app.services.llm_classifier import LLMClassifier
from app.services.rag_service import RAGService, RAGChunk
from app.services.websocket_manager import WebSocketManager


class TestLLMClassifier:
    def setup_method(self):
        self.classifier = LLMClassifier()

    def test_gdpr_detection(self):
        email = EmailIngest(
            message_id="gdpr_test",
            sender="marcus.del@fintech-startup.co",
            recipient="support@company.com",
            subject="GDPR Article 20 Data Portability Request",
            body="Under GDPR Article 20, I request export of all my data in machine-readable format.",
            timestamp=datetime.now(timezone.utc)
        )
        result = self.classifier._detect_forced_classification(email)
        assert result is not None
        assert result.category == "Compliance"
        assert result.subcategory == "GDPR Article 20"
        assert result.urgency == "Critical"
        assert result.requires_human is True
        assert result.confidence >= 0.9

    def test_ransomware_detection(self):
        email = EmailIngest(
            message_id="ransom_test",
            sender="attacker@evil.com",
            recipient="support@company.com",
            subject="Pay or we publish",
            body="We have encrypted your systems. Send 2 BTC to this wallet or we publish all data.",
            timestamp=datetime.now(timezone.utc)
        )
        result = self.classifier._detect_forced_classification(email)
        assert result is not None
        assert result.category == "Security"
        assert result.subcategory == "Ransomware/Extortion"
        assert result.urgency == "Critical"
        assert result.requires_human is True
        assert result.sentiment_score <= -0.8

    def test_normal_email_no_forced_classification(self):
        email = EmailIngest(
            message_id="normal_test",
            sender="customer@example.com",
            recipient="support@company.com",
            subject="Question about pricing",
            body="Hi, I'd like to know more about your Standard plan features and pricing.",
            timestamp=datetime.now(timezone.utc)
        )
        result = self.classifier._detect_forced_classification(email)
        assert result is None

    def test_fallback_classification_refund(self):
        result = self.classifier._fallback_classification("I want a refund for my purchase")
        assert result["category"] == "Billing"
        assert "refund" in result["keywords_detected"]

    def test_fallback_classification_outage(self):
        result = self.classifier._fallback_classification("Our system is down, nothing is working")
        assert result["category"] == "Technical"
        assert result["urgency"] == "High"

    def test_fallback_classification_urgent(self):
        result = self.classifier._fallback_classification("This is urgent and critical, P0 emergency")
        assert result["urgency"] == "Critical"

    def test_json_extraction_valid(self):
        text = '{"category": "Billing", "urgency": "High"}'
        result = self.classifier._extract_json(text)
        assert result is not None
        parsed = json.loads(result)
        assert parsed["category"] == "Billing"

    def test_json_extraction_with_preamble(self):
        text = 'Here is the classification:\n{"category": "Billing"}\nDone.'
        result = self.classifier._extract_json(text)
        assert result is not None
        assert "Billing" in result

    def test_json_extraction_invalid(self):
        text = "This is not JSON at all"
        result = self.classifier._extract_json(text)
        assert result is None


class TestSpecialScenarios:
    def setup_method(self):
        self.classifier = LLMClassifier()

    def test_gdpr_never_auto_reply(self):
        email = EmailIngest(
            message_id="gdpr_no_reply",
            sender="marcus.del@fintech-startup.co",
            recipient="support@company.com",
            subject="GDPR Article 20 Request",
            body="I formally request data portability under GDPR Article 20.",
            timestamp=datetime.now(timezone.utc)
        )
        result = self.classifier._detect_forced_classification(email)
        assert result.requires_human is True
        assert result.urgency == "Critical"

    def test_ransomware_never_auto_reply(self):
        email = EmailIngest(
            message_id="ransom_no_reply",
            sender="attacker@evil.com",
            recipient="support@company.com",
            subject="Ransomware notice",
            body="Send 2 bitcoin or we publish all your customer data.",
            timestamp=datetime.now(timezone.utc)
        )
        result = self.classifier._detect_forced_classification(email)
        assert result.requires_human is True
        assert result.urgency == "Critical"

    def test_spam_never_auto_reply(self):
        email = EmailIngest(
            message_id="spam_no_reply",
            sender="spammer@spam.com",
            recipient="support@company.com",
            subject="Free money",
            body="Nigerian prince wire transfer opportunity",
            timestamp=datetime.now(timezone.utc)
        )
        heuristic = heuristic_filter(email)
        assert heuristic.is_spam is True

    def test_security_threat_detection(self):
        email = EmailIngest(
            message_id="security_threat",
            sender="security@company.com",
            recipient="support@company.com",
            subject="Suspicious login detected",
            body="Suspicious login from unknown IP address. Possible unauthorized access. This is urgent.",
            timestamp=datetime.now(timezone.utc)
        )
        heuristic = heuristic_filter(email)
        assert heuristic.is_security is True
        assert heuristic.is_urgent is True


class TestWebSocketManager:
    def test_manager_creation(self):
        manager = WebSocketManager()
        assert manager.global_connections is not None
        assert manager.active_connections is not None

    def test_event_payloads(self):
        manager = WebSocketManager()
        assert hasattr(manager, 'send_email_event')
        assert hasattr(manager, 'send_classification_event')
        assert hasattr(manager, 'send_agent_event')
        assert hasattr(manager, 'send_action_event')
        assert hasattr(manager, 'send_stats_update')


class TestClassificationResult:
    def test_valid_classification(self):
        result = ClassificationResult(
            category="Billing",
            urgency="High",
            sentiment_score=-0.5,
            confidence=0.85,
            requires_human=False
        )
        assert result.category == "Billing"
        assert result.urgency == "High"

    def test_invalid_urgency(self):
        with pytest.raises(Exception):
            ClassificationResult(
                category="Billing",
                urgency="INVALID",
                sentiment_score=0.0,
                confidence=0.5
            )

    def test_sentiment_bounds(self):
        with pytest.raises(Exception):
            ClassificationResult(
                category="Test",
                urgency="Low",
                sentiment_score=2.0,
                confidence=0.5
            )

    def test_confidence_bounds(self):
        with pytest.raises(Exception):
            ClassificationResult(
                category="Test",
                urgency="Low",
                sentiment_score=0.0,
                confidence=1.5
            )


class TestAgentTraceIntegrity:
    def test_full_trace_structure(self):
        trace = AgentTrace(
            email_id="test-123",
            classification={"category": "Technical", "urgency": "Critical"},
            steps=[
                AgentStep(step_number=1, thought="Check thread", action="get_thread_history", action_input={"sender_email": "bob@test.com"}, observation='{"threads": 3}'),
                AgentStep(step_number=2, thought="Check SLA", action="search_knowledge_base", action_input={"query": "SLA policy"}, observation='{"chunks": 3}'),
                AgentStep(step_number=3, thought="Escalate", action="escalate_to_human", action_input={"email_id": "test-123", "reason": "P0", "priority": "Critical"}, observation='{"status": "escalated"}'),
            ],
            final_recommendation="Escalate to human",
            escalate=True,
            escalation_brief="P0 outage with legal threat",
            tools_used=["get_thread_history", "search_knowledge_base", "escalate_to_human"],
            dry_run=False
        )
        assert len(trace.steps) == 3
        assert trace.escalate is True
        assert len(trace.tools_used) == 3

    def test_max_steps_enforcement(self):
        from app.services.agent_service import AgentService
        class FakeDB:
            pass
        service = AgentService(FakeDB())
        assert service.max_steps == 6

    def test_dry_run_flag(self):
        trace = AgentTrace(
            email_id="dry-run",
            classification={"category": "General"},
            steps=[],
            final_recommendation="Test",
            escalate=False,
            tools_used=[],
            dry_run=True
        )
        assert trace.dry_run is True


class TestRAGChunking:
    def test_pricing_policy_chunking(self):
        service = RAGService()
        content = """# Pricing Policy

## Starter Tier
- Price: $49/month
- Up to 5 users
- Basic support

## Standard Tier
- Price: $149/month
- Up to 25 users
- Priority support

## Enterprise Tier
- Custom pricing
- Unlimited users
- Dedicated support
- SLA guarantees
"""
        chunks = service.chunk_document("pricing_policy.md", content)
        assert len(chunks) >= 1
        assert all(c["source"] == "pricing_policy.md" for c in chunks)

    def test_sla_policy_chunking(self):
        service = RAGService()
        content = """# SLA Policy

## Uptime Guarantee
We guarantee 99.9% uptime.

## Incident Response
P0: 15 minutes
P1: 1 hour
P2: 4 hours

## Service Credits
10% for 99.0-99.9%
25% for 95.0-99.0%
50% for below 95.0%
"""
        chunks = service.chunk_document("sla_policy.md", content)
        assert len(chunks) >= 1

    def test_refund_policy_for_karen(self):
        service = RAGService()
        query = "I want a refund I'm leaving bad experience"
        embedding = service.model.encode([query])
        assert embedding.shape[1] == 384

    def test_empty_document(self):
        service = RAGService()
        chunks = service.chunk_document("empty.md", "")
        assert len(chunks) == 0


class TestEmailEdgeCases:
    def test_empty_subject(self):
        email = EmailIngest(
            message_id="no_subject",
            sender="test@example.com",
            recipient="support@company.com",
            subject="",
            body="Hello, I have a question.",
            timestamp=datetime.now(timezone.utc)
        )
        assert email.subject == ""
        result = heuristic_filter(email)
        assert result.is_spam is False

    def test_whitespace_only_body(self):
        email = EmailIngest(
            message_id="whitespace",
            sender="test@example.com",
            recipient="support@company.com",
            body="   ",
            timestamp=datetime.now(timezone.utc)
        )
        result = heuristic_filter(email)
        assert result.is_spam is False

    def test_very_long_body_truncation(self):
        long_body = "A" * 15000
        email = EmailIngest(
            message_id="long_body",
            sender="test@example.com",
            recipient="support@company.com",
            body=long_body,
            timestamp=datetime.now(timezone.utc)
        )
        assert len(email.body) <= 10000

    def test_html_entities_in_body(self):
        email = EmailIngest(
            message_id="html_entities",
            sender="test@example.com",
            recipient="support@company.com",
            body="Help with &amp; &lt;issue&gt; &quot;urgent&quot;",
            timestamp=datetime.now(timezone.utc)
        )
        result = heuristic_filter(email)
        assert result.is_spam is False

    def test_duplicate_message_id_detection(self):
        message_id = "dup_test_001"
        email1 = EmailIngest(
            message_id=message_id,
            sender="test@example.com",
            recipient="support@company.com",
            body="First send",
            timestamp=datetime.now(timezone.utc)
        )
        email2 = EmailIngest(
            message_id=message_id,
            sender="test@example.com",
            recipient="support@company.com",
            body="Duplicate send",
            timestamp=datetime.now(timezone.utc)
        )
        assert email1.message_id == email2.message_id
