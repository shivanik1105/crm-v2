# 🎬 Demo Commands - Quick Reference

## 🔧 Pre-Demo Setup (Run Once)

```bash
# 1. Fix contact data (populate churn risk & account values)
docker compose cp fix_contacts.sql postgres:/tmp/fix_contacts.sql
docker compose exec postgres psql -U crm -d crm_db -f /tmp/fix_contacts.sql

# 2. Clear old emails for clean demo (optional)
docker compose exec postgres psql -U crm -d crm_db -c "DELETE FROM emails; DELETE FROM threads;"

# 3. Verify system is running
docker compose ps
```

---

## 🎯 Demo Commands

### Start Real-Time Simulation (Slow - Best for Demo)
```bash
docker compose exec backend python /app/scripts/simulate_stream.py --file /app/email-data-advanced.json --speed 1
```
**Shows**: Emails appearing one per second in real-time

### Quick Test (5 Emails Only)
```bash
docker compose exec backend python /app/scripts/simulate_stream.py --file /app/email-data-advanced.json --speed 1 --limit 5
```

### Fast Bulk Load (All 60 Emails)
```bash
docker compose exec backend python /app/scripts/simulate_stream.py --file /app/email-data-advanced.json --speed 0.1
```

---

## 📊 Verification Commands

### Check Email Count
```bash
docker compose exec postgres psql -U crm -d crm_db -c "SELECT COUNT(*) FROM emails;"
```

### View Recent Emails
```bash
docker compose exec postgres psql -U crm -d crm_db -c "SELECT sender, subject, category, urgency, status FROM emails ORDER BY timestamp DESC LIMIT 10;"
```

### Check Contact Risk Scores
```bash
docker compose exec postgres psql -U crm -d crm_db -c "SELECT email, churn_risk_score, account_value, tier FROM contacts WHERE churn_risk_score > 0 ORDER BY churn_risk_score DESC;"
```

### View At-Risk Accounts
```bash
docker compose exec postgres psql -U crm -d crm_db -c "SELECT email, churn_risk_score, account_value FROM contacts WHERE churn_risk_score > 50 ORDER BY churn_risk_score DESC;"
```

---

## 🐛 Troubleshooting

### Restart Services
```bash
docker compose restart backend frontend
```

### View Logs
```bash
# Backend logs (see email processing)
docker compose logs backend -f

# All services
docker compose logs -f
```

### Reset Everything
```bash
docker compose down -v
docker compose up -d --build
# Then run pre-demo setup again
```

---

## 🌐 URLs

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **WebSocket**: ws://localhost:8000/ws

---

## ✅ Quick Health Check

```bash
# All should return "healthy" or show data
curl http://localhost:8000/health
curl http://localhost:8000/api/dashboard/stats
docker compose ps
```

---

## 🎤 Demo Talking Points

1. **"This is a production-ready real-time system"**
   - Point to green "Live" indicator

2. **"Watch emails populate automatically"**
   - Start simulation at speed 1
   - No refresh needed

3. **"AI analyzes each email"**
   - Show category, sentiment, urgency
   - Explain confidence scores

4. **"Special scenarios trigger alerts"**
   - GDPR requests escalate
   - Ransomware detected
   - VIP customers prioritized

5. **"Analytics show customer health"**
   - Navigate to Analytics page
   - Karen at 85% churn risk ($2,400/mo account)
   - Sentiment trends over time

6. **"Agent makes intelligent decisions"**
   - Auto-reply vs. escalate
   - Uses knowledge base (RAG)
   - Tools: search policies, check reputation

---

## 📋 Pre-Demo Checklist

- [ ] Services running: `docker compose ps`
- [ ] Contact data populated (check Analytics page)
- [ ] Browser open to http://localhost:5173
- [ ] Green "Live" badge visible
- [ ] Terminal ready with simulation command
- [ ] Clear inbox (optional for clean demo)

**You're ready! 🚀**
