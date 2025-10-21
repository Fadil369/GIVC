/**
 * GIVC Healthcare Platform - Cloudflare Access JWT Validation Worker
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * This worker validates Cloudflare Access JWT tokens and forwards
 * authenticated requests to the main application.
 * 
 * Based on Cloudflare Access documentation:
 * https://developers.cloudflare.com/cloudflare-one/tutorials/access-workers/
 */

import { logger } from './services/logger.js';

// Cloudflare Access Configuration
const ACCESS_CONFIG = {
  // Application Audience (AUD) tag from Cloudflare Access
  AUD: '5bc270d16bb84f830d04e92712d45cfdbf3527f3fdb8aecba8ec30296add9b22',
  
  // Your CF Access team domain
  TEAM_DOMAIN: 'https://fadil369.cloudflareaccess.com',
  
  // JWKs URL for token verification
  get CERTS_URL() {
    return `${this.TEAM_DOMAIN}/cdn-cgi/access/certs`;
  }
};

/**
 * Fetch and cache JWKs (JSON Web Key Set)
 */
class JWKSCache {
  constructor() {
    this.cache = null;
    this.cacheTime = 0;
    this.cacheTTL = 3600000; // 1 hour in milliseconds
  }

  async getKeys() {
    const now = Date.now();
    
    // Return cached keys if still valid
    if (this.cache && (now - this.cacheTime) < this.cacheTTL) {
      return this.cache;
    }

    // Fetch fresh keys
    try {
      const response = await fetch(ACCESS_CONFIG.CERTS_URL);
      if (!response.ok) {
        throw new Error(`Failed to fetch JWKs: ${response.status}`);
      }
      
      const jwks = await response.json();
      this.cache = jwks;
      this.cacheTime = now;
      
      return jwks;
    } catch (error) {
      logger.error('Error fetching JWKs', {
        errorMessage: error.message,
        certsUrl: ACCESS_CONFIG.CERTS_URL,
        operation: 'getKeys'
      });
      
      // Return cached keys if available, even if expired
      if (this.cache) {
        logger.warn('Using expired JWKS cache due to fetch error', {
          cacheAge: Date.now() - this.cacheTime
        });
        return this.cache;
      }
      
      throw error;
    }
  }
}

const jwksCache = new JWKSCache();

/**
 * Verify JWT token using Web Crypto API
 */
async function verifyJWT(token) {
  try {
    // Parse JWT without verification first
    const parts = token.split('.');
    if (parts.length !== 3) {
      throw new Error('Invalid JWT format');
    }

    // Decode header and payload
    const header = JSON.parse(atob(parts[0]));
    const payload = JSON.parse(atob(parts[1]));

    // Check if token is expired
    const now = Math.floor(Date.now() / 1000);
    if (payload.exp && payload.exp < now) {
      throw new Error('Token expired');
    }

    // Verify issuer and audience
    if (payload.iss !== ACCESS_CONFIG.TEAM_DOMAIN) {
      throw new Error('Invalid issuer');
    }

    if (payload.aud && !payload.aud.includes(ACCESS_CONFIG.AUD)) {
      throw new Error('Invalid audience');
    }

    // Get JWKs for signature verification
    const jwks = await jwksCache.getKeys();
    
    // Find matching key
    const key = jwks.keys.find(k => k.kid === header.kid);
    if (!key) {
      throw new Error('No matching key found in JWKS');
    }

    // Import the public key
    const cryptoKey = await crypto.subtle.importKey(
      'jwk',
      key,
      {
        name: 'RSASSA-PKCS1-v1_5',
        hash: 'SHA-256'
      },
      false,
      ['verify']
    );

    // Verify signature
    const encoder = new TextEncoder();
    const data = encoder.encode(`${parts[0]}.${parts[1]}`);
    const signature = base64UrlDecode(parts[2]);

    const isValid = await crypto.subtle.verify(
      'RSASSA-PKCS1-v1_5',
      cryptoKey,
      signature,
      data
    );

    if (!isValid) {
      throw new Error('Invalid signature');
    }

    return {
      valid: true,
      payload: payload,
      user: {
        email: payload.email || 'unknown',
        id: payload.sub || 'unknown',
        name: payload.name || 'Unknown User',
        groups: payload.groups || [],
        country: payload.country || null,
        idp: payload.idp || null
      }
    };
  } catch (error) {
    return {
      valid: false,
      error: error.message
    };
  }
}

/**
 * Base64 URL decode
 */
function base64UrlDecode(str) {
  // Replace URL-safe characters
  str = str.replace(/-/g, '+').replace(/_/g, '/');
  
  // Add padding
  while (str.length % 4) {
    str += '=';
  }
  
  // Decode base64
  const binary = atob(str);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  
  return bytes.buffer;
}

/**
 * Verify Cloudflare Access JWT Token
 */
async function verifyAccessToken(request) {
  // Check for AUD configuration
  if (!ACCESS_CONFIG.AUD) {
    return {
      valid: false,
      status: 500,
      message: 'Missing required audience configuration'
    };
  }

  // Get token from header
  const token = request.headers.get('cf-access-jwt-assertion');

  if (!token) {
    return {
      valid: false,
      status: 403,
      message: 'Missing required CF Access JWT token'
    };
  }

  // Verify the token
  const verification = await verifyJWT(token);
  
  if (!verification.valid) {
    return {
      valid: false,
      status: 403,
      message: `Invalid token: ${verification.error}`
    };
  }

  return {
    valid: true,
    payload: verification.payload,
    user: verification.user
  };
}

/**
 * Create CORS headers
 */
function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, cf-access-jwt-assertion',
    'Access-Control-Max-Age': '86400'
  };
}

/**
 * Create JSON response
 */
function jsonResponse(data, status = 200, additionalHeaders = {}) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...corsHeaders(),
      ...additionalHeaders
    }
  });
}

/**
 * Main Worker Handler
 */
export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: corsHeaders()
      });
    }

    // Health check endpoint (no auth required)
    if (url.pathname === '/health' || url.pathname === '/api/v1/health') {
      return jsonResponse({
        status: 'healthy',
        service: 'access-validator',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
      });
    }

    // Verify Access token
    const verification = await verifyAccessToken(request);

    if (!verification.valid) {
      return jsonResponse(
        {
          status: false,
          message: verification.message,
          code: 'UNAUTHORIZED'
        },
        verification.status
      );
    }

    // Log successful authentication
    logger.info('Access verification successful', {
      userEmail: verification.user.email,
      userId: verification.user.id,
      path: url.pathname,
      method: request.method,
      timestamp: new Date().toISOString(),
      eventType: 'authentication_success'
    });

    // Add user info to request headers for downstream services
    const modifiedRequest = new Request(request);
    modifiedRequest.headers.set('X-User-Email', verification.user.email);
    modifiedRequest.headers.set('X-User-ID', verification.user.id);
    modifiedRequest.headers.set('X-User-Name', verification.user.name);
    modifiedRequest.headers.set('X-User-Groups', JSON.stringify(verification.user.groups));
    modifiedRequest.headers.set('X-Authenticated', 'true');
    modifiedRequest.headers.set('X-Auth-Method', 'cloudflare-access');

    // Return success response for validation endpoint
    if (url.pathname === '/validate' || url.pathname === '/api/v1/validate') {
      return jsonResponse({
        status: true,
        message: 'Token validation successful',
        user: {
          email: verification.user.email,
          id: verification.user.id,
          name: verification.user.name,
          groups: verification.user.groups
        },
        authenticated: true,
        timestamp: new Date().toISOString()
      });
    }

    // For other endpoints, you can forward to your main application
    // or return the validated user information
    return jsonResponse({
      status: true,
      message: 'Access validated',
      user: verification.user,
      hint: 'Forward this request to your application backend with the X-User-* headers'
    });
  }
};
