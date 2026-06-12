import sys
sys.path.insert(0, 'backend')

import asyncio
import json
import time
import httpx

async def main():
    async with httpx.AsyncClient() as client:
        # Wait for server
        for i in range(30):
            try:
                r = await client.get('http://127.0.0.1:8000/health', timeout=2)
                if r.status_code == 200:
                    break
            except:
                pass
            await asyncio.sleep(1)
        
        with open('email-data-advanced.json', 'r') as f:
            emails = json.load(f)
        
        for email in emails:
            try:
                r = await client.post(
                    'http://127.0.0.1:8000/api/ingest',
                    json=email,
                    timeout=60
                )
                data = r.json()
                if data.get('existing'):
                    print(f"EXIST {email['message_id']}")
                else:
                    print(f"OK {email['message_id']}")
            except Exception as e:
                print(f"ERR {email['message_id']}: {str(e)[:50]}")
            await asyncio.sleep(0.5)
        
        print("Done")

asyncio.run(main())
