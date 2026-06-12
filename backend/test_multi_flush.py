import asyncio
from app.database import init_db, AsyncSessionLocal
from app.models.email import Email
from sqlalchemy import select
import uuid

async def test():
    await init_db()
    async with AsyncSessionLocal() as db:
        email = Email(
            id=str(uuid.uuid4()),
            message_id='multi_flush_test',
            thread_id='thread-id',
            sender='test@test.com',
            recipient='support@test.com',
            subject='Multi flush test',
            body='Testing multi flush',
            timestamp='2024-01-15T10:30:00',
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
        print('After flush 1:', email.id)
        
        email.category = 'Modified'
        await db.flush()
        print('After flush 2:', email.category)
        
        await db.commit()
        print('After commit')
    
    async with AsyncSessionLocal() as db2:
        result = await db2.execute(select(Email).where(Email.message_id == 'multi_flush_test'))
        row = result.scalar_one_or_none()
        if row:
            print('Found:', row.message_id, row.category)
        else:
            print('Not found')

asyncio.run(test())
