import asyncio
import json
from typing import Optional
import httpx
from datetime import datetime
from app.config import settings

class StreamSimulator:
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def load_email_data(self, file_path: str) -> list:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, dict) and "emails" in data:
            emails = data["emails"]
        elif isinstance(data, list):
            emails = data
        else:
            emails = []
        
        # Sort by timestamp
        emails.sort(key=lambda e: e.get("timestamp", ""))
        return emails
    
    async def simulate(
        self,
        file_path: str = "email-data-advanced.json",
        speed: Optional[int] = None
    ):
        speed = speed or settings.STREAM_SPEED
        
        try:
            emails = await self.load_email_data(file_path)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return
        except json.JSONDecodeError:
            print(f"Invalid JSON in {file_path}")
            return
        
        print(f"Starting simulation of {len(emails)} emails at speed {speed}/sec")
        
        for i, email in enumerate(emails, 1):
            try:
                response = await self.client.post(
                    f"{self.api_url}/api/ingest",
                    json=email
                )
                
                status = "OK" if response.status_code in (200, 201) else f"ERR {response.status_code}"
                print(f"[{i}/{len(emails)}] {email.get('message_id', 'unknown')} | {email.get('sender', 'unknown')} | {status}")
                
                if speed > 0:
                    await asyncio.sleep(1.0 / speed)
                    
            except Exception as e:
                print(f"[{i}/{len(emails)}] Error: {e}")
        
        print("Simulation complete.")
    
    async def close(self):
        await self.client.aclose()

# CLI entry point
async def main():
    import argparse
    parser = argparse.ArgumentParser(description="Simulate email stream to CRM")
    parser.add_argument("--file", default="email-data-advanced.json", help="Path to email JSON file")
    parser.add_argument("--speed", type=int, default=1, help="Emails per second (0 = all at once)")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()
    
    simulator = StreamSimulator(api_url=args.url)
    try:
        await simulator.simulate(file_path=args.file, speed=args.speed)
    finally:
        await simulator.close()

if __name__ == "__main__":
    asyncio.run(main())
