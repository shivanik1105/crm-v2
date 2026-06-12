import asyncio
import json
import argparse
import httpx
from pathlib import Path

async def load_email_data(file_path: str) -> list:
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    if isinstance(data, dict) and "emails" in data:
        emails = data["emails"]
    elif isinstance(data, list):
        emails = data
    else:
        emails = []
    
    emails.sort(key=lambda e: e.get("timestamp", ""))
    return emails

async def simulate(file_path: str, speed: int, url: str):
    try:
        emails = await load_email_data(file_path)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return
    except json.JSONDecodeError:
        print(f"Invalid JSON in {file_path}")
        return
    
    print(f"Starting simulation of {len(emails)} emails at speed {speed}/sec")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, email in enumerate(emails, 1):
            try:
                response = await client.post(f"{url}/api/ingest", json=email)
                status = "OK" if response.status_code in (200, 201) else f"ERR {response.status_code}"
                print(f"[{i}/{len(emails)}] {email.get('message_id', 'unknown')} | {email.get('sender', 'unknown')} | {status}")
                
                if speed > 0:
                    await asyncio.sleep(1.0 / speed)
            except Exception as e:
                print(f"[{i}/{len(emails)}] Error: {e}")
    
    print("Simulation complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate email stream to CRM")
    parser.add_argument("--file", default="email-data-advanced.json", help="Path to email JSON file")
    parser.add_argument("--speed", type=int, default=1, help="Emails per second (0 = all at once)")
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="API base URL")
    args = parser.parse_args()
    
    asyncio.run(simulate(args.file, args.speed, args.url))
