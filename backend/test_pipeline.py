import asyncio
import httpx

async def test_full_pipeline():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://127.0.0.1:8000/api/ingest',
            json={
                'message_id': 'final_test_002',
                'sender': 'test@example.com',
                'recipient': 'support@company.com',
                'subject': 'URGENT: System outage - all services down',
                'body': 'Our entire production system is down. All customers are affected. This is a critical P0 incident requiring immediate attention.',
                'timestamp': '2024-06-11T10:30:00Z'
            }
        )
        print(f'Ingest Status: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Email ID: {data["email_id"]}')
            print(f'Status: {data["status"]}')
            
            await asyncio.sleep(2)
            email_response = await client.get(f"http://127.0.0.1:8000/api/emails/{data['email_id']}")
            print(f'Email retrieval: {email_response.status_code}')
            if email_response.status_code == 200:
                email_data = email_response.json()
                print(f'Category: {email_data["category"]}')
                print(f'Urgency: {email_data["urgency"]}')
                print(f'Status: {email_data["status"]}')
                print(f'Classification: {email_data["classification_result"]}')
            else:
                print(f'Email retrieval error: {email_response.text}')
                
            # Try to get by message_id
            list_response = await client.get(f"http://127.0.0.1:8000/api/emails/")
            if list_response.status_code == 200:
                emails = list_response.json()
                for e in emails:
                    if e['message_id'] == 'final_test_002':
                        print(f'Found email in list: {e["id"]}')
                        email_response2 = await client.get(f"http://127.0.0.1:8000/api/emails/{e['id']}")
                        print(f'Email retrieval by list ID: {email_response2.status_code}')
                        break

asyncio.run(test_full_pipeline())
