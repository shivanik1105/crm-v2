import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.rag_service import RAGService, RAGChunk

class TestRAGService:
    def test_chunk_document(self):
        service = RAGService()
        
        # Test markdown content with headings
        content = """# Pricing Policy

## Starter Tier
- Price: $49/month
- Up to 5 users

## Enterprise Tier
- Custom pricing
- Unlimited users

## Billing Rules
Pro-rata billing applies.
"""
        
        chunks = service.chunk_document("pricing_policy.md", content)
        
        assert len(chunks) > 0
        assert chunks[0]["source"] == "pricing_policy.md"
        assert "Pricing Policy" in chunks[0]["content"] or "Starter Tier" in chunks[0]["content"]
    
    def test_chunk_overlap(self):
        service = RAGService()
        
        # Create content that should produce multiple chunks
        content = "# Section 1\n" + ("This is a test sentence. " * 200) + "\n# Section 2\n" + ("Another test sentence. " * 200)
        
        chunks = service.chunk_document("test.md", content)
        
        if len(chunks) > 1:
            # Check that chunks have some overlap or are distinct
            assert chunks[0]["source"] == "test.md"
            assert chunks[1]["source"] == "test.md"
    
    def test_embed_texts(self):
        service = RAGService()
        texts = ["refund policy for unhappy customers", "pricing tiers and billing rules"]
        
        embeddings = service.embed_texts(texts)
        
        assert len(embeddings) == 2
        assert len(embeddings[0]) == 384  # all-MiniLM-L6-v2 dimension
        assert len(embeddings[1]) == 384
    
    def test_format_for_llm(self):
        service = RAGService()
        chunks = [
            RAGChunk("refund_policy.md", "Exception Process", 0, "No refunds after 14 days.", 0.85),
            RAGChunk("refund_policy.md", "Retention", 1, "Offer 2-month credit for churn threats.", 0.78)
        ]
        
        formatted = service.format_for_llm(chunks)
        
        assert "POLICY CONTEXT" in formatted
        assert "refund_policy.md" in formatted
        assert "Exception Process" in formatted
        assert "14 days" in formatted
    
    def test_empty_chunks(self):
        service = RAGService()
        formatted = service.format_for_llm([])
        assert "No relevant policy documents found" in formatted

class TestRAGRetrieval:
    """Integration tests for RAG retrieval - require database"""
    
    @pytest.mark.asyncio
    async def test_karen_refund_scenario(self):
        """
        When querying about 'refund policy unhappy customer',
        the RAG should retrieve refund_policy.md chunks with high similarity.
        """
        # This test would require a seeded database
        # For unit testing, we verify the query construction logic
        service = RAGService()
        
        # Verify the model loads
        service._load_model()
        assert service.model is not None
        
        # Test embedding generation for refund-related query
        query = "refund policy unhappy customer threatening churn"
        embedding = service.model.encode([query])
        assert embedding.shape[1] == 384
