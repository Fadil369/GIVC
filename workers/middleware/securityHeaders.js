/**
 * GIVC Healthcare Platform - Enhanced Security Headers Middleware
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Comprehensive security headers for HIPAA compliance and OWASP best practices
 */

/**
 * Generate comprehensive security headers
 * @param {Object} options - Configuration options
 * @param {boolean} options.isDevelopment - Development mode flag
 * @param {string} options.origin - Request origin for CORS
 * @param {boolean} options.enableCSP - Enable Content Security Policy
 * @returns {Object} Security headers object
 */
export function getSecurityHeaders(options = {}) {
  const {
    isDevelopment = false,
    origin = null,
    enableCSP = true,
  } = options;

  // Allowed origins for CORS
  const allowedOrigins = isDevelopment
    ? ['http://localhost:3000', 'http://localhost:5173', 'http://localhost:8787', 'https://givc.thefadil.site']
    : ['https://givc.thefadil.site', 'https://www.givc.thefadil.site', 'https://givc.pages.dev'];

  // Determine CORS origin
  const corsOrigin = origin && allowedOrigins.includes(origin)
    ? origin
    : (isDevelopment ? '*' : allowedOrigins[0]);

  const headers = {
    // CORS Headers
    'Access-Control-Allow-Origin': corsOrigin,
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, PATCH, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, X-Client-Version, X-Request-ID, X-Encryption-Status, X-Audit-Required',
    'Access-Control-Expose-Headers': 'X-Request-ID, X-Rate-Limit-Remaining, X-Rate-Limit-Reset',
    'Access-Control-Max-Age': '86400', // 24 hours
    'Access-Control-Allow-Credentials': 'true',

    // Security Headers - OWASP Recommended
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    
    // Referrer Policy - Protect against information leakage
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    
    // Permissions Policy (formerly Feature-Policy) - HIPAA Compliance
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()',
    
    // Strict Transport Security (HSTS) - Force HTTPS
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    
    // Cache Control for sensitive data
    'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0',
    'Pragma': 'no-cache',
    'Expires': '0',
    
    // Additional Security Headers
    'X-DNS-Prefetch-Control': 'off',
    'X-Download-Options': 'noopen',
    'X-Permitted-Cross-Domain-Policies': 'none',
  };

  // Content Security Policy - Comprehensive CSP
  if (enableCSP) {
    const cspDirectives = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com", // Allow CDN for libraries
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "font-src 'self' data: https://fonts.gstatic.com",
      "img-src 'self' data: https: blob:",
      "connect-src 'self' https://api.cloudflare.com https://*.cloudflare.com",
      "media-src 'self' data: blob:",
      "object-src 'none'",
      "frame-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'none'",
      "upgrade-insecure-requests",
    ];

    // Relaxed CSP for development
    if (isDevelopment) {
      cspDirectives.push("report-uri /api/v1/csp-report");
    } else {
      cspDirectives.push("block-all-mixed-content");
    }

    headers['Content-Security-Policy'] = cspDirectives.join('; ');
  }

  return headers;
}

/**
 * Apply security headers to a Response object
 * @param {Response} response - The response object
 * @param {Object} options - Configuration options
 * @returns {Response} Response with security headers
 */
export function applySecurityHeaders(response, options = {}) {
  const headers = getSecurityHeaders(options);
  const newResponse = new Response(response.body, response);

  // Apply all security headers
  Object.entries(headers).forEach(([key, value]) => {
    newResponse.headers.set(key, value);
  });

  return newResponse;
}

/**
 * Create CORS preflight response
 * @param {Object} options - Configuration options
 * @returns {Response} CORS preflight response
 */
export function createPreflightResponse(options = {}) {
  const headers = getSecurityHeaders(options);
  
  return new Response(null, {
    status: 204,
    headers: headers,
  });
}

/**
 * Get rate limit headers
 * @param {Object} rateLimitInfo - Rate limit information
 * @returns {Object} Rate limit headers
 */
export function getRateLimitHeaders(rateLimitInfo) {
  return {
    'X-RateLimit-Limit': rateLimitInfo.limit?.toString() || '100',
    'X-RateLimit-Remaining': rateLimitInfo.remaining?.toString() || '0',
    'X-RateLimit-Reset': rateLimitInfo.resetTime?.toString() || Date.now().toString(),
    'Retry-After': rateLimitInfo.retryAfter?.toString() || '60',
  };
}

/**
 * Validate request security requirements
 * @param {Request} request - The incoming request
 * @returns {Object} Validation result
 */
export function validateRequestSecurity(request) {
  const issues = [];
  const url = new URL(request.url);

  // Check HTTPS in production
  if (url.protocol !== 'https:' && !url.hostname.includes('localhost')) {
    issues.push({
      severity: 'critical',
      message: 'Request must use HTTPS',
      code: 'INSECURE_PROTOCOL',
    });
  }

  // Check for required security headers in sensitive requests
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(request.method)) {
    const contentType = request.headers.get('Content-Type');
    if (!contentType) {
      issues.push({
        severity: 'high',
        message: 'Content-Type header is required',
        code: 'MISSING_CONTENT_TYPE',
      });
    }

    // Check for encryption status header for PHI data
    if (url.pathname.includes('/medivault') || url.pathname.includes('/patient')) {
      const encryptionStatus = request.headers.get('X-Encryption-Status');
      if (!encryptionStatus || encryptionStatus !== 'enabled') {
        issues.push({
          severity: 'critical',
          message: 'PHI data must be encrypted',
          code: 'MISSING_ENCRYPTION',
        });
      }
    }
  }

  // Check for audit requirements on sensitive endpoints
  const sensitiveEndpoints = ['/api/v1/medivault', '/api/v1/agents', '/api/v1/compliance'];
  if (sensitiveEndpoints.some(endpoint => url.pathname.startsWith(endpoint))) {
    const auditHeader = request.headers.get('X-Audit-Required');
    if (!auditHeader) {
      issues.push({
        severity: 'medium',
        message: 'Audit tracking header recommended for sensitive operations',
        code: 'MISSING_AUDIT_HEADER',
      });
    }
  }

  return {
    valid: issues.filter(i => i.severity === 'critical').length === 0,
    issues,
    criticalIssues: issues.filter(i => i.severity === 'critical').length,
    highIssues: issues.filter(i => i.severity === 'high').length,
  };
}

/**
 * Create error response with security headers
 * @param {string} message - Error message
 * @param {number} status - HTTP status code
 * @param {Object} options - Additional options
 * @returns {Response} Error response with security headers
 */
export function createSecureErrorResponse(message, status = 500, options = {}) {
  const body = JSON.stringify({
    error: true,
    message,
    status,
    timestamp: new Date().toISOString(),
    requestId: options.requestId || crypto.randomUUID(),
  });

  const response = new Response(body, {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  return applySecurityHeaders(response, options);
}

/**
 * Generate request ID for tracking
 * @returns {string} Unique request ID
 */
export function generateRequestId() {
  return `req_${Date.now()}_${Math.random().toString(36).substring(2, 15)}`;
}

/**
 * Enhanced CORS configuration for specific routes
 * @param {string} route - API route
 * @returns {Object} Route-specific CORS configuration
 */
export function getRouteSpecificCORS(route) {
  const configs = {
    '/api/v1/auth': {
      allowCredentials: true,
      maxAge: 3600, // 1 hour
    },
    '/api/v1/medivault': {
      allowCredentials: true,
      maxAge: 600, // 10 minutes
      additionalHeaders: ['X-File-ID', 'X-Encryption-Key'],
    },
    '/api/v1/agents': {
      allowCredentials: true,
      maxAge: 1800, // 30 minutes
      additionalHeaders: ['X-Agent-Type', 'X-Processing-ID'],
    },
  };

  return configs[route] || {
    allowCredentials: false,
    maxAge: 3600,
  };
}

export default {
  getSecurityHeaders,
  applySecurityHeaders,
  createPreflightResponse,
  getRateLimitHeaders,
  validateRequestSecurity,
  createSecureErrorResponse,
  generateRequestId,
  getRouteSpecificCORS,
};
