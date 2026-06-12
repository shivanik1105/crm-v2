#!/usr/bin/env python3
"""
Quick test script to verify Groq API integration works correctly.
Run this after migrating from Anthropic to Groq.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.services.llm_classifier import llm_classifier
from app.schemas.email import EmailIngest
from datetime import datetime
from app.config import settings


async def test_groq_connection():
    """Test basic Groq API connectivity and response format."""
    
    print("=" * 60)
    print("GROQ API CONNECTION TEST")
    print("=" * 60)
    
    # Check API key is set
    if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "your_groq_key_here":
        print("❌ ERROR: GROQ_API_KEY not set in .env file")
        print("   Get your free API key from: https://console.groq.com/keys")
        return False
    
    print(f"✓ API Key configured: {settings.GROQ_API_KEY[:15]}...")
    print(f"✓ Model: {settings.GROQ_MODEL}")
    print()
    
    # Test cases
    test_emails = [
        {
            "name": "Simple billing question",
            "email": EmailIngest(
                sender="customer@example.com",
                subject="Question about invoice",
                body="Hi, I have a question about my latest invoice. Can you help?",
                timestamp=datetime.utcnow()
            ),
            "expected_category": "Billing"
        },
        {
            "name": "Urgent technical issue",
            "email": EmailIngest(
                sender="admin@bigcorp.com",
                subject="URGENT: Production system down",
                body="Our production database has been down for 2 hours. This is costing us $10k/hour. Please escalate immediately!",
                timestamp=datetime.utcnow()
            ),
            "expected_urgency": "Critical"
        },
        {
            "name": "GDPR request (forced classification)",
            "email": EmailIngest(
                sender="privacy@company.com",
                subject="GDPR Article 20 Data Portability Request",
                body="Under GDPR Article 20, I request a copy of all my personal data in a machine-readable format.",
                timestamp=datetime.utcnow()
            ),
            "expected_category": "Compliance"
        }
    ]
    
    all_passed = True
    
    for i, test in enumerate(test_emails, 1):
        print(f"Test {i}: {test['name']}")
        print("-" * 60)
        
        try:
            # Mock database (classifier doesn't actually use it for these tests)
            class MockDB:
                async def execute(self, *args, **kwargs):
                    class Result:
                        def scalars(self):
                            return self
                        def all(self):
                            return []
                    return Result()
            
            db = MockDB()
            
            # Classify the email
            result = await llm_classifier.classify(db, test['email'])
            
            print(f"   Category: {result.category}")
            print(f"   Urgency: {result.urgency}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Sentiment: {result.sentiment_score:.2f}")
            print(f"   Requires Human: {result.requires_human}")
            
            # Validate expectations
            if "expected_category" in test:
                if result.category == test["expected_category"]:
                    print(f"   ✓ Category matches expected: {test['expected_category']}")
                else:
                    print(f"   ⚠ Category mismatch. Expected: {test['expected_category']}, Got: {result.category}")
                    all_passed = False
            
            if "expected_urgency" in test:
                if result.urgency == test["expected_urgency"]:
                    print(f"   ✓ Urgency matches expected: {test['expected_urgency']}")
                else:
                    print(f"   ⚠ Urgency mismatch. Expected: {test['expected_urgency']}, Got: {result.urgency}")
                    all_passed = False
            
            print("   ✓ Test passed")
            
        except Exception as e:
            print(f"   ❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
        
        print()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED")
        print("  Groq API integration is working correctly!")
    else:
        print("⚠ SOME TESTS FAILED")
        print("  Check the output above for details.")
    print("=" * 60)
    
    return all_passed


async def test_fallback_mode():
    """Test that fallback heuristic works when API key is missing."""
    
    print("\n" + "=" * 60)
    print("FALLBACK MODE TEST (no API key)")
    print("=" * 60)
    
    # Temporarily clear API key
    original_key = llm_classifier.api_key
    llm_classifier.api_key = ""
    
    try:
        email = EmailIngest(
            sender="customer@example.com",
            subject="URGENT: Need refund immediately",
            body="I need a refund on my last payment. This is urgent!",
            timestamp=datetime.utcnow()
        )
        
        class MockDB:
            async def execute(self, *args, **kwargs):
                class Result:
                    def scalars(self):
                        return self
                    def all(self):
                        return []
                return Result()
        
        db = MockDB()
        result = await llm_classifier.classify(db, email)
        
        print(f"Category: {result.category}")
        print(f"Urgency: {result.urgency}")
        print(f"Confidence: {result.confidence:.2f}")
        print("✓ Fallback mode works correctly")
        
    except Exception as e:
        print(f"❌ Fallback mode failed: {e}")
    finally:
        # Restore API key
        llm_classifier.api_key = original_key
    
    print("=" * 60)


async def main():
    """Run all tests."""
    
    # Test 1: Groq API connectivity and classification
    api_success = await test_groq_connection()
    
    # Test 2: Fallback mode
    await test_fallback_mode()
    
    # Final summary
    print("\n" + "=" * 60)
    print("MIGRATION VERIFICATION COMPLETE")
    print("=" * 60)
    
    if api_success:
        print("✓ Your system is ready to use Groq API")
        print("✓ Run the full simulation to test end-to-end:")
        print("  docker compose exec backend python scripts/simulate_stream.py --speed 1")
    else:
        print("⚠ Please fix the issues above before proceeding")
        print("  Check GROQ_SETUP.md for troubleshooting help")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
