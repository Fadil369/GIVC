/**
 * GIVC Healthcare Platform - Test Setup
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Global test configuration and setup
 */

import { expect, afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom';
import * as matchers from '@testing-library/jest-dom/matchers';

// Extend Vitest matchers
expect.extend(matchers);

// Cleanup after each test
afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

// Mock environment variables for testing
vi.mock('import.meta', () => ({
  env: {
    MODE: 'test',
    VITE_API_URL: 'https://api.test.givc.local',
    VITE_CLOUDFLARE_ACCOUNT_ID: 'test-account-id',
    VITE_HIPAA_COMPLIANCE_LEVEL: 'full',
    VITE_ENABLE_AI_AGENTS: 'true',
    VITE_ENABLE_MEDIVAULT: 'true',
    VITE_ENABLE_AUDIT_LOGGING: 'true',
    VITE_LOG_LEVEL: 'debug',
    DEV: false,
    PROD: false,
  },
}));

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
  takeRecords() {
    return [];
  }
};

// Mock ResizeObserver
global.ResizeObserver = class ResizeObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  unobserve() {}
};

// Mock fetch for API tests
global.fetch = vi.fn();

// Console suppression for cleaner test output
const originalError = console.error;
const originalWarn = console.warn;

beforeAll(() => {
  console.error = (...args: any[]) => {
    // Suppress React act() warnings and other expected errors
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('act(') ||
        args[0].includes('Not implemented: HTMLFormElement.prototype.submit') ||
        args[0].includes('Error: Could not parse CSS stylesheet'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };

  console.warn = (...args: any[]) => {
    // Suppress expected warnings
    if (
      typeof args[0] === 'string' &&
      args[0].includes('componentWillReceiveProps')
    ) {
      return;
    }
    originalWarn.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
  console.warn = originalWarn;
});

// Custom test utilities
export const testUtils = {
  /**
   * Wait for async operations
   */
  wait: (ms: number = 0) => new Promise((resolve) => setTimeout(resolve, ms)),

  /**
   * Mock successful API response
   */
  mockApiSuccess: (data: any) => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => data,
      headers: new Headers(),
    });
  },

  /**
   * Mock API error response
   */
  mockApiError: (status: number = 500, message: string = 'Server Error') => {
    (global.fetch as any).mockResolvedValueOnce({
      ok: false,
      status,
      json: async () => ({ error: message }),
      headers: new Headers(),
    });
  },

  /**
   * Create mock PHI data for testing
   * (with sanitization markers)
   */
  createMockPHI: () => ({
    patientId: 'TEST-001',
    firstName: 'John',
    lastName: 'Doe',
    ssn: '***-**-****', // Pre-sanitized
    dob: '****-**-**', // Pre-sanitized
    email: 'j***@test.com', // Pre-sanitized
    phone: '***-***-****', // Pre-sanitized
    medicalRecordNumber: 'MRN-TEST-001',
  }),
};
