import axios, { AxiosError } from 'axios';
import { getConfig } from '@/config/validateEnv';
import { logger } from './logger';
import type { FollowUpFilters, FollowUpSnapshot } from '@/types/followUp';

const config = getConfig();
const baseURL = config.api.baseUrl || 'http://localhost:8000';
const timeout = config.api.timeout || 30000;

const client = axios.create({
  baseURL,
  timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

client.interceptors.request.use((req) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    req.headers = req.headers ?? {};
    req.headers.Authorization = `Bearer ${token}`;
  }
  return req;
});

client.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const message = error.response?.data ?? error.message;
    logger.error('Follow-up API request failed', {
      status: error.response?.status,
      message,
    });
    return Promise.reject(error);
  }
);

const buildQueryParams = (filters: FollowUpFilters = {}) => {
  const params = new URLSearchParams();
  const { includeNonAlerts = true, priority, branch, status, shouldAlert } = filters;

  params.set('include_non_alerts', String(includeNonAlerts));

  if (priority) {
    params.set('priority', priority);
  }

  if (branch) {
    params.set('branch', branch);
  }

  if (status) {
    params.set('status', status);
  }

  if (typeof shouldAlert === 'boolean') {
    params.set('should_alert', String(shouldAlert));
  }

  return params;
};

export async function getFollowUpSnapshot(filters: FollowUpFilters = {}): Promise<FollowUpSnapshot> {
  const params = buildQueryParams(filters);
  const response = await client.get<FollowUpSnapshot>('/api/follow-ups', { params });
  return response.data;
}
