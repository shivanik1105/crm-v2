from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.email import Email
from app.models.action import Action
from app.models.audit_log import AuditLog
from app.services.websocket_manager import ws_manager
from app.utils.error_envelope import ErrorEnvelope
from datetime import datetime

router = APIRouter()

@router.post("/{email_id}")
async def respond_to_email(
    email_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Email).where(Email.id == email_id)
    result = await db.execute(stmt)
    email = result.scalar_one_or_none()
    
    if email is None:
        return ErrorEnvelope.create(
            error_code="NOT_FOUND",
            message="Email not found",
            status_code=404
        )
    
    email.status = "Replied"
    await db.commit()
    
    await ws_manager.send_action_event("reply_sent", email_id, {"status": "Replied"})
    
    return {
        "email_id": email_id,
        "status": "Replied",
        "message": "Email marked as replied"
    }

@router.patch("/drafts/{email_id}")
async def update_draft(
    email_id: str,
    draft_body: dict,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Email).where(Email.id == email_id)
    result = await db.execute(stmt)
    email = result.scalar_one_or_none()
    
    if email is None:
        return ErrorEnvelope.create(
            error_code="NOT_FOUND",
            message="Email not found",
            status_code=404
        )
    
    draft_text = draft_body.get("draft_body", "")
    if email.classification_result is None:
        email.classification_result = {}
    email.classification_result["draft_body"] = draft_text
    email.status = "Drafted"
    await db.commit()
    
    await ws_manager.send_action_event("draft_updated", email_id, {"has_draft": True})
    
    return {
        "email_id": email_id,
        "draft_updated": True,
        "draft_body": draft_text,
        "status": "Drafted"
    }

@router.post("/drafts/{email_id}/approve")
async def approve_draft(
    email_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Email).where(Email.id == email_id)
    result = await db.execute(stmt)
    email = result.scalar_one_or_none()
    
    if email is None:
        return ErrorEnvelope.create(
            error_code="NOT_FOUND",
            message="Email not found",
            status_code=404
        )
    
    email.status = "Replied"
    
    action = Action(
        email_id=email_id,
        action_type="Auto-Reply",
        status="Approved",
        description="Draft approved and sent",
        assigned_to="system"
    )
    db.add(action)
    
    audit = AuditLog(
        entity_type="email",
        entity_id=email_id,
        action="draft_approved",
        actor="user",
        diff={"status_change": "Drafted -> Replied"}
    )
    db.add(audit)
    
    await db.commit()
    
    await ws_manager.send_action_event("draft_approved", email_id, {"status": "Replied"})
    
    return {
        "email_id": email_id,
        "status": "Replied",
        "message": "Draft approved and reply sent",
        "approved_at": datetime.utcnow().isoformat()
    }
