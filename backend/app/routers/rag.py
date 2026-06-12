from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.rag_service import rag_service
from app.utils.error_envelope import ErrorEnvelope

router = APIRouter()

@router.get("/search")
async def search_rag(
    q: str = Query(..., min_length=1),
    top_k: int = Query(default=3, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    chunks = await rag_service.search(db, q, top_k=top_k)
    
    return {
        "query": q,
        "results": [
            {
                "source": c.source,
                "heading": c.heading,
                "chunk_index": c.chunk_index,
                "content": c.content,
                "similarity_score": round(c.score, 4)
            }
            for c in chunks
        ],
        "total": len(chunks)
    }
