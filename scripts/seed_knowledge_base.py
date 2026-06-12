import asyncio
import json
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from app.database import engine
from app.models.knowledge_chunk import KnowledgeChunk
from app.services.rag_service import rag_service

KB_DIR = Path(__file__).parent.parent / "knowledge_base"

async def seed():
    from app.database import init_db, engine
    await init_db()
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        md_files = sorted(KB_DIR.glob("*.md"))
        total_chunks = 0
        
        for md_file in md_files:
            print(f"Processing {md_file.name}...")
            content = md_file.read_text(encoding="utf-8")
            
            chunks = rag_service.chunk_document(str(md_file), content)
            texts = [c["content"] for c in chunks]
            
            if not texts:
                continue
            
            embeddings = rag_service.embed_texts(texts)
            
            from sqlalchemy import select
            existing_stmt = select(KnowledgeChunk.source, KnowledgeChunk.chunk_index).where(
                KnowledgeChunk.source == md_file.name
            )
            result = await session.execute(existing_stmt)
            existing = set((r.source, r.chunk_index) for r in result.all())
            
            inserted = 0
            for chunk_data, embedding in zip(chunks, embeddings):
                if (chunk_data["source"], chunk_data["chunk_index"]) in existing:
                    continue
                
                kb_chunk = KnowledgeChunk(
                    source=chunk_data["source"],
                    heading=chunk_data["heading"],
                    chunk_index=chunk_data["chunk_index"],
                    content=chunk_data["content"],
                    embedding=json.dumps(embedding),
                    meta={
                        "heading": chunk_data["heading"],
                        "chunk_index": chunk_data["chunk_index"]
                    }
                )
                session.add(kb_chunk)
                inserted += 1
            
            await session.commit()
            total_chunks += inserted
            print(f"  Inserted {inserted} new chunks from {md_file.name}")
        
        print(f"\nSeeded {total_chunks} chunks from {len(md_files)} documents")
    
if __name__ == "__main__":
    asyncio.run(seed())
