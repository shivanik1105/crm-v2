import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        response = await client.get('http://127.0.0.1:8000/api/dashboard/stats')
        print(f'Stats: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Total: {data["total_emails"]}')
            print(f'Threads: {data["total_threads"]}')
            print(f'Needs Human: {data["needs_human"]}')
            print(f'Escalated: {data["escalated"]}')

asyncio.run(test())
