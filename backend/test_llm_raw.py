import asyncio
import json
from app.services.llm_classifier import llm_classifier
from app.schemas.email import EmailIngest
from app.database import AsyncSessionLocal
from datetime import datetime
import httpx
from app.config import settings

async def test_llm_raw():
    email = EmailIngest(
        message_id='test_llm_001',
        sender='test@example.com',
        recipient='support@company.com',
        subject='I want a refund',
        body='I want a refund for my purchase. It was within 14 days.',
        timestamp=datetime.now()
    )
    
    # Build the prompts as the classifier does
    from app.services.rag_service import rag_service
    from app.schemas.classification import ClassificationResult
    
    async with AsyncSessionLocal() as db:
        query = f"{email.subject or ''} {email.body[:500]}"
        rag_chunks = await rag_service.search(db, query, top_k=3)
        rag_context = rag_service.format_for_llm(rag_chunks)
        
        schema_json = ClassificationResult.model_json_schema()
        
        system_prompt = f"""You are an AI email triage specialist.

{rag_context}

CRITICAL RULES:
1. Never auto-reply to: spam, ransomware threats, legal threats, or GDPR requests
2. If confidence < 0.70, set requires_human = true"""
        
        user_prompt = f"""Analyze this email and return ONLY JSON matching this schema:
{json.dumps(schema_json, indent=2)}

Email:
From: {email.sender}
Subject: {email.subject or "(no subject)"}
Body: {email.body[:3000]}

Output ONLY JSON."""
        
        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "SenAI CRM"
        }
        
        payload = {
            "model": settings.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 256
        }
        
        # Build actual prompts using classifier methods
        from app.services.rag_service import rag_service
        from app.schemas.classification import ClassificationResult
        
        query = f"{email.subject or ''} {email.body[:500]}"
        rag_chunks = await rag_service.search(db, query, top_k=1)
        rag_context = rag_service.format_for_llm(rag_chunks)
        
        schema_json = ClassificationResult.model_json_schema()
        
        system_prompt = llm_classifier._build_system_prompt(rag_context, "")
        user_prompt = llm_classifier._build_user_prompt(email, json.dumps(schema_json, indent=2))
        
        print(f'System prompt length: {len(system_prompt)} chars')
        print(f'User prompt length: {len(user_prompt)} chars')
        
        payload = {
            "model": settings.GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 128
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload
                )
                print(f'API Status: {response.status_code}')
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    print(f'Raw Response (first 500 chars):\n{content[:500]}')
                    
                    json_str = llm_classifier._extract_json(content)
                    print(f'\nExtracted JSON: {json_str[:200] if json_str else None}')
                    if json_str:
                        try:
                            parsed = json.loads(json_str)
                            print(f'Parsed: {json.dumps(parsed, indent=2)[:500]}')
                        except Exception as e:
                            print(f'Parse error: {e}')
                else:
                    print(f'API Error: {response.text[:500]}')
            except Exception as e:
                print(f'Request error: {e}')

asyncio.run(test_llm_raw())
