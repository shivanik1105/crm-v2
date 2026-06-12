import asyncio
from app.database import init_db, AsyncSessionLocal
from app.models.email import Email
from app.models.thread import Thread
from app.models.contact import Contact
from app.services.agent_service import AgentService
from sqlalchemy import select
import uuid
from datetime import datetime

async def test():
    await init_db()
    async with AsyncSessionLocal() as db:
        contact = Contact(
            id=str(uuid.uuid4()),
            email='test6@test.com',
            name='Test6',
            tier='Starter',
            account_value=0.0,
            vip_status=False,
            churn_risk_score=0.0
        )
        db.add(contact)
        await db.flush()
        
        thread = Thread(
            id=str(uuid.uuid4()),
            sender_email='test6@test.com',
            contact_id=contact.id,
            subject='Test6',
            category='General',
            status='Open'
        )
        db.add(thread)
        await db.flush()
        
        email = Email(
            id=str(uuid.uuid4()),
            message_id='agent_test_004',
            thread_id=thread.id,
            sender='test6@test.com',
            recipient='support@test.com',
            subject='Test6',
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
        
        # Call agent service run_agent
        agent_service = AgentService(db)
        trace = await agent_service.run_agent(
            str(email.id),
            {
                'category': 'Test',
                'urgency': 'Low',
                'sentiment_score': 0.0,
                'confidence': 0.5,
                'requires_human': False
            },
            is_dry_run=False
        )
        print('Agent trace:', trace.escalate, trace.final_recommendation)
        
        email.category = 'Modified'
        await db.commit()
        print('Committed')
    
    async with AsyncSessionLocal() as db2:
        result = await db2.execute(select(Email).where(Email.message_id == 'agent_test_004'))
        row = result.scalar_one_or_none()
        if row:
            print('Found:', row.message_id, row.category)
        else:
            print('Not found')

asyncio.run(test())
