import asyncio
from app.database import init_db, AsyncSessionLocal
from app.models.email import Email
from app.models.thread import Thread
from app.models.contact import Contact
from app.models.action import Action
from app.services.agent_service import AgentService
from app.schemas.agent import AgentStep, AgentTrace
from sqlalchemy import select
import uuid
from datetime import datetime

async def test():
    await init_db()
    async with AsyncSessionLocal() as db:
        contact = Contact(
            id=str(uuid.uuid4()),
            email='test7@test.com',
            name='Test7',
            tier='Starter',
            account_value=0.0,
            vip_status=False,
            churn_risk_score=0.0
        )
        db.add(contact)
        await db.flush()
        
        thread = Thread(
            id=str(uuid.uuid4()),
            sender_email='test7@test.com',
            contact_id=contact.id,
            subject='Test7',
            category='General',
            status='Open'
        )
        db.add(thread)
        await db.flush()
        
        email = Email(
            id=str(uuid.uuid4()),
            message_id='agent_test_005',
            thread_id=thread.id,
            sender='test7@test.com',
            recipient='support@test.com',
            subject='Test7',
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
        
        # Simulate _store_trace
        trace = AgentTrace(
            email_id=str(email.id),
            classification={'category': 'Test'},
            steps=[AgentStep(step_number=1, thought='Test', action='test', action_input={})],
            final_recommendation='Test',
            escalate=False,
            tools_used=[],
            completed_at=datetime.utcnow(),
            dry_run=False
        )
        
        try:
            action = Action(
                email_id=str(email.id),
                action_type='Agent-Run',
                status='Completed',
                description=trace.final_recommendation,
                agent_reasoning_log=[step.model_dump() for step in trace.steps]
            )
            db.add(action)
            await db.flush()
            print('Action flushed successfully')
        except Exception as e:
            print(f'Action flush failed: {e}')
            await db.rollback()
        
        email.category = 'Modified'
        await db.commit()
        print('Committed')
    
    async with AsyncSessionLocal() as db2:
        result = await db2.execute(select(Email).where(Email.message_id == 'agent_test_005'))
        row = result.scalar_one_or_none()
        if row:
            print('Found:', row.message_id, row.category)
        else:
            print('Not found')

asyncio.run(test())
