// CredX AI API Service
const API_BASE = '/api/v1';

let authToken = localStorage.getItem('credx_token') || '';
let currentUser = JSON.parse(localStorage.getItem('credx_user') || 'null');

async function fetchWithAuth(url, options = {}) {
  const headers = options.headers || {};
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }
  if (!headers['Content-Type'] && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers
  });

  if (response.status === 401) {
    console.warn("Session expired or unauthorized. Logging in with demo credentials...");
  }

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'API Error' }));
    throw new Error(errorData.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

const CredXAPI = {
  async login(email, password) {
    const data = await fetchWithAuth('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
    authToken = data.access_token;
    currentUser = data.user;
    localStorage.setItem('credx_token', authToken);
    localStorage.setItem('credx_user', JSON.stringify(currentUser));
    return data;
  },

  getCurrentUser() {
    return currentUser;
  },

  async getPortfolioSummary() {
    return fetchWithAuth('/analytics/portfolio-summary');
  },

  async listApplications(search = '', status = '') {
    let query = '?limit=100';
    if (search) query += `&search=${encodeURIComponent(search)}`;
    if (status) query += `&status_filter=${encodeURIComponent(status)}`;
    return fetchWithAuth(`/applications/${query}`);
  },

  async getApplication(id) {
    return fetchWithAuth(`/applications/${id}`);
  },

  async createApplication(payload) {
    return fetchWithAuth('/applications/', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async assessApplication(id) {
    return fetchWithAuth(`/assessment/${id}/assess`, {
      method: 'POST'
    });
  },

  async getAssessment(id) {
    return fetchWithAuth(`/assessment/${id}`);
  },

  async simulateWhatIf(payload) {
    return fetchWithAuth('/assessment/simulate-what-if', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async submitUnderwriterDecision(id, payload) {
    return fetchWithAuth(`/underwriting/${id}/decide`, {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  },

  async getFairnessReport() {
    return fetchWithAuth('/fairness/audit-report');
  },

  async getModelMetadata() {
    return fetchWithAuth('/model-ops/metadata');
  },

  async getAuditLogs() {
    return fetchWithAuth('/audit/logs?limit=50');
  }
};

