import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.schemas.email import EmailIngest, EmailIngestResponse
from app.models.email import Email
from app.models.thread import Thread
from app.models.contact import Contact
from app.models.audit_log import AuditLog
from app.services.heuristic_filter import heuristic_filter
from app.services.llm_classifier import llm_classifier
from app.services.agent_service import AgentService
from app.services.sentiment_tracker import sentiment_tracker
from app.services.websocket_manager import ws_manager
from app.utils.error_envelope import ErrorEnvelope, CRMException

router = APIRouter()

async def process_email_async(db: AsyncSession, email_data: EmailIngest):
    heuristic_result = heuristic_filter(email_data)
    
    stmt = select(Thread).where(Thread.sender_email == email_data.sender)
    result = await db.execute(stmt)
    thread = result.scalar_one_or_none()
    
    if thread is None:
        contact_stmt = select(Contact).where(Contact.email == email_data.sender)
        contact_result = await db.execute(contact_stmt)
        contact = contact_result.scalar_one_or_none()
        
        if contact is None:
            contact = Contact(
                email=email_data.sender,
                name=email_data.sender.split("@")[0].replace(".", " ").title(),
                tier="Starter",
                account_value=0.0,
                vip_status=False,
                churn_risk_score=0.0
            )
            db.add(contact)
            await db.flush()
        
        thread = Thread(
            sender_email=email_data.sender,
            contact_id=contact.id,
            subject=email_data.subject,
            category="General",
            status="Open"
        )
        db.add(thread)
        await db.flush()
    else:
        thread.last_updated_at = datetime.utcnow()
    
    body = email_data.body
    body_truncated = len(body) > 10000
    if body_truncated:
        body = body[:10000]
    
    print("Creating Email with timestamp type:", type(email_data.timestamp), "value:", email_data.timestamp)
    email_record = Email(
        id=str(uuid.uuid4()),
        message_id=email_data.message_id,
        thread_id=thread.id,
        sender=email_data.sender,
        recipient=email_data.recipient,
        subject=email_data.subject,
        body=body,
        body_truncated=body_truncated,
        timestamp=email_data.timestamp,
        category="General",
        sentiment_score=0.0,
        urgency="Low",
        confidence=0.0,
        requires_human=heuristic_result.is_spam or heuristic_result.is_security,
        status="Processing",
        raw_entities={"heuristic_flags": heuristic_result.flags},
        classification_result={}
    )
    
    db.add(email_record)
    await db.flush()
    
    # Capture email_id immediately after flush
    email_id = email_record.id
    
    await ws_manager.send_email_event({
        "email_id": email_id,
        "message_id": email_data.message_id,
        "sender": email_data.sender,
        "subject": email_data.subject,
        "status": "Processing"
    })
    
    if not heuristic_result.is_spam:
        from sqlalchemy import select as sa_select
        email_history_stmt = sa_select(Email).where(Email.thread_id == thread.id).order_by(Email.timestamp)
        email_history_result = await db.execute(email_history_stmt)
        history_emails = email_history_result.scalars().all()
        
        emails_in_thread = []
        for e in history_emails:
            emails_in_thread.append(f"[{e.timestamp}] {e.sender}: {e.subject or 'No subject'} (sentiment: {e.sentiment_score})")
        thread_history = "\n".join(emails_in_thread[-10:])
        
        classification = await llm_classifier.classify(db, email_data, thread_history)
        
        email_record.category = classification.category
        email_record.sentiment_score = classification.sentiment_score
        email_record.urgency = classification.urgency
        email_record.confidence = classification.confidence
        email_record.requires_human = classification.requires_human or heuristic_result.is_security
        email_record.classification_result = classification.model_dump()
        
        thread.category = classification.category
        
        await ws_manager.send_classification_event(email_id, classification.model_dump())
        
        # Capture all values BEFORE agent run to avoid aiosqlite lazy-loading issues
        email_record.category = classification.category
        email_record.sentiment_score = classification.sentiment_score
        email_record.urgency = classification.urgency
        email_record.confidence = classification.confidence
        email_record.requires_human = classification.requires_human or heuristic_result.is_security
        email_record.classification_result = classification.model_dump()
        thread.category = classification.category
        
        await ws_manager.send_classification_event(email_id, classification.model_dump())
        
        agent_service = AgentService(db)
        trace = await agent_service.run_agent(
            email_id,
            classification.model_dump(),
            is_dry_run=False
        )
        
        # Apply agent decisions to ORM object
        if trace.escalate:
            email_record.status = "Escalated"
            thread.status = "Escalated"
        elif trace.draft_reply:
            email_record.status = "Drafted"
        
        # Capture all final values
        final_status = email_record.status
        final_category = email_record.category
        final_urgency = email_record.urgency
        
        await ws_manager.send_agent_event(email_id, {
            "steps": len(trace.steps),
            "escalate": trace.escalate,
            "final_recommendation": trace.final_recommendation,
            "tools_used": trace.tools_used
        })
        
        await sentiment_tracker.record_sentiment(
            email_data.sender,
            email_id,
            classification.sentiment_score,
            email_data.timestamp
        )
    else:
        email_record.status = "Spam"
        thread.status = "Spam"
        final_status = "Spam"
        final_category = "Spam"
        final_urgency = "Low"
    
    print("About to commit email record")
    await db.commit()
    print("Committed email record")
    
    audit = AuditLog(
        entity_type="email",
        entity_id=email_id,
        action="ingested",
        actor="system",
        diff={
            "message_id": email_data.message_id,
            "sender": email_data.sender,
            "heuristic_flags": heuristic_result.flags,
            "final_status": final_status
        }
    )
    db.add(audit)
    await db.commit()
    
    await ws_manager.send_action_event("email_processed", email_id, {
        "status": final_status,
        "category": final_category,
        "urgency": final_urgency
    })
    
    return email_id

@router.post("/ingest", response_model=EmailIngestResponse)
async def ingest_email(
    request: Request,
    email_data: EmailIngest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    if not email_data.message_id or not email_data.sender or not email_data.body:
        return ErrorEnvelope.create(
            error_code="VALIDATION_ERROR",
            message="Missing required fields: message_id, sender, body",
            status_code=400
        )
    
    stmt = select(Email).where(Email.message_id == email_data.message_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()
    
    if existing:
        return EmailIngestResponse(
            job_id=str(existing.id),
            status="existing",
            message="Email already ingested",
            existing=True,
            email_id=str(existing.id)
        )
    
    if len(email_data.body) > 10000:
        email_data.body = email_data.body[:10000]
    
    try:
        email_id = await process_email_async(db, email_data)
    except Exception as e:
        import traceback
        print("ERROR in process_email_async:", e)
        traceback.print_exc()
        raise
    
    return EmailIngestResponse(
        job_id=email_id,
        status="processed",
        message="Email ingested and processed",
        existing=False,
        email_id=email_id
    )

@router.get("/status/{job_id}")
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Email).where(Email.id == job_id)
    result = await db.execute(stmt)
    email = result.scalar_one_or_none()
    
    if email is None:
        return ErrorEnvelope.create(
            error_code="NOT_FOUND",
            message="Email not found",
            status_code=404
        )
    
    return {
        "job_id": job_id,
        "status": email.status,
        "category": email.category,
        "urgency": email.urgency,
        "requires_human": email.requires_human,
        "classification": email.classification_result
    }
