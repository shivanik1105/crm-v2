import asyncio
from app.database import AsyncSessionLocal
from app.models.email import Email
from sqlalchemy import select

async def check_flags():
    async with AsyncSessionLocal() as db:
        stmt = select(Email).limit(20)
        result = await db.execute(stmt)
        emails = result.scalars().all()
        for email in emails:
            print(f'{email.message_id}:')
            print(f'  status: {email.status}')
            print(f'  requires_human: {email.requires_human}')
            print(f'  heuristic_flags: {email.raw_entities}')
            print(f'  classification: {email.classification_result}')
            print()

asyncio.run(check_flags())
