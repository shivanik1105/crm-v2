import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.routers import api_router
from app.routers.websocket import router as ws_router
from app.database import engine, Base, init_db, AsyncSessionLocal
from app.utils.error_envelope import CRMException, crm_exception_handler
from app.config import settings

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

async def seed_knowledge_base():
    """Load knowledge base documents into the database"""
    from app.services.rag_service import rag_service
    from app.models.knowledge_chunk import KnowledgeChunk
    from sqlalchemy import select
    
    kb_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "knowledge_base")
    if not os.path.exists(kb_dir):
        logger.warning(f"Knowledge base directory not found: {kb_dir}")
        return
    
    async with AsyncSessionLocal() as db:
        # Check if already seeded
        result = await db.execute(select(KnowledgeChunk))
        existing = result.scalars().all()
        if existing:
            logger.info(f"Knowledge base already seeded with {len(existing)} chunks")
            return
        
        # Load all markdown files
        kb_files = [f for f in os.listdir(kb_dir) if f.endswith('.md')]
        total_chunks = 0
        
        for filename in kb_files:
            file_path = os.path.join(kb_dir, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Chunk the document
                chunks = rag_service.chunk_document(file_path, content)
                
                if not chunks:
                    continue
                
                # Embed chunks
                texts = [c["content"] for c in chunks]
                embeddings = rag_service.embed_texts(texts)
                
                # Store in database
                for i, chunk in enumerate(chunks):
                    import json
                    kb_chunk = KnowledgeChunk(
                        source=chunk["source"],
                        heading=chunk["heading"],
                        chunk_index=chunk["chunk_index"],
                        content=chunk["content"],
                        embedding=json.dumps(embeddings[i])
                    )
                    db.add(kb_chunk)
                    total_chunks += 1
                
                logger.info(f"Loaded {len(chunks)} chunks from {filename}")
                
            except Exception as e:
                logger.error(f"Error loading {filename}: {e}")
                continue
        
        await db.commit()
        logger.info(f"Knowledge base seeded with {total_chunks} total chunks")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up SenAI CRM...")
    await init_db()
    logger.info("Database initialized")
    
    # Seed knowledge base
    await seed_knowledge_base()
    
    yield
    logger.info("Shutting down SenAI CRM...")
    await engine.dispose()

app = FastAPI(
    title="SenAI CRM",
    description="Agentic CRM Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_exception_handler(CRMException, crm_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(ws_router)

# Serve frontend static files
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_dist, "index.html"))
    
    @app.get("/{path:path}")
    async def serve_frontend_paths(path: str):
        # API routes should be handled first, so this only catches non-API paths
        if path.startswith("api") or path.startswith("health") or path.startswith("docs") or path.startswith("openapi"):
            return {"detail": "Not Found"}
        file_path = os.path.join(frontend_dist, path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    async def root():
        return {"message": "SenAI CRM API", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0", "env": settings.ENV}
