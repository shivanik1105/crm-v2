import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';
const WS_BASE = import.meta.env.VITE_WS_URL || `ws://${window.location.hostname}:8000`;

const client = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const api = {
  ingestEmail: (data) => client.post('/ingest', data),
  getJobStatus: (jobId) => client.get(`/status/${jobId}`),

  getEmails: (params = {}) => client.get('/emails/', { params }),
  getEmail: (emailId) => client.get(`/emails/${emailId}`),
  getEmailReasoning: (emailId) => client.get(`/emails/${emailId}/reasoning`),
  getEmailRAGContext: (emailId) => client.get(`/emails/${emailId}/rag-context`),

  getThread: (email) => client.get(`/threads/${email}`),

  respond: (emailId) => client.post(`/respond/${emailId}`),
  updateDraft: (emailId, draft) => client.patch(`/respond/drafts/${emailId}`, { draft_body: draft }),
  approveDraft: (emailId) => client.post(`/respond/drafts/${emailId}/approve`),

  getSentimentTrend: (sender, days = 30) => client.get('/analytics/sentiment-trend', { params: { sender, days } }),
  getCategoryDistribution: () => client.get('/analytics/category-distribution'),
  getAtRiskAccounts: () => client.get('/analytics/at-risk'),
  getAgentPerformance: () => client.get('/analytics/agent-performance'),
  getResponseTimeHeatmap: () => client.get('/analytics/response-time-heatmap'),

  searchRAG: (q, topK = 3) => client.get('/rag/search', { params: { q, top_k: topK } }),

  getReputation: (companyName) => client.get('/intelligence/reputation', { params: { company_name: companyName } }),

  dryRunAgent: (emailId) => client.post(`/agent/dry-run/${emailId}`),

  getContact: (email) => client.get(`/contacts/${email}`),
  updateContact: (email, updates) => client.patch(`/contacts/${email}`, updates),

  getDashboardStats: () => client.get('/dashboard/stats'),

  getAuditLog: (entityType, entityId) => client.get(`/audit/${entityType}/${entityId}`),

  bulkMarkSpam: (emailIds) => client.post('/emails/bulk/spam', { email_ids: emailIds }),
  bulkAssign: (emailIds, assignee) => client.post('/emails/bulk/assign', { email_ids: emailIds, assignee }),
  bulkArchive: (emailIds) => client.post('/emails/bulk/archive', { email_ids: emailIds }),

  getThreadSummary: (email) => client.get(`/threads/${email}/summary`),
};

export class WebSocketClient {
  constructor() {
    this.ws = null;
    this.listeners = {};
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 1000;
  }

  connect() {
    try {
      this.ws = new WebSocket(`${WS_BASE}/ws`);

      this.ws.onopen = () => {
        console.log('[WS] Connected');
        this.reconnectAttempts = 0;
        this._emit('connected', {});
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this._emit(message.type, message.data);
          this._emit('*', message);
        } catch (e) {
          console.error('[WS] Parse error:', e);
        }
      };

      this.ws.onclose = () => {
        console.log('[WS] Disconnected');
        this._emit('disconnected', {});
        this._attemptReconnect();
      };

      this.ws.onerror = (error) => {
        console.error('[WS] Error:', error);
        this._emit('error', error);
      };
    } catch (e) {
      console.error('[WS] Connection failed:', e);
      this._attemptReconnect();
    }
  }

  _attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      setTimeout(() => this.connect(), delay);
    }
  }

  on(event, callback) {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
    return () => {
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    };
  }

  _emit(event, data) {
    if (this.listeners[event]) {
      this.listeners[event].forEach(cb => cb(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export const wsClient = new WebSocketClient();

export default client;
