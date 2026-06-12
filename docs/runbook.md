# Operations Runbook

## Daily Health Checks

### 1. Service Status
```bash
# Check all services are running
docker compose ps

# Expected output:
# NAME                SERVICE   STATUS
# crm-postgres-1      postgres  Up (healthy)
# crm-redis-1         redis     Up
# crm-backend-1       backend   Up
# crm-frontend-1      frontend  Up
```

### 2. API Health
```bash
# Check backend health
curl http://localhost:8000/health | jq

# Expected:
# {
#   "status": "healthy",
#   "version": "1.0.0"
# }
```

### 3. Database Connectivity
```bash
# Test PostgreSQL connection
docker compose exec postgres pg_isready -U crm -d crm_db

# Expected: accepting connections
```

### 4. Redis Connectivity
```bash
# Test Redis connection
docker compose exec redis redis-cli ping

# Expected: PONG
```

### 5. Email Statistics
```bash
# Get dashboard stats
curl http://localhost:8000/api/dashboard/stats | jq

# Check for anomalies:
# - High escalation rate (>50%)
# - Low auto-reply rate (<20%)
# - High spam rate (>30%)
```

---

## Common Operations

### Ingest Test Email
```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "test_001",
    "sender": "test@example.com",
    "recipient": "support@company.com",
    "subject": "Test email",
    "body": "This is a test email.",
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

### Simulate Email Stream
```bash
# Ingest all 60 emails at 1 email/sec
docker compose exec backend python scripts/simulate_stream.py --speed 1

# Ingest at 10 emails/sec (load test)
docker compose exec backend python scripts/simulate_stream.py --speed 10

# Ingest specific email
docker compose exec backend python scripts/simulate_stream.py --message-id msg_001
```

### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
docker compose logs -f redis

# Last 100 lines
docker compose logs --tail=100 backend
```

### Restart Services
```bash
# Restart single service
docker compose restart backend

# Restart all services
docker compose restart

# Hard restart (recreate containers)
docker compose down
docker compose up -d
```

### Database Operations

#### View Email Count
```bash
docker compose exec postgres psql -U crm -d crm_db -c "SELECT COUNT(*) FROM emails;"
```

#### View Thread Count
```bash
docker compose exec postgres psql -U crm -d crm_db -c "SELECT COUNT(*) FROM threads;"
```

#### View Contact Count
```bash
docker compose exec postgres psql -U crm -d crm_db -c "SELECT COUNT(*) FROM contacts;"
```

#### View Status Distribution
```bash
docker compose exec postgres psql -U crm -d crm_db -c "
  SELECT status, COUNT(*) 
  FROM emails 
  GROUP BY status 
  ORDER BY count DESC;
"
```

#### View Category Distribution
```bash
docker compose exec postgres psql -U crm -d crm_db -c "
  SELECT category, COUNT(*) 
  FROM emails 
  GROUP BY category 
  ORDER BY count DESC;
"
```

#### View Urgency Distribution
```bash
docker compose exec postgres psql -U crm -d crm_db -c "
  SELECT urgency, COUNT(*) 
  FROM emails 
  GROUP BY urgency 
  ORDER BY count DESC;
"
```

#### View Escalated Emails
```bash
docker compose exec postgres psql -U crm -d crm_db -c "
  SELECT id, sender, subject, urgency, created_at 
  FROM emails 
  WHERE status = 'Escalated' 
  ORDER BY created_at DESC 
  LIMIT 10;
"
```

#### View Spam Emails
```bash
docker compose exec postgres psql -U crm -d crm_db -c "
  SELECT id, sender, subject, created_at 
  FROM emails 
  WHERE status = 'Spam' 
  ORDER BY created_at DESC 
  LIMIT 10;
"
```

#### Reset Database (Development Only)
```bash
# WARNING: This deletes all data!
docker compose down -v
docker compose up -d
docker compose exec backend alembic upgrade head
docker compose exec backend python scripts/seed_knowledge_base.py
docker compose exec backend python scripts/create_sample_data.py
```

### Knowledge Base Operations

#### Re-seed Knowledge Base
```bash
docker compose exec backend python scripts/seed_knowledge_base.py
```

#### View Knowledge Chunks
```bash
docker compose exec postgres psql -U crm -d crm_db -c "
  SELECT source, COUNT(*) 
  FROM knowledge_chunks 
  GROUP BY source 
  ORDER BY count DESC;
"
```

#### Test RAG Search
```bash
curl "http://localhost:8000/api/rag/search?q=refund+policy&top_k=3" | jq
```

### Redis Operations

#### View Sentiment Data
```bash
docker compose exec redis redis-cli keys "sentiment:*"
```

#### View Cache Keys
```bash
docker compose exec redis redis-cli keys "*"
```

#### Flush Redis Cache
```bash
docker compose exec redis redis-cli flushall
```

### Agent Operations

#### Test Agent Dry Run
```bash
# Get first email ID
EMAIL_ID=$(docker compose exec postgres psql -U crm -d crm_db -t -c "SELECT id FROM emails LIMIT 1;" | xargs)

# Run dry run
curl -X POST "http://localhost:8000/api/agent/dry-run/$EMAIL_ID" | jq
```

#### View Agent Actions
```bash
docker compose exec postgres psql -U crm -d crm_db -c "
  SELECT action_type, COUNT(*) 
  FROM actions 
  GROUP BY action_type 
  ORDER BY count DESC;
"
```

---

## Monitoring

### Performance Metrics

#### API Response Times
```bash
# Check backend logs for slow requests
docker compose logs backend | grep "ms"
```

#### Database Query Performance
```bash
# View slow queries (>100ms)
docker compose exec postgres psql -U crm -d crm_db -c "
  SELECT query, calls, total_time, mean_time 
  FROM pg_stat_statements 
  WHERE mean_time > 100 
  ORDER BY mean_time DESC 
  LIMIT 10;
"
```

#### Redis Memory Usage
```bash
docker compose exec redis redis-cli info memory | grep used_memory_human
```

### Alert Conditions

Set up alerts for:
- **High escalation rate:** >50% of emails require human review
- **Low confidence:** Average confidence <0.70
- **Spam spike:** >30% of emails marked as spam
- **Agent failures:** Agent errors >10% of runs
- **Database connection failures:** >5 failures/hour
- **Redis connection failures:** >5 failures/hour
- **Groq API failures:** >10 failures/hour

---

## Backup & Recovery

### Database Backup
```bash
# Create backup
docker compose exec postgres pg_dump -U crm crm_db > backup_$(date +%Y%m%d).sql

# Restore from backup
docker compose exec -T postgres psql -U crm crm_db < backup_20240115.sql
```

### Volume Backup
```bash
# Backup all volumes
docker run --rm -v crm_pgdata:/data -v $(pwd):/backup alpine tar czf /backup/pgdata_backup.tar.gz /data

# Restore volumes
docker run --rm -v crm_pgdata:/data -v $(pwd):/backup alpine tar xzf /backup/pgdata_backup.tar.gz -C /
```

---

## Scaling

### Horizontal Scaling (Backend)
```bash
# Scale to 3 backend instances
docker compose up -d --scale backend=3
```

### Vertical Scaling
```bash
# Increase backend memory limit (docker-compose.yml)
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
```

---

## Deployment

### Production Deployment Checklist
- [ ] Set strong database password
- [ ] Enable HTTPS/TLS
- [ ] Configure OAuth2/SSO authentication
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure log aggregation (ELK/Loki)
- [ ] Set up automated backups
- [ ] Enable rate limiting
- [ ] Configure CORS for specific domains
- [ ] Set up secrets manager
- [ ] Enable database connection pooling
- [ ] Configure Redis persistence
- [ ] Set up alerting (PagerDuty/OpsGenie)

---

## Incident Response

### P0: Service Down
1. Check service status: `docker compose ps`
2. Check logs: `docker compose logs backend`
3. Restart service: `docker compose restart backend`
4. Verify health: `curl http://localhost:8000/health`
5. If still down, check database: `docker compose exec postgres pg_isready`
6. If database down, restart: `docker compose restart postgres`

### P1: High Error Rate
1. Check logs for errors: `docker compose logs backend | grep ERROR`
2. Check Groq API status: `curl https://api.groq.com/status`
3. Check database connections: `docker compose exec postgres psql -U crm -d crm_db -c "SELECT count(*) FROM pg_stat_activity;"`
4. Check Redis: `docker compose exec redis redis-cli info clients`
5. If Groq down, system falls back to heuristic classification (reduced accuracy)

### P2: Slow Performance
1. Check database slow queries (see Monitoring section)
2. Check Redis memory: `docker compose exec redis redis-cli info memory`
3. Check backend CPU/memory: `docker stats`
4. Consider scaling horizontally (see Scaling section)

---

## Contact

For issues or questions:
- GitHub Issues: https://github.com/yourusername/senai-crm/issues
- Email: intern@senai.com
