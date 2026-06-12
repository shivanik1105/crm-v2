from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from app.database import get_db
from app.models.email import Email
from app.models.action import Action
from app.models.audit_log import AuditLog
from app.services.websocket_manager import ws_manager
from typing import Optional, List
from uuid import UUID
from datetime import datetime

router = APIRouter()

@router.get("/")
async def list_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    category: Optional[str] = None,
    urgency: Optional[str] = None,
    status: Optional[str] = None,
    requires_human: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Email).order_by(desc(Email.timestamp))
    
    if category:
        stmt = stmt.where(Email.category == category)
    if urgency:
        stmt = stmt.where(Email.urgency == urgency)
    if status:
        stmt = stmt.where(Email.status == status)
    if requires_human is not None:
        stmt = stmt.where(Email.requires_human == requires_human)
    
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    emails = result.scalars().all()
    
    return [
        {
            "id": str(e.id),
            "message_id": e.message_id,
            "sender": e.sender,
            "subject": e.subject,
            "body": e.body[:200] + "..." if len(e.body) > 200 else e.body,
            "timestamp": e.timestamp.isoformat(),
            "category": e.category,
            "sentiment_score": e.sentiment_score,
            "urgency": e.urgency,
            "confidence": e.confidence,
            "requires_human": e.requires_human,
            "status": e.status,
            "thread_id": str(e.thread_id)
        }
        for e in emails
    ]

@router.get("/{email_id}")
async def get_email(
    email_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Email).where(Email.id == email_id)
    result = await db.execute(stmt)
    email = result.scalar_one_or_none()
    
    if not email:
        raise HTTPException(404, "Email not found")
    
    return {
        "id": str(email.id),
        "message_id": email.message_id,
        "sender": email.sender,
        "recipient": email.recipient,
        "subject": email.subject,
        "body": email.body,
        "timestamp": email.timestamp.isoformat(),
        "category": email.category,
        "sentiment_score": email.sentiment_score,
        "urgency": email.urgency,
        "confidence": email.confidence,
        "requires_human": email.requires_human,
        "status": email.status,
        "classification_result": email.classification_result,
        "reasoning_trace": email.reasoning_trace or {},
        "rag_chunks": email.rag_chunks or [],
        "thread_id": str(email.thread_id),
        "created_at": email.created_at.isoformat()
    }

@router.get("/{email_id}/reasoning")
async def get_email_reasoning(
    email_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Email).where(Email.id == email_id)
    result = await db.execute(stmt)
    email = result.scalar_one_or_none()
    
    if not email:
        raise HTTPException(404, "Email not found")
    
    classification = email.classification_result or {}
    
    reasoning = {
        "email_id": str(email.id),
        "scenario_detected": classification.get("scenario_detected"),
        "confidence": classification.get("confidence", 0.0),
        "rag_context_used": classification.get("rag_context_used", False),
        "reasoning_steps": [
            {
                "step": 1,
                "thought": f"Analyzing email from {email.sender}",
                "action": "Heuristic filtering",
                "observation": f"Category: {email.category}, Urgency: {email.urgency}",
                "next_step": "RAG retrieval"
            },
            {
                "step": 2,
                "thought": "Searching knowledge base for relevant policies",
                "action": "Vector similarity search",
                "observation": f"Found {len(classification.get('rag_chunks', []))} relevant policy chunks",
                "next_step": "LLM classification"
            },
            {
                "step": 3,
                "thought": "Classifying with LLM using context",
                "action": "Groq API call with RAG context",
                "observation": f"Confidence: {classification.get('confidence', 0):.2f}, Keywords: {', '.join(classification.get('keywords_detected', [])[:3])}",
                "next_step": "Final decision"
            }
        ],
        "final_decision": classification.get("suggested_action", "Route to appropriate team"),
        "escalation_triggered": email.requires_human,
        "keywords_detected": classification.get("keywords_detected", []),
        "escalation_reason": classification.get("escalation_reason")
    }
    
    return reasoning

@router.get("/{email_id}/rag-context")
async def get_rag_context(
    email_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Email).where(Email.id == email_id)
    result = await db.execute(stmt)
    email = result.scalar_one_or_none()
    
    if not email:
        raise HTTPException(404, "Email not found")
    
    from app.services.rag_service import rag_service
    
    query = f"{email.subject or ''} {email.body[:500]}"
    chunks = await rag_service.search(db, query, top_k=3)
    
    return {
        "email_id": str(email.id),
        "query": query[:200],
        "chunks_retrieved": [
            {
                "source": chunk.source,
                "heading": chunk.heading,
                "content": chunk.content[:300] + "..." if len(chunk.content) > 300 else chunk.content,
                "similarity_score": round(chunk.score, 3),
                "chunk_index": chunk.chunk_index
            }
            for chunk in chunks
        ],
        "total_chunks": len(chunks)
    }

@router.post("/bulk/spam")
async def bulk_mark_spam(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    email_ids = payload.get("email_ids", [])
    updated = 0
    for eid in email_ids:
        try:
            stmt = select(Email).where(Email.id == eid)
            result = await db.execute(stmt)
            email = result.scalar_one_or_none()
            if email:
                email.status = "Spam"
                updated += 1
        except Exception:
            continue
    await db.commit()
    await ws_manager.send_action_event("bulk_spam", "", {"count": updated})
    return {"updated": updated, "status": "Spam"}

@router.post("/bulk/assign")
async def bulk_assign(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    email_ids = payload.get("email_ids", [])
    assignee = payload.get("assignee", "unassigned")
    updated = 0
    for eid in email_ids:
        try:
            stmt = select(Email).where(Email.id == eid)
            result = await db.execute(stmt)
            email = result.scalar_one_or_none()
            if email:
                action = Action(
                    email_id=eid,
                    action_type="Assigned",
                    status="Assigned",
                    assigned_to=assignee,
                    description=f"Assigned to {assignee}"
                )
                db.add(action)
                updated += 1
        except Exception:
            continue
    await db.commit()
    return {"updated": updated, "assignee": assignee}

@router.post("/bulk/archive")
async def bulk_archive(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    email_ids = payload.get("email_ids", [])
    updated = 0
    for eid in email_ids:
        try:
            stmt = select(Email).where(Email.id == eid)
            result = await db.execute(stmt)
            email = result.scalar_one_or_none()
            if email:
                email.status = "Archived"
                updated += 1
        except Exception:
            continue
    await db.commit()
    await ws_manager.send_action_event("bulk_archive", "", {"count": updated})
    return {"updated": updated, "status": "Archived"}
