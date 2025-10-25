/**
 * Production-Grade Logger Service
 * HIPAA-Compliant Structured Logging
 */

export class Logger {
  private isDevelopment = typeof window !== 'undefined' && window.location.hostname === 'localhost';
  
  private formatLog(level: string, message: string, context: any = {}) {
    return {
      timestamp: new Date().toISOString(),
      level,
      message,
      context,
      environment: this.isDevelopment ? 'development' : 'production',
      url: typeof window !== 'undefined' ? window.location.href : 'server'
    };
  }

  debug(message: string, context: any = {}) {
    // Only log in development
    if (this.isDevelopment) {
      console.debug(this.formatLog('DEBUG', message, context));
    }
  }

  info(message: string, context: any = {}) {
    // Always log info
    this.sendToAnalytics(this.formatLog('INFO', message, context));
  }

  warn(message: string, context: any = {}) {
    // Always log warnings
    console.warn(this.formatLog('WARN', message, context));
    this.sendToAnalytics(this.formatLog('WARN', message, context));
  }

  error(message: string, error?: Error, context: any = {}) {
    // Always log errors
    const errorContext = {
      ...context,
      stack: error?.stack,
      message: error?.message
    };
    console.error(this.formatLog('ERROR', message, errorContext));
    this.sendToAnalytics(this.formatLog('ERROR', message, errorContext));
    
    // Send to error tracking (Sentry)
    if (typeof (window as any).Sentry !== 'undefined') {
      (window as any).Sentry.captureException(error, { extra: context });
    }
  }

  critical(message: string, error?: Error, context: any = {}) {
    // Always log critical errors
    const errorContext = {
      ...context,
      stack: error?.stack,
      message: error?.message
    };
    console.error('🚨 CRITICAL:', this.formatLog('CRITICAL', message, errorContext));
    this.sendToAnalytics(this.formatLog('CRITICAL', message, errorContext));
    
    // Immediate alert for critical issues
    if (typeof (window as any).Sentry !== 'undefined') {
      (window as any).Sentry.captureException(error, { 
        level: 'fatal',
        extra: context 
      });
    }
  }

  private sendToAnalytics(log: any) {
    // Send to Workers Analytics or external monitoring
    if (typeof navigator !== 'undefined' && navigator.sendBeacon) {
      try {
        navigator.sendBeacon('/api/v1/logs', JSON.stringify(log));
      } catch (err) {
        // Silently fail if analytics endpoint unavailable
      }
    }
  }

  // Specialized logging methods
  logAuthEvent(action: string, userId: string, result: string) {
    this.info('AUTH_EVENT', { action, userId, result });
  }

  logAPICall(method: string, endpoint: string, status: number, duration: number) {
    this.info('API_CALL', { method, endpoint, status, duration });
  }

  logPHIAccess(resourceType: string, action: string, userId: string) {
    this.info('PHI_ACCESS', { resourceType, action, userId });
  }

  logEncryption(operation: string, status: string, dataType: string) {
    this.debug('ENCRYPTION', { operation, status, dataType });
  }
}

// Export singleton
export const logger = new Logger();
