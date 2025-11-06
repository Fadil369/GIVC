/**
 * Production-Grade Logger Service
 * HIPAA-Compliant Structured Logging
 */

interface LogContext {
  [key: string]: any;
}

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  context: LogContext;
  environment: string;
  url?: string;
}

export class Logger {
  private isDevelopment: boolean;

  constructor() {
    this.isDevelopment = typeof globalThis !== 'undefined' && 
      (globalThis.location?.hostname === 'localhost' || 
       globalThis.location?.hostname === '127.0.0.1');
  }

  private formatLog(level: string, message: string, context: LogContext = {}): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      environment: this.isDevelopment ? 'development' : 'production',
      url: typeof globalThis !== 'undefined' && globalThis.location 
        ? globalThis.location.href 
        : 'server'
    };
  }

  debug(message: string, context: LogContext = {}): void {
    // Only log in development
    if (this.isDevelopment) {
      console.debug(this.formatLog('DEBUG', message, context));
    }
  }

  info(message: string, context: LogContext = {}): void {
    // Always log info
    const log = this.formatLog('INFO', message, context);
    console.info(log);
    this.sendToAnalytics(log);
  }

  warn(message: string, context: LogContext = {}): void {
    // Always log warnings
    const log = this.formatLog('WARN', message, context);
    console.warn(log);
    this.sendToAnalytics(log);
  }

  error(message: string, error?: Error | unknown, context: LogContext = {}): void {
    // Always log errors
    const errorContext: LogContext = {
      ...context,
      stack: error instanceof Error ? error.stack : undefined,
      errorMessage: error instanceof Error ? error.message : String(error)
    };
    const log = this.formatLog('ERROR', message, errorContext);
    console.error(log);
    this.sendToAnalytics(log);
    
    // Send to error tracking (Sentry)
    if (typeof globalThis !== 'undefined' && (globalThis as any).Sentry) {
      (globalThis as any).Sentry.captureException(error, { extra: context });
    }
  }

  critical(message: string, error?: Error | unknown, context: LogContext = {}): void {
    // Always log critical errors
    const errorContext: LogContext = {
      ...context,
      stack: error instanceof Error ? error.stack : undefined,
      errorMessage: error instanceof Error ? error.message : String(error)
    };
    const log = this.formatLog('CRITICAL', message, errorContext);
    console.error('🚨 CRITICAL:', log);
    this.sendToAnalytics(log);
    
    // Immediate alert for critical issues
    if (typeof globalThis !== 'undefined' && (globalThis as any).Sentry) {
      (globalThis as any).Sentry.captureException(error, { 
        level: 'fatal',
        extra: context 
      });
    }
  }

  private sendToAnalytics(log: LogEntry): void {
    // Send to Workers Analytics or external monitoring
    try {
      if (typeof navigator !== 'undefined' && navigator.sendBeacon) {
        navigator.sendBeacon('/api/v1/logs', JSON.stringify(log));
      }
    } catch (err) {
      // Silently fail if analytics endpoint unavailable
    }
  }

  // Specialized logging methods
  logAuthEvent(action: string, userId: string, result: string): void {
    this.info('AUTH_EVENT', { action, userId, result });
  }

  logAPICall(method: string, endpoint: string, status: number, duration: number): void {
    this.info('API_CALL', { method, endpoint, status, duration });
  }

  logPHIAccess(resourceType: string, action: string, userId: string): void {
    this.info('PHI_ACCESS', { resourceType, action, userId });
  }

  logEncryption(operation: string, status: string, dataType: string): void {
    this.debug('ENCRYPTION', { operation, status, dataType });
  }
}

// Export singleton
export const logger = new Logger();
