/**
 * NeoStats Platform API Client
 * Clean fetch wrapper for FastAPI backend endpoints
 */

const API_BASE = '/api';

const api = {
  async getOverview() {
    const res = await fetch(`${API_BASE}/overview`);
    if (!res.ok) throw new Error(`Failed to fetch overview: ${res.statusText}`);
    return await res.json();
  },

  async getEDAInsights() {
    const res = await fetch(`${API_BASE}/eda/insights`);
    if (!res.ok) throw new Error(`Failed to fetch insights: ${res.statusText}`);
    return await res.json();
  },

  async getEDACategories() {
    const res = await fetch(`${API_BASE}/eda/categories`);
    if (!res.ok) throw new Error(`Failed to fetch categories: ${res.statusText}`);
    return await res.json();
  },

  async getEDADataQuality() {
    const res = await fetch(`${API_BASE}/eda/data-quality`);
    if (!res.ok) throw new Error(`Failed to fetch data quality: ${res.statusText}`);
    return await res.json();
  },

  async getEDAPortfolio() {
    const res = await fetch(`${API_BASE}/eda/portfolio`);
    if (!res.ok) throw new Error(`Failed to fetch portfolio: ${res.statusText}`);
    return await res.json();
  },

  async getRiskPresets() {
    const res = await fetch(`${API_BASE}/risk/presets`);
    if (!res.ok) throw new Error(`Failed to fetch presets: ${res.statusText}`);
    return await res.json();
  },

  async getRiskSamples() {
    const res = await fetch(`${API_BASE}/risk/samples`);
    if (!res.ok) throw new Error(`Failed to fetch samples: ${res.statusText}`);
    return await res.json();
  },

  async lookupApplicant(skId) {
    const res = await fetch(`${API_BASE}/risk/lookup/${skId}`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `Applicant ID ${skId} not found`);
    }
    return await res.json();
  },

  async evaluateRisk(payload) {
    const res = await fetch(`${API_BASE}/risk/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Risk assessment failed');
    }
    return await res.json();
  },

  async getDecisionRules(filter = 'all') {
    const url = filter && filter !== 'all' ? `${API_BASE}/rules?risk=${filter}` : `${API_BASE}/rules`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to fetch rules: ${res.statusText}`);
    return await res.json();
  },

  async getChatSamples() {
    const res = await fetch(`${API_BASE}/chat/samples`);
    if (!res.ok) throw new Error(`Failed to fetch samples: ${res.statusText}`);
    return await res.json();
  },

  async sendChatMessage(question, sessionId = null) {
    const payload = { question };
    if (sessionId) payload.session_id = sessionId;
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Chat query failed');
    }
    return await res.json();
  },

  async clearChat(sessionId = null) {
    const payload = sessionId ? { session_id: sessionId } : {};
    const res = await fetch(`${API_BASE}/chat/clear`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Clear chat failed');
    }
    return await res.json();
  }
};
