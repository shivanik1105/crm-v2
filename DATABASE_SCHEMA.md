# Database Schema & ER Diagram

## Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            SENAI CRM DATABASE SCHEMA                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐
│       CONTACTS           │
├──────────────────────────┤
│ PK  id (UUID)            │
│     email (str)          │◄────────────┐
│     name (str)           │             │
│     company (str)        │             │ 1:N
│     tier (str)           │             │
│     account_value (float)│             │
│     churn_risk_score(int)│             │
│     vip_status (bool)    │             │
│     tags (json)          │             │
│     metadata (json)      │             │
│     created_at (ts)      │             │
└──────────────────────────┘             │
                                         │
                                         │
┌──────────────────────────┐             │
│        THREADS           │             │
├──────────────────────────┤             │
│ PK  id (UUID)            │             │
│ FK  contact_id ──────────┼─────────────┘
│     subject (str)        │◄────────────┐
│     status (str)         │             │
│     priority (int)       │             │ 1:N
│     last_updated_at (ts) │             │
│     sentiment_trend (str)│             │
│     created_at (ts)      │             │
└──────────────────────────┘             │
                                         │
                                         │
┌──────────────────────────┐             │
│         EMAILS           │             │
├──────────────────────────┤             │
│ PK  id (UUID)            │             │
│ FK  thread_id ───────────┼─────────────┘
│     sender (str)         │
│     subject (str)        │
│     body (text)          │
│     category (str)       │  ┌─ billing, support, complaint
│     sentiment_score(float)│  │  outage, feature, refund, spam
│     urgency_score (int)  │  └─ gdpr, ransomware
│     confidence (float)   │
│     priority_score (int) │
│     status (str)         │  ← Open, InProgress, Replied, Escalated, Closed
│     requires_human (bool)│
│     processed_at (ts)    │
│     timestamp (ts)       │  ← Email received time
│     created_at (ts)      │  ← Processed time (for response time calc)
│     heuristic_flags(json)│
└──────────────────────────┘
         │
         │ 1:N
         ▼
┌──────────────────────────┐
│        ACTIONS           │
├──────────────────────────┤
│ PK  id (UUID)            │
│ FK  email_id ────────────┼─────┐
│     action_type (str)    │     │
│     suggested_reply (text)│    │
│     confidence (float)   │     │
│     reasoning (text)     │     │
│     tools_used (list str)│     │
│     agent_reasoning_log  │     │
│       (json)             │     │  ◄─ Full LangChain trace
│     rag_context (json)   │     │  ◄─ Retrieved KB chunks
│     web_intelligence_id  │     │
│       (UUID nullable)    │     │
│     executed_at (ts)     │     │
│     created_at (ts)      │     │
└──────────────────────────┘     │
                                 │
                                 │
┌──────────────────────────┐     │
│   KNOWLEDGE_CHUNKS       │     │
├──────────────────────────┤     │
│ PK  id (UUID)            │     │
│     chunk_text (text)    │     │
│     embedding (vector)   │◄────┼──── pgvector(1536) for RAG
│     source_file (str)    │     │
│     chunk_index (int)    │     │
│     metadata (json)      │     │
│     created_at (ts)      │     │
└──────────────────────────┘     │
                                 │
                                 │
┌──────────────────────────┐     │
│   WEB_INTELLIGENCE       │     │
├──────────────────────────┤     │
│ PK  id (UUID)            │     │
│ FK  email_id ────────────┼─────┘
│     domain (str)         │
│     company_name (str)   │
│     reputation_score(int)│
│     recent_complaints(int)│
│     scraped_data (json)  │
│     scraped_at (ts)      │
│     created_at (ts)      │
└──────────────────────────┘


┌──────────────────────────┐
│      AUDIT_LOGS          │
├──────────────────────────┤
│ PK  id (UUID)            │
│     entity_type (str)    │
│     entity_id (UUID)     │
│     action (str)         │
│     user_id (str null)   │
│     details (json)       │
│     ip_address (str null)│
│     created_at (ts)      │
└──────────────────────────┘
```

## Table Details

### 1. CONTACTS
Stores customer/sender information with churn risk scoring.

| Column             | Type    | Constraints      | Description                          |
|--------------------|---------|------------------|--------------------------------------|
| id                 | UUID    | PK               | Unique identifier                    |
| email              | String  | UNIQUE, NOT NULL | Contact email address                |
| name               | String  | NULL             | Full name                            |
| company            | String  | NULL             | Company name                         |
| tier               | String  | NULL             | Starter/Standard/Enterprise          |
| account_value      | Float   | DEFAULT 0        | Monthly recurring revenue            |
| churn_risk_score   | Integer | DEFAULT 0        | 0-100 churn probability              |
| vip_status         | Boolean | DEFAULT False    | VIP flag                             |
| tags               | JSON    | NULL             | Custom tags array                    |
| metadata           | JSON    | NULL             | Additional metadata                  |
| created_at         | DateTime| NOT NULL         | Record creation timestamp            |

**Indexes:**
- `ix_contacts_email` on `email`
- `ix_contacts_churn_risk_score` on `churn_risk_score`

---

### 2. THREADS
Groups emails by sender/subject for conversation tracking.

| Column             | Type    | Constraints      | Description                          |
|--------------------|---------|------------------|--------------------------------------|
| id                 | UUID    | PK               | Unique identifier                    |
| contact_id         | UUID    | FK → contacts.id | Owner of thread                      |
| subject            | String  | NOT NULL         | Email subject/topic                  |
| status             | String  | NOT NULL         | Open/InProgress/Closed               |
| priority           | Integer | DEFAULT 0        | Thread priority score                |
| last_updated_at    | DateTime| NOT NULL         | Last activity timestamp              |
| sentiment_trend    | String  | NULL             | improving/deteriorating/stable       |
| created_at         | DateTime| NOT NULL         | Thread creation timestamp            |

**Indexes:**
- `ix_threads_contact_id` on `contact_id`
- `ix_threads_status` on `status`

---

### 3. EMAILS
Core email records with classification results.

| Column             | Type    | Constraints      | Description                          |
|--------------------|---------|------------------|--------------------------------------|
| id                 | UUID    | PK               | Unique identifier                    |
| thread_id          | UUID    | FK → threads.id  | Parent thread                        |
| sender             | String  | NOT NULL         | Email sender address                 |
| subject            | String  | NOT NULL         | Email subject line                   |
| body               | Text    | NOT NULL         | Email body content                   |
| category           | String  | NOT NULL         | LLM classification category          |
| sentiment_score    | Float   | NOT NULL         | -1.0 to 1.0 sentiment                |
| urgency_score      | Integer | NOT NULL         | 1-5 urgency level                    |
| confidence         | Float   | NOT NULL         | 0-1 classification confidence        |
| priority_score     | Integer | NOT NULL         | Computed priority 1-10               |
| status             | String  | NOT NULL         | Open/Replied/Escalated/Closed        |
| requires_human     | Boolean | DEFAULT False    | Escalation flag                      |
| processed_at       | DateTime| NULL             | LLM processing completion time       |
| timestamp          | DateTime| NOT NULL (tz)    | Email received time                  |
| created_at         | DateTime| NOT NULL (tz)    | Ingestion time (for response calc)   |
| heuristic_flags    | JSON    | NULL             | Spam/GDPR/Ransomware flags           |

**Indexes:**
- `ix_emails_thread_id` on `thread_id`
- `ix_emails_sender` on `sender`
- `ix_emails_category` on `category`
- `ix_emails_status` on `status`
- `ix_emails_timestamp` on `timestamp`

**Categories:** `billing`, `support`, `complaint`, `outage`, `feature_request`, `refund`, `spam`, `gdpr`, `ransomware`

---

### 4. ACTIONS
Agent decisions and reasoning traces.

| Column                 | Type    | Constraints      | Description                          |
|------------------------|---------|------------------|--------------------------------------|
| id                     | UUID    | PK               | Unique identifier                    |
| email_id               | UUID    | FK → emails.id   | Related email                        |
| action_type            | String  | NOT NULL         | auto_reply/escalate/draft/flag       |
| suggested_reply        | Text    | NULL             | Agent-generated response             |
| confidence             | Float   | NOT NULL         | 0-1 action confidence                |
| reasoning              | Text    | NULL             | Human-readable explanation           |
| tools_used             | JSON    | NULL             | List of tools invoked                |
| agent_reasoning_log    | JSON    | NULL             | Full LangChain trace                 |
| rag_context            | JSON    | NULL             | Retrieved knowledge chunks           |
| web_intelligence_id    | UUID    | FK → web_intel   | Related web scraping data            |
| executed_at            | DateTime| NULL             | Action execution time                |
| created_at             | DateTime| NOT NULL         | Record creation timestamp            |

**Indexes:**
- `ix_actions_email_id` on `email_id`

---

### 5. KNOWLEDGE_CHUNKS
RAG knowledge base with vector embeddings.

| Column             | Type    | Constraints      | Description                          |
|--------------------|---------|------------------|--------------------------------------|
| id                 | UUID    | PK               | Unique identifier                    |
| chunk_text         | Text    | NOT NULL         | Text content chunk                   |
| embedding          | Vector  | NOT NULL         | pgvector(1536) embedding             |
| source_file        | String  | NOT NULL         | Original .md filename                |
| chunk_index        | Integer | NOT NULL         | Chunk position in source             |
| metadata           | JSON    | NULL             | Additional metadata                  |
| created_at         | DateTime| NOT NULL         | Record creation timestamp            |

**Vector Index:**
- `ix_knowledge_chunks_embedding` using `vector_cosine_ops` for similarity search

**Source Files:**
1. `pricing_policy.md` - Pricing plans and limits
2. `sla_policy.md` - SLA commitments
3. `refund_policy.md` - Refund terms
4. `api_docs.md` - API documentation
5. `compliance_faq.md` - GDPR/compliance info
6. `escalation_matrix.md` - When to escalate

---

### 6. WEB_INTELLIGENCE
Scraped company reputation data (stubbed).

| Column             | Type    | Constraints      | Description                          |
|--------------------|---------|------------------|--------------------------------------|
| id                 | UUID    | PK               | Unique identifier                    |
| email_id           | UUID    | FK → emails.id   | Related email                        |
| domain             | String  | NOT NULL         | Company domain                       |
| company_name       | String  | NULL             | Extracted company name               |
| reputation_score   | Integer | DEFAULT 0        | 0-100 reputation score               |
| recent_complaints  | Integer | DEFAULT 0        | Count of recent complaints           |
| scraped_data       | JSON    | NULL             | Raw scraped data                     |
| scraped_at         | DateTime| NOT NULL         | Scraping timestamp                   |
| created_at         | DateTime| NOT NULL         | Record creation timestamp            |

**Indexes:**
- `ix_web_intelligence_email_id` on `email_id`
- `ix_web_intelligence_domain` on `domain`

---

### 7. AUDIT_LOGS
System audit trail for compliance.

| Column             | Type    | Constraints      | Description                          |
|--------------------|---------|------------------|--------------------------------------|
| id                 | UUID    | PK               | Unique identifier                    |
| entity_type        | String  | NOT NULL         | Table name (emails, threads, etc.)   |
| entity_id          | UUID    | NOT NULL         | Record ID                            |
| action             | String  | NOT NULL         | create/update/delete                 |
| user_id            | String  | NULL             | User who performed action            |
| details            | JSON    | NULL             | Changed fields                       |
| ip_address         | String  | NULL             | Request IP                           |
| created_at         | DateTime| NOT NULL         | Action timestamp                     |

**Indexes:**
- `ix_audit_logs_entity` on `(entity_type, entity_id)`
- `ix_audit_logs_created_at` on `created_at`

---

## SQL Schema Export

```sql
-- PostgreSQL 16 with pgvector extension

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- CONTACTS TABLE
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    company VARCHAR(255),
    tier VARCHAR(50),
    account_value FLOAT DEFAULT 0,
    churn_risk_score INTEGER DEFAULT 0,
    vip_status BOOLEAN DEFAULT FALSE,
    tags JSONB,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX ix_contacts_email ON contacts(email);
CREATE INDEX ix_contacts_churn_risk_score ON contacts(churn_risk_score);

-- THREADS TABLE
CREATE TABLE threads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID NOT NULL REFERENCES contacts(id) ON DELETE CASCADE,
    subject VARCHAR(500) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Open',
    priority INTEGER DEFAULT 0,
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    sentiment_trend VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX ix_threads_contact_id ON threads(contact_id);
CREATE INDEX ix_threads_status ON threads(status);

-- EMAILS TABLE
CREATE TABLE emails (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
    sender VARCHAR(255) NOT NULL,
    subject VARCHAR(500) NOT NULL,
    body TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    sentiment_score FLOAT NOT NULL,
    urgency_score INTEGER NOT NULL,
    confidence FLOAT NOT NULL,
    priority_score INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Open',
    requires_human BOOLEAN DEFAULT FALSE,
    processed_at TIMESTAMP WITH TIME ZONE,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    heuristic_flags JSONB
);

CREATE INDEX ix_emails_thread_id ON emails(thread_id);
CREATE INDEX ix_emails_sender ON emails(sender);
CREATE INDEX ix_emails_category ON emails(category);
CREATE INDEX ix_emails_status ON emails(status);
CREATE INDEX ix_emails_timestamp ON emails(timestamp);

-- KNOWLEDGE_CHUNKS TABLE
CREATE TABLE knowledge_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_text TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    source_file VARCHAR(255) NOT NULL,
    chunk_index INTEGER NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX ix_knowledge_chunks_embedding ON knowledge_chunks 
    USING ivfflat (embedding vector_cosine_ops);

-- ACTIONS TABLE
CREATE TABLE actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_id UUID NOT NULL REFERENCES emails(id) ON DELETE CASCADE,
    action_type VARCHAR(50) NOT NULL,
    suggested_reply TEXT,
    confidence FLOAT NOT NULL,
    reasoning TEXT,
    tools_used JSONB,
    agent_reasoning_log JSONB,
    rag_context JSONB,
    web_intelligence_id UUID,
    executed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX ix_actions_email_id ON actions(email_id);

-- WEB_INTELLIGENCE TABLE
CREATE TABLE web_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email_id UUID NOT NULL REFERENCES emails(id) ON DELETE CASCADE,
    domain VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    reputation_score INTEGER DEFAULT 0,
    recent_complaints INTEGER DEFAULT 0,
    scraped_data JSONB,
    scraped_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX ix_web_intelligence_email_id ON web_intelligence(email_id);
CREATE INDEX ix_web_intelligence_domain ON web_intelligence(domain);

-- AUDIT_LOGS TABLE
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(50) NOT NULL,
    user_id VARCHAR(255),
    details JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE INDEX ix_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX ix_audit_logs_created_at ON audit_logs(created_at);
```

---

## Database Migrations

Managed via **Alembic**.

### Migration Files
Location: `backend/migrations/versions/`

1. **001_initial_schema.py** - Creates all base tables
2. **002_add_reasoning_trace.py** - Adds `agent_reasoning_log` column to actions

### Running Migrations

```bash
# Apply all migrations
docker compose exec backend alembic upgrade head

# Create new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Rollback one version
docker compose exec backend alembic downgrade -1
```

---

## Data Relationships Summary

```
Contact (1) ──→ (N) Threads ──→ (N) Emails
                                    │
                                    ├──→ (N) Actions
                                    │
                                    └──→ (0..1) WebIntelligence

KnowledgeChunks ←─ vector search ─→ Actions.rag_context

AuditLogs ──references──→ Any Entity (polymorphic)
```
