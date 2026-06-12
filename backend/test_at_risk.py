import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient() as client:
        r = await client.get('http://127.0.0.1:8000/api/analytics/at-risk', timeout=10)
        data = r.json()
        accounts = data.get("accounts", [])
        print(f'At-risk accounts: {len(accounts)}')
        for acc in accounts:
            print(f"  {acc['sender']}: churn={acc['churn_risk_score']}, value=${acc['account_value']}/mo, unresolved={acc['unresolved_threads']}, trend={acc['sentiment_trend']}")

asyncio.run(test())
