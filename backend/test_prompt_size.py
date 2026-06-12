import asyncio
from app.services.llm_classifier import llm_classifier
from app.schemas.email import EmailIngest
from app.database import AsyncSessionLocal
from datetime import datetime

async def test_prompt_size():
    email = EmailIngest(
        message_id='test_llm_001',
        sender='test@example.com',
        recipient='support@company.com',
        subject='I want a refund',
        body='I want a refund for my purchase. It was within 14 days.',
        timestamp=datetime.now()
    )
    
    from app.services.rag_service import rag_service
    
    async with AsyncSessionLocal() as db:
        query = f"{email.subject or ''} {email.body[:500]}"
        rag_chunks = await rag_service.search(db, query, top_k=3)
        rag_context = rag_service.format_for_llm(rag_chunks)
        
        system_prompt = llm_classifier._build_system_prompt(rag_context, "")
        user_prompt = llm_classifier._build_user_prompt(email, "")
        
        print(f'System prompt length: {len(system_prompt)} chars')
        print(f'User prompt length: {len(user_prompt)} chars')
        print(f'Total: {len(system_prompt) + len(user_prompt)} chars')
        print(f'\nRAG context:')
        print(rag_context)

asyncio.run(test_prompt_size())
