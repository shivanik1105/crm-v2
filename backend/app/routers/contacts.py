from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.contact import Contact
from app.utils.error_envelope import ErrorEnvelope

router = APIRouter()

@router.get("/{email}")
async def get_contact(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Contact).where(Contact.email == email)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    
    if contact is None:
        return ErrorEnvelope.create(
            error_code="NOT_FOUND",
            message="Contact not found",
            status_code=404
        )
    
    return {
        "id": str(contact.id),
        "email": contact.email,
        "name": contact.name,
        "tier": contact.tier,
        "account_value": contact.account_value,
        "vip_status": contact.vip_status,
        "churn_risk_score": contact.churn_risk_score,
        "created_at": contact.created_at.isoformat() if contact.created_at else None,
        "updated_at": contact.updated_at.isoformat() if contact.updated_at else None
    }

@router.patch("/{email}")
async def update_contact(
    email: str,
    updates: dict,
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Contact).where(Contact.email == email)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    
    if contact is None:
        return ErrorEnvelope.create(
            error_code="NOT_FOUND",
            message="Contact not found",
            status_code=404
        )
    
    allowed_fields = ["name", "tier", "account_value", "vip_status", "churn_risk_score"]
    for field in allowed_fields:
        if field in updates:
            setattr(contact, field, updates[field])
    
    await db.commit()
    
    return {
        "email": email,
        "updated": True,
        "fields": list(updates.keys())
    }
