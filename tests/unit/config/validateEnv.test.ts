/**
 * GIVC Healthcare Platform - Environment Validation Tests
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Unit tests for validateEnv.js - Critical HIPAA component
 * Target Coverage: 90%+
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { validateEnvironment, getConfig, isFeatureEnabled } from '@/config/validateEnv';

describe('Environment Validation', () => {
  describe('validateEnvironment()', () => {
    it('should pass validation with all required variables', () => {
      const result = validateEnvironment();
      
      expect(result.isValid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should detect missing critical environment variables', () => {
      // Mock missing env vars
      const originalEnv = import.meta.env;
      vi.stubGlobal('import.meta', {
        env: {
          ...originalEnv,
          VITE_API_URL: undefined,
          VITE_CLOUDFLARE_ACCOUNT_ID: undefined,
        },
      });

      const result = validateEnvironment();
      
      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
      expect(result.errors.some(e => e.includes('VITE_API_URL'))).toBe(true);
      
      // Restore
      vi.stubGlobal('import.meta', { env: originalEnv });
    });

    it('should validate HIPAA compliance level', () => {
      const originalEnv = import.meta.env;
      vi.stubGlobal('import.meta', {
        env: {
          ...originalEnv,
          VITE_HIPAA_COMPLIANCE_LEVEL: 'invalid-level',
        },
      });

      const result = validateEnvironment();
      
      expect(result.warnings.some(w => w.includes('HIPAA'))).toBe(true);
      
      // Restore
      vi.stubGlobal('import.meta', { env: originalEnv });
    });

    it('should provide helpful error messages', () => {
      const originalEnv = import.meta.env;
      vi.stubGlobal('import.meta', {
        env: {
          MODE: 'test',
        },
      });

      const result = validateEnvironment();
      
      result.errors.forEach(error => {
        expect(error).toMatch(/VITE_/);
        expect(error.length).toBeGreaterThan(10);
      });
      
      // Restore
      vi.stubGlobal('import.meta', { env: originalEnv });
    });
  });

  describe('getConfig()', () => {
    it('should return configuration object', () => {
      const config = getConfig();
      
      expect(config).toBeDefined();
      expect(config).toHaveProperty('VITE_API_URL');
      expect(config).toHaveProperty('VITE_CLOUDFLARE_ACCOUNT_ID');
      expect(config).toHaveProperty('VITE_HIPAA_COMPLIANCE_LEVEL');
    });

    it('should return string values for all configs', () => {
      const config = getConfig();
      
      Object.values(config).forEach(value => {
        expect(typeof value).toBe('string');
      });
    });

    it('should handle missing values gracefully', () => {
      const config = getConfig();
      
      // Should not throw
      expect(() => config.VITE_API_URL).not.toThrow();
    });
  });

  describe('isFeatureEnabled()', () => {
    it('should return true for enabled features', () => {
      const originalEnv = import.meta.env;
      vi.stubGlobal('import.meta', {
        env: {
          ...originalEnv,
          VITE_ENABLE_AI_AGENTS: 'true',
        },
      });

      expect(isFeatureEnabled('VITE_ENABLE_AI_AGENTS')).toBe(true);
      
      // Restore
      vi.stubGlobal('import.meta', { env: originalEnv });
    });

    it('should return false for disabled features', () => {
      const originalEnv = import.meta.env;
      vi.stubGlobal('import.meta', {
        env: {
          ...originalEnv,
          VITE_ENABLE_AI_AGENTS: 'false',
        },
      });

      expect(isFeatureEnabled('VITE_ENABLE_AI_AGENTS')).toBe(false);
      
      // Restore
      vi.stubGlobal('import.meta', { env: originalEnv });
    });

    it('should return false for missing features', () => {
      expect(isFeatureEnabled('VITE_NONEXISTENT_FEATURE')).toBe(false);
    });

    it('should handle case-insensitive values', () => {
      const originalEnv = import.meta.env;
      vi.stubGlobal('import.meta', {
        env: {
          ...originalEnv,
          VITE_TEST_FEATURE: 'TRUE',
        },
      });

      expect(isFeatureEnabled('VITE_TEST_FEATURE')).toBe(true);
      
      // Restore
      vi.stubGlobal('import.meta', { env: originalEnv });
    });
  });

  describe('HIPAA Compliance Validation', () => {
    it('should validate full HIPAA compliance level', () => {
      const originalEnv = import.meta.env;
      vi.stubGlobal('import.meta', {
        env: {
          ...originalEnv,
          VITE_HIPAA_COMPLIANCE_LEVEL: 'full',
        },
      });

      const result = validateEnvironment();
      expect(result.isValid).toBe(true);
      
      // Restore
      vi.stubGlobal('import.meta', { env: originalEnv });
    });

    it('should warn on partial HIPAA compliance', () => {
      const originalEnv = import.meta.env;
      vi.stubGlobal('import.meta', {
        env: {
          ...originalEnv,
          VITE_HIPAA_COMPLIANCE_LEVEL: 'partial',
        },
      });

      const result = validateEnvironment();
      expect(result.warnings.length).toBeGreaterThan(0);
      
      // Restore
      vi.stubGlobal('import.meta', { env: originalEnv });
    });

    it('should require audit logging for HIPAA', () => {
      const originalEnv = import.meta.env;
      vi.stubGlobal('import.meta', {
        env: {
          ...originalEnv,
          VITE_HIPAA_COMPLIANCE_LEVEL: 'full',
          VITE_ENABLE_AUDIT_LOGGING: 'false',
        },
      });

      const result = validateEnvironment();
      expect(result.errors.some(e => e.includes('audit'))).toBe(true);
      
      // Restore
      vi.stubGlobal('import.meta', { env: originalEnv });
    });
  });

  describe('Production vs Development', () => {
    it('should have stricter validation in production', () => {
      const originalEnv = import.meta.env;
      vi.stubGlobal('import.meta', {
        env: {
          ...originalEnv,
          MODE: 'production',
          VITE_API_URL: '',
        },
      });

      const result = validateEnvironment();
      expect(result.errors.length).toBeGreaterThan(0);
      
      // Restore
      vi.stubGlobal('import.meta', { env: originalEnv });
    });

    it('should allow missing optional vars in development', () => {
      const originalEnv = import.meta.env;
      vi.stubGlobal('import.meta', {
        env: {
          ...originalEnv,
          MODE: 'development',
          VITE_ANALYTICS_ID: '',
        },
      });

      const result = validateEnvironment();
      // Should not error on optional vars in dev
      expect(result.isValid).toBe(true);
      
      // Restore
      vi.stubGlobal('import.meta', { env: originalEnv });
    });
  });
});
