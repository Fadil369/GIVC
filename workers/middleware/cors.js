/**
 * GIVC Healthcare Platform - CORS Middleware
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 */

export function createCors() {
  return {
    'Access-Control-Allow-Origin': '*', // In production, set to specific domain
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With, X-Encryption-Status, X-Audit-Required',
    'Access-Control-Max-Age': '86400',
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  };
}