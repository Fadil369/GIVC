/**
 * GIVC Healthcare Platform - Production Logger for Workers
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Centralized logging utility for Cloudflare Workers
 * Replaces console.log/warn/error with structured logging
 */

/**
 * Log levels
 */
const LogLevel = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
  CRITICAL: 4,
};

/**
 * Get log level from environment
 * @param {Object} env - Environment variables
 * @returns {number} Log level
 */
function getLogLevel(env) {
  const level = env?.LOG_LEVEL || 'info';
  return LogLevel[level.toUpperCase()] || LogLevel.INFO;
}

/**
 * Format log message
 * @param {string} level - Log level
 * @param {string} message - Log message
 * @param {Object} context - Additional context
 * @returns {Object} Formatted log entry
 */
function formatLog(level, message, context = {}) {
  return {
    timestamp: new Date().toISOString(),
    level,
    message,
    ...context,
    service: 'givc-workers',
  };
}

/**
 * Production logger class
 */
class Logger {
  constructor(env = {}) {
    this.env = env;
    this.level = getLogLevel(env);
  }

  /**
   * Check if log level is enabled
   * @param {number} level - Log level
   * @returns {boolean} Is enabled
   */
  isEnabled(level) {
    return level >= this.level;
  }

  /**
   * Debug log (development only)
   * @param {string} message - Log message
   * @param {Object} context - Additional context
   */
  debug(message, context = {}) {
    if (this.isEnabled(LogLevel.DEBUG)) {
      const log = formatLog('debug', message, context);
      // In production, send to analytics
      if (this.env.ENVIRONMENT === 'production') {
        this.sendToAnalytics(log);
      } else {
        console.debug('[DEBUG]', JSON.stringify(log, null, 2));
      }
    }
  }

  /**
   * Info log
   * @param {string} message - Log message
   * @param {Object} context - Additional context
   */
  info(message, context = {}) {
    if (this.isEnabled(LogLevel.INFO)) {
      const log = formatLog('info', message, context);
      this.sendToAnalytics(log);
    }
  }

  /**
   * Warning log
   * @param {string} message - Log message
   * @param {Object} context - Additional context
   */
  warn(message, context = {}) {
    if (this.isEnabled(LogLevel.WARN)) {
      const log = formatLog('warn', message, context);
      this.sendToAnalytics(log);
      
      // Also send to monitoring in production
      if (this.env.ENVIRONMENT === 'production') {
        this.sendToMonitoring(log);
      }
    }
  }

  /**
   * Error log
   * @param {string} message - Log message
   * @param {Object} context - Additional context
   */
  error(message, context = {}) {
    if (this.isEnabled(LogLevel.ERROR)) {
      const log = formatLog('error', message, context);
      this.sendToAnalytics(log);
      this.sendToMonitoring(log);
      
      // Store in audit log for HIPAA compliance
      if (this.env.AUDIT_LOGS) {
        this.storeAuditLog(log);
      }
    }
  }

  /**
   * Critical log (system failure)
   * @param {string} message - Log message
   * @param {Object} context - Additional context
   */
  critical(message, context = {}) {
    const log = formatLog('critical', message, context);
    this.sendToAnalytics(log);
    this.sendToMonitoring(log);
    this.storeAuditLog(log);
    
    // Trigger alerts for critical issues
    this.triggerAlert(log);
  }

  /**
   * Send log to analytics
   * @param {Object} log - Log entry
   */
  async sendToAnalytics(log) {
    try {
      // In Cloudflare Workers, use Workers Analytics Engine or KV
      if (this.env.ANALYTICS) {
        await this.env.ANALYTICS.writeDataPoint({
          blobs: [log.level, log.message, log.service],
          doubles: [Date.now()],
          indexes: [log.level],
        });
      }
    } catch (error) {
      // Fallback to console in case of analytics failure
      console.error('[Logger] Analytics failed:', error.message);
    }
  }

  /**
   * Send to monitoring system
   * @param {Object} log - Log entry
   */
  async sendToMonitoring(log) {
    try {
      // Send to external monitoring (e.g., Sentry, Datadog)
      if (this.env.MONITORING_ENDPOINT) {
        await fetch(this.env.MONITORING_ENDPOINT, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.env.MONITORING_TOKEN}`,
          },
          body: JSON.stringify(log),
        });
      }
    } catch (error) {
      console.error('[Logger] Monitoring failed:', error.message);
    }
  }

  /**
   * Store in audit log (HIPAA compliance)
   * @param {Object} log - Log entry
   */
  async storeAuditLog(log) {
    try {
      if (this.env.AUDIT_LOGS) {
        const key = `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        await this.env.AUDIT_LOGS.put(key, JSON.stringify(log), {
          expirationTtl: 60 * 60 * 24 * 365 * 7, // 7 years (HIPAA requirement)
          metadata: {
            level: log.level,
            timestamp: log.timestamp,
          },
        });
      }
    } catch (error) {
      console.error('[Logger] Audit log failed:', error.message);
    }
  }

  /**
   * Trigger alert for critical issues
   * @param {Object} log - Log entry
   */
  async triggerAlert(log) {
    try {
      // Trigger PagerDuty, OpsGenie, or similar
      if (this.env.ALERT_WEBHOOK) {
        await fetch(this.env.ALERT_WEBHOOK, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            severity: 'critical',
            message: log.message,
            context: log,
            timestamp: log.timestamp,
          }),
        });
      }
    } catch (error) {
      console.error('[Logger] Alert failed:', error.message);
    }
  }

  /**
   * Security event logging (HIPAA-specific)
   * @param {string} event - Event type
   * @param {Object} details - Event details
   */
  async logSecurityEvent(event, details = {}) {
    const log = {
      ...formatLog('security', `Security Event: ${event}`, details),
      eventType: event,
      phi_detected: details.phiDetected || false,
      user_id: details.userId || 'unknown',
      client_ip: details.clientIp || 'unknown',
    };

    this.error(`[SECURITY] ${event}`, log);
    
    // Store in separate security log
    if (this.env.SECURITY_LOGS) {
      const key = `security_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      await this.env.SECURITY_LOGS.put(key, JSON.stringify(log), {
        expirationTtl: 60 * 60 * 24 * 365 * 10, // 10 years
      });
    }
  }
}

/**
 * Create logger instance
 * @param {Object} env - Environment variables
 * @returns {Logger} Logger instance
 */
export function createLogger(env = {}) {
  return new Logger(env);
}

/**
 * Default export for direct usage
 */
export default {
  createLogger,
  LogLevel,
};
