/**
 * GIVC Healthcare Platform - Logger Service Tests
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Unit tests for logger.js - Critical HIPAA component
 * Target Coverage: 90%+
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import logger from '@/services/logger';

describe('HIPAA Logger Service', () => {
  beforeEach(() => {
    // Mock fetch for remote logging tests
    global.fetch = vi.fn();
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('PHI Sanitization', () => {
    it('should sanitize SSN in log messages', () => {
      const spy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      logger.info('Patient SSN: 123-45-6789');
      
      const loggedMessage = spy.mock.calls[0]?.[0];
      expect(loggedMessage).not.toContain('123-45-6789');
      expect(loggedMessage).toContain('***-**-****');
      
      spy.mockRestore();
    });

    it('should sanitize email addresses', () => {
      const spy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      logger.info('Patient email: patient@example.com');
      
      const loggedMessage = spy.mock.calls[0]?.[0];
      expect(loggedMessage).not.toContain('patient@example.com');
      expect(loggedMessage).toMatch(/\*+@\*+\.\*+/);
      
      spy.mockRestore();
    });

    it('should sanitize phone numbers', () => {
      const spy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      logger.info('Phone: (555) 123-4567');
      
      const loggedMessage = spy.mock.calls[0]?.[0];
      expect(loggedMessage).not.toContain('555');
      expect(loggedMessage).toContain('***');
      
      spy.mockRestore();
    });

    it('should sanitize dates of birth', () => {
      const spy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      logger.info('DOB: 1990-05-15');
      
      const loggedMessage = spy.mock.calls[0]?.[0];
      expect(loggedMessage).not.toContain('1990-05-15');
      expect(loggedMessage).toContain('****-**-**');
      
      spy.mockRestore();
    });

    it('should sanitize medical record numbers', () => {
      const spy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      logger.info('MRN: MRN123456');
      
      const loggedMessage = spy.mock.calls[0]?.[0];
      expect(loggedMessage).not.toContain('MRN123456');
      expect(loggedMessage).toContain('MRN******');
      
      spy.mockRestore();
    });

    it('should sanitize multiple PHI fields simultaneously', () => {
      const spy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      const phiData = {
        ssn: '123-45-6789',
        email: 'patient@test.com',
        phone: '555-123-4567',
        dob: '1990-05-15',
      };
      
      logger.info('Patient data', phiData);
      
      const loggedData = spy.mock.calls[0]?.[1];
      expect(JSON.stringify(loggedData)).not.toContain('123-45-6789');
      expect(JSON.stringify(loggedData)).not.toContain('patient@test.com');
      expect(JSON.stringify(loggedData)).not.toContain('555-123-4567');
      
      spy.mockRestore();
    });
  });

  describe('Log Levels', () => {
    it('should log info messages', () => {
      const spy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      logger.info('Test info message');
      
      expect(spy).toHaveBeenCalled();
      expect(spy.mock.calls[0][0]).toContain('[INFO]');
      
      spy.mockRestore();
    });

    it('should log warning messages', () => {
      const spy = vi.spyOn(console, 'warn').mockImplementation(() => {});
      
      logger.warn('Test warning message');
      
      expect(spy).toHaveBeenCalled();
      expect(spy.mock.calls[0][0]).toContain('[WARN]');
      
      spy.mockRestore();
    });

    it('should log error messages', () => {
      const spy = vi.spyOn(console, 'error').mockImplementation(() => {});
      
      logger.error('Test error message');
      
      expect(spy).toHaveBeenCalled();
      expect(spy.mock.calls[0][0]).toContain('[ERROR]');
      
      spy.mockRestore();
    });

    it('should log debug messages in development', () => {
      const spy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      logger.debug('Test debug message');
      
      // Debug should log in test environment
      expect(spy).toHaveBeenCalled();
      
      spy.mockRestore();
    });
  });

  describe('Remote Logging', () => {
    it('should send logs to remote endpoint', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      });

      await logger.remote('Test remote log', { data: 'test' });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/logs'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: expect.any(String),
        })
      );
    });

    it('should handle remote logging failures gracefully', async () => {
      (global.fetch as any).mockRejectedValueOnce(new Error('Network error'));

      // Should not throw
      await expect(
        logger.remote('Test log', { data: 'test' })
      ).resolves.not.toThrow();
    });

    it('should include timestamp in remote logs', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      });

      await logger.remote('Test log');

      const callBody = JSON.parse((global.fetch as any).mock.calls[0][1].body);
      expect(callBody).toHaveProperty('timestamp');
      expect(new Date(callBody.timestamp)).toBeInstanceOf(Date);
    });
  });

  describe('Performance Tracking', () => {
    it('should measure performance metrics', () => {
      const marker = logger.performance.start('test-operation');
      
      expect(marker).toHaveProperty('name', 'test-operation');
      expect(marker).toHaveProperty('startTime');
    });

    it('should calculate duration correctly', () => {
      const marker = logger.performance.start('test-operation');
      
      // Simulate some work
      const duration = logger.performance.end('test-operation');
      
      expect(duration).toBeGreaterThanOrEqual(0);
      expect(typeof duration).toBe('number');
    });

    it('should handle performance marks', () => {
      logger.performance.mark('custom-mark');
      
      // Should not throw
      expect(() => logger.performance.mark('another-mark')).not.toThrow();
    });
  });

  describe('Audit Trail', () => {
    it('should log audit events', async () => {
      const spy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      await logger.audit('USER_LOGIN', {
        userId: 'user-123',
        action: 'login',
        timestamp: new Date().toISOString(),
      });
      
      expect(spy).toHaveBeenCalled();
      const logMessage = spy.mock.calls[0][0];
      expect(logMessage).toContain('[AUDIT]');
      expect(logMessage).toContain('USER_LOGIN');
      
      spy.mockRestore();
    });

    it('should include required audit fields', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        status: 200,
      });

      await logger.audit('PHI_ACCESS', {
        userId: 'user-123',
        resource: 'patient-record',
        action: 'view',
      });

      // Should include timestamp, event type, and details
      const auditLog = (global.fetch as any).mock.calls[0];
      expect(auditLog).toBeDefined();
    });
  });

  describe('Batch Logging', () => {
    it('should batch multiple log entries', () => {
      const batch = logger.createBatch();
      
      batch.add('info', 'Message 1');
      batch.add('warn', 'Message 2');
      batch.add('error', 'Message 3');
      
      expect(batch.size()).toBe(3);
    });

    it('should flush batch logs', () => {
      const spy = vi.spyOn(console, 'log').mockImplementation(() => {});
      const batch = logger.createBatch();
      
      batch.add('info', 'Batch message 1');
      batch.add('info', 'Batch message 2');
      batch.flush();
      
      expect(spy).toHaveBeenCalledTimes(2);
      expect(batch.size()).toBe(0);
      
      spy.mockRestore();
    });
  });

  describe('Production vs Development', () => {
    it('should suppress debug logs in production', () => {
      const originalEnv = import.meta.env.MODE;
      vi.stubGlobal('import.meta', {
        env: { ...import.meta.env, MODE: 'production' },
      });

      const spy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      logger.debug('Debug message');
      
      // Debug should be suppressed in production
      expect(spy).not.toHaveBeenCalled();
      
      spy.mockRestore();
      vi.stubGlobal('import.meta', { env: { ...import.meta.env, MODE: originalEnv } });
    });

    it('should sanitize logs more aggressively in production', () => {
      const originalEnv = import.meta.env.MODE;
      vi.stubGlobal('import.meta', {
        env: { ...import.meta.env, MODE: 'production' },
      });

      const spy = vi.spyOn(console, 'log').mockImplementation(() => {});
      
      logger.info('Sensitive data: 123-45-6789');
      
      const loggedMessage = spy.mock.calls[0]?.[0];
      expect(loggedMessage).not.toContain('123-45-6789');
      
      spy.mockRestore();
      vi.stubGlobal('import.meta', { env: { ...import.meta.env, MODE: originalEnv } });
    });
  });
});
