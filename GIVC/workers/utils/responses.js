/**
 * GIVC Healthcare Platform - Response Utilities
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Standardized response helpers for consistent API responses
 */

import { createCors } from '../middleware/cors.js';

/**
 * Generate a standardized error response
 * @param {string} code - Error code for client handling
 * @param {string} message - Human-readable error message
 * @param {number} status - HTTP status code
 * @param {Object} metadata - Additional error metadata
 * @returns {Response} Standardized error response
 */
export function errorResponse(code, message, status = 400, metadata = {}) {
  const corsHeaders = createCors();
  
  return new Response(JSON.stringify({
    success: false,
    error: { 
      code, 
      message,
      ...metadata
    },
    timestamp: new Date().toISOString(),
    requestId: `req_${Date.now()}`,
  }), {
    status,
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

/**
 * Generate a standardized success response
 * @param {Object} data - Response data
 * @param {string} message - Success message
 * @param {Object} metadata - Additional response metadata
 * @returns {Response} Standardized success response
 */
export function successResponse(data, message = 'Success', metadata = {}) {
  const corsHeaders = createCors();
  
  return new Response(JSON.stringify({
    success: true,
    data,
    message,
    timestamp: new Date().toISOString(),
    requestId: `req_${Date.now()}`,
    ...metadata
  }), {
    headers: { ...corsHeaders, 'Content-Type': 'application/json' }
  });
}

/**
 * Validate if an object is a File instance with proper checks
 * @param {any} obj - Object to validate
 * @returns {boolean} True if valid File, false otherwise
 */
export function isValidFile(obj) {
  return obj instanceof File && obj.size > 0 && obj.name && obj.name.trim() !== '';
}

/**
 * Sanitize filename to prevent path traversal and injection attacks
 * @param {string} filename - Original filename
 * @returns {string} Sanitized filename
 */
export function sanitizeFilename(filename) {
  if (!filename || typeof filename !== 'string') {
    return 'unknown_file';
  }
  
  return filename
    .replace(/[^a-zA-Z0-9._-]/g, '_') // Replace unsafe characters
    .replace(/\.{2,}/g, '.') // Prevent multiple consecutive dots
    .replace(/^\.+|\.+$/g, '') // Remove leading/trailing dots
    .substring(0, 255) // Limit length
    || 'sanitized_file'; // Fallback if everything was removed
}