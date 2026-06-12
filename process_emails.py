import sys
sys.path.insert(0, 'backend')

import asyncio
import json
import time
import urllib.request

async def main():
    # Wait for server
    for i in range(30):
        try:
            urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)
            break
        except:
            time.sleep(1)
    
    with open('email-data-advanced.json', 'r') as f:
        emails = json.load(f)
    
    for email in emails:
        try:
            req = urllib.request.Request(
                'http://127.0.0.1:8000/api/ingest',
                data=json.dumps(email).encode(),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            r = urllib.request.urlopen(req, timeout=60)
            print(f"OK {email['message_id']}")
        except Exception as e:
            print(f"ERR {email['message_id']}: {str(e)[:50]}")
        time.sleep(0.2)
    
    print("Done")

asyncio.run(main())
