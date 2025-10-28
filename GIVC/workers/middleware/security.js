/**
 * GIVC Healthcare Platform - Security Middleware
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * HIPAA-compliant security middleware for authentication, authorization,
 * encryption, and audit logging.
 */

// Enhanced CORS Configuration with security improvements
export function createCors(origin = '*', isDevelopment = false) {
  const allowedOrigins = isDevelopment 
    ? ['http://localhost:3000', 'http://localhost:5173', 'https://givc.thefadil.site']
    : ['https://givc.thefadil.site', 'https://www.givc.thefadil.site'];
    
  const corsOrigin = Array.isArray(allowedOrigins) && origin !== '*' 
    ? (allowedOrigins.includes(origin) ? origin : 'null')
    : origin;

  return {
    'Access-Control-Allow-Origin': corsOrigin,
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, X-Client-Version, X-Request-ID',
    'Access-Control-Max-Age': '86400',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; connect-src 'self' https:; font-src 'self' data:; object-src 'none'; base-uri 'self'",
  };
}

// Enhanced Authentication with improved security
export async function authenticateRequest(request, env) {
  try {
    const authHeader = request.headers.get('Authorization');
    const clientIp = request.headers.get('CF-Connecting-IP') || 
                     request.headers.get('X-Forwarded-For') || 
                     'unknown';
    
    // Check rate limiting first
    const rateLimitResult = await checkRateLimit(env, clientIp);
    if (!rateLimitResult.allowed) {
      return { 
        success: false, 
        error: 'Rate limit exceeded',
        retryAfter: rateLimitResult.retryAfter 
      };
    }
    
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      await logSecurityEvent(env, {
        type: 'authentication_failure',
        reason: 'missing_authorization_header',
        clientIp,
        timestamp: new Date(),
        severity: 'medium'
      });
      return { success: false, error: 'No valid authorization header' };
    }

    const token = authHeader.substring(7);
    
    // Enhanced token validation
    if (!token || token.length < 10) {
      await logSecurityEvent(env, {
        type: 'authentication_failure',
        reason: 'invalid_token_format',
        clientIp,
        timestamp: new Date(),
        severity: 'medium'
      });
      return { success: false, error: 'Invalid token format' };
    }
    
    // PRODUCTION: Use real JWT validation from auth.js
    // This function is deprecated - use authenticateRequest from auth.js instead
    try {
      const { verifyJWT } = await import('../utils/jwt.js');
      const payload = await verifyJWT(token, env.JWT_SECRET);
      
      if (!payload) {
        await logSecurityEvent(env, {
          type: 'authentication_failure',
          reason: 'invalid_jwt',
          clientIp,
          timestamp: new Date(),
          severity: 'high'
        });
        return { success: false, error: 'Invalid or expired token' };
      }

      // Fetch user from database
      const user = await env.DB.prepare(
        'SELECT id, email, name, role, permissions FROM users WHERE id = ? AND active = 1'
      ).bind(payload.sub).first();

      if (!user) {
        return { success: false, error: 'User not found' };
      }

      user.permissions = user.permissions ? JSON.parse(user.permissions) : [];
      user.sessionId = generateSessionId();
      
      await logSecurityEvent(env, {
        type: 'authentication_success',
        userId: user.id,
        clientIp,
        timestamp: new Date(),
        severity: 'low'
      });
      
      return { success: true, user };

    } catch (jwtError) {
      await logSecurityEvent(env, {
        type: 'authentication_failure',
        reason: 'jwt_verification_failed',
        clientIp,
        timestamp: new Date(),
        severity: 'high'
      });
      return { success: false, error: 'Invalid token' };
    }

  } catch (error) {
    logger.error('Authentication error:', error);
    return { success: false, error: 'Authentication service error' };
  }
}

// Rate limiting implementation
export async function checkRateLimit(env, clientIp, limit = 100, windowMs = 60000) {
  try {
    const key = `rate_limit:${clientIp}`;
    const now = Date.now();
    const windowStart = now - windowMs;
    
    // Get current request count from KV
    const currentData = await env.HEALTHCARE_KV.get(key);
    let requests = currentData ? JSON.parse(currentData) : [];
    
    // Remove old requests outside the window
    requests = requests.filter(timestamp => timestamp > windowStart);
    
    // Check if limit exceeded
    if (requests.length >= limit) {
      const oldestRequest = Math.min(...requests);
      const retryAfter = Math.ceil((oldestRequest + windowMs - now) / 1000);
      
      return { 
        allowed: false, 
        retryAfter,
        remaining: 0 
      };
    }
    
    // Add current request
    requests.push(now);
    
    // Store updated requests with TTL
    await env.HEALTHCARE_KV.put(key, JSON.stringify(requests), {
      expirationTtl: Math.ceil(windowMs / 1000)
    });
    
    return { 
      allowed: true, 
      remaining: limit - requests.length,
      resetTime: windowStart + windowMs
    };
  } catch (error) {
    logger.error('Rate limiting error:', error);
    // Allow request if rate limiting fails
    return { allowed: true, remaining: 99 };
  }
}

// Generate secure session ID
function generateSessionId() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < 32; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return result;
}

// Encryption/Decryption (DEPRECATED - use encryption.js instead)
export async function encrypt(data, key) {
  // DEPRECATED: Use workers/middleware/encryption.js instead
  // This function is maintained for backwards compatibility only
  const { encrypt: encryptProd } = await import('./encryption.js');
  return await encryptProd(data, key);
}

export async function decrypt(encryptedData, key) {
  // DEPRECATED: Use workers/middleware/encryption.js instead
  // This function is maintained for backwards compatibility only
  const { decrypt: decryptProd } = await import('./encryption.js');
  return await decryptProd(encryptedData, key);
}

// Enhanced audit logging with security events
export async function logSecurityEvent(env, event) {
  try {
    const eventId = `security_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    const securityRecord = {
      id: eventId,
      type: event.type,
      severity: event.severity || 'medium',
      timestamp: event.timestamp.toISOString(),
      clientIp: event.clientIp || 'unknown',
      userId: event.userId || null,
      reason: event.reason || null,
      userAgent: event.userAgent || 'unknown',
      metadata: event.metadata || {}
    };

    // Store in KV for immediate access
    await env.AUDIT_LOGS.put(eventId, JSON.stringify(securityRecord), {
      expirationTtl: 7 * 24 * 60 * 60, // 7 days
    });
    
    // Also store critical events in D1 for longer retention
    if (event.severity === 'critical' || event.severity === 'high') {
      await env.HEALTHCARE_DB.prepare(
        'INSERT INTO security_logs (id, type, severity, timestamp, client_ip, user_id, reason, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
      ).bind(
        eventId,
        event.type,
        event.severity,
        event.timestamp.toISOString(),
        event.clientIp,
        event.userId,
        event.reason,
        JSON.stringify(event.metadata || {})
      ).run();
    }
    
    return eventId;
  } catch (error) {
    logger.error('Failed to log security event:', error);
    return null;
  }
}

// Audit Logging
export async function logAuditEvent(env, event) {
  const auditId = `audit_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  
  const auditRecord = {
    id: auditId,
    type: event.type,
    severity: event.severity,
    description: event.description,
    userId: event.userId,
    resourceId: event.resourceId || null,
    timestamp: event.timestamp.toISOString(),
    resolved: event.resolved,
    resolution: event.resolution || null,
    resolvedAt: event.resolvedAt ? event.resolvedAt.toISOString() : null,
    resolvedBy: event.resolvedBy || null,
    ipAddress: event.ipAddress || 'unknown',
    userAgent: event.userAgent || 'unknown',
    metadata: event.metadata || {},
  };

  try {
    // Store in KV with TTL for compliance (7 years = 2557 days)
    await env.AUDIT_LOGS.put(auditId, JSON.stringify(auditRecord), {
      expirationTtl: 2557 * 24 * 60 * 60, // 7 years in seconds
    });
    
    // For critical events, also store in D1 database for better querying
    if (event.severity === 'critical' || event.severity === 'high') {
      await env.HEALTHCARE_DB.prepare(
        'INSERT INTO audit_logs (id, type, severity, description, user_id, resource_id, timestamp, resolved) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'
      ).bind(
        auditId,
        event.type,
        event.severity,
        event.description,
        event.userId,
        event.resourceId,
        event.timestamp.toISOString(),
        event.resolved ? 1 : 0
      ).run();
    }
    
    return auditId;
  } catch (error) {
    logger.error('Failed to log audit event:', error);
    return null;
  }
}

// HIPAA Compliance Validation
export function validateHIPAACompliance(request, data) {
  const violations = [];
  
  // Check for PHI in request
  if (data && typeof data === 'object') {
    const phiFields = ['ssn', 'social_security', 'dob', 'date_of_birth', 'phone', 'address'];
    
    for (const field of phiFields) {
      if (data[field] && !isEncrypted(data[field])) {
        violations.push(`Unencrypted PHI field: ${field}`);
      }
    }
  }
  
  // Check for proper encryption headers
  const encryptionHeader = request.headers.get('X-Encryption-Status');
  if (!encryptionHeader || encryptionHeader !== 'enabled') {
    violations.push('Missing or invalid encryption status header');
  }
  
  // Check for audit trail requirements
  const auditHeader = request.headers.get('X-Audit-Required');
  if (auditHeader === 'true') {
    // Audit logging is required for this request
  }
  
  return {
    compliant: violations.length === 0,
    violations,
  };
}

// Helper function to check if data is encrypted
function isEncrypted(data) {
  // PRODUCTION: Check for AES-256-GCM format (iv:authTag:ciphertext)
  if (typeof data !== 'string') return false;
  const parts = data.split(':');
  if (parts.length !== 3) return false;
  const hexPattern = /^[0-9a-f]+$/i;
  return hexPattern.test(parts[0]) && hexPattern.test(parts[1]);
}

// Rate limiting
export class RateLimiter {
  constructor(env) {
    this.env = env;
  }
  
  async isAllowed(identifier, limit = 100, window = 3600) {
    const key = `rate_limit_${identifier}`;
    const now = Math.floor(Date.now() / 1000);
    const windowStart = now - window;
    
    try {
      const current = await this.env.MEDICAL_METADATA.get(key);
      let requests = current ? JSON.parse(current) : [];
      
      // Filter out old requests
      requests = requests.filter(timestamp => timestamp > windowStart);
      
      if (requests.length >= limit) {
        return false;
      }
      
      // Add current request
      requests.push(now);
      
      // Store updated list
      await this.env.MEDICAL_METADATA.put(key, JSON.stringify(requests), {
        expirationTtl: window,
      });
      
      return true;
    } catch (error) {
      logger.error('Rate limiting error:', error);
      return true; // Allow request if rate limiting fails
    }
  }
}

// Input validation and sanitization
import DOMPurify from 'dompurify';

import logger from './services/logger';

export function sanitizeInput(input) {
  if (typeof input !== 'string') {
    return input;
  }
  
  // Use DOMPurify to sanitize input
  return DOMPurify.sanitize(input);
}

// File type validation for medical files
export function validateMedicalFile(file) {
  const allowedTypes = [
    'application/dicom',
    'application/pdf',
    'image/jpeg',
    'image/png',
    'image/tiff',
    'text/plain',
    'text/hl7',
    'application/xml',
  ];
  
  const allowedExtensions = [
    '.dcm', '.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.txt', '.hl7', '.xml'
  ];
  
  const maxSize = 100 * 1024 * 1024; // 100MB
  
  const violations = [];
  
  if (!allowedTypes.includes(file.type)) {
    violations.push(`Invalid file type: ${file.type}`);
  }
  
  const extension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
  if (!allowedExtensions.includes(extension)) {
    violations.push(`Invalid file extension: ${extension}`);
  }
  
  if (file.size > maxSize) {
    violations.push(`File too large: ${file.size} bytes (max: ${maxSize})`);
  }
  
  return {
    valid: violations.length === 0,
    violations,
  };
}

// Generate secure file URLs with expiration
export function generateSecureFileUrl(fileId, env, expirationMinutes = 60) {
  const expires = Date.now() + (expirationMinutes * 60 * 1000);
  const signature = btoa(`${fileId}_${expires}_${env.ENCRYPTION_KEY}`);
  
  return {
    url: `/api/v1/medivault/files/${fileId}?signature=${signature}&expires=${expires}`,
    expires: new Date(expires),
  };
}

// Verify secure file URL
export function verifySecureFileUrl(fileId, signature, expires, env) {
  if (Date.now() > parseInt(expires)) {
    return { valid: false, reason: 'URL expired' };
  }
  
  const expectedSignature = btoa(`${fileId}_${expires}_${env.ENCRYPTION_KEY}`);
  if (signature !== expectedSignature) {
    return { valid: false, reason: 'Invalid signature' };
  }
  
  return { valid: true };
}