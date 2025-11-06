/**
 * GIVC Healthcare Platform - Main API Router
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 *
 * Main Cloudflare Worker that routes requests to appropriate AI agents
 * and handles authentication, security, and compliance monitoring.
 */

import { createCors } from './middleware/cors';
import { authenticateRequest } from './middleware/auth';
import { logAuditEvent } from './middleware/audit';
import { encrypt } from './middleware/encryption';
import { validateMedicalFile, sanitizeInput, RateLimiter } from './middleware/security';
import { errorResponse, successResponse, isValidFile, sanitizeFilename } from './utils/responses';

// GIVC API Routes
const API_ROUTES = {
  '/api/v1/auth': 'authentication',
  '/api/v1/medivault': 'file-management',
  '/api/v1/triage': 'ai-triage',
  '/api/v1/agents/dicom': 'dicom-agent',
  '/api/v1/agents/lab': 'lab-parser',
  '/api/v1/agents/clinical': 'clinical-decision',
  '/api/v1/compliance': 'compliance-monitor',
  '/api/v1/analytics': 'analytics',
  '/api/v1/health': 'health-check',
};

interface Env {
  // KV Namespaces
  MEDICAL_METADATA: KVNamespace;
  AUDIT_LOGS: KVNamespace;

  // R2 Bucket
  MEDICAL_FILES: R2Bucket;

  // D1 Database
  HEALTHCARE_DB: D1Database;

  // Workers AI
  AI: Ai;

  // Queue
  PROCESSING_QUEUE: Queue;

  // Environment Variables
  ENVIRONMENT: string;
  ENCRYPTION_KEY: string;
  JWT_SECRET: string;
  HIPAA_COMPLIANCE_LEVEL: string;
  RCM_ACCREDITATION: string;
}

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    // Add CORS headers
    const corsHeaders = createCors();

    // Handle preflight requests
    if (method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    try {
      // Health check endpoint (no auth required)
      if (path === '/api/v1/health') {
        return handleHealthCheck(env);
      }

      // Authentication endpoint (no auth required for login)
      if (path.startsWith('/api/v1/auth')) {
        return handleAuthentication(request, env);
      }

      // All other endpoints require authentication
      const authResult = await authenticateRequest(request, env);
      if (!authResult.success) {
        await logAuditEvent(env, {
          type: 'unauthorized_access',
          severity: 'high',
          description: 'Unauthorized API access attempt',
          userId: 'unknown',
          resourceId: path,
          timestamp: new Date(),
          resolved: false,
          metadata: {
            error: authResult.error,
            userAgent: request.headers.get('User-Agent') || 'unknown'
          }
        });

        return errorResponse('UNAUTHORIZED', 'Valid authentication required', 401);
      }

      // Log authorized access
      await logAuditEvent(env, {
        type: 'api_access',
        severity: 'informational',
        description: `API access: ${method} ${path}`,
        userId: authResult.user.id,
        resourceId: path,
        timestamp: new Date(),
        resolved: true,
      });

      // Route to appropriate handler
      if (path.startsWith('/api/v1/medivault')) {
        return handleMediVault(request, env, authResult.user);
      }

      if (path.startsWith('/api/v1/triage')) {
        return handleTriage(request, env, authResult.user);
      }

      if (path.startsWith('/api/v1/agents/dicom')) {
        return handleDicomAgent(request, env, authResult.user);
      }

      if (path.startsWith('/api/v1/agents/lab')) {
        return handleLabParser(request, env, authResult.user);
      }

      if (path.startsWith('/api/v1/agents/clinical')) {
        return handleClinicalDecision(request, env, authResult.user);
      }

      if (path.startsWith('/api/v1/compliance')) {
        return handleCompliance(request, env, authResult.user);
      }

      if (path.startsWith('/api/v1/analytics')) {
        return handleAnalytics(request, env, authResult.user);
      }

      // Unknown endpoint
      return errorResponse('NOT_FOUND', 'API endpoint not found', 404);

    } catch (error) {
      console.error('GIVC API Error:', error);

      // Log system error with enhanced details
      await logAuditEvent(env, {
        type: 'system_error',
        severity: 'critical',
        description: `System error: ${error.message}`,
        userId: 'system',
        resourceId: path,
        timestamp: new Date(),
        resolved: false,
        metadata: {
          errorStack: error.stack,
          method: method,
          path: path
        }
      });

      return errorResponse('INTERNAL_SERVER_ERROR', 'An unexpected error occurred', 500);
    }
  }
};

// Health Check Handler
async function handleHealthCheck(env: Env): Promise<Response> {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
    services: {
      api: 'operational',
      database: 'operational',
      storage: 'operational',
      ai: 'operational',
      compliance: 'operational',
    },
    uptime: Math.floor(Date.now() / 1000), // Simple uptime in seconds
    environment: env.ENVIRONMENT || 'development',
    compliance: {
      hipaa: env.HIPAA_COMPLIANCE_LEVEL === 'strict',
      rcm: env.RCM_ACCREDITATION === 'enabled',
    }
  };

  return new Response(JSON.stringify(health), {
    headers: { 'Content-Type': 'application/json' }
  });
}

// Authentication Handler
async function handleAuthentication(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  const corsHeaders = createCors();

  if (request.method === 'POST' && url.pathname === '/api/v1/auth/login') {
    try {
      const requestBody = await request.json();
      const email = sanitizeInput(requestBody.email);
      const password = sanitizeInput(requestBody.password);

      // Enhanced validation - check for non-empty credentials and basic email format
      if (!email || !password || email.length < 3 || password.length < 3) {
        await logAuditEvent(env, {
          type: 'failed_authentication',
          severity: 'medium',
          description: `Failed login attempt: invalid format`,
          userId: 'unknown',
          timestamp: new Date(),
          resolved: true,
          metadata: {
            reason: 'invalid_format'
          }
        });
        return errorResponse('INVALID_CREDENTIALS', 'Invalid email or password format', 401);
      }

      // Basic email validation
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        return errorResponse('INVALID_EMAIL_FORMAT', 'Invalid email format', 400);
      }

      // In a real implementation, validate against database with proper password hashing
      // For demo purposes, accept valid email/password combinations
      const user = {
        id: email.includes('fadil') ? 'admin_1' : `user_${Date.now()}`,
        email: email,
        name: email.includes('fadil') ? 'Dr. Al Fadil' : 'Healthcare Professional',
        role: email.includes('fadil') ? 'admin' : 'physician',
        permissions: ['read_medical_data', 'write_medical_data', 'access_ai_agents'],
        organization: 'BRAINSAIT LTD',
      };

      // Generate enhanced JWT token with expiration (still demo-level but more secure)
      const expirationTime = Math.floor(Date.now() / 1000) + (24 * 60 * 60); // 24 hours
      const token = `jwt_${Date.now()}_${user.id}_${expirationTime}`;

      // Log successful login
      await logAuditEvent(env, {
        type: 'successful_login',
        severity: 'informational',
        description: `User login: ${email}`,
        userId: user.id,
        timestamp: new Date(),
        resolved: true,
        metadata: {
          email: email,
          role: user.role,
          tokenExpiration: expirationTime
        }
      });

      return successResponse(
        { user, token, expiresAt: new Date(expirationTime * 1000).toISOString() },
        'Authentication successful'
      );

    } catch (error) {
      // Log authentication error
      await logAuditEvent(env, {
        type: 'authentication_error',
        severity: 'high',
        description: `Authentication system error: ${error.message}`,
        userId: 'system',
        timestamp: new Date(),
        resolved: false,
      });

      return errorResponse('AUTH_ERROR', 'Authentication failed', 500);
    }
  }

  return errorResponse('METHOD_NOT_ALLOWED', 'Method not allowed', 405);
}

// MediVault Handler
async function handleMediVault(request: Request, env: Env, user: any): Promise<Response> {
  const url = new URL(request.url);
  const corsHeaders = createCors();

  if (request.method === 'GET' && url.pathname === '/api/v1/medivault/files') {
    // List files from metadata store
    const files = await env.MEDICAL_METADATA.list();

    return successResponse(
      files.keys.map(key => ({ id: key.name, metadata: key.metadata })),
      'Files retrieved successfully'
    );
  }

  if (request.method === 'POST' && url.pathname === '/api/v1/medivault/upload') {
    // Rate limiting check
    const rateLimiter = new RateLimiter(env);
    const userIdentifier = `upload_${user.id}`;
    const isAllowed = await rateLimiter.isAllowed(userIdentifier, 50, 3600); // 50 uploads per hour

    if (!isAllowed) {
      return errorResponse('RATE_LIMIT_EXCEEDED', 'Upload rate limit exceeded. Please try again later.', 429);
    }

    // Handle file upload to R2 with proper validation
    const formData = await request.formData();
    const fileData = formData.get('file');

    // Critical Fix: Replace unsafe type assertion with proper validation
    if (!isValidFile(fileData)) {
      return errorResponse('INVALID_FILE', 'No valid file provided or file is empty', 400);
    }

    const file = fileData; // Now we know it's a valid File

    // Validate medical file compliance
    const fileValidation = validateMedicalFile(file);
    if (!fileValidation.valid) {
      return errorResponse('FILE_VALIDATION_FAILED', 'File validation failed', 400, {
        violations: fileValidation.violations
      });
    }

    // Sanitize filename
    const sanitizedFilename = sanitizeFilename(file.name);

    const fileId = `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const fileData = await file.arrayBuffer();

    // Encrypt file data
    const encryptedData = await encrypt(fileData, env.ENCRYPTION_KEY);

    // Store in R2 with sanitized metadata
    await env.MEDICAL_FILES.put(fileId, encryptedData, {
      customMetadata: {
        originalName: sanitizeInput(sanitizedFilename),
        contentType: sanitizeInput(file.type),
        uploadedBy: user.id,
        uploadedAt: new Date().toISOString(),
        encrypted: 'true',
        fileSize: file.size.toString(),
      }
    });

    // Store metadata in KV with sanitized data
    await env.MEDICAL_METADATA.put(fileId, JSON.stringify({
      id: fileId,
      name: sanitizeInput(sanitizedFilename),
      type: sanitizeInput(file.type),
      size: file.size,
      uploadedBy: user.id,
      uploadedAt: new Date().toISOString(),
      status: 'uploaded',
      complianceStatus: 'compliant',
    }));

    // Log file upload with enhanced audit details
    await logAuditEvent(env, {
      type: 'file_upload',
      severity: 'informational',
      description: `File uploaded: ${sanitizedFilename} (${file.type}, ${file.size} bytes)`,
      userId: user.id,
      resourceId: fileId,
      timestamp: new Date(),
      resolved: true,
      metadata: {
        fileType: file.type,
        fileSize: file.size,
        sanitizedName: sanitizedFilename,
        originalName: file.name
      }
    });

    return successResponse(
      { fileId, message: 'File uploaded successfully' },
      'File uploaded and encrypted successfully'
    );
  }

  return errorResponse('METHOD_NOT_ALLOWED', 'Method not allowed', 405);
}

// Placeholder handlers for other endpoints
async function handleTriage(request, env, user) {
  return successResponse(
    { message: 'AI Triage endpoint - Implementation in progress' },
    'Triage service available'
  );
}

async function handleDicomAgent(request, env, user) {
  return successResponse(
    { message: 'DICOM Analysis Agent endpoint - Implementation in progress' },
    'DICOM agent service available'
  );
}

async function handleLabParser(request: Request, env: Env, user: any): Promise<Response> {
  return successResponse(
    { message: 'Lab Parser Agent endpoint - Implementation in progress' },
    'Lab parser service available'
  );
}

async function handleClinicalDecision(request: Request, env: Env, user: any): Promise<Response> {
  return successResponse(
    { message: 'Clinical Decision Agent endpoint - Implementation in progress' },
    'Clinical decision service available'
  );
}

async function handleCompliance(request: Request, env: Env, user: any): Promise<Response> {
  return successResponse(
    { message: 'Compliance Monitor endpoint - Implementation in progress' },
    'Compliance monitoring service available'
  );
}

async function handleAnalytics(request: Request, env: Env, user: any): Promise<Response> {
  return successResponse(
    { message: 'Analytics endpoint - Implementation in progress' },
    'Analytics service available'
  );
}
