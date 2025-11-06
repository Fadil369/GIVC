/**
 * GIVC Healthcare Platform - Encryption Middleware
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * PRODUCTION VERSION - HIPAA-compliant AES-256-GCM encryption
 */

import { encrypt as cryptoEncrypt, decrypt as cryptoDecrypt } from '../utils/crypto.js';
import { detectPHI, maskPHI } from '../utils/phi.js';
import { logger } from '../services/logger.js';

/**
 * Encrypt data using AES-256-GCM
 * @param {string|Object|ArrayBuffer} data - Data to encrypt
 * @param {string} key - Encryption key (base64 or raw)
 * @returns {Promise<string>} Encrypted data with IV and auth tag
 */
export async function encrypt(data, key) {
  try {
    // Convert data to string if needed
    let plaintext;
    if (data instanceof ArrayBuffer) {
      const bytes = new Uint8Array(data);
      plaintext = String.fromCharCode(...bytes);
    } else if (typeof data === 'object') {
      plaintext = JSON.stringify(data);
    } else {
      plaintext = String(data);
    }

    // Detect PHI in plaintext
    const phiDetection = detectPHI(plaintext);
    if (phiDetection.detected && phiDetection.riskLevel !== 'none') {
      logger.warn('Encrypting data with PHI detected', {
        phiTypesCount: phiDetection.types.length,
        phiTypes: phiDetection.types,
        riskLevel: phiDetection.riskLevel,
        operation: 'encrypt',
        eventType: 'phi_encryption'
      });
    }

    // Encrypt using production AES-256-GCM
    return await cryptoEncrypt(plaintext, key);

  } catch (error) {
    throw new Error(`Encryption failed: ${error.message}`);
  }
}

/**
 * Decrypt data using AES-256-GCM
 * @param {string} encryptedData - Encrypted data (format: iv:authTag:ciphertext)
 * @param {string} key - Decryption key (base64 or raw)
 * @returns {Promise<Uint8Array>} Decrypted data as bytes
 */
export async function decrypt(encryptedData, key) {
  try {
    // Decrypt using production AES-256-GCM
    const decrypted = await cryptoDecrypt(encryptedData, key);
    
    // Return as Uint8Array for consistency
    return new TextEncoder().encode(decrypted);

  } catch (error) {
    throw new Error(`Decryption failed: ${error.message}`);
  }
}

/**
 * Check if data is encrypted (production format check)
 * @param {string} data - Data to check
 * @returns {boolean} True if data appears encrypted
 */
export function isEncrypted(data) {
  if (typeof data !== 'string') {
    return false;
  }
  
  // Production format: iv:authTag:ciphertext (hex:hex:base64)
  const parts = data.split(':');
  if (parts.length !== 3) {
    return false;
  }
  
  // Check if IV and auth tag are hex
  const hexPattern = /^[0-9a-f]+$/i;
  return hexPattern.test(parts[0]) && hexPattern.test(parts[1]);
}

/**
 * Encrypt file with metadata
 * @param {ArrayBuffer} fileData - File data
 * @param {string} key - Encryption key
 * @param {Object} metadata - File metadata
 * @returns {Promise<Object>} Encrypted file with metadata
 */
export async function encryptFile(fileData, key, metadata = {}) {
  try {
    // Convert file to base64
    const bytes = new Uint8Array(fileData);
    const base64Data = btoa(String.fromCharCode(...bytes));

    // Encrypt file data
    const encrypted = await encrypt(base64Data, key);

    // Create metadata with encryption info
    const encryptedMetadata = {
      ...metadata,
      encrypted: true,
      algorithm: 'AES-256-GCM',
      encryptedAt: new Date().toISOString(),
    };

    return {
      data: encrypted,
      metadata: encryptedMetadata,
    };

  } catch (error) {
    throw new Error(`File encryption failed: ${error.message}`);
  }
}

/**
 * Decrypt file with metadata validation
 * @param {string} encryptedData - Encrypted file data
 * @param {string} key - Decryption key
 * @param {Object} metadata - File metadata
 * @returns {Promise<ArrayBuffer>} Decrypted file data
 */
export async function decryptFile(encryptedData, key, metadata = {}) {
  try {
    // Validate metadata
    if (!metadata.encrypted || metadata.algorithm !== 'AES-256-GCM') {
      throw new Error('Invalid encryption metadata');
    }

    // Decrypt file data
    const decryptedBytes = await decrypt(encryptedData, key);
    
    // Convert from base64 to ArrayBuffer
    const base64Data = new TextDecoder().decode(decryptedBytes);
    const binaryString = atob(base64Data);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    return bytes.buffer;

  } catch (error) {
    throw new Error(`File decryption failed: ${error.message}`);
  }
}

/**
 * Encrypt sensitive fields in an object
 * @param {Object} obj - Object with sensitive fields
 * @param {string[]} fields - Field names to encrypt
 * @param {string} key - Encryption key
 * @returns {Promise<Object>} Object with encrypted fields
 */
export async function encryptFields(obj, fields, key) {
  const result = { ...obj };
  
  for (const field of fields) {
    if (obj[field]) {
      result[field] = await encrypt(obj[field], key);
    }
  }
  
  return result;
}

/**
 * Decrypt sensitive fields in an object
 * @param {Object} obj - Object with encrypted fields
 * @param {string[]} fields - Field names to decrypt
 * @param {string} key - Decryption key
 * @returns {Promise<Object>} Object with decrypted fields
 */
export async function decryptFields(obj, fields, key) {
  const result = { ...obj };
  
  for (const field of fields) {
    if (obj[field] && isEncrypted(obj[field])) {
      const decryptedBytes = await decrypt(obj[field], key);
      result[field] = new TextDecoder().decode(decryptedBytes);
    }
  }
  
  return result;
}

/**
 * Encrypt and mask PHI data
 * @param {string} data - Data containing PHI
 * @param {string} key - Encryption key
 * @returns {Promise<Object>} Encrypted data with PHI mask
 */
export async function encryptAndMaskPHI(data, key) {
  const phiDetection = detectPHI(data);
  
  return {
    encrypted: await encrypt(data, key),
    masked: maskPHI(data),
    phiDetected: phiDetection.detected,
    phiTypes: phiDetection.types,
    riskLevel: phiDetection.riskLevel,
  };
}