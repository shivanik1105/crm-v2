#!/bin/bash
cd /mnt/f/shivani/VSCode/projects/crm

echo "=== SenAI CRM - Running ==="
echo ""

# Check services
echo "📦 Service Status:"
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Test API health
echo "🔍 Testing API Health..."
curl -s http://localhost:8000/health | jq .
echo ""

# Run email simulation
echo "📧 Starting Email Simulation (60 emails at 2/sec)..."
docker compose exec backend python /app/scripts/simulate_stream.py --file /app/email-data-advanced.json --speed 2 --url http://localhost:8000
echo ""

# Show dashboard stats
echo "📊 Dashboard Stats:"
curl -s http://localhost:8000/api/dashboard/stats | jq .
echo ""

echo "✅ Access Points:"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8000/docs"
echo "   Backend:  http://localhost:8000/health"
echo ""
