from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.thread import Thread
from app.models.email import Email
from app.utils.error_envelope import ErrorEnvelope
import httpx
from app.config import settings

router = APIRouter()

@router.get("/{contact_email}")
async def get_thread_by_contact(
    contact_email: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Thread)
        .options(selectinload(Thread.emails))
        .options(selectinload(Thread.contact))
        .where(Thread.sender_email == contact_email)
        .order_by(Thread.last_updated_at.desc())
    )
    result = await db.execute(stmt)
    threads = result.scalars().all()
    
    if not threads:
        return ErrorEnvelope.create(
            error_code="NOT_FOUND",
            message=f"No threads found for {contact_email}",
            status_code=404
        )
    
    response = []
    for thread in threads:
        emails_data = []
        for email in thread.emails:
            emails_data.append({
                "id": str(email.id),
                "message_id": email.message_id,
                "sender": email.sender,
                "recipient": email.recipient,
                "subject": email.subject,
                "body": email.body,
                "body_truncated": email.body_truncated,
                "timestamp": email.timestamp.isoformat(),
                "category": email.category,
                "sentiment_score": email.sentiment_score,
                "urgency": email.urgency,
                "confidence": email.confidence,
                "requires_human": email.requires_human,
                "status": email.status,
                "raw_entities": email.raw_entities,
                "classification_result": email.classification_result,
                "created_at": email.created_at.isoformat()
            })
        
        response.append({
            "id": str(thread.id),
            "sender_email": thread.sender_email,
            "subject": thread.subject,
            "category": thread.category,
            "status": thread.status,
            "last_updated_at": thread.last_updated_at.isoformat() if thread.last_updated_at else None,
            "created_at": thread.created_at.isoformat() if thread.created_at else None,
            "emails": emails_data
        })
    
    return response

@router.get("/{contact_email}/summary")
async def get_thread_summary(
    contact_email: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Thread)
        .options(selectinload(Thread.emails))
        .where(Thread.sender_email == contact_email)
        .order_by(Thread.last_updated_at.desc())
    )
    result = await db.execute(stmt)
    threads = result.scalars().all()
    
    if not threads:
        return ErrorEnvelope.create(
            error_code="NOT_FOUND",
            message=f"No threads found for {contact_email}",
            status_code=404
        )
    
    thread = threads[0]
    emails = thread.emails
    
    if len(emails) < 2:
        return {
            "summary": f"Single email from {contact_email}: {emails[0].subject if emails else 'No subject'}",
            "email_count": len(emails),
            "generated_by": "system"
        }
    
    email_context = "\n".join([
        f"[{e.timestamp}] {e.sender}: {e.subject or 'No subject'} | Sentiment: {e.sentiment_score} | Category: {e.category}\n{e.body[:200]}"
        for e in emails
    ])
    
    if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "your_key_here":
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": settings.GROQ_MODEL,
                        "messages": [
                            {
                                "role": "system",
                                "content": "Summarize this email thread in exactly 3 sentences. Focus on: (1) what the customer wants, (2) key issues/escalations, (3) current status."
                            },
                            {
                                "role": "user",
                                "content": f"Email thread from {contact_email} ({len(emails)} emails):\n\n{email_context[:3000]}"
                            }
                        ],
                        "temperature": 0.3,
                        "max_tokens": 200
                    }
                )
                response.raise_for_status()
                data = response.json()
                summary = data["choices"][0]["message"]["content"].strip()
                return {
                    "summary": summary,
                    "email_count": len(emails),
                    "generated_by": "llm"
                }
        except Exception:
            pass
    
    sentiments = [e.sentiment_score for e in emails]
    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
    categories = list(set(e.category for e in emails if e.category))
    urgency_levels = list(set(e.urgency for e in emails if e.urgency))
    
    summary = f"Thread with {len(emails)} emails from {contact.email if hasattr(contact_email, 'email') else contact_email} "
    summary += f"covering {', '.join(categories[:3])}. "
    summary += f"Overall sentiment is {'positive' if avg_sentiment > 0.1 else 'negative' if avg_sentiment < -0.1 else 'neutral'} (avg: {avg_sentiment:.2f}). "
    summary += f"Max urgency: {max(urgency_levels, key=lambda u: ['Low', 'Medium', 'High', 'Critical'].index(u) if u in ['Low', 'Medium', 'High', 'Critical'] else 0)}."
    
    return {
        "summary": summary,
        "email_count": len(emails),
        "generated_by": "heuristic"
    }
