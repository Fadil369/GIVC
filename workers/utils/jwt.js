/**
 * GIVC Healthcare Platform - Production JWT Utilities
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Production-grade JWT signing and verification using Web Crypto API
 */

import { importKey } from './crypto.js';

/**
 * Base64URL encode
 * @param {ArrayBuffer|Uint8Array} data 
 * @returns {string}
 */
function base64UrlEncode(data) {
  const bytes = data instanceof ArrayBuffer ? new Uint8Array(data) : data;
  const base64 = btoa(String.fromCharCode(...bytes));
  return base64
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

/**
 * Base64URL decode
 * @param {string} str 
 * @returns {Uint8Array}
 */
function base64UrlDecode(str) {
  str = str.replace(/-/g, '+').replace(/_/g, '/');
  while (str.length % 4) {
    str += '=';
  }
  const binary = atob(str);
  return Uint8Array.from(binary, c => c.charCodeAt(0));
}

/**
 * Sign a JWT token
 * @param {Object} payload - JWT payload
 * @param {string} secret - Signing secret
 * @param {Object} options - Options (expiresIn, issuer, audience)
 * @returns {Promise<string>} JWT token
 */
export async function signJWT(payload, secret, options = {}) {
  const encoder = new TextEncoder();
  
  // Prepare header
  const header = {
    alg: 'HS256',
    typ: 'JWT'
  };
  
  // Prepare payload with claims
  const now = Math.floor(Date.now() / 1000);
  const claims = {
    ...payload,
    iat: now,
    ...(options.expiresIn && { exp: now + options.expiresIn }),
    ...(options.issuer && { iss: options.issuer }),
    ...(options.audience && { aud: options.audience })
  };
  
  // Encode header and payload
  const headerEncoded = base64UrlEncode(encoder.encode(JSON.stringify(header)));
  const payloadEncoded = base64UrlEncode(encoder.encode(JSON.stringify(claims)));
  
  // Create signing input
  const signingInput = `${headerEncoded}.${payloadEncoded}`;
  
  // Import secret as key
  const keyData = await crypto.subtle.digest('SHA-256', encoder.encode(secret));
  const key = await crypto.subtle.importKey(
    'raw',
    keyData,
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );
  
  // Sign
  const signature = await crypto.subtle.sign(
    'HMAC',
    key,
    encoder.encode(signingInput)
  );
  
  const signatureEncoded = base64UrlEncode(new Uint8Array(signature));
  
  return `${signingInput}.${signatureEncoded}`;
}

/**
 * Verify and decode a JWT token
 * @param {string} token - JWT token
 * @param {string} secret - Verification secret
 * @param {Object} options - Options (issuer, audience)
 * @returns {Promise<Object>} Decoded payload
 */
export async function verifyJWT(token, secret, options = {}) {
  const encoder = new TextEncoder();
  
  // Split token
  const parts = token.split('.');
  if (parts.length !== 3) {
    throw new Error('Invalid JWT format');
  }
  
  const [headerEncoded, payloadEncoded, signatureEncoded] = parts;
  
  // Decode header and payload
  const header = JSON.parse(new TextDecoder().decode(base64UrlDecode(headerEncoded)));
  const payload = JSON.parse(new TextDecoder().decode(base64UrlDecode(payloadEncoded)));
  
  // Verify algorithm
  if (header.alg !== 'HS256') {
    throw new Error('Unsupported algorithm');
  }
  
  // Verify signature
  const signingInput = `${headerEncoded}.${payloadEncoded}`;
  const keyData = await crypto.subtle.digest('SHA-256', encoder.encode(secret));
  const key = await crypto.subtle.importKey(
    'raw',
    keyData,
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['verify']
  );
  
  const signature = base64UrlDecode(signatureEncoded);
  const valid = await crypto.subtle.verify(
    'HMAC',
    key,
    signature,
    encoder.encode(signingInput)
  );
  
  if (!valid) {
    throw new Error('Invalid signature');
  }
  
  // Verify expiration
  const now = Math.floor(Date.now() / 1000);
  if (payload.exp && payload.exp < now) {
    throw new Error('Token expired');
  }
  
  // Verify issuer
  if (options.issuer && payload.iss !== options.issuer) {
    throw new Error('Invalid issuer');
  }
  
  // Verify audience
  if (options.audience) {
    const audiences = Array.isArray(payload.aud) ? payload.aud : [payload.aud];
    if (!audiences.includes(options.audience)) {
      throw new Error('Invalid audience');
    }
  }
  
  return {
    header,
    payload,
    valid: true
  };
}

/**
 * Decode JWT without verification (for debugging)
 * @param {string} token 
 * @returns {Object}
 */
export function decodeJWT(token) {
  const parts = token.split('.');
  if (parts.length !== 3) {
    throw new Error('Invalid JWT format');
  }
  
  const header = JSON.parse(new TextDecoder().decode(base64UrlDecode(parts[0])));
  const payload = JSON.parse(new TextDecoder().decode(base64UrlDecode(parts[1])));
  
  return { header, payload };
}
