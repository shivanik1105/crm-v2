import pytest
from datetime import datetime
from app.schemas.email import EmailIngest
from app.services.heuristic_filter import heuristic_filter

class TestHeuristicFilter:
    def test_spam_keywords(self):
        spam_bodies = [
            "Nigerian prince needs your help with wire transfer",
            "SEO service guaranteed first page Google ranking",
            "Click here to earn $10,000 per week from home",
            "You've been selected for a free prize",
            "Free money bitcoin investment opportunity"
        ]
        for body in spam_bodies:
            email = EmailIngest(
                message_id="spam_test",
                sender="test@test.com",
                recipient="support@company.com",
                body=body,
                timestamp=datetime.utcnow()
            )
            result = heuristic_filter(email)
            assert result.is_spam == True, f"Failed for: {body[:50]}"
            assert result.initial_priority_score < 50
    
    def test_spam_domains(self):
        for domain in ["spam.com", "10minutemail.com", "guerrillamail.com"]:
            email = EmailIngest(
                message_id="spam_domain_test",
                sender=f"user@{domain}",
                recipient="support@company.com",
                body="Regular content here",
                timestamp=datetime.utcnow()
            )
            result = heuristic_filter(email)
            assert result.is_spam == True
    
    def test_urgency_keywords(self):
        urgent_bodies = [
            "This is urgent and requires immediate attention",
            "P0 outage affecting all customers",
            "Legal action will be taken if not resolved",
            "Cease and desist notice",
            "Ransomware attack in progress",
            "Lawsuit pending",
            "Data breach detected",
            "Critical system failure",
            "Emergency escalation required"
        ]
        for body in urgent_bodies:
            email = EmailIngest(
                message_id="urgent_test",
                sender="test@test.com",
                recipient="support@company.com",
                body=body,
                timestamp=datetime.utcnow()
            )
            result = heuristic_filter(email)
            assert result.is_urgent == True, f"Failed for: {body[:50]}"
            assert result.initial_priority_score > 50
    
    def test_security_keywords(self):
        security_bodies = [
            "Ransomware encrypted all files",
            "Pay 2 BTC in bitcoin to decrypt",
            "Hackers breached our system",
            "Suspicious login from unknown IP",
            "Unauthorized access to database",
            "Data leak detected",
            "Send bitcoin or we publish data"
        ]
        for body in security_bodies:
            email = EmailIngest(
                message_id="security_test",
                sender="test@test.com",
                recipient="support@company.com",
                body=body,
                timestamp=datetime.utcnow()
            )
            result = heuristic_filter(email)
            assert result.is_security == True, f"Failed for: {body[:50]}"
            assert result.initial_priority_score > 70
    
    def test_priority_score_capped(self):
        email = EmailIngest(
            message_id="priority_test",
            sender="test@test.com",
            recipient="support@company.com",
            body="URGENT ransomware bitcoin breach lawsuit critical emergency escalate",
            timestamp=datetime.utcnow()
        )
        result = heuristic_filter(email)
        assert result.initial_priority_score <= 100
        assert result.initial_priority_score >= 0
    
    def test_internal_domain(self):
        email = EmailIngest(
            message_id="internal_test",
            sender="employee@internal.com",
            recipient="support@company.com",
            body="Regular internal request",
            timestamp=datetime.utcnow()
        )
        result = heuristic_filter(email)
        assert result.is_internal == True
    
    def test_neutral_email(self):
        email = EmailIngest(
            message_id="neutral_test",
            sender="customer@example.com",
            recipient="support@company.com",
            body="Hello, I hope you're having a great day. I wanted to ask about your product features.",
            timestamp=datetime.utcnow()
        )
        result = heuristic_filter(email)
        assert result.is_spam == False
        assert result.is_security == False
        assert result.is_urgent == False
        assert result.initial_priority_score == 50
        assert result.flags == []
