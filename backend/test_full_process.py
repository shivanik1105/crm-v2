import asyncio
from app.database import init_db, AsyncSessionLocal
from app.schemas.email import EmailIngest
from app.routers.ingest import process_email_async
from app.models.email import Email
from sqlalchemy import select

async def test():
    await init_db()
    async with AsyncSessionLocal() as db:
        email_data = EmailIngest(
            message_id='full_test_001',
            sender='bob@example.com',
            recipient='support@company.com',
            subject='URGENT: System outage',
            body='Our system is down. This is a P0 emergency.',
            timestamp='2024-01-15T10:30:00Z'
        )
        result = await process_email_async(db, email_data)
        print('Result:', result)
    
    async with AsyncSessionLocal() as db2:
        result = await db2.execute(select(Email).where(Email.message_id == 'full_test_001'))
        row = result.scalar_one_or_none()
        if row:
            print('Found:', row.message_id, row.category, row.status)
        else:
            print('Not found')

asyncio.run(test())
