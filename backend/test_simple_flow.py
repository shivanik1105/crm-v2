import asyncio
from app.database import init_db, AsyncSessionLocal
from app.models.email import Email
from app.models.thread import Thread
from app.models.contact import Contact
from sqlalchemy import select
import uuid
from datetime import datetime

async def test():
    await init_db()
    async with AsyncSessionLocal() as db:
        contact = Contact(
            id=str(uuid.uuid4()),
            email='test2@test.com',
            name='Test2',
            tier='Starter',
            account_value=0.0,
            vip_status=False,
            churn_risk_score=0.0
        )
        db.add(contact)
        await db.flush()
        print('Contact flushed')
        
        thread = Thread(
            id=str(uuid.uuid4()),
            sender_email='test2@test.com',
            contact_id=contact.id,
            subject='Test2',
            category='General',
            status='Open'
        )
        db.add(thread)
        await db.flush()
        print('Thread flushed')
        
        email = Email(
            id=str(uuid.uuid4()),
            message_id='simple_test_002',
            thread_id=thread.id,
            sender='test2@test.com',
            recipient='support@test.com',
            subject='Test2',
            body='Test body',
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
        print('Email flushed:', email.id)
        
        # Simulate what process_email_async does after flush
        email.category = 'Modified'
        print('Email category modified')
        
        await db.commit()
        print('Committed')
        
        # Create AuditLog
        from app.models.audit_log import AuditLog
        audit = AuditLog(
            entity_type='email',
            entity_id=email.id,
            action='ingested',
            actor='system',
            diff={}
        )
        db.add(audit)
        await db.commit()
        print('Audit committed')
    
    async with AsyncSessionLocal() as db2:
        result = await db2.execute(select(Email).where(Email.message_id == 'simple_test_002'))
        row = result.scalar_one_or_none()
        if row:
            print('Found:', row.message_id, row.category)
        else:
            print('Not found')

asyncio.run(test())
