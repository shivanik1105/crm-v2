import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient() as client:
        # Check Karen's sentiment trend
        r = await client.get('http://127.0.0.1:8000/api/analytics/sentiment-trend?sender=karen@example.com&days=30', timeout=10)
        data = r.json()
        print(f'Karen sentiment trend:')
        print(f'  Trend direction: {data.get("trend_direction")}')
        print(f'  Moving average: {data.get("moving_average")}')
        print(f'  Alert triggered: {data.get("alert_triggered")}')
        print(f'  Points: {len(data.get("points", []))}')
        for point in data.get("points", [])[:5]:
            print(f"    {point['timestamp']}: {point['sentiment_score']}")

asyncio.run(test())
