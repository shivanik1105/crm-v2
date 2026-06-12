import httpx
import asyncio

async def test_sentiment():
    async with httpx.AsyncClient() as client:
        # Test different senders
        senders = ['alice@example.com', 'bob@example.com', 'karen@example.com']
        for sender in senders:
            response = await client.get(f'http://127.0.0.1:8000/api/analytics/sentiment-trend?sender={sender}&days=30')
            print(f'{sender}: {response.status_code}')
            if response.status_code == 200:
                data = response.json()
                print(f'  Points: {len(data["points"])}')
                print(f'  Trend: {data["trend_direction"]}')

asyncio.run(test_sentiment())
