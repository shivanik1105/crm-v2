import sys
sys.path.insert(0, 'backend')

import asyncio
import json
import time
import aiohttp

async def main():
    async with aiohttp.ClientSession() as session:
        # Wait for server
        for i in range(30):
            try:
                async with session.get('http://127.0.0.1:8000/health', timeout=2):
                    break
            except:
                await asyncio.sleep(1)
        
        with open('email-data-advanced.json', 'r') as f:
            emails = json.load(f)
        
        async def process_one(email):
            try:
                async with session.post(
                    'http://127.0.0.1:8000/api/ingest',
                    json=email,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    data = await resp.json()
                    if data.get('existing'):
                        print(f"EXIST {email['message_id']}")
                    else:
                        print(f"OK {email['message_id']}")
            except Exception as e:
                print(f"ERR {email['message_id']}: {str(e)[:50]}")
        
        # Process 5 at a time
        semaphore = asyncio.Semaphore(5)
        async def limited_process(email):
            async with semaphore:
                await process_one(email)
        
        tasks = [limited_process(e) for e in emails]
        await asyncio.gather(*tasks)
        print("Done")

asyncio.run(main())
