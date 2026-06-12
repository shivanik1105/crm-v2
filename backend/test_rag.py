import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        response = await client.get('http://127.0.0.1:8000/api/rag/search?q=refund+policy', timeout=10)
        print(f'RAG: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Results: {len(data["results"])}')
            for r in data['results']:
                print(f'  - {r["source"]}: {r["heading"]} (score: {r["similarity_score"]:.3f})')

asyncio.run(test())
