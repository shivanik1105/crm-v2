import asyncio
from app.database import init_db, AsyncSessionLocal
from app.models.email import Email
from sqlalchemy import select
import uuid
from datetime import datetime

async def test():
    await init_db()
    async with AsyncSessionLocal() as db:
        email = Email(
            id='test-id-2',
            message_id='orm_test_001',
            thread_id='thread-id',
            sender='test@test.com',
            recipient='support@test.com',
            subject='ORM test',
            body='Testing ORM insert',
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
            category='Test',
            sentiment_score=0.0,
            urgency='Low',
            confidence=0.5,
            requires_human=False,
            status='New',
            raw_entities={},
            classification_result={}
        )
        db.add(email)
        await db.flush()
        print('After flush:', email.id)
        await db.commit()
        print('After commit')
    
    async with AsyncSessionLocal() as db2:
        result = await db2.execute(select(Email).where(Email.message_id == 'orm_test_001'))
        row = result.scalar_one_or_none()
        if row:
            print('Found:', row.message_id)
        else:
            print('Not found')

asyncio.run(test())
