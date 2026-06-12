import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        response = await client.get('http://127.0.0.1:8000/', timeout=10)
        print(f'Root: {response.status_code}')
        if response.status_code == 200:
            print(f'Length: {len(response.text)}')
            print(f'Is HTML: {response.text.startswith("<")}')

asyncio.run(test())
