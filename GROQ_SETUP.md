# Groq API Setup Guide

## Getting Your Free Groq API Key

1. **Visit Groq Console:**
   - Go to https://console.groq.com

2. **Sign Up / Log In:**
   - Create a free account or log in with Google/GitHub
   - No credit card required for the free tier

3. **Generate API Key:**
   - Navigate to "API Keys" in the left sidebar
   - Click "Create API Key"
   - Give it a name (e.g., "SenAI-CRM")
   - Copy the key immediately (shown only once)

4. **Add to .env:**
   ```bash
   GROQ_API_KEY=gsk_your_actual_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

## Available Models

Groq offers several models optimized for different use cases:

### Recommended for SenAI CRM:
- **llama-3.3-70b-versatile** (default)
  - Best balance of speed and accuracy
  - 128k context window
  - ~800 tokens/sec inference speed
  - Excellent for email classification

### Alternative Models:
- **llama-3.1-70b-versatile**
  - Slightly older, still very capable
  - 128k context window

- **mixtral-8x7b-32768**
  - Faster inference (~1000 tokens/sec)
  - Good for simpler classification tasks
  - 32k context window

- **llama-3.1-8b-instant**
  - Ultra-fast (~1500 tokens/sec)
  - Lower accuracy but good for high-volume scenarios
  - 128k context window

## Rate Limits (Free Tier)

- **Requests:** 30 requests/min
- **Tokens:** 14,400 tokens/min
- **Daily limit:** 7,000 requests/day

For the CRM email ingestion rate of ~1 email/sec, you'll use ~60 requests/min during simulation, which may hit the free tier limit. For production, consider:
- Groq paid tier ($0.10-$0.70 per 1M tokens)
- Batch processing with delays
- Hybrid approach (heuristic filter first, LLM only for uncertain cases)

## Monitoring Usage

Visit https://console.groq.com/usage to monitor:
- Request count
- Token usage
- Rate limit status
- Cost breakdown (paid tier)

## Troubleshooting

### "Rate limit exceeded" error:
```python
# Add retry logic or reduce STREAM_SPEED
docker compose exec backend python scripts/simulate_stream.py --speed 0.5
```

### "Invalid API key" error:
- Verify the key starts with `gsk_`
- Check for whitespace in .env file
- Regenerate key in console if needed

### Slow response times:
- Groq is designed for speed; if you see >2s latency, check network
- Try a different model (llama-3.1-8b-instant for maximum speed)

## Why Groq?

✅ **Speed:** 10-100x faster than traditional cloud LLM APIs  
✅ **Cost:** Significantly cheaper per token than OpenAI/Anthropic  
✅ **Open Models:** Llama 3.3 is open-weight and transparent  
✅ **No Vendor Lock-in:** Easy to switch models or providers  
✅ **Great for Real-Time:** Perfect for CRM email triage use case  

## Switching Back to Anthropic (if needed)

If you want to use Claude instead:

1. Update `backend/app/config.py`:
   ```python
   ANTHROPIC_API_KEY: str = ""
   ```

2. Update `backend/app/services/llm_classifier.py` to use Anthropic API format

3. Update `.env`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-...
   ```

4. Reinstall `anthropic` package in `pyproject.toml`
