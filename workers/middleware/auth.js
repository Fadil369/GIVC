/**
 * GIVC Healthcare Platform - Authentication Middleware
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 */

/**
 * Authenticate request with enhanced token validation
 * @param {Request} request - HTTP request object
 * @param {Object} env - Environment variables
 * @returns {Object} Authentication result with user info or error
 */
export async function authenticateRequest(request, env) {
  const authHeader = request.headers.get('Authorization');
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return { success: false, error: 'No valid authorization header' };
  }

  const token = authHeader.substring(7);
  
  // Enhanced token validation - support both old and new token formats
  if (token.startsWith('jwt_')) {
    // Parse token parts for enhanced validation
    const tokenParts = token.split('_');
    
    // New format: jwt_timestamp_userId_expiration
    if (tokenParts.length >= 4) {
      const expirationTime = parseInt(tokenParts[3]);
      const currentTime = Math.floor(Date.now() / 1000);
      
      // Check token expiration
      if (currentTime > expirationTime) {
        return { success: false, error: 'Token expired' };
      }
    }
    
    // Extract user info from token (simplified for demo)
    const user = {
      id: tokenParts.length >= 3 ? tokenParts[2] : '1',
      email: 'demo@givc.thefadil.site',
      name: 'Healthcare Professional',
      role: 'physician',
      permissions: ['read_medical_data', 'write_medical_data', 'access_ai_agents'],
      organization: 'BRAINSAIT LTD',
    };
    
    // Adjust user info based on ID
    if (user.id.includes('admin')) {
      user.email = 'admin@givc.thefadil.site';
      user.name = 'Dr. Al Fadil';
      user.role = 'admin';
      user.permissions.push('admin_access', 'user_management');
    }
    
    return { success: true, user };
  }

  return { success: false, error: 'Invalid token format' };
}

/**
 * Generate JWT token with enhanced security (demo version)
 * @param {Object} user - User object
 * @param {string} secret - JWT secret
 * @returns {string} JWT token
 */
export function generateJWT(user, secret) {
  // Enhanced JWT generation for demo with expiration
  const header = btoa(JSON.stringify({ alg: 'HS256', typ: 'JWT' }));
  const expirationTime = Math.floor(Date.now() / 1000) + (24 * 60 * 60); // 24 hours
  
  const payload = btoa(JSON.stringify({
    sub: user.id,
    email: user.email,
    role: user.role,
    exp: expirationTime,
    iat: Math.floor(Date.now() / 1000),
    iss: 'givc-healthcare',
  }));
  
  // In production, use proper HMAC signing with the secret
  const signature = btoa(`${header}.${payload}.${secret}`).substring(0, 32);
  
  return `${header}.${payload}.${signature}`;
}