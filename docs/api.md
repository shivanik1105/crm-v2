# API Reference

Base URL: `http://localhost:8000/api`

Interactive docs: `http://localhost:8000/docs` (Swagger UI)

## Authentication

None (all endpoints are open in this assessment implementation).

## Error Response Format

All errors return a standardized envelope:

```json
{
  "error_code": "VALIDATION_ERROR",
  "message": "Missing required fields: message_id, sender, body",
  "details": {}
}
```

Error codes:
- `VALIDATION_ERROR` - Invalid request payload
- `NOT_FOUND` - Resource not found
- `INTERNAL_ERROR` - Server error
- `SCRAPE_ERROR` - Web scraping failed

---

## Email Ingestion

### POST /ingest

Ingest a new email into the system.

**Request:**
```json
{
  "message_id": "msg_001",
  "sender": "customer@example.com",
  "recipient": "support@company.com",
  "subject": "Billing question",
  "body": "Hi, I have a question about my invoice...",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processed",
  "message": "Email ingested and processed",
  "existing": false,
  "email_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Status codes:**
- `200` - Success
- `400` - Validation error
- `409` - Duplicate message_id (returns existing email)

---

### GET /status/{job_id}

Check processing status of an ingested email.

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "Replied",
  "category": "Billing",
  "urgency": "Medium",
  "requires_human": false,
  "classification": {
    "category": "Billing",
    "urgency": "Medium",
    "sentiment_score": -0.2,
    "confidence": 0.87
  }
}
```

---

## Email Management

### GET /emails/

List all emails with filters.

**Query parameters:**
- `skip` (int, default=0) - Pagination offset
- `limit` (int, default=50, max=100) - Page size
- `category` (string) - Filter by category
- `urgency` (string) - Filter by urgency
- `status` (string) - Filter by status
- `requires_human` (boolean) - Filter by human review flag

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "message_id": "msg_001",
    "sender": "customer@example.com",
    "subject": "Billing question",
    "body": "Hi, I have a question...",
    "timestamp": "2024-01-15T10:30:00Z",
    "category": "Billing",
    "sentiment_score": -0.2,
    "urgency": "Medium",
    "confidence": 0.87,
    "requires_human": false,
    "status": "Replied",
    "thread_id": "660e8400-e29b-41d4-a716-446655440000"
  }
]
```

---

### GET /emails/{email_id}

Get single email with full details.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "message_id": "msg_001",
  "sender": "customer@example.com",
  "recipient": "support@company.com",
  "subject": "Billing question",
  "body": "Full email body...",
  "timestamp": "2024-01-15T10:30:00Z",
  "category": "Billing",
  "sentiment_score": -0.2,
  "urgency": "Medium",
  "confidence": 0.87,
  "requires_human": false,
  "status": "Replied",
  "classification_result": {...},
  "reasoning_trace": {...},
  "rag_chunks": [...],
  "thread_id": "660e8400-e29b-41d4-a716-446655440000"
}
```

---

### GET /emails/{email_id}/reasoning

Get AI reasoning trace for an email.

**Response:**
```json
{
  "email_id": "550e8400-e29b-41d4-a716-446655440000",
  "scenario_detected": null,
  "confidence": 0.87,
  "rag_context_used": true,
  "reasoning_steps": [
    {
      "step": 1,
      "thought": "Analyzing email from customer@example.com",
      "action": "Heuristic filtering",
      "observation": "Category: Billing, Urgency: Medium",
      "next_step": "RAG retrieval"
    }
  ],
  "final_decision": "Draft reply citing refund policy",
  "escalation_triggered": false
}
```

---

### GET /emails/{email_id}/rag-context

Get RAG chunks used for this email.

**Response:**
```json
{
  "email_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "Billing question refund policy",
  "chunks_retrieved": [
    {
      "source": "refund_policy.md",
      "heading": "Exception Process",
      "content": "No refunds after 14 days...",
      "similarity_score": 0.85,
      "chunk_index": 2
    }
  ],
  "total_chunks": 3
}
```

---

## Bulk Actions

### POST /emails/bulk/spam

Mark multiple emails as spam.

**Request:**
```json
{
  "email_ids": ["id1", "id2", "id3"]
}
```

**Response:**
```json
{
  "updated": 3,
  "status": "Spam"
}
```

---

### POST /emails/bulk/assign

Assign multiple emails to a team member.

**Request:**
```json
{
  "email_ids": ["id1", "id2"],
  "assignee": "john@company.com"
}
```

**Response:**
```json
{
  "updated": 2,
  "assignee": "john@company.com"
}
```

---

### POST /emails/bulk/archive

Archive multiple emails.

**Request:**
```json
{
  "email_ids": ["id1", "id2"]
}
```

**Response:**
```json
{
  "updated": 2,
  "status": "Archived"
}
```

---

## Thread Management

### GET /threads/{contact_email}

Get all threads for a contact.

**Response:**
```json
[
  {
    "id": "660e8400-e29b-41d4-a716-446655440000",
    "sender_email": "customer@example.com",
    "subject": "Billing question",
    "category": "Billing",
    "status": "Open",
    "last_updated_at": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-15T10:30:00Z",
    "emails": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "sender": "customer@example.com",
        "subject": "Billing question",
        "body": "...",
        "timestamp": "2024-01-15T10:30:00Z",
        "category": "Billing",
        "sentiment_score": -0.2,
        "urgency": "Medium"
      }
    ]
  }
]
```

---

### GET /threads/{contact_email}/summary

Get AI-generated thread summary.

**Response:**
```json
{
  "summary": "Customer has sent 5 emails about billing issues. Initial inquiry was neutral, but sentiment has deteriorated to -0.6 due to lack of response. Latest email threatens churn. Recommend immediate escalation to Account Executive with retention offer.",
  "email_count": 5,
  "generated_by": "llm"
}
```

---

## Respond & Drafts

### POST /respond/{email_id}

Mark email as replied.

**Response:**
```json
{
  "email_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "Replied",
  "message": "Email marked as replied"
}
```

---

### PATCH /respond/drafts/{email_id}

Update draft reply for an email.

**Request:**
```json
{
  "draft_body": "Dear Customer,\n\nThank you for reaching out..."
}
```

**Response:**
```json
{
  "email_id": "550e8400-e29b-41d4-a716-446655440000",
  "draft_updated": true,
  "draft_body": "Dear Customer,...",
  "status": "Drafted"
}
```

---

### POST /respond/drafts/{email_id}/approve

Approve and send draft reply.

**Response:**
```json
{
  "email_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "Replied",
  "message": "Draft approved and reply sent",
  "approved_at": "2024-01-15T11:00:00Z"
}
```

---

## Analytics

### GET /analytics/sentiment-trend

Get sentiment trend for a sender.

**Query parameters:**
- `sender` (string, required) - Email address
- `days` (int, default=30, max=365) - Time window

**Response:**
```json
{
  "sender": "customer@example.com",
  "points": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "sentiment_score": -0.2,
      "email_id": "550e8400-e29b-41d4-a716-446655440000"
    }
  ],
  "moving_average": -0.35,
  "trend_direction": "deteriorating",
  "alert_triggered": false
}
```

---

### GET /analytics/category-distribution

Get category distribution across all emails.

**Response:**
```json
{
  "distribution": [
    {
      "category": "Billing",
      "count": 15,
      "percentage": 25.0
    },
    {
      "category": "Technical",
      "count": 12,
      "percentage": 20.0
    }
  ],
  "total": 60
}
```

---

### GET /analytics/at-risk

Get at-risk accounts.

**Response:**
```json
{
  "accounts": [
    {
      "sender": "karen@retail-co.com",
      "churn_risk_score": 85.0,
      "account_value": 149.0,
      "unresolved_threads": 3,
      "last_email_date": "2024-01-10T10:30:00Z",
      "sentiment_trend": "deteriorating"
    }
  ],
  "total_at_risk": 1
}
```

---

### GET /analytics/agent-performance

Get agent performance metrics.

**Response:**
```json
{
  "auto_reply_rate": 45.0,
  "escalation_rate": 30.0,
  "avg_confidence": 0.82,
  "avg_tools_used": 4.2,
  "total_processed": 60,
  "total_escalated": 18
}
```

---

### GET /analytics/response-time-heatmap

Get response time heatmap by hour/day.

**Response:**
```json
{
  "heatmap": [
    {
      "day": "Mon",
      "hour": "8:00",
      "avg_response": 15.5,
      "count": 12
    }
  ]
}
```

---

## RAG

### GET /rag/search

Search knowledge base via RAG.

**Query parameters:**
- `q` (string, required) - Search query
- `top_k` (int, default=3, max=10) - Number of results

**Response:**
```json
{
  "query": "refund policy",
  "results": [
    {
      "source": "refund_policy.md",
      "heading": "Exception Process",
      "chunk_index": 2,
      "content": "No refunds after 14 days...",
      "similarity_score": 0.85
    }
  ],
  "total": 3
}
```

---

## Intelligence

### GET /intelligence/reputation

Get public reputation data for a company.

**Query parameters:**
- `company_name` (string, required) - Company name

**Response:**
```json
{
  "company": "SenAI",
  "data": {
    "source": "simulated",
    "company": "SenAI",
    "g2_rating": 4.2,
    "g2_review_count": 150,
    "trustpilot_rating": 3.8,
    "common_themes": ["Good UI", "Slow support"]
  }
}
```

---

## Agent

### POST /agent/dry-run/{email_id}

Run agent in planning mode (no execution).

**Response:**
```json
{
  "email_id": "550e8400-e29b-41d4-a716-446655440000",
  "trace": {
    "email_id": "550e8400-e29b-41d4-a716-446655440000",
    "classification": {...},
    "steps": [
      {
        "step_number": 1,
        "thought": "Check thread history",
        "action": "get_thread_history",
        "action_input": {"sender_email": "customer@example.com"},
        "observation": "{\"threads\": 3}"
      }
    ],
    "final_recommendation": "Draft reply and queue for review",
    "draft_reply": "Dear Customer,...",
    "escalate": false,
    "tools_used": ["get_thread_history", "search_knowledge_base", "draft_reply"],
    "dry_run": true
  },
  "proposed_actions": ["get_thread_history", "search_knowledge_base", "draft_reply"],
  "confidence": 0.87
}
```

---

## Contacts

### GET /contacts/{email}

Get contact profile.

**Response:**
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "email": "customer@example.com",
  "name": "John Doe",
  "tier": "Standard",
  "account_value": 149.0,
  "vip_status": false,
  "churn_risk_score": 25.0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

### PATCH /contacts/{email}

Update contact fields.

**Request:**
```json
{
  "vip_status": true,
  "churn_risk_score": 85.0
}
```

**Response:**
```json
{
  "email": "customer@example.com",
  "updated": true,
  "fields": ["vip_status", "churn_risk_score"]
}
```

---

## Dashboard

### GET /dashboard/stats

Get dashboard statistics.

**Response:**
```json
{
  "total_emails": 60,
  "total_threads": 30,
  "total_contacts": 25,
  "status_breakdown": {
    "New": 10,
    "Replied": 27,
    "Escalated": 18,
    "Spam": 5
  },
  "urgency_breakdown": {
    "Low": 30,
    "Medium": 15,
    "High": 10,
    "Critical": 5
  },
  "needs_human": 18,
  "auto_replied": 27,
  "escalated": 18
}
```

---

## Audit

### GET /audit/{entity_type}/{entity_id}

Get audit log for an entity.

**Response:**
```json
{
  "entity_type": "email",
  "entity_id": "550e8400-e29b-41d4-a716-446655440000",
  "logs": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440000",
      "action": "ingested",
      "actor": "system",
      "diff": {
        "message_id": "msg_001",
        "sender": "customer@example.com"
      },
      "timestamp": "2024-01-15T10:30:00Z",
      "ip_address": null,
      "user_agent": null
    }
  ],
  "total": 1
}
```

---

## WebSocket

### WS /api/ws

Connect to real-time event stream.

**Events:**

```json
{
  "type": "email_ingested",
  "data": {
    "email_id": "550e8400-e29b-41d4-a716-446655440000",
    "message_id": "msg_001",
    "sender": "customer@example.com",
    "subject": "Billing question",
    "status": "Processing"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

```json
{
  "type": "email_classified",
  "data": {
    "email_id": "550e8400-e29b-41d4-a716-446655440000",
    "classification": {
      "category": "Billing",
      "urgency": "Medium",
      "sentiment_score": -0.2,
      "confidence": 0.87
    }
  },
  "timestamp": "2024-01-15T10:30:01Z"
}
```

```json
{
  "type": "agent_decision",
  "data": {
    "email_id": "550e8400-e29b-41d4-a716-446655440000",
    "trace": {
      "steps": 4,
      "escalate": false,
      "final_recommendation": "Draft reply",
      "tools_used": ["get_thread_history", "search_knowledge_base", "draft_reply"]
    }
  },
  "timestamp": "2024-01-15T10:30:05Z"
}
```

```json
{
  "type": "action_taken",
  "data": {
    "action_type": "reply_sent",
    "email_id": "550e8400-e29b-41d4-a716-446655440000",
    "details": {"status": "Replied"}
  },
  "timestamp": "2024-01-15T10:30:06Z"
}
```

---

## Health Check

### GET /health

Check service health.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```
