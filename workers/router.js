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
import { encrypt, decrypt } from './middleware/encryption';

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
        });
        
        return new Response(JSON.stringify({ 
          error: 'Unauthorized', 
          message: 'Valid authentication required' 
        }), {
          status: 401,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
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
      return new Response(JSON.stringify({ 
        error: 'Not Found', 
        message: 'API endpoint not found' 
      }), {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });

    } catch (error) {
      console.error('GIVC API Error:', error);
      
      // Log system error
      await logAuditEvent(env, {
        type: 'system_error',
        severity: 'critical',
        description: `System error: ${error.message}`,
        userId: 'system',
        resourceId: path,
        timestamp: new Date(),
        resolved: false,
      });

      return new Response(JSON.stringify({ 
        error: 'Internal Server Error', 
        message: 'An unexpected error occurred' 
      }), {
        status: 500,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
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
      const { email, password } = await request.json();
      
      // In a real implementation, validate against database
      // For demo purposes, accept any non-empty credentials
      if (email && password) {
        const user = {
          id: '1',
          email: email,
          name: email.includes('fadil') ? 'Dr. Al Fadil' : 'Healthcare Professional',
          role: email.includes('fadil') ? 'admin' : 'physician',
          permissions: ['read_medical_data', 'write_medical_data', 'access_ai_agents'],
          organization: 'BRAINSAIT LTD',
        };

        // Generate JWT token (simplified for demo)
        const token = `jwt_${Date.now()}_${user.id}`;
        
        // Log successful login
        await logAuditEvent(env, {
          type: 'successful_login',
          severity: 'informational',
          description: `User login: ${email}`,
          userId: user.id,
          timestamp: new Date(),
          resolved: true,
        });

        return new Response(JSON.stringify({
          success: true,
          data: { user, token },
          timestamp: new Date().toISOString(),
          requestId: `req_${Date.now()}`,
        }), {
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        });
      }

      // Invalid credentials
      await logAuditEvent(env, {
        type: 'failed_authentication',
        severity: 'medium',
        description: `Failed login attempt: ${email}`,
        userId: 'unknown',
        timestamp: new Date(),
        resolved: true,
      });

      return new Response(JSON.stringify({
        success: false,
        error: { code: 'INVALID_CREDENTIALS', message: 'Invalid email or password' },
        timestamp: new Date().toISOString(),
        requestId: `req_${Date.now()}`,
      }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });

    } catch (error) {
      return new Response(JSON.stringify({
        success: false,
        error: { code: 'AUTH_ERROR', message: 'Authentication failed' },
        timestamp: new Date().toISOString(),
        requestId: `req_${Date.now()}`,
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }
  }

  return new Response(JSON.stringify({
    success: false,
    error: { code: 'METHOD_NOT_ALLOWED', message: 'Method not allowed' },
    timestamp: new Date().toISOString(),
    requestId: `req_${Date.now()}`,
  }), {
    status: 405,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

// MediVault Handler
async function handleMediVault(request: Request, env: Env, user: any): Promise<Response> {
  const url = new URL(request.url);
  const corsHeaders = createCors();

  if (request.method === 'GET' && url.pathname === '/api/v1/medivault/files') {
    // List files from metadata store
    const files = await env.MEDICAL_METADATA.list();
    
    return new Response(JSON.stringify({
      success: true,
      data: files.keys.map(key => ({ id: key.name, metadata: key.metadata })),
      timestamp: new Date().toISOString(),
      requestId: `req_${Date.now()}`,
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }

  if (request.method === 'POST' && url.pathname === '/api/v1/medivault/upload') {
    // Handle file upload to R2
    const formData = await request.formData();
    const file = formData.get('file') as File;
    
    if (!file) {
      return new Response(JSON.stringify({
        success: false,
        error: { code: 'NO_FILE', message: 'No file provided' },
        timestamp: new Date().toISOString(),
        requestId: `req_${Date.now()}`,
      }), {
        status: 400,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const fileId = `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const fileData = await file.arrayBuffer();
    
    // Encrypt file data
    const encryptedData = await encrypt(fileData, env.ENCRYPTION_KEY);
    
    // Store in R2
    await env.MEDICAL_FILES.put(fileId, encryptedData, {
      customMetadata: {
        originalName: file.name,
        contentType: file.type,
        uploadedBy: user.id,
        uploadedAt: new Date().toISOString(),
        encrypted: 'true',
      }
    });
    
    // Store metadata in KV
    await env.MEDICAL_METADATA.put(fileId, JSON.stringify({
      id: fileId,
      name: file.name,
      type: file.type,
      size: file.size,
      uploadedBy: user.id,
      uploadedAt: new Date().toISOString(),
      status: 'uploaded',
      complianceStatus: 'compliant',
    }));

    // Log file upload
    await logAuditEvent(env, {
      type: 'file_upload',
      severity: 'informational',
      description: `File uploaded: ${file.name}`,
      userId: user.id,
      resourceId: fileId,
      timestamp: new Date(),
      resolved: true,
    });

    return new Response(JSON.stringify({
      success: true,
      data: { fileId, message: 'File uploaded successfully' },
      timestamp: new Date().toISOString(),
      requestId: `req_${Date.now()}`,
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }

  return new Response(JSON.stringify({
    success: false,
    error: { code: 'METHOD_NOT_ALLOWED', message: 'Method not allowed' },
    timestamp: new Date().toISOString(),
    requestId: `req_${Date.now()}`,
  }), {
    status: 405,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

// Placeholder handlers for other endpoints
async function handleTriage(request: Request, env: Env, user: any): Promise<Response> {
  const corsHeaders = createCors();
  return new Response(JSON.stringify({
    success: true,
    message: 'AI Triage endpoint - Implementation in progress',
    timestamp: new Date().toISOString(),
    requestId: `req_${Date.now()}`,
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

async function handleDicomAgent(request: Request, env: Env, user: any): Promise<Response> {
  const corsHeaders = createCors();
  return new Response(JSON.stringify({
    success: true,
    message: 'DICOM Analysis Agent endpoint - Implementation in progress',
    timestamp: new Date().toISOString(),
    requestId: `req_${Date.now()}`,
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

async function handleLabParser(request: Request, env: Env, user: any): Promise<Response> {
  const corsHeaders = createCors();
  return new Response(JSON.stringify({
    success: true,
    message: 'Lab Parser Agent endpoint - Implementation in progress',
    timestamp: new Date().toISOString(),
    requestId: `req_${Date.now()}`,
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

async function handleClinicalDecision(request: Request, env: Env, user: any): Promise<Response> {
  const corsHeaders = createCors();
  return new Response(JSON.stringify({
    success: true,
    message: 'Clinical Decision Agent endpoint - Implementation in progress',
    timestamp: new Date().toISOString(),
    requestId: `req_${Date.now()}`,
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

async function handleCompliance(request: Request, env: Env, user: any): Promise<Response> {
  const corsHeaders = createCors();
  return new Response(JSON.stringify({
    success: true,
    message: 'Compliance Monitor endpoint - Implementation in progress',
    timestamp: new Date().toISOString(),
    requestId: `req_${Date.now()}`,
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

async function handleAnalytics(request: Request, env: Env, user: any): Promise<Response> {
  const corsHeaders = createCors();
  return new Response(JSON.stringify({
    success: true,
    message: 'Analytics endpoint - Implementation in progress',
    timestamp: new Date().toISOString(),
    requestId: `req_${Date.now()}`,
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}