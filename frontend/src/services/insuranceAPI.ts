import axios from 'axios';

import type {
    APIResponse,
    ChatMessage,
    ChatSession,
    Claim,
    Customer,
    FraudAlert,
    InsurancePlan,
    PaginatedResponse,
    PaginationParams,
    PlanRecommendation,
    RiskAssessment,
} from '@/types/insurance';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8787/api/v1';

// Configure axios with default settings
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('givc_auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('givc_auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export class InsuranceAPIService {
  // Customer Service & Support APIs
  static async createChatSession(customerId: string, category: string): Promise<APIResponse<ChatSession>> {
    const response = await apiClient.post('/customer-support/chat/sessions', {
      customerId,
      category,
    });
    return response.data;
  }

  static async sendChatMessage(
    sessionId: string,
    message: string,
    type: 'text' | 'file' = 'text'
  ): Promise<APIResponse<ChatMessage>> {
    const response = await apiClient.post(`/customer-support/chat/sessions/${sessionId}/messages`, {
      content: message,
      type,
    });
    return response.data;
  }

  static async getChatSession(sessionId: string): Promise<APIResponse<ChatSession>> {
    const response = await apiClient.get(`/customer-support/chat/sessions/${sessionId}`);
    return response.data;
  }

  static async getChatSessions(
    customerId: string,
    params?: PaginationParams
  ): Promise<APIResponse<PaginatedResponse<ChatSession>>> {
    const response = await apiClient.get(`/customer-support/chat/customers/${customerId}/sessions`, {
      params,
    });
    return response.data;
  }

  static async escalateToHuman(sessionId: string, reason: string): Promise<APIResponse<ChatSession>> {
    const response = await apiClient.post(`/customer-support/chat/sessions/${sessionId}/escalate`, {
      reason,
    });
    return response.data;
  }

  static async rateChatSession(
    sessionId: string,
    rating: number,
    feedback?: string
  ): Promise<APIResponse<void>> {
    const response = await apiClient.post(`/customer-support/chat/sessions/${sessionId}/rate`, {
      rating,
      feedback,
    });
    return response.data;
  }

  // Claims Processing APIs
  static async submitClaim(claimData: Partial<Claim>): Promise<APIResponse<Claim>> {
    const response = await apiClient.post('/claims', claimData);
    return response.data;
  }

  static async getClaim(claimId: string): Promise<APIResponse<Claim>> {
    const response = await apiClient.get(`/claims/${claimId}`);
    return response.data;
  }

  static async getClaims(
    customerId?: string,
    params?: PaginationParams
  ): Promise<APIResponse<PaginatedResponse<Claim>>> {
    const response = await apiClient.get('/claims', {
      params: { customerId, ...params },
    });
    return response.data;
  }

  static async uploadClaimDocument(
    claimId: string,
    file: File,
    type: string
  ): Promise<APIResponse<{ documentId: string }>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);

    const response = await apiClient.post(`/claims/${claimId}/documents`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  static async processClaimWithAI(claimId: string): Promise<APIResponse<Claim>> {
    const response = await apiClient.post(`/claims/${claimId}/ai-process`);
    return response.data;
  }

  static async detectClaimFraud(claimId: string): Promise<APIResponse<FraudAlert[]>> {
    const response = await apiClient.post(`/claims/${claimId}/fraud-detection`);
    return response.data;
  }

  // Risk Assessment APIs
  static async performRiskAssessment(
    customerId: string,
    type: 'enrollment' | 'renewal' | 'claims_analysis'
  ): Promise<APIResponse<RiskAssessment>> {
    const response = await apiClient.post('/risk-assessment', {
      customerId,
      type,
    });
    return response.data;
  }

  static async getRiskAssessment(assessmentId: string): Promise<APIResponse<RiskAssessment>> {
    const response = await apiClient.get(`/risk-assessment/${assessmentId}`);
    return response.data;
  }

  static async getCustomerRiskHistory(
    customerId: string,
    params?: PaginationParams
  ): Promise<APIResponse<PaginatedResponse<RiskAssessment>>> {
    const response = await apiClient.get(`/risk-assessment/customer/${customerId}`, {
      params,
    });
    return response.data;
  }

  // Plan Recommendations APIs
  static async generatePlanRecommendations(customerId: string): Promise<APIResponse<PlanRecommendation>> {
    const response = await apiClient.post('/plan-recommendations', {
      customerId,
    });
    return response.data;
  }

  static async getPlanRecommendations(customerId: string): Promise<APIResponse<PlanRecommendation[]>> {
    const response = await apiClient.get(`/plan-recommendations/customer/${customerId}`);
    return response.data;
  }

  static async comparePlans(planIds: string[]): Promise<APIResponse<InsurancePlan[]>> {
    const response = await apiClient.post('/plans/compare', {
      planIds,
    });
    return response.data;
  }

  static async getAvailablePlans(
    customerId?: string,
    params?: PaginationParams
  ): Promise<APIResponse<PaginatedResponse<InsurancePlan>>> {
    const response = await apiClient.get('/plans', {
      params: { customerId, ...params },
    });
    return response.data;
  }

  // Customer Management APIs
  static async getCustomer(customerId: string): Promise<APIResponse<Customer>> {
    const response = await apiClient.get(`/customers/${customerId}`);
    return response.data;
  }

  static async updateCustomer(customerId: string, updates: Partial<Customer>): Promise<APIResponse<Customer>> {
    const response = await apiClient.put(`/customers/${customerId}`, updates);
    return response.data;
  }

  static async getCustomerProfile(customerId: string): Promise<APIResponse<Customer>> {
    const response = await apiClient.get(`/customers/${customerId}/profile`);
    return response.data;
  }

  // Document Processing APIs
  static async extractDocumentData(file: File): Promise<APIResponse<Record<string, any>>> {
    const formData = new FormData();
    formData.append('document', file);

    const response = await apiClient.post('/documents/extract', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  static async validateMedicalDocument(
    file: File,
    expectedType: string
  ): Promise<APIResponse<{ valid: boolean; confidence: number; issues: string[] }>> {
    const formData = new FormData();
    formData.append('document', file);
    formData.append('expectedType', expectedType);

    const response = await apiClient.post('/documents/validate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  // Analytics APIs
  static async getAnalyticsDashboard(
    customerId?: string,
    dateRange?: { start: string; end: string }
  ): Promise<APIResponse<any>> {
    const response = await apiClient.get('/analytics/dashboard', {
      params: { customerId, ...dateRange },
    });
    return response.data;
  }

  static async getFraudAlerts(params?: PaginationParams): Promise<APIResponse<PaginatedResponse<FraudAlert>>> {
    const response = await apiClient.get('/analytics/fraud-alerts', {
      params,
    });
    return response.data;
  }

  // Compliance APIs
  static async runComplianceCheck(type?: string): Promise<APIResponse<any>> {
    const response = await apiClient.post('/compliance/check', { type });
    return response.data;
  }

  static async getComplianceReports(params?: PaginationParams): Promise<APIResponse<PaginatedResponse<any>>> {
    const response = await apiClient.get('/compliance/reports', {
      params,
    });
    return response.data;
  }

  // Health Education APIs
  static async getEducationalContent(
    category?: string,
    customerId?: string,
    params?: PaginationParams
  ): Promise<APIResponse<PaginatedResponse<any>>> {
    const response = await apiClient.get('/education/content', {
      params: { category, customerId, ...params },
    });
    return response.data;
  }

  static async getPersonalizedContent(customerId: string): Promise<APIResponse<any[]>> {
    const response = await apiClient.get(`/education/personalized/${customerId}`);
    return response.data;
  }

  static async trackContentEngagement(
    contentId: string,
    action: 'view' | 'complete' | 'share' | 'rate',
    data?: any
  ): Promise<APIResponse<void>> {
    const response = await apiClient.post(`/education/content/${contentId}/track`, {
      action,
      data,
    });
    return response.data;
  }
}

export default InsuranceAPIService;
