import asyncio
from app.database import AsyncSessionLocal
from app.models.email import Email
from sqlalchemy import select, func

async def test_distribution():
    async with AsyncSessionLocal() as db:
        stmt = select(Email.sentiment_score, func.count(Email.id)).group_by(Email.sentiment_score).order_by(Email.sentiment_score)
        result = await db.execute(stmt)
        rows = result.all()
        print('Sentiment distribution:')
        for score, count in rows:
            print(f'  {score}: {count}')

asyncio.run(test_distribution())
