import asyncio
from app.database import init_db, engine
from sqlalchemy import text

async def test():
    await init_db()
    async with engine.begin() as conn:
        await conn.execute(text("INSERT INTO emails (id, message_id, thread_id, sender, recipient, subject, body, timestamp, category, sentiment_score, urgency, confidence, requires_human, status) VALUES ('test-id', 'raw_test_001', 'thread-id', 'test@test.com', 'support@test.com', 'test', 'test body', '2024-01-15T10:30:00', 'Test', 0.0, 'Low', 0.5, 0, 'New')"))
    
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT * FROM emails WHERE message_id = 'raw_test_001'"))
        row = result.fetchone()
        if row:
            print('Found:', row)
        else:
            print('Not found')

asyncio.run(test())
