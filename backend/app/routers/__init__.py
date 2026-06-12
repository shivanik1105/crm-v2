from fastapi import APIRouter
from app.routers import (
    ingest,
    emails,
    threads,
    respond,
    analytics,
    rag,
    intelligence,
    agent,
    contacts,
    dashboard,
    audit
)

api_router = APIRouter()

# Include all routers
api_router.include_router(ingest.router, tags=["Ingest"])
api_router.include_router(emails.router, prefix="/emails", tags=["Emails"])
api_router.include_router(threads.router, prefix="/threads", tags=["Threads"])
api_router.include_router(respond.router, prefix="/respond", tags=["Respond"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(rag.router, prefix="/rag", tags=["RAG"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["Intelligence"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])
api_router.include_router(contacts.router, prefix="/contacts", tags=["Contacts"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(audit.router, prefix="/audit", tags=["Audit"])
