from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.web_scraper import web_scraper
from app.utils.error_envelope import ErrorEnvelope

router = APIRouter()

@router.get("/reputation")
async def get_reputation(
    company_name: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await web_scraper.scrape_public_sentiment(company_name)
        return {
            "company": company_name,
            "data": result
        }
    except Exception as e:
        return ErrorEnvelope.create(
            error_code="SCRAPE_ERROR",
            message=f"Failed to scrape reputation data: {str(e)}",
            status_code=500
        )
