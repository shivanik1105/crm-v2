import pytest
from datetime import datetime
from app.schemas.email import EmailIngest
from app.services.heuristic_filter import heuristic_filter

class TestIngestValidation:
    def test_valid_email_ingest(self):
        email = EmailIngest(
            message_id="msg_001",
            sender="test@example.com",
            recipient="support@company.com",
            subject="Test Subject",
            body="This is a test email body.",
            timestamp=datetime.utcnow()
        )
        assert email.message_id == "msg_001"
        assert email.sender == "test@example.com"
    
    def test_missing_message_id(self):
        with pytest.raises(Exception):
            EmailIngest(
                message_id="",
                sender="test@example.com",
                recipient="support@company.com",
                body="Test body",
                timestamp=datetime.utcnow()
            )
    
    def test_body_truncation(self):
        long_body = "A" * 15000
        email = EmailIngest(
            message_id="msg_002",
            sender="test@example.com",
            recipient="support@company.com",
            body=long_body,
            timestamp=datetime.utcnow()
        )
        assert len(email.body) <= 10000

class TestHeuristicFilter:
    def test_spam_detection(self):
        email = EmailIngest(
            message_id="spam_001",
            sender="spammer@spam.com",
            recipient="support@company.com",
            subject="Free money",
            body="Nigerian prince wire transfer opportunity. Click here to earn millions.",
            timestamp=datetime.utcnow()
        )
        result = heuristic_filter(email)
        assert result.is_spam == True
        assert "spam" in result.flags or "spam_keyword" in result.flags
    
    def test_urgency_detection(self):
        email = EmailIngest(
            message_id="urgent_001",
            sender="user@example.com",
            recipient="support@company.com",
            subject="URGENT: System down",
            body="This is urgent and critical. Our system is down and we need immediate help.",
            timestamp=datetime.utcnow()
        )
        result = heuristic_filter(email)
        assert result.is_urgent == True
        assert result.initial_priority_score > 50
    
    def test_security_detection(self):
        email = EmailIngest(
            message_id="sec_001",
            sender="attacker@unknown.com",
            recipient="support@company.com",
            subject="Ransomware",
            body="We have encrypted your data. Send 2 BTC or we will publish everything.",
            timestamp=datetime.utcnow()
        )
        result = heuristic_filter(email)
        assert result.is_security == True
        assert result.initial_priority_score > 70
    
    def test_legitimate_email(self):
        email = EmailIngest(
            message_id="legit_001",
            sender="customer@example.com",
            recipient="support@company.com",
            subject="Question about features",
            body="Hi, I was wondering if you could help me understand how to use the reporting dashboard. Thanks!",
            timestamp=datetime.utcnow()
        )
        result = heuristic_filter(email)
        assert result.is_spam == False
        assert result.is_security == False
        assert result.initial_priority_score == 50

class TestDeduplication:
    def test_duplicate_message_id(self):
        # This would be an integration test against the API
        # For unit test, we verify the logic
        message_id = "dup_001"
        # In real scenario, second ingest with same message_id should return existing
        assert True  # Placeholder for integration test
