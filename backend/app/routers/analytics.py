from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, extract
from app.database import get_db
from app.models.email import Email
from app.models.thread import Thread
from app.models.contact import Contact
from app.models.action import Action
from app.services.sentiment_tracker import sentiment_tracker
from app.utils.error_envelope import ErrorEnvelope
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/sentiment-trend")
async def get_sentiment_trend(
    sender: str = Query(...),
    days: int = Query(default=30, ge=1, le=365),
    db: AsyncSession = Depends(get_db)
):
    trend = await sentiment_tracker.get_sentiment_trend(sender, days)
    return trend

@router.get("/category-distribution")
async def get_category_distribution(
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Email.category, func.count(Email.id)).group_by(Email.category)
    result = await db.execute(stmt)
    rows = result.all()
    
    total = sum(r[1] for r in rows)
    distribution = []
    for category, count in rows:
        distribution.append({
            "category": category,
            "count": count,
            "percentage": round(count / total * 100, 2) if total > 0 else 0
        })
    
    return {
        "distribution": distribution,
        "total": total
    }

@router.get("/at-risk")
async def get_at_risk_accounts(
    db: AsyncSession = Depends(get_db)
):
    # Get all contacts with their email stats
    from sqlalchemy import func
    
    # Get contacts with negative sentiment trends
    sentiment_stmt = (
        select(
            Email.sender,
            func.avg(Email.sentiment_score).label("avg_sentiment"),
            func.count(Email.id).label("email_count"),
            func.min(Email.sentiment_score).label("min_sentiment")
        )
        .group_by(Email.sender)
        .having(func.avg(Email.sentiment_score) < -0.3)
    )
    result = await db.execute(sentiment_stmt)
    negative_senders = result.all()
    
    accounts = {}
    
    # Add contacts with negative sentiment
    for row in negative_senders:
        sender = row.sender
        contact_stmt = select(Contact).where(Contact.email == sender)
        contact_result = await db.execute(contact_stmt)
        contact = contact_result.scalar_one_or_none()
        
        accounts[sender] = {
            "sender": sender,
            "churn_risk_score": contact.churn_risk_score if contact else 50,
            "account_value": contact.account_value if contact else 0,
            "unresolved_threads": 0,
            "last_email_date": None,
            "sentiment_trend": "deteriorating",
            "avg_sentiment": round(float(row.avg_sentiment), 3),
            "email_count": row.email_count
        }
    
    # Get contacts with unresolved threads > 48h
    cutoff = datetime.utcnow() - timedelta(hours=48)
    thread_stmt = (
        select(Thread, Contact)
        .join(Contact, Thread.contact_id == Contact.id)
        .where(Thread.status != "Closed")
        .where(Thread.last_updated_at < cutoff)
    )
    thread_result = await db.execute(thread_stmt)
    stale_threads = thread_result.all()
    
    for thread, contact in stale_threads:
        if contact.email not in accounts:
            accounts[contact.email] = {
                "sender": contact.email,
                "churn_risk_score": contact.churn_risk_score,
                "account_value": contact.account_value,
                "unresolved_threads": 0,
                "last_email_date": thread.last_updated_at.isoformat() if thread.last_updated_at else None,
                "sentiment_trend": "unknown",
                "avg_sentiment": 0,
                "email_count": 0
            }
        accounts[contact.email]["unresolved_threads"] += 1
    
    # Get contacts with high churn risk score
    risk_stmt = select(Contact).where(Contact.churn_risk_score > 70)
    risk_result = await db.execute(risk_stmt)
    high_risk = risk_result.scalars().all()
    
    for contact in high_risk:
        if contact.email not in accounts:
            accounts[contact.email] = {
                "sender": contact.email,
                "churn_risk_score": contact.churn_risk_score,
                "account_value": contact.account_value,
                "unresolved_threads": 0,
                "last_email_date": None,
                "sentiment_trend": "high_risk",
                "avg_sentiment": 0,
                "email_count": 0
            }
    
    return {
        "accounts": list(accounts.values()),
        "total_at_risk": len(accounts)
    }

@router.get("/agent-performance")
async def get_agent_performance(
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Email)
    result = await db.execute(stmt)
    emails = result.scalars().all()
    
    total = len(emails)
    if total == 0:
        return {
            "auto_reply_rate": 0.0,
            "escalation_rate": 0.0,
            "avg_confidence": 0.0,
            "avg_tools_used": 0.0,
            "total_processed": 0,
            "total_escalated": 0
        }
    
    replied = sum(1 for e in emails if e.status == "Replied")
    escalated = sum(1 for e in emails if e.status == "Escalated" or e.requires_human)
    avg_confidence = sum(e.confidence for e in emails) / total
    
    action_stmt = select(Action)
    action_result = await db.execute(action_stmt)
    actions = action_result.scalars().all()
    
    total_tools = 0
    for action in actions:
        if action.agent_reasoning_log:
            total_tools += len(action.agent_reasoning_log)
    
    avg_tools = total_tools / len(actions) if actions else 0
    
    return {
        "auto_reply_rate": round(replied / total * 100, 2),
        "escalation_rate": round(escalated / total * 100, 2),
        "avg_confidence": round(avg_confidence, 3),
        "avg_tools_used": round(avg_tools, 2),
        "total_processed": total,
        "total_escalated": escalated
    }

@router.get("/response-time-heatmap")
async def get_response_time_heatmap(
    db: AsyncSession = Depends(get_db)
):
    try:
        # Use raw SQL for better reliability
        from sqlalchemy import text
        
        query = text("""
            SELECT 
                to_char(timestamp, 'Dy') as day,
                (EXTRACT(HOUR FROM timestamp)::INT / 4 * 4) as hour_block,
                AVG(EXTRACT(EPOCH FROM (created_at - timestamp))/60) as avg_minutes,
                COUNT(*) as email_count
            FROM emails
            WHERE created_at > timestamp
            GROUP BY to_char(timestamp, 'Dy'), (EXTRACT(HOUR FROM timestamp)::INT / 4 * 4)
            ORDER BY 
                CASE to_char(timestamp, 'Dy')
                    WHEN 'Mon' THEN 1 WHEN 'Tue' THEN 2 WHEN 'Wed' THEN 3
                    WHEN 'Thu' THEN 4 WHEN 'Fri' THEN 5 WHEN 'Sat' THEN 6 WHEN 'Sun' THEN 7
                END,
                hour_block
        """)
        
        result = await db.execute(query)
        rows = result.fetchall()
        
        data = []
        for row in rows:
            data.append({
                "day": row[0],
                "hour": f"{int(row[1])}:00",
                "avg_response": round(float(row[2]), 1),
                "count": int(row[3])
            })
        
        return {"heatmap": data}
    except Exception as e:
        print(f"Heatmap error: {e}")
        return {"heatmap": []}
