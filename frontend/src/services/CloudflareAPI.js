// GIVC Platform Cloudflare Workers API Integration
const API_BASE_URL = import.meta.env.PROD 
  ? 'https://api.givc.workers.dev' 
  : 'http://localhost:8787';

class CloudflareAPI {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.headers = {
      'Content-Type': 'application/json',
      'X-GIVC-Platform': 'frontend'
    };
  }

  // Set authentication token
  setAuthToken(token) {
    this.headers['Authorization'] = `Bearer ${token}`;
  }

  // Generic API request handler
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const config = {
      method: 'GET',
      headers: { ...this.headers },
      ...options
    };

    if (options.body && typeof options.body === 'object') {
      config.body = JSON.stringify(options.body);
    }

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      } else {
        return await response.text();
      }
    } catch (error) {
      logger.error('Cloudflare API Request Failed:', error);
      throw error;
    }
  }

  // Document Management (R2 + KV Integration)
  async uploadDocument(file, metadata = {}) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify({
      ...metadata,
      uploadedAt: new Date().toISOString(),
      platform: 'givc-frontend'
    }));

    return this.request('/api/documents/upload', {
      method: 'POST',
      headers: {
        'Authorization': this.headers['Authorization'],
        'X-GIVC-Platform': 'frontend'
        // Don't set Content-Type for FormData
      },
      body: formData
    });
  }

  async getDocuments(params = {}) {
    const queryParams = new URLSearchParams(params);
    return this.request(`/api/documents?${queryParams}`);
  }

  async getDocument(documentId) {
    return this.request(`/api/documents/${documentId}`);
  }

  async deleteDocument(documentId) {
    return this.request(`/api/documents/${documentId}`, {
      method: 'DELETE'
    });
  }

  async updateDocumentMetadata(documentId, metadata) {
    return this.request(`/api/documents/${documentId}/metadata`, {
      method: 'PUT',
      body: metadata
    });
  }

  // Claims Processing Integration
  async submitClaim(claimData) {
    return this.request('/api/claims/submit', {
      method: 'POST',
      body: {
        ...claimData,
        submittedAt: new Date().toISOString(),
        source: 'givc-platform'
      }
    });
  }

  async getClaims(filters = {}) {
    const queryParams = new URLSearchParams(filters);
    return this.request(`/api/claims?${queryParams}`);
  }

  async getClaim(claimId) {
    return this.request(`/api/claims/${claimId}`);
  }

  async processClaimWithAI(claimId) {
    return this.request(`/api/claims/${claimId}/ai-process`, {
      method: 'POST'
    });
  }

  async updateClaimStatus(claimId, status, notes = '') {
    return this.request(`/api/claims/${claimId}/status`, {
      method: 'PUT',
      body: { status, notes, updatedAt: new Date().toISOString() }
    });
  }

  // Risk Assessment Engine
  async performRiskAssessment(patientData) {
    return this.request('/api/risk-assessment/analyze', {
      method: 'POST',
      body: {
        ...patientData,
        assessmentDate: new Date().toISOString(),
        platform: 'givc'
      }
    });
  }

  async getRiskAssessments(patientId) {
    return this.request(`/api/risk-assessment/patient/${patientId}`);
  }

  async getRiskTrends(timeframe = '30d') {
    return this.request(`/api/risk-assessment/trends?timeframe=${timeframe}`);
  }

  // AI Customer Support Integration
  async submitSupportRequest(requestData) {
    return this.request('/api/support/submit', {
      method: 'POST',
      body: {
        ...requestData,
        timestamp: new Date().toISOString(),
        platform: 'givc-frontend'
      }
    });
  }

  async getSupportTickets(filters = {}) {
    const queryParams = new URLSearchParams(filters);
    return this.request(`/api/support/tickets?${queryParams}`);
  }

  async chatWithAI(message, conversationId = null) {
    return this.request('/api/support/ai-chat', {
      method: 'POST',
      body: {
        message,
        conversationId,
        timestamp: new Date().toISOString(),
        language: localStorage.getItem('givc-language') || 'en'
      }
    });
  }

  // AI Triage Services
  async performTriage(symptoms, patientInfo = {}) {
    return this.request('/api/triage/assess', {
      method: 'POST',
      body: {
        symptoms,
        patientInfo,
        timestamp: new Date().toISOString(),
        language: localStorage.getItem('givc-language') || 'en'
      }
    });
  }

  async getTriageHistory(patientId) {
    return this.request(`/api/triage/history/${patientId}`);
  }

  // GraphQL RAG Services
  async queryWithRAG(query, context = {}) {
    return this.request('/api/graphql/rag', {
      method: 'POST',
      body: {
        query: `
          query GIVCSearch($input: String!, $context: JSON) {
            ragSearch(input: $input, context: $context) {
              results {
                id
                content
                relevanceScore
                source
                metadata
              }
              totalResults
              processingTime
            }
          }
        `,
        variables: {
          input: query,
          context: {
            ...context,
            platform: 'givc',
            language: localStorage.getItem('givc-language') || 'en'
          }
        }
      }
    });
  }

  async getSchemaInfo() {
    return this.request('/api/graphql/schema');
  }

  // KV Namespace Operations
  async getKVData(namespace, key) {
    return this.request(`/api/kv/${namespace}/${key}`);
  }

  async setKVData(namespace, key, value, metadata = {}) {
    return this.request(`/api/kv/${namespace}/${key}`, {
      method: 'PUT',
      body: {
        value,
        metadata: {
          ...metadata,
          updatedAt: new Date().toISOString(),
          platform: 'givc'
        }
      }
    });
  }

  async deleteKVData(namespace, key) {
    return this.request(`/api/kv/${namespace}/${key}`, {
      method: 'DELETE'
    });
  }

  async listKVKeys(namespace, prefix = '') {
    const queryParams = new URLSearchParams({ prefix });
    return this.request(`/api/kv/${namespace}/keys?${queryParams}`);
  }

  // Analytics and Monitoring
  async getAnalytics(type, timeframe = '24h') {
    return this.request(`/api/analytics/${type}?timeframe=${timeframe}`);
  }

  async getSystemHealth() {
    return this.request('/api/health');
  }

  async getMetrics(service) {
    return this.request(`/api/metrics/${service}`);
  }

  // User Management Integration
  async getCurrentUser() {
    return this.request('/api/user/profile');
  }

  async updateUserProfile(profileData) {
    return this.request('/api/user/profile', {
      method: 'PUT',
      body: profileData
    });
  }

  async getUserPreferences() {
    return this.request('/api/user/preferences');
  }

  async updateUserPreferences(preferences) {
    return this.request('/api/user/preferences', {
      method: 'PUT',
      body: preferences
    });
  }

  // Real-time Notifications (Server-Sent Events)
  createEventStream(channel) {
    const url = `${this.baseURL}/api/events/${channel}`;
    const eventSource = new EventSource(url, {
      headers: this.headers
    });
    
    return eventSource;
  }

  // Batch Operations
  async batchRequest(requests) {
    return this.request('/api/batch', {
      method: 'POST',
      body: {
        requests,
        timestamp: new Date().toISOString()
      }
    });
  }
}

// Create singleton instance
const cloudflareAPI = new CloudflareAPI();

// Export both the class and instance
export { CloudflareAPI };
export default cloudflareAPI;
