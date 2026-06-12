# Troubleshooting Guide

## Common Issues

### 1. Docker Compose Won't Start

**Symptom:**
```
Error: Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Solution:**
```bash
# Start Docker Desktop (Windows)
# Or in WSL:
sudo service docker start

# Verify Docker is running
docker ps
```

---

### 2. Backend Container Exits Immediately

**Symptom:**
```
crm-backend-1 exited with code 1
```

**Solution:**
```bash
# Check logs
docker compose logs backend

# Common causes:
# 1. Database not ready
# 2. Missing environment variables
# 3. Port already in use

# Wait for postgres health check
docker compose ps
# Wait until postgres shows (healthy)

# Check .env file exists and has GROQ_API_KEY
cat .env | grep GROQ_API_KEY

# Check port 8000 is free
netstat -ano | findstr :8000
# Or in WSL:
sudo lsof -i :8000
```

---

### 3. Frontend Can't Connect to Backend

**Symptom:**
Browser console shows:
```
GET http://localhost:8000/api/emails/ net::ERR_CONNECTION_REFUSED
```

**Solution:**
```bash
# Check backend is running
docker compose ps
curl http://localhost:8000/health

# Check Vite proxy config
cat frontend/vite.config.js

# Restart frontend
docker compose restart frontend

# Check backend logs for CORS errors
docker compose logs backend | grep CORS
```

---

### 4. Database Connection Failed

**Symptom:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check postgres is running
docker compose ps
docker compose exec postgres pg_isready -U crm -d crm_db

# Check DATABASE_URL in .env
cat .env | grep DATABASE_URL

# Restart postgres
docker compose restart postgres

# Wait for health check
sleep 10
docker compose exec postgres pg_isready -U crm -d crm_db

# Check postgres logs
docker compose logs postgres
```

---

### 5. Redis Connection Failed

**Symptom:**
```
redis.exceptions.ConnectionError: Error connecting to localhost:6379
```

**Solution:**
```bash
# Check redis is running
docker compose ps
docker compose exec redis redis-cli ping

# Check REDIS_URL in .env
cat .env | grep REDIS_URL

# Restart redis
docker compose restart redis

# Note: Redis is optional - system works without it (graceful degradation)
```

---

### 6. Groq API Key Invalid

**Symptom:**
```
httpx.HTTPStatusError: 401 Unauthorized
```

**Solution:**
```bash
# Verify API key in .env
cat .env | grep GROQ_API_KEY

# Test API key
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer YOUR_GROQ_API_KEY"

# Get new key: https://console.groq.com/keys

# Note: System falls back to heuristic classification if API fails
```

---

### 7. Migrations Failed

**Symptom:**
```
alembic.util.exc.CommandError: Target database is not up to date
```

**Solution:**
```bash
# Check current migration
docker compose exec backend alembic current

# Apply migrations
docker compose exec backend alembic upgrade head

# If migration conflict, reset (development only)
docker compose down -v
docker compose up -d
docker compose exec backend alembic upgrade head
```

---

### 8. Knowledge Base Not Seeded

**Symptom:**
RAG search returns empty results:
```json
{"query": "refund", "results": [], "total": 0}
```

**Solution:**
```bash
# Seed knowledge base
docker compose exec backend python scripts/seed_knowledge_base.py

# Verify chunks exist
docker compose exec postgres psql -U crm -d crm_db -c "SELECT COUNT(*) FROM knowledge_chunks;"
# Expected: ~50 chunks
```

---

### 9. WebSocket Connection Failed

**Symptom:**
Frontend shows "Offline" indicator, no real-time updates.

**Solution:**
```bash
# Check backend logs for WebSocket errors
docker compose logs backend | grep WebSocket

# Check Vite proxy config for WebSocket
cat frontend/vite.config.js | grep ws

# Restart backend
docker compose restart backend

# Check browser console for WebSocket errors
# Expected: ws://localhost:8000/api/ws
```

---

### 10. Port Already in Use

**Symptom:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**Solution:**
```bash
# Find process using port (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or in WSL
sudo lsof -i :8000
sudo kill -9 <PID>

# Or change port in docker-compose.yml
services:
  backend:
    ports:
      - "8001:8000"
```

---

### 11. Email Ingestion Slow

**Symptom:**
Email ingestion takes >10 seconds.

**Solution:**
```bash
# Check Groq API latency
time curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer YOUR_GROQ_API_KEY"

# Check database query performance
docker compose exec postgres psql -U crm -d crm_db -c "
  SELECT query, mean_time 
  FROM pg_stat_statements 
  WHERE query LIKE '%emails%' 
  ORDER BY mean_time DESC;
"

# Check RAG retrieval time
time curl "http://localhost:8000/api/rag/search?q=test"

# Consider:
# - Upgrading Groq plan for higher rate limits
# - Adding database indexes
# - Caching RAG results
```

---

### 12. Agent Not Executing

**Symptom:**
Emails ingested but no agent actions in database.

**Solution:**
```bash
# Check agent logs
docker compose logs backend | grep agent

# Check if email requires human review
docker compose exec postgres psql -U crm -d crm_db -c "
  SELECT id, sender, requires_human, status 
  FROM emails 
  ORDER BY created_at DESC 
  LIMIT 5;
"

# Check agent service is running
docker compose exec backend python -c "from app.services.agent_service import AgentService; print('OK')"

# Test agent manually
EMAIL_ID=$(docker compose exec postgres psql -U crm -d crm_db -t -c "SELECT id FROM emails LIMIT 1;" | xargs)
curl -X POST "http://localhost:8000/api/agent/dry-run/$EMAIL_ID" | jq
```

---

### 13. Sentiment Tracking Not Working

**Symptom:**
Sentiment trend returns empty:
```json
{"sender": "test@example.com", "points": [], "moving_average": 0.0}
```

**Solution:**
```bash
# Check Redis is running
docker compose exec redis redis-cli ping

# Check sentiment keys
docker compose exec redis redis-cli keys "sentiment:*"

# Check sentiment_tracker service
docker compose logs backend | grep sentiment

# Note: Sentiment tracking requires Redis. If Redis unavailable, returns empty.
```

---

### 14. Frontend Build Failed

**Symptom:**
```
ERROR: Failed to resolve import "react-router-dom"
```

**Solution:**
```bash
# Install dependencies
cd frontend
npm install

# Or rebuild container
docker compose build frontend
docker compose up -d frontend
```

---

### 15. Tests Failing

**Symptom:**
```
pytest tests/ -v
FAILED tests/test_advanced.py::TestLLMClassifier::test_gdpr_detection
```

**Solution:**
```bash
# Run tests in Docker (recommended)
docker compose exec backend pytest tests/ -v

# Or locally with venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
pytest tests/ -v

# Check for missing dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.11+
```

---

## Debug Mode

### Enable Debug Logging
```bash
# Set LOG_LEVEL=DEBUG in .env
echo "LOG_LEVEL=DEBUG" >> .env

# Restart backend
docker compose restart backend

# Check logs
docker compose logs -f backend
```

### Enable SQL Query Logging
```bash
# Edit backend/app/database.py
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Enable SQL logging
    ...
)

# Restart backend
docker compose restart backend
```

### Enable WebSocket Debug
```bash
# Check browser console
# Open DevTools → Console → Filter: "WS"

# Check backend logs
docker compose logs -f backend | grep WebSocket
```

---

## Performance Profiling

### Backend Profiling
```bash
# Install profiling tools
docker compose exec backend pip install py-spy

# Profile backend process
docker compose exec backend py-spy top --pid 1

# Generate flame graph
docker compose exec backend py-spy record -o profile.svg --pid 1
```

### Database Profiling
```bash
# Enable query stats
docker compose exec postgres psql -U crm -d crm_db -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"

# View slow queries
docker compose exec postgres psql -U crm -d crm_db -c "
  SELECT query, calls, total_time, mean_time 
  FROM pg_stat_statements 
  ORDER BY mean_time DESC 
  LIMIT 10;
"
```

---

## Getting Help

### Check Documentation
- [Architecture](architecture.md) - System design
- [API Reference](api.md) - Endpoint documentation
- [Operations Runbook](runbook.md) - Daily operations

### Check Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend

# Last 100 lines
docker compose logs --tail=100 backend
```

### Open GitHub Issue
https://github.com/yourusername/senai-crm/issues

Include:
- Error message
- Steps to reproduce
- Docker compose logs
- Environment (OS, Docker version, Python version)
