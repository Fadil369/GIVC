/**
 * GIVC Healthcare Platform - Authentication Middleware
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * PRODUCTION VERSION - HIPAA-compliant authentication
 */

import { verifyJWT, signJWT } from '../utils/jwt.js';
import { verifyPassword } from '../utils/crypto.js';
import { generateUUID } from '../utils/crypto.js';
import { logSecurityEvent, logAudit } from './audit.js';

/**
 * Authenticate request with production JWT validation
 * @param {Request} request - HTTP request object
 * @param {Object} env - Environment variables (D1, KV, secrets)
 * @returns {Object} Authentication result with user info or error
 */
export async function authenticateRequest(request, env) {
  const authHeader = request.headers.get('Authorization');
  const clientIp = request.headers.get('CF-Connecting-IP') || 'unknown';
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    await logSecurityEvent(env, {
      type: 'auth_missing_header',
      severity: 'medium',
      clientIp,
      reason: 'Missing or invalid Authorization header',
    });
    return { success: false, error: 'No valid authorization header' };
  }

  const token = authHeader.substring(7);
  
  try {
    // Verify JWT signature and expiration
    const payload = await verifyJWT(token, env.JWT_SECRET);
    
    if (!payload) {
      await logSecurityEvent(env, {
        type: 'auth_invalid_token',
        severity: 'high',
        clientIp,
        reason: 'Invalid JWT signature or expired token',
      });
      return { success: false, error: 'Invalid or expired token' };
    }

    // Fetch user from D1 database
    const user = await env.DB.prepare(
      'SELECT id, email, name, role, permissions, organization, active FROM users WHERE id = ? AND active = 1'
    ).bind(payload.sub).first();

    if (!user) {
      await logSecurityEvent(env, {
        type: 'auth_user_not_found',
        severity: 'high',
        clientIp,
        userId: payload.sub,
        reason: 'User not found or inactive',
      });
      return { success: false, error: 'User not found or inactive' };
    }

    // Parse permissions from JSON
    user.permissions = user.permissions ? JSON.parse(user.permissions) : [];

    // Check session validity
    const sessionHash = await hashToken(token);
    const session = await env.DB.prepare(
      'SELECT id, expires_at, active FROM sessions WHERE token_hash = ? AND active = 1'
    ).bind(sessionHash).first();

    if (!session) {
      await logSecurityEvent(env, {
        type: 'auth_session_invalid',
        severity: 'high',
        clientIp,
        userId: user.id,
        reason: 'Session not found or inactive',
      });
      return { success: false, error: 'Session invalid' };
    }

    // Update session activity
    await env.DB.prepare(
      'UPDATE sessions SET last_activity = datetime("now") WHERE id = ?'
    ).bind(session.id).run();

    // Log successful authentication
    await logAudit(env, {
      type: 'authentication_success',
      severity: 'informational',
      description: `User ${user.email} authenticated successfully`,
      userId: user.id,
      clientIp,
    });

    return { 
      success: true, 
      user,
      sessionId: session.id
    };

  } catch (error) {
    await logSecurityEvent(env, {
      type: 'auth_error',
      severity: 'critical',
      clientIp,
      reason: `Authentication error: ${error.message}`,
    });
    
    return { 
      success: false, 
      error: 'Authentication failed',
      details: error.message 
    };
  }
}

/**
 * Login user with email and password
 * @param {string} email - User email
 * @param {string} password - User password (plain text)
 * @param {Object} env - Environment variables
 * @param {Request} request - HTTP request for logging
 * @returns {Object} Login result with token or error
 */
export async function loginUser(email, password, env, request) {
  const clientIp = request.headers.get('CF-Connecting-IP') || 'unknown';
  const userAgent = request.headers.get('User-Agent') || 'unknown';

  try {
    // Fetch user from database
    const user = await env.DB.prepare(
      'SELECT id, email, name, role, permissions, password_hash, organization, active FROM users WHERE email = ?'
    ).bind(email).first();

    if (!user) {
      await logSecurityEvent(env, {
        type: 'login_failed_user_not_found',
        severity: 'medium',
        clientIp,
        reason: `Login attempt for non-existent user: ${email}`,
      });
      
      // Generic error to prevent user enumeration
      return { 
        success: false, 
        error: 'Invalid credentials' 
      };
    }

    if (!user.active) {
      await logSecurityEvent(env, {
        type: 'login_failed_inactive_user',
        severity: 'high',
        clientIp,
        userId: user.id,
        reason: `Login attempt for inactive user: ${email}`,
      });
      
      return { 
        success: false, 
        error: 'Account is inactive' 
      };
    }

    // Verify password
    const isValidPassword = await verifyPassword(password, user.password_hash);

    if (!isValidPassword) {
      await logSecurityEvent(env, {
        type: 'login_failed_invalid_password',
        severity: 'high',
        clientIp,
        userId: user.id,
        reason: `Invalid password for user: ${email}`,
      });
      
      return { 
        success: false, 
        error: 'Invalid credentials' 
      };
    }

    // Generate JWT
    const token = await signJWT(
      {
        sub: user.id,
        email: user.email,
        role: user.role,
        iss: 'givc-healthcare',
        aud: 'givc-platform',
      },
      env.JWT_SECRET,
      '24h'
    );

    // Create session
    const sessionId = generateUUID();
    const tokenHash = await hashToken(token);
    const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString();

    await env.DB.prepare(`
      INSERT INTO sessions (id, user_id, token_hash, created_at, expires_at, last_activity, client_ip, user_agent, active)
      VALUES (?, ?, ?, datetime('now'), ?, datetime('now'), ?, ?, 1)
    `).bind(sessionId, user.id, tokenHash, expiresAt, clientIp, userAgent).run();

    // Update last login
    await env.DB.prepare(
      'UPDATE users SET last_login = datetime("now") WHERE id = ?'
    ).bind(user.id).run();

    // Log successful login
    await logAudit(env, {
      type: 'user_login',
      severity: 'informational',
      description: `User ${user.email} logged in successfully`,
      userId: user.id,
      clientIp,
    });

    // Parse permissions
    const permissions = user.permissions ? JSON.parse(user.permissions) : [];

    return {
      success: true,
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role,
        permissions,
        organization: user.organization,
      },
    };

  } catch (error) {
    await logSecurityEvent(env, {
      type: 'login_error',
      severity: 'critical',
      clientIp,
      reason: `Login error: ${error.message}`,
    });

    return {
      success: false,
      error: 'Login failed',
      details: error.message,
    };
  }
}

/**
 * Logout user by invalidating session
 * @param {string} token - JWT token
 * @param {Object} env - Environment variables
 * @returns {Object} Logout result
 */
export async function logoutUser(token, env) {
  try {
    const tokenHash = await hashToken(token);

    // Mark session as inactive
    await env.DB.prepare(
      'UPDATE sessions SET active = 0, logout_at = datetime("now") WHERE token_hash = ?'
    ).bind(tokenHash).run();

    return { success: true };
  } catch (error) {
    return { 
      success: false, 
      error: 'Logout failed',
      details: error.message 
    };
  }
}

/**
 * Hash token for session storage (SHA-256)
 * @param {string} token - JWT token
 * @returns {Promise<string>} Hex-encoded hash
 */
async function hashToken(token) {
  const encoder = new TextEncoder();
  const data = encoder.encode(token);
  const hash = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}