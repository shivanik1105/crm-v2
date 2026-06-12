import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.knowledge_chunk import KnowledgeChunk
from app.config import settings

class RAGChunk:
    def __init__(self, source: str, heading: str, chunk_index: int, content: str, score: float):
        self.source = source
        self.heading = heading
        self.chunk_index = chunk_index
        self.content = content
        self.score = score

class RAGService:
    def __init__(self):
        self.model = None
        self._load_model()
        self._in_memory_cache = []  # List of (chunk, embedding_np)
    
    def _load_model(self):
        if self.model is None:
            try:
                self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            except Exception:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def chunk_document(self, file_path: str, content: str) -> List[Dict[str, Any]]:
        chunk_size_chars = 1600
        overlap_chars = 200
        
        lines = content.split('\n')
        current_heading = ""
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#'):
                if current_chunk.strip():
                    chunks.append({
                        "source": os.path.basename(file_path),
                        "heading": current_heading,
                        "chunk_index": chunk_index,
                        "content": current_chunk.strip()
                    })
                    chunk_index += 1
                current_heading = stripped.lstrip('#').strip()
                current_chunk = line + "\n"
            else:
                current_chunk += line + "\n"
                if len(current_chunk) >= chunk_size_chars:
                    chunks.append({
                        "source": os.path.basename(file_path),
                        "heading": current_heading,
                        "chunk_index": chunk_index,
                        "content": current_chunk.strip()
                    })
                    chunk_index += 1
                    if len(current_chunk) > overlap_chars:
                        current_chunk = current_chunk[-overlap_chars:]
                    else:
                        current_chunk = ""
        
        if current_chunk.strip():
            chunks.append({
                "source": os.path.basename(file_path),
                "heading": current_heading,
                "chunk_index": chunk_index,
                "content": current_chunk.strip()
            })
        
        return chunks
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        embeddings = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embeddings.tolist()
    
    async def search(self, db: AsyncSession, query: str, top_k: int = 3, min_similarity: float = 0.3) -> List[RAGChunk]:
        self._load_model()
        
        # Load all chunks from DB if cache is empty
        if not self._in_memory_cache:
            stmt = select(KnowledgeChunk)
            result = await db.execute(stmt)
            rows = result.scalars().all()
            for row in rows:
                try:
                    emb = np.array(json.loads(row.embedding), dtype=np.float32)
                    self._in_memory_cache.append((row, emb))
                except Exception:
                    continue
        
        if not self._in_memory_cache:
            return []
        
        query_embedding = self.model.encode([query], show_progress_bar=False, convert_to_numpy=True)[0]
        query_embedding = query_embedding.astype(np.float32)
        
        # Cosine similarity
        results = []
        for row, emb in self._in_memory_cache:
            similarity = np.dot(query_embedding, emb) / (np.linalg.norm(query_embedding) * np.linalg.norm(emb) + 1e-8)
            if similarity >= min_similarity:
                results.append((similarity, row))
        
        results.sort(key=lambda x: x[0], reverse=True)
        
        chunks = []
        for similarity, row in results[:top_k]:
            chunks.append(RAGChunk(
                source=row.source,
                heading=row.heading or "",
                chunk_index=row.chunk_index,
                content=row.content,
                score=float(similarity)
            ))
        
        return chunks
    
    def format_for_llm(self, chunks: List[RAGChunk]) -> str:
        if not chunks:
            return "No relevant policy documents found."
        
        lines = ["POLICY CONTEXT:"]
        for i, chunk in enumerate(chunks, 1):
            lines.append(f"[{i}] {chunk.source}#{chunk.heading}: {chunk.content[:300]}")
        
        return "\n".join(lines)

rag_service = RAGService()
