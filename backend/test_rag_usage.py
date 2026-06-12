import asyncio
from app.database import AsyncSessionLocal
from app.models.email import Email
from sqlalchemy import select

async def check_rag():
    async with AsyncSessionLocal() as db:
        stmt = select(Email).limit(5)
        result = await db.execute(stmt)
        emails = result.scalars().all()
        for email in emails:
            print(f'{email.message_id}:')
            print(f'  category: {email.category}')
            print(f'  classification_result: {email.classification_result}')
            print()

asyncio.run(check_rag())
