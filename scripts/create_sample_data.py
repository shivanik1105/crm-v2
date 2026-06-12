import asyncio
import os
import sys
from datetime import datetime, timedelta
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings
from app.models.contact import Contact
from app.models.thread import Thread
from app.models.email import Email
import uuid

async def create_sample_data():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        sample_contacts = [
            {"email": "alice@example.com", "name": "Alice Smith", "tier": "Enterprise", "account_value": 2400.0, "vip_status": True, "churn_risk_score": 15.0},
            {"email": "bob@example.com", "name": "Bob Jones", "tier": "Enterprise", "account_value": 2400.0, "vip_status": True, "churn_risk_score": 25.0},
            {"email": "karen@example.com", "name": "Karen Davis", "tier": "Standard", "account_value": 149.0, "vip_status": False, "churn_risk_score": 85.0},
            {"email": "eleanor@example.com", "name": "Eleanor Wright", "tier": "Enterprise", "account_value": 5000.0, "vip_status": True, "churn_risk_score": 10.0},
            {"email": "spammer@spam.com", "name": "Spam Bot", "tier": "Starter", "account_value": 0.0, "vip_status": False, "churn_risk_score": 0.0},
        ]
        
        contact_map = {}
        for c_data in sample_contacts:
            contact = Contact(
                id=uuid.uuid4(),
                **c_data
            )
            session.add(contact)
            contact_map[c_data["email"]] = contact
        
        await session.flush()
        
        # Create sample threads and emails
        sample_emails = [
            {
                "sender": "alice@example.com",
                "subject": "Billing question about Enterprise upgrade",
                "body": "Hi team, I upgraded from Standard annual to Enterprise mid-cycle and I'm confused about the pro-rata billing on my latest invoice. Can you clarify?",
                "category": "Billing",
                "urgency": "Medium",
                "sentiment": 0.1
            },
            {
                "sender": "bob@example.com",
                "subject": "URGENT: 6-hour outage on our instance",
                "body": "We experienced a 6-hour complete outage yesterday. This is unacceptable for our Enterprise plan. I need a full RCA and service credit immediately.",
                "category": "Technical",
                "urgency": "Critical",
                "sentiment": -0.8
            },
            {
                "sender": "karen@example.com",
                "subject": "Refund request + public review warning",
                "body": "I am extremely dissatisfied with your service and I want a full refund. If I don't get it within 48 hours I will post a public review on Trustpilot and tell everyone in my network to avoid your company.",
                "category": "Billing",
                "urgency": "High",
                "sentiment": -0.9
            },
            {
                "sender": "eleanor@example.com",
                "subject": "HIPAA BAA and SOC 2 report for 200-seat deal",
                "body": "We're closing a 200-seat Enterprise deal but our compliance team requires a signed HIPAA BAA and your latest SOC 2 Type II report under NDA. Can you provide these within 2 business days?",
                "category": "Compliance",
                "urgency": "High",
                "sentiment": 0.3
            },
            {
                "sender": "spammer@spam.com",
                "subject": "Wire transfer opportunity",
                "body": "Dear friend, I am a Nigerian prince and I need your help with a wire transfer of $10 million. Click here to earn your share.",
                "category": "Spam",
                "urgency": "Low",
                "sentiment": 0.0
            }
        ]
        
        for i, e_data in enumerate(sample_emails):
            thread = Thread(
                id=uuid.uuid4(),
                sender_email=e_data["sender"],
                contact_id=contact_map[e_data["sender"]].id,
                subject=e_data["subject"],
                category=e_data["category"],
                status="Open" if e_data["category"] != "Spam" else "Spam"
            )
            session.add(thread)
            await session.flush()
            
            email = Email(
                id=uuid.uuid4(),
                message_id=f"sample-{i:03d}",
                thread_id=thread.id,
                sender=e_data["sender"],
                recipient="support@company.com",
                subject=e_data["subject"],
                body=e_data["body"],
                body_truncated=False,
                timestamp=datetime.utcnow() - timedelta(days=random.randint(0, 5)),
                category=e_data["category"],
                sentiment_score=e_data["sentiment"],
                urgency=e_data["urgency"],
                confidence=0.85,
                requires_human=e_data["urgency"] == "Critical",
                status="New" if e_data["category"] != "Spam" else "Spam",
                raw_entities={},
                classification_result={
                    "category": e_data["category"],
                    "urgency": e_data["urgency"],
                    "sentiment_score": e_data["sentiment"],
                    "confidence": 0.85
                }
            )
            session.add(email)
        
        await session.commit()
        print(f"Created {len(sample_contacts)} contacts and {len(sample_emails)} sample emails")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_sample_data())
