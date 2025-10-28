/**
 * OASIS API Client
 * Frontend integration with FastAPI backend for NPHIES claims processing
 */

import axios, { AxiosInstance, AxiosError } from 'axios';

// Types
export interface HealthStatus {
  status: string;
  timestamp: string;
  version: string;
  environment: string;
  services: Record<string, boolean>;
}

export interface EligibilityCheckRequest {
  member_id: string;
  payer_id: string;
  service_date?: string;
}

export interface EligibilityResponse {
  eligible: boolean;
  member_id: string;
  coverage_status: string;
  benefits?: any;
  message?: string;
}

export interface ClaimSubmission {
  claim_id: string;
  patient_id: string;
  provider_id: string;
  payer_id: string;
  service_date: string;
  diagnosis_codes: string[];
  procedure_codes: string[];
  total_amount: number;
  attachments?: string[];
}

export interface ClaimResponse {
  claim_id: string;
  status: string;
  submission_date: string;
  outcome?: string;
  message?: string;
  reference_number?: string;
}

export interface PriorAuthRequest {
  patient_id: string;
  provider_id: string;
  payer_id: string;
  service_type: string;
  diagnosis_codes: string[];
  procedure_codes: string[];
  requested_date: string;
  clinical_notes?: string;
}

export interface PriorAuthResponse {
  authorization_id: string;
  status: string;
  approval_number?: string;
  valid_until?: string;
  message?: string;
}

export interface AnalyticsDashboard {
  period: string;
  total_claims: number;
  approved_claims: number;
  rejected_claims: number;
  pending_claims: number;
  total_amount: number;
  approval_rate: number;
  rejection_reasons: Record<string, number>;
  trends: Record<string, any>;
}

export interface ApiError {
  error: boolean;
  message: string;
  detail?: string;
  timestamp: string;
}

// API Client Class
class OASISApiClient {
  private client: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = import.meta.env.VITE_OASIS_API_URL || 'http://localhost:8000';
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if available
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<ApiError>) => {
        if (error.response) {
          // Server responded with error
          const apiError = error.response.data;
          console.error('API Error:', apiError);
          return Promise.reject(apiError);
        } else if (error.request) {
          // Request made but no response
          console.error('Network Error:', error.message);
          return Promise.reject({
            error: true,
            message: 'Network error - unable to reach server',
            timestamp: new Date().toISOString(),
          });
        } else {
          // Something else happened
          console.error('Error:', error.message);
          return Promise.reject({
            error: true,
            message: error.message,
            timestamp: new Date().toISOString(),
          });
        }
      }
    );
  }

  // ==========================================================================
  // System Endpoints
  // ==========================================================================

  async getHealth(): Promise<HealthStatus> {
    const response = await this.client.get<HealthStatus>('/api/health');
    return response.data;
  }

  async getRootInfo() {
    const response = await this.client.get('/');
    return response.data;
  }

  // ==========================================================================
  // Eligibility Endpoints
  // ==========================================================================

  async checkEligibility(request: EligibilityCheckRequest): Promise<EligibilityResponse> {
    const response = await this.client.post<EligibilityResponse>(
      '/api/eligibility/check',
      request
    );
    return response.data;
  }

  // ==========================================================================
  // Claims Endpoints
  // ==========================================================================

  async submitClaim(claim: ClaimSubmission): Promise<ClaimResponse> {
    const response = await this.client.post<ClaimResponse>(
      '/api/claims/submit',
      claim
    );
    return response.data;
  }

  async getClaimStatus(claimId: string): Promise<ClaimResponse> {
    const response = await this.client.get<ClaimResponse>(
      `/api/claims/${claimId}`
    );
    return response.data;
  }

  async listClaims(params?: {
    status_filter?: string;
    from_date?: string;
    to_date?: string;
    limit?: number;
  }) {
    const response = await this.client.get('/api/claims', { params });
    return response.data;
  }

  // ==========================================================================
  // Prior Authorization Endpoints
  // ==========================================================================

  async requestPriorAuth(request: PriorAuthRequest): Promise<PriorAuthResponse> {
    const response = await this.client.post<PriorAuthResponse>(
      '/api/prior-auth/request',
      request
    );
    return response.data;
  }

  async getPriorAuthStatus(authId: string) {
    const response = await this.client.get(`/api/prior-auth/${authId}`);
    return response.data;
  }

  // ==========================================================================
  // Analytics Endpoints
  // ==========================================================================

  async getAnalyticsDashboard(params?: {
    period?: string;
    provider_id?: string;
  }): Promise<AnalyticsDashboard> {
    const response = await this.client.get<AnalyticsDashboard>(
      '/api/analytics/dashboard',
      { params }
    );
    return response.data;
  }

  async getRejectionAnalysis(params?: {
    from_date?: string;
    to_date?: string;
  }) {
    const response = await this.client.get('/api/analytics/rejections', { params });
    return response.data;
  }

  async getTrends(params?: {
    metric?: string;
    period?: string;
  }) {
    const response = await this.client.get('/api/analytics/trends', { params });
    return response.data;
  }
}

// Export singleton instance
export const oasisApi = new OASISApiClient();

// Export individual functions for convenience
export default oasisApi;
