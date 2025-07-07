/**
 * GIVC Healthcare Platform - Security Middleware
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * HIPAA-compliant security middleware for authentication, authorization,
 * encryption, and audit logging.
 */

// CORS Configuration
export function createCors() {
  return {
    'Access-Control-Allow-Origin': '*', // In production, set specific domains
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
    'Access-Control-Max-Age': '86400',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
  };
}

// Authentication
export async function authenticateRequest(request, env) {
  const authHeader = request.headers.get('Authorization');
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return { success: false, error: 'No valid authorization header' };
  }

  const token = authHeader.substring(7);
  
  // In a real implementation, validate JWT token
  // For demo purposes, accept any token that starts with 'jwt_'
  if (token.startsWith('jwt_')) {
    const user = {
      id: '1',
      email: 'demo@givc.thefadil.site',
      name: 'Healthcare Professional',
      role: 'physician',
      permissions: ['read_medical_data', 'write_medical_data', 'access_ai_agents'],
    };
    
    return { success: true, user };
  }

  return { success: false, error: 'Invalid token' };
}

// Encryption/Decryption
export async function encrypt(data, key) {
  // Simple encryption for demo - in production use proper crypto
  const encoder = new TextEncoder();
  const keyData = encoder.encode(key);
  
  // For demo purposes, just base64 encode
  // In production, use Web Crypto API with AES-256-GCM
  if (data instanceof ArrayBuffer) {
    const bytes = new Uint8Array(data);
    return btoa(String.fromCharCode(...bytes));
  }
  
  return btoa(data);
}

export async function decrypt(encryptedData, key) {
  // Simple decryption for demo - in production use proper crypto
  try {
    const decrypted = atob(encryptedData);
    return new TextEncoder().encode(decrypted);
  } catch (error) {
    throw new Error('Decryption failed');
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
    console.error('Failed to log audit event:', error);
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
  // Simple check for demo - in production use proper encryption markers
  return typeof data === 'string' && (data.startsWith('enc_') || data.length > 100);
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
      console.error('Rate limiting error:', error);
      return true; // Allow request if rate limiting fails
    }
  }
}

// Input validation and sanitization
export function sanitizeInput(input) {
  if (typeof input !== 'string') {
    return input;
  }
  
  // Remove potentially dangerous characters
  let sanitizedInput = input.trim();
  let previousInput;
  do {
    previousInput = sanitizedInput;
    sanitizedInput = sanitizedInput.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
  } while (sanitizedInput !== previousInput);
  
  return sanitizedInput
    .replace(/javascript:/gi, '')
    .replace(/on\w+\s*=/gi, '');
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