# SenAI CRM - Screen Recording Demo Script

## Setup (before recording)
1. Open terminal and run: `cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000`
2. Open browser and navigate to: `http://localhost:8000`
3. The frontend should be served automatically by the backend

## Demo Script (5-10 minutes)

### 1. System Overview & Email Ingestion (1-2 minutes)
**Opening:**
"Hi, I'm [Your Name]. This is my submission for the SenAI AI Intern Technical Assessment — a production-grade Agentic CRM Intelligence Platform."

**Navigate to the Dashboard:**
- Show the Mission Control Inbox
- Point out the real-time WebSocket indicator (green "Live" badge)
- Show the stats cards: Total Emails, Needs Human, Auto-Replied, Escalated, Avg Confidence, Pending

**Email Ingestion:**
- Mention that 60 real emails from `email-data-advanced.json` have been processed
- Show the tab system: All | Critical | Needs Human | Auto-Replied | Escalated | Spam
- Click on the "Critical" tab to show urgent emails
- Show color-coded urgency badges: Critical (red), High (orange), Medium (yellow), Low (green)
- Show category badges: Billing (blue), Compliance (purple), Security (red), etc.

### 2. Agent Reasoning Trace — Bob Outage Escalation (2-3 minutes)
**Navigate to Thread:**
- Search for "bob" or find bob@example.com in the inbox
- Click on the thread to open the Thread Workspace

**Show the workspace layout:**
- Left pane: Email content with entity highlights (monetary amounts, ticket IDs, deadlines)
- Center pane: Thread timeline with sentiment indicators
- Right pane: Contact card and Classification summary

**Click the "Agent" tab:**
- Show the Agent Reasoning Panel with step-by-step trace
- Point out: Thought → Action → Observation for each step
- Show the tools used: search_knowledge_base, get_thread_history, get_contact_profile, escalate_to_human
- Show the Final Recommendation: "Escalate to human team"
- Show the escalation reason and draft reply

**Explain the agent logic:**
- "The agent read the full thread history (4 emails) before deciding"
- "It checked Bob's account status (Enterprise tier)"
- "It searched the SLA policy for credit obligations"
- "It recognized the legal threat and flagged for legal review"
- "It drafted an empathetic holding reply citing the SLA policy"
- "Finally, it escalated to human with a pre-filled brief"

### 3. RAG Retrieval Debug View (1-2 minutes)
**Navigate to the RAG tab:**
- Click on the "RAG Context" tab in the Thread Workspace
- Show the retrieved knowledge chunks
- Show: source document, heading, content preview, similarity score
- Explain: "These are real chunks from our internal knowledge base — pricing policy, SLA policy, refund policy, API docs, compliance FAQ, and escalation matrix"

**Show the debug endpoint:**
- Open a new tab to `http://localhost:8000/api/rag/search?q=refund+policy`
- Show the JSON response with retrieved chunks and similarity scores
- Explain: "The RAG pipeline uses sentence-transformers embeddings and in-memory numpy similarity search for this demo"

### 4. Karen Churn Scenario with Web Intelligence (2-3 minutes)
**Navigate to Karen's thread:**
- Search for "karen" or find karen@example.com
- Show the thread with 3+ emails showing escalating sentiment

**Show the Sentiment Trend:**
- Navigate to the Analytics Dashboard
- Show the Sentiment Trend chart for karen@example.com
- Point out the deteriorating sentiment line
- Show the At-Risk Accounts panel with Karen flagged

**Show Web Intelligence:**
- In the Thread Workspace, show the classification summary
- Point out: "The system detected the churn threat and the public review threat"
- Explain: "The agent retrieved the escalation matrix and refund policy, then suggested a retention offer"
- Show the suggested action in the Classification panel

### 5. Analytics Dashboard (1-2 minutes)
**Navigate to Analytics:**
- Click the "Analytics" tab in the navigation

**Show the charts:**
- Sentiment Trend line chart (showing data for alice, bob, karen)
- Category Distribution pie chart (showing Billing, Compliance, Security, General, etc.)
- Response Time Heatmap (showing processing times by hour of day)
- At-Risk Accounts panel (showing senders with negative sentiment)
- Agent Performance metrics (auto-reply rate, escalation rate, avg confidence, tools used)

**Show the stats cards:**
- Total Emails: 60+
- Total Threads: 30+
- Needs Human: [X]
- Auto-Replied: [X]
- Escalated: [X]
- Avg Confidence: [X]%
- Contacts: [X]

### 6. Key Features Summary (30 seconds)
**Closing:**
"To summarize what I've built:
- Real-time email ingestion with deduplication and schema validation
- Multi-layer intelligence: heuristic pre-filter → LLM classification with RAG grounding → autonomous agent
- RAG pipeline with 6 internal policy documents, chunked and embedded
- Sentiment trend tracking with deterioration detection
- Thread-based conversation context for the agent
- WebSocket real-time updates
- Full audit logging
- Production-ready backend with proper error handling and idempotency"

**Technical Stack:**
- Backend: FastAPI + SQLAlchemy async + SQLite
- AI: OpenRouter (meta-llama/llama-3.3-70b-instruct) + sentence-transformers embeddings
- Frontend: React + Tailwind CSS + Recharts
- Real-time: WebSocket with auto-reconnect
- RAG: In-memory numpy similarity (production would use Pinecone/Chroma)

**Trade-offs & Decisions:**
"I chose SQLite over PostgreSQL because it's zero-config and perfect for demos, but the schema is fully compatible with pgvector if needed. I used in-memory RAG for speed but implemented the chunking and embedding pipeline exactly as required. The agent uses ReAct-style reasoning with a max 6-step limit to prevent infinite loops."

## End of Demo

**Thank you for your time!**
