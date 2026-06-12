from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.email import Email
from app.models.thread import Thread
from app.models.contact import Contact
from app.models.action import Action

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    # Email counts
    email_stmt = select(func.count(Email.id))
    email_result = await db.execute(email_stmt)
    total_emails = email_result.scalar()
    
    # Thread counts
    thread_stmt = select(func.count(Thread.id))
    thread_result = await db.execute(thread_stmt)
    total_threads = thread_result.scalar()
    
    # Contact counts
    contact_stmt = select(func.count(Contact.id))
    contact_result = await db.execute(contact_stmt)
    total_contacts = contact_result.scalar()
    
    # Status breakdown
    status_stmt = select(Email.status, func.count(Email.id)).group_by(Email.status)
    status_result = await db.execute(status_stmt)
    status_breakdown = {status: count for status, count in status_result.all()}
    
    # Urgency breakdown
    urgency_stmt = select(Email.urgency, func.count(Email.id)).group_by(Email.urgency)
    urgency_result = await db.execute(urgency_stmt)
    urgency_breakdown = {urgency: count for urgency, count in urgency_result.all()}
    
    # Requires human count
    human_stmt = select(func.count(Email.id)).where(Email.requires_human == True)
    human_result = await db.execute(human_stmt)
    needs_human = human_result.scalar()
    
    # Average confidence
    avg_conf_stmt = select(func.avg(Email.confidence))
    avg_conf_result = await db.execute(avg_conf_stmt)
    avg_confidence = avg_conf_result.scalar() or 0.0
    
    # Pending count (New or Processing status)
    pending_stmt = select(func.count(Email.id)).where(
        Email.status.in_(["New", "Processing"])
    )
    pending_result = await db.execute(pending_stmt)
    pending = pending_result.scalar()
    
    return {
        "total_emails": total_emails,
        "total_threads": total_threads,
        "total_contacts": total_contacts,
        "status_breakdown": status_breakdown,
        "urgency_breakdown": urgency_breakdown,
        "needs_human": needs_human,
        "auto_replied": status_breakdown.get("Replied", 0),
        "escalated": status_breakdown.get("Escalated", 0),
        "avg_confidence": round(avg_confidence * 100, 1),
        "pending": pending
    }
