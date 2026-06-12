import asyncio
from app.database import AsyncSessionLocal
from app.models.email import Email
from sqlalchemy import select

async def test_db():
    async with AsyncSessionLocal() as db:
        stmt = select(Email).where(Email.sender == 'alice@example.com').limit(5)
        result = await db.execute(stmt)
        emails = result.scalars().all()
        print(f'Emails for alice: {len(emails)}')
        for email in emails:
            print(f'  {email.message_id}: sentiment={email.sentiment_score}, timestamp={email.timestamp}')

asyncio.run(test_db())
