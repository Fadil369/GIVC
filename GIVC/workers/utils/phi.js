/**
 * GIVC Healthcare Platform - PHI Detection and Masking
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * HIPAA-compliant PHI (Protected Health Information) detection and masking
 */

/**
 * PHI Detection Patterns
 */
const PHI_PATTERNS = {
  // Social Security Number (SSN)
  ssn: {
    regex: /\b\d{3}-\d{2}-\d{4}\b|\b\d{9}\b/g,
    description: 'Social Security Number',
    severity: 'critical'
  },
  
  // Phone Numbers
  phone: {
    regex: /\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b/g,
    description: 'Phone Number',
    severity: 'high'
  },
  
  // Email Addresses
  email: {
    regex: /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g,
    description: 'Email Address',
    severity: 'high'
  },
  
  // Medical Record Number (MRN)
  mrn: {
    regex: /\b(?:MRN|Medical Record Number|Patient ID|Chart #?):\s*([A-Z0-9-]+)\b/gi,
    description: 'Medical Record Number',
    severity: 'critical'
  },
  
  // Date of Birth
  dob: {
    regex: /\b(?:DOB|Date of Birth|Born):\s*(\d{1,2}\/\d{1,2}\/\d{4}|\d{4}-\d{2}-\d{2})\b/gi,
    description: 'Date of Birth',
    severity: 'critical'
  },
  
  // Credit Card Numbers (simplified)
  creditCard: {
    regex: /\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b/g,
    description: 'Credit Card Number',
    severity: 'critical'
  },
  
  // US Driver's License (various formats)
  driversLicense: {
    regex: /\b(?:DL|Driver's License|License #?):\s*([A-Z0-9]+)\b/gi,
    description: "Driver's License",
    severity: 'high'
  },
  
  // IP Addresses
  ipAddress: {
    regex: /\b(?:\d{1,3}\.){3}\d{1,3}\b/g,
    description: 'IP Address',
    severity: 'medium'
  },
  
  // Physical Addresses (simplified)
  address: {
    regex: /\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Way)\b/gi,
    description: 'Physical Address',
    severity: 'high'
  }
};

/**
 * Detect PHI in text
 * @param {string} text - Text to analyze
 * @returns {Object} Detection results
 */
export function detectPHI(text) {
  if (!text || typeof text !== 'string') {
    return {
      hasPHI: false,
      types: [],
      matches: []
    };
  }
  
  const detected = [];
  const matches = [];
  
  for (const [type, config] of Object.entries(PHI_PATTERNS)) {
    const found = text.match(config.regex);
    if (found && found.length > 0) {
      detected.push({
        type,
        description: config.description,
        severity: config.severity,
        count: found.length
      });
      
      matches.push(...found.map(match => ({
        type,
        value: match,
        severity: config.severity
      })));
    }
  }
  
  return {
    hasPHI: detected.length > 0,
    types: detected,
    matches,
    totalMatches: matches.length,
    riskLevel: calculateRiskLevel(detected)
  };
}

/**
 * Calculate risk level based on detected PHI
 * @param {Array} detected 
 * @returns {string}
 */
function calculateRiskLevel(detected) {
  if (detected.length === 0) return 'none';
  
  const hasCritical = detected.some(d => d.severity === 'critical');
  const hasHigh = detected.some(d => d.severity === 'high');
  
  if (hasCritical && detected.length >= 3) return 'critical';
  if (hasCritical) return 'high';
  if (hasHigh && detected.length >= 2) return 'high';
  if (hasHigh) return 'medium';
  return 'low';
}

/**
 * Mask PHI in text
 * @param {string} text - Text to mask
 * @param {Object} options - Masking options
 * @returns {string} Masked text
 */
export function maskPHI(text, options = {}) {
  if (!text || typeof text !== 'string') {
    return text;
  }
  
  const {
    maskChar = '*',
    preserveLength = false,
    customMasks = {}
  } = options;
  
  let masked = text;
  
  for (const [type, config] of Object.entries(PHI_PATTERNS)) {
    const customMask = customMasks[type];
    
    if (customMask === false) {
      // Skip this type
      continue;
    }
    
    masked = masked.replace(config.regex, (match) => {
      if (customMask) {
        return typeof customMask === 'function' ? customMask(match) : customMask;
      }
      
      if (preserveLength) {
        return maskChar.repeat(match.length);
      }
      
      return `[${type.toUpperCase()}_REDACTED]`;
    });
  }
  
  return masked;
}

/**
 * Sanitize object by masking PHI in all string properties
 * @param {Object} obj - Object to sanitize
 * @param {Object} options - Masking options
 * @returns {Object} Sanitized object
 */
export function sanitizePHI(obj, options = {}) {
  if (!obj || typeof obj !== 'object') {
    return obj;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => sanitizePHI(item, options));
  }
  
  const sanitized = {};
  
  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === 'string') {
      sanitized[key] = maskPHI(value, options);
    } else if (typeof value === 'object' && value !== null) {
      sanitized[key] = sanitizePHI(value, options);
    } else {
      sanitized[key] = value;
    }
  }
  
  return sanitized;
}

/**
 * Validate if text contains PHI (for logging/audit)
 * @param {string} text 
 * @returns {boolean}
 */
export function containsPHI(text) {
  const result = detectPHI(text);
  return result.hasPHI;
}

/**
 * Get PHI-safe version of text for logging
 * @param {string} text 
 * @returns {string}
 */
export function getSafeText(text) {
  const detection = detectPHI(text);
  
  if (!detection.hasPHI) {
    return text;
  }
  
  return maskPHI(text, { preserveLength: false });
}

/**
 * Validate PHI handling compliance
 * @param {Object} data - Data to validate
 * @returns {Object} Validation result
 */
export function validatePHICompliance(data) {
  const violations = [];
  
  // Check if data is encrypted
  if (!data.encrypted) {
    violations.push('Data is not encrypted');
  }
  
  // Check for unmasked PHI in logs
  if (data.logs) {
    for (const log of data.logs) {
      const detection = detectPHI(log.message);
      if (detection.hasPHI) {
        violations.push(`Unmasked PHI found in log: ${detection.types.map(t => t.type).join(', ')}`);
      }
    }
  }
  
  // Check for PHI in request metadata
  if (data.metadata) {
    const metadataStr = JSON.stringify(data.metadata);
    const detection = detectPHI(metadataStr);
    if (detection.hasPHI && detection.riskLevel !== 'low') {
      violations.push(`High-risk PHI found in metadata: ${detection.types.map(t => t.type).join(', ')}`);
    }
  }
  
  return {
    compliant: violations.length === 0,
    violations,
    recommendations: violations.length > 0 ? [
      'Encrypt all PHI before storage',
      'Mask PHI in logs and audit trails',
      'Use PHI detection before transmitting data'
    ] : []
  };
}
