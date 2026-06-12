import asyncio
from app.services.llm_classifier import llm_classifier
from app.schemas.email import EmailIngest
from app.database import AsyncSessionLocal
from datetime import datetime

async def test_llm():
    email = EmailIngest(
        message_id='test_llm_001',
        sender='test@example.com',
        recipient='support@company.com',
        subject='I want a refund',
        body='I want a refund for my purchase. It was within 14 days.',
        timestamp=datetime.now()
    )
    
    async with AsyncSessionLocal() as db:
        result = await llm_classifier.classify(db, email, "")
        print(f'Category: {result.category}')
        print(f'Urgency: {result.urgency}')
        print(f'Confidence: {result.confidence}')
        print(f'Sentiment: {result.sentiment_score}')
        print(f'Requires human: {result.requires_human}')
        print(f'Escalation reason: {result.escalation_reason}')

asyncio.run(test_llm())
