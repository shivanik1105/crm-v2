import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        response = await client.get('http://127.0.0.1:8000/assets/index-DeRR8BoI.css', timeout=10)
        print(f'CSS: {response.status_code}')

asyncio.run(test())
