import asyncio
from app.config import settings

print(f"API Key: {settings.GROQ_API_KEY[:20]}...")
print(f"Model: {settings.GROQ_MODEL}")
print(f"Database: {settings.DATABASE_URL}")
