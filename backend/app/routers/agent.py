from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.email import Email
from app.services.agent_service import AgentService
from app.utils.error_envelope import ErrorEnvelope

router = APIRouter()

@router.post("/dry-run/{email_id}")
async def dry_run_agent(
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
    
    classification = email.classification_result or {
        "category": email.category,
        "urgency": email.urgency,
        "sentiment_score": email.sentiment_score,
        "confidence": email.confidence,
        "requires_human": email.requires_human
    }
    
    agent_service = AgentService(db)
    trace = await agent_service.dry_run(email_id, classification)
    
    return {
        "email_id": email_id,
        "trace": {
            "email_id": trace.email_id,
            "classification": trace.classification,
            "steps": [step.model_dump() for step in trace.steps],
            "final_recommendation": trace.final_recommendation,
            "draft_reply": trace.draft_reply,
            "escalate": trace.escalate,
            "escalation_brief": trace.escalation_brief,
            "tools_used": trace.tools_used,
            "completed_at": trace.completed_at.isoformat(),
            "dry_run": trace.dry_run
        },
        "proposed_actions": trace.tools_used,
        "confidence": classification.get("confidence", 0.0)
    }
