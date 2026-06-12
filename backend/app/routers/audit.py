from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.audit_log import AuditLog
from app.utils.error_envelope import ErrorEnvelope

router = APIRouter()

@router.get("/{entity_type}/{entity_id}")
async def get_audit_log(
    entity_type: str,
    entity_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(AuditLog)
        .where(AuditLog.entity_type == entity_type)
        .where(AuditLog.entity_id == entity_id)
        .order_by(AuditLog.timestamp.desc())
    )
    result = await db.execute(stmt)
    logs = result.scalars().all()
    
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "logs": [
            {
                "id": str(log.id),
                "action": log.action,
                "actor": log.actor,
                "diff": log.diff,
                "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent
            }
            for log in logs
        ],
        "total": len(logs)
    }
