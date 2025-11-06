/**
 * GIVC Healthcare Platform - Production Cryptography Utilities
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * HIPAA-compliant encryption using Web Crypto API with AES-256-GCM
 */

import { logger } from '../services/logger.js';

/**
 * Generate a random encryption key
 * @returns {Promise<CryptoKey>}
 */
export async function generateKey() {
  return await crypto.subtle.generateKey(
    {
      name: 'AES-GCM',
      length: 256
    },
    true,
    ['encrypt', 'decrypt']
  );
}

/**
 * Import a key from raw bytes
 * @param {ArrayBuffer|Uint8Array} keyData 
 * @returns {Promise<CryptoKey>}
 */
export async function importKey(keyData) {
  // Ensure keyData is 32 bytes for AES-256
  const encoder = new TextEncoder();
  let keyBytes;
  
  if (typeof keyData === 'string') {
    // Hash the string to get 32 bytes
    keyBytes = await crypto.subtle.digest('SHA-256', encoder.encode(keyData));
  } else if (keyData instanceof ArrayBuffer) {
    keyBytes = keyData;
  } else if (keyData instanceof Uint8Array) {
    keyBytes = keyData.buffer;
  } else {
    throw new Error('Invalid key data type');
  }

  return await crypto.subtle.importKey(
    'raw',
    keyBytes,
    { name: 'AES-GCM' },
    false,
    ['encrypt', 'decrypt']
  );
}

/**
 * Encrypt data using AES-256-GCM
 * @param {string|ArrayBuffer} data - Data to encrypt
 * @param {string|CryptoKey} key - Encryption key
 * @returns {Promise<string>} Base64-encoded encrypted data with IV
 */
export async function encrypt(data, key) {
  try {
    const encoder = new TextEncoder();
    
    // Import key if it's a string
    const cryptoKey = typeof key === 'string' ? await importKey(key) : key;
    
    // Generate random IV (12 bytes for GCM)
    const iv = crypto.getRandomValues(new Uint8Array(12));
    
    // Convert data to bytes
    const dataBytes = typeof data === 'string' 
      ? encoder.encode(data)
      : new Uint8Array(data);
    
    // Encrypt
    const encrypted = await crypto.subtle.encrypt(
      {
        name: 'AES-GCM',
        iv: iv,
        tagLength: 128
      },
      cryptoKey,
      dataBytes
    );
    
    // Combine IV and encrypted data
    const combined = new Uint8Array(iv.length + encrypted.byteLength);
    combined.set(iv, 0);
    combined.set(new Uint8Array(encrypted), iv.length);
    
    // Return as base64
    return btoa(String.fromCharCode(...combined));
  } catch (error) {
    logger.error('Encryption error', {
      errorMessage: error.message,
      errorStack: error.stack,
      operation: 'encrypt'
    });
    throw new Error('Failed to encrypt data');
  }
}

/**
 * Decrypt data using AES-256-GCM
 * @param {string} encryptedData - Base64-encoded encrypted data with IV
 * @param {string|CryptoKey} key - Decryption key
 * @returns {Promise<ArrayBuffer>} Decrypted data
 */
export async function decrypt(encryptedData, key) {
  try {
    // Import key if it's a string
    const cryptoKey = typeof key === 'string' ? await importKey(key) : key;
    
    // Decode base64
    const combined = Uint8Array.from(atob(encryptedData), c => c.charCodeAt(0));
    
    // Extract IV and encrypted data
    const iv = combined.slice(0, 12);
    const encrypted = combined.slice(12);
    
    // Decrypt
    const decrypted = await crypto.subtle.decrypt(
      {
        name: 'AES-GCM',
        iv: iv,
        tagLength: 128
      },
      cryptoKey,
      encrypted
    );
    
    return decrypted;
  } catch (error) {
    logger.error('Decryption error', {
      errorMessage: error.message,
      errorStack: error.stack,
      operation: 'decrypt'
    });
    throw new Error('Failed to decrypt data');
  }
}

/**
 * Decrypt and return as string
 * @param {string} encryptedData 
 * @param {string|CryptoKey} key 
 * @returns {Promise<string>}
 */
export async function decryptToString(encryptedData, key) {
  const decrypted = await decrypt(encryptedData, key);
  const decoder = new TextDecoder();
  return decoder.decode(decrypted);
}

/**
 * Hash data using SHA-256
 * @param {string} data 
 * @returns {Promise<string>} Hex-encoded hash
 */
export async function hash(data) {
  const encoder = new TextEncoder();
  const dataBytes = encoder.encode(data);
  const hashBuffer = await crypto.subtle.digest('SHA-256', dataBytes);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Hash password using bcrypt-like algorithm (using PBKDF2)
 * @param {string} password 
 * @param {number} rounds - Number of iterations (default 100000)
 * @returns {Promise<string>} Hashed password with salt
 */
export async function hashPassword(password, rounds = 100000) {
  const encoder = new TextEncoder();
  const salt = crypto.getRandomValues(new Uint8Array(16));
  
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    encoder.encode(password),
    'PBKDF2',
    false,
    ['deriveBits']
  );
  
  const derivedBits = await crypto.subtle.deriveBits(
    {
      name: 'PBKDF2',
      salt: salt,
      iterations: rounds,
      hash: 'SHA-256'
    },
    keyMaterial,
    256
  );
  
  const hashBytes = new Uint8Array(derivedBits);
  const hashHex = Array.from(hashBytes).map(b => b.toString(16).padStart(2, '0')).join('');
  const saltHex = Array.from(salt).map(b => b.toString(16).padStart(2, '0')).join('');
  
  // Format: $pbkdf2$rounds$salt$hash
  return `$pbkdf2$${rounds}$${saltHex}$${hashHex}`;
}

/**
 * Verify password against hash
 * @param {string} password 
 * @param {string} hash 
 * @returns {Promise<boolean>}
 */
export async function verifyPassword(password, hash) {
  try {
    const parts = hash.split('$');
    if (parts.length !== 5 || parts[1] !== 'pbkdf2') {
      throw new Error('Invalid hash format');
    }
    
    const rounds = parseInt(parts[2], 10);
    const saltHex = parts[3];
    const hashHex = parts[4];
    
    const encoder = new TextEncoder();
    const salt = new Uint8Array(saltHex.match(/.{1,2}/g).map(byte => parseInt(byte, 16)));
    
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      encoder.encode(password),
      'PBKDF2',
      false,
      ['deriveBits']
    );
    
    const derivedBits = await crypto.subtle.deriveBits(
      {
        name: 'PBKDF2',
        salt: salt,
        iterations: rounds,
        hash: 'SHA-256'
      },
      keyMaterial,
      256
    );
    
    const derivedHashHex = Array.from(new Uint8Array(derivedBits))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
    
    // Constant-time comparison
    return timingSafeEqual(derivedHashHex, hashHex);
  } catch (error) {
    logger.error('Password verification error', {
      errorMessage: error.message,
      errorStack: error.stack,
      operation: 'verifyPassword'
    });
    return false;
  }
}

/**
 * Timing-safe string comparison
 * @param {string} a 
 * @param {string} b 
 * @returns {boolean}
 */
function timingSafeEqual(a, b) {
  if (a.length !== b.length) {
    return false;
  }
  
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  
  return result === 0;
}

/**
 * Generate a random token
 * @param {number} length - Token length in bytes
 * @returns {string} Hex-encoded token
 */
export function generateToken(length = 32) {
  const bytes = crypto.getRandomValues(new Uint8Array(length));
  return Array.from(bytes).map(b => b.toString(16).padStart(2, '0')).join('');
}

/**
 * Generate a secure random UUID
 * @returns {string}
 */
export function generateUUID() {
  return crypto.randomUUID();
}
