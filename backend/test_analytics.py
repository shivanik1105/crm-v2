import httpx
import asyncio

async def test_analytics():
    async with httpx.AsyncClient() as client:
        # Test sentiment trend
        response = await client.get('http://127.0.0.1:8000/api/analytics/sentiment-trend?sender=alice@example.com&days=30')
        print(f'Sentiment Trend: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'  Points: {len(data["points"])}')
            print(f'  Trend: {data["trend_direction"]}')
        
        # Test at-risk
        response = await client.get('http://127.0.0.1:8000/api/analytics/at-risk')
        print(f'At-Risk: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'  Accounts: {data["total_at_risk"]}')
        
        # Test response time heatmap
        response = await client.get('http://127.0.0.1:8000/api/analytics/response-time-heatmap')
        print(f'Heatmap: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'  Data points: {len(data["heatmap"])}')
        
        # Test agent performance
        response = await client.get('http://127.0.0.1:8000/api/analytics/agent-performance')
        print(f'Agent Performance: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'  Processed: {data["total_processed"]}')
            print(f'  Escalated: {data["total_escalated"]}')
            print(f'  Escalation Rate: {data["escalation_rate"]}%')

asyncio.run(test_analytics())
