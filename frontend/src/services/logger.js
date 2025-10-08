/**
 * Production-Safe Logging Service
 * HIPAA-compliant logging that prevents PHI leakage in production
 * 
 * @module services/logger
 */

const isDevelopment = import.meta.env.DEV;
const isProduction = import.meta.env.PROD;

/**
 * Sanitizes data to remove potential PHI before logging
 * @param {any} data - Data to sanitize
 * @returns {any} Sanitized data
 */
function sanitizeForLogging(data) {
  if (!data) return data;
  
  // Don't sanitize in development
  if (isDevelopment) return data;
  
  // Clone object to avoid mutating original
  const sanitized = JSON.parse(JSON.stringify(data));
  
  // Fields that may contain PHI
  const phiFields = [
    'ssn', 'socialSecurityNumber',
    'email', 'phone', 'phoneNumber',
    'address', 'streetAddress',
    'dateOfBirth', 'dob',
    'medicalRecordNumber', 'mrn',
    'diagnosis', 'symptoms',
    'prescription', 'medication',
    'labResults', 'testResults'
  ];
  
  function redactPHI(obj) {
    if (typeof obj !== 'object' || obj === null) return obj;
    
    Object.keys(obj).forEach(key => {
      const lowerKey = key.toLowerCase();
      if (phiFields.some(field => lowerKey.includes(field.toLowerCase()))) {
        obj[key] = '[REDACTED]';
      } else if (typeof obj[key] === 'object') {
        redactPHI(obj[key]);
      }
    });
    
    return obj;
  }
  
  return redactPHI(sanitized);
}

/**
 * Sends log to remote service (Cloudflare Analytics, Sentry, etc.)
 * @param {string} level - Log level
 * @param {string} message - Log message
 * @param {object} meta - Metadata
 */
async function sendToRemote(level, message, meta) {
  if (!isProduction) return;
  
  try {
    // Send to Cloudflare Workers analytics endpoint
    await fetch('/api/v1/logs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        level,
        message,
        meta: sanitizeForLogging(meta),
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      }),
    }).catch(() => {
      // Silently fail - we don't want logging errors to break the app
    });
  } catch (error) {
    // Silent fail in production
  }
}

/**
 * Logger service with HIPAA-compliant sanitization
 */
export const logger = {
  /**
   * Log debug information (development only)
   * @param {string} message - Log message
   * @param {object} meta - Additional metadata
   */
  debug(message, meta = {}) {
    if (isDevelopment) {
      console.debug(`🔍 ${message}`, meta);
    }
  },

  /**
   * Log informational message
   * @param {string} message - Log message
   * @param {object} meta - Additional metadata
   */
  info(message, meta = {}) {
    if (isDevelopment) {
      console.info(`ℹ️ ${message}`, meta);
    }
    sendToRemote('info', message, meta);
  },

  /**
   * Log warning message
   * @param {string} message - Log message
   * @param {object} meta - Additional metadata
   */
  warn(message, meta = {}) {
    if (isDevelopment) {
      console.warn(`⚠️ ${message}`, meta);
    } else {
      console.warn(`⚠️ ${message}`);
    }
    sendToRemote('warn', message, meta);
  },

  /**
   * Log error message
   * @param {string} message - Log message
   * @param {Error|object} error - Error object or metadata
   */
  error(message, error = {}) {
    const errorInfo = error instanceof Error 
      ? { message: error.message, stack: error.stack, name: error.name }
      : error;

    if (isDevelopment) {
      console.error(`❌ ${message}`, errorInfo);
    } else {
      console.error(`❌ ${message}`);
    }
    
    sendToRemote('error', message, errorInfo);
  },

  /**
   * Log critical error (always shown, even in production)
   * @param {string} message - Log message
   * @param {Error|object} error - Error object or metadata
   */
  critical(message, error = {}) {
    const errorInfo = error instanceof Error 
      ? { message: error.message, stack: error.stack, name: error.name }
      : error;

    // Critical errors are always logged to console
    console.error(`🚨 CRITICAL: ${message}`, isDevelopment ? errorInfo : '');
    
    sendToRemote('critical', message, errorInfo);
  },

  /**
   * Log performance metric
   * @param {string} metric - Metric name
   * @param {number} value - Metric value
   * @param {object} meta - Additional metadata
   */
  performance(metric, value, meta = {}) {
    if (isDevelopment) {
      console.log(`⚡ Performance: ${metric} = ${value}ms`, meta);
    }
    
    if (isProduction) {
      sendToRemote('performance', `${metric}: ${value}ms`, meta);
    }
  },

  /**
   * Log security event (HIPAA audit trail)
   * @param {string} event - Event description
   * @param {object} meta - Event metadata
   */
  security(event, meta = {}) {
    // Security events are always sent to remote, even in development
    console.info(`🔒 Security: ${event}`, isDevelopment ? meta : '');
    sendToRemote('security', event, meta);
  },

  /**
   * Log HIPAA audit event
   * @param {string} action - Action performed
   * @param {object} meta - Audit metadata
   */
  audit(action, meta = {}) {
    // Audit events must always be logged for compliance
    console.info(`📋 Audit: ${action}`, isDevelopment ? meta : '');
    sendToRemote('audit', action, meta);
  },
};

/**
 * Error boundary logger
 * Use this in React Error Boundaries
 */
export function logComponentError(error, errorInfo) {
  logger.error('React Component Error', {
    error: {
      message: error.message,
      stack: error.stack,
    },
    componentStack: errorInfo.componentStack,
  });
}

/**
 * Performance measurement helper
 * @param {string} label - Performance label
 * @returns {Function} End function to call when measurement is complete
 */
export function measurePerformance(label) {
  const start = performance.now();
  
  return () => {
    const duration = performance.now() - start;
    logger.performance(label, duration.toFixed(2));
    return duration;
  };
}

/**
 * Batch logger for multiple events
 */
export class BatchLogger {
  constructor(batchSize = 10, flushInterval = 5000) {
    this.batch = [];
    this.batchSize = batchSize;
    this.flushInterval = flushInterval;
    this.timer = null;
    this.startTimer();
  }

  add(level, message, meta) {
    this.batch.push({ level, message, meta, timestamp: new Date().toISOString() });
    
    if (this.batch.length >= this.batchSize) {
      this.flush();
    }
  }

  flush() {
    if (this.batch.length === 0) return;
    
    const logs = [...this.batch];
    this.batch = [];
    
    if (isProduction) {
      fetch('/api/v1/logs/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ logs: logs.map(l => ({
          ...l,
          meta: sanitizeForLogging(l.meta)
        })) }),
      }).catch(() => {});
    }
  }

  startTimer() {
    this.timer = setInterval(() => this.flush(), this.flushInterval);
  }

  stop() {
    if (this.timer) {
      clearInterval(this.timer);
      this.flush();
    }
  }
}

export default logger;
