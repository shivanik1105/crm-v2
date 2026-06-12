import asyncio
import json
import httpx

async def process_all_emails():
    with open('email-data-advanced.json', 'r') as f:
        emails = json.load(f)
    
    print(f"Processing {len(emails)} emails...")
    
    async with httpx.AsyncClient() as client:
        for i, email in enumerate(emails):
            try:
                response = await client.post(
                    'http://127.0.0.1:8000/api/ingest',
                    json=email,
                    timeout=60.0
                )
                if response.status_code == 200:
                    data = response.json()
                    print(f"[{i+1}/{len(emails)}] {email['message_id']} -> {data['status']} (category: {data.get('category', 'N/A')})")
                elif response.status_code == 422:
                    print(f"[{i+1}/{len(emails)}] {email['message_id']} -> VALIDATION ERROR")
                    print(f"  Response: {response.text}")
                else:
                    print(f"[{i+1}/{len(emails)}] {email['message_id']} -> ERROR {response.status_code}")
                    print(f"  Response: {response.text[:200]}")
            except Exception as e:
                print(f"[{i+1}/{len(emails)}] {email['message_id']} -> EXCEPTION: {e}")
            
            # Small delay to not overwhelm the server
            await asyncio.sleep(0.1)
    
    print("Done processing all emails!")

if __name__ == "__main__":
    asyncio.run(process_all_emails())
