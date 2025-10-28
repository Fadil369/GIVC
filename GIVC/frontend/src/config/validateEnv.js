/**
 * Environment Variable Validation
 * Ensures all required environment variables are present before app starts
 * 
 * HIPAA Compliance: Validates security-critical configuration
 */

const requiredEnvVars = [
  'VITE_APP_NAME',
  'VITE_API_BASE_URL',
  'VITE_HIPAA_COMPLIANCE_LEVEL',
];

const optionalEnvVars = [
  'VITE_CLOUDFLARE_ACCOUNT_ID',
  'VITE_CLOUDFLARE_ZONE_ID',
  'VITE_ENABLE_PWA',
  'VITE_ENABLE_ANALYTICS',
];

/**
 * Validates that all required environment variables are present
 * @throws {Error} If any required variables are missing
 */
export function validateEnv() {
  const missing = [];
  const warnings = [];

  // Check required variables
  requiredEnvVars.forEach(varName => {
    const value = import.meta.env[varName];
    if (!value || value === '' || value === 'undefined') {
      missing.push(varName);
    }
  });

  // Check optional but recommended variables
  optionalEnvVars.forEach(varName => {
    const value = import.meta.env[varName];
    if (!value || value === '' || value === 'undefined') {
      warnings.push(varName);
    }
  });

  // Throw error if required variables are missing
  if (missing.length > 0) {
    const errorMessage = `
╔═══════════════════════════════════════════════════════════╗
║  ⚠️  CRITICAL: Missing Required Environment Variables      ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  The following environment variables are required but     ║
║  were not found in your configuration:                    ║
║                                                           ║
${missing.map(v => `║  ❌ ${v.padEnd(55)} ║`).join('\n')}
║                                                           ║
║  To fix this:                                             ║
║  1. Copy .env.example to .env.local                       ║
║  2. Fill in the required values                           ║
║  3. Restart the development server                        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    `.trim();
    
    throw new Error(errorMessage);
  }

  // Log warnings for optional variables
  if (warnings.length > 0 && import.meta.env.DEV) {
    console.warn('⚠️ Optional environment variables not set:', warnings);
    console.warn('Some features may not work as expected.');
  }

  // Validate HIPAA compliance level
  const hipaaLevel = import.meta.env.VITE_HIPAA_COMPLIANCE_LEVEL;
  const validLevels = ['strict', 'moderate', 'minimal'];
  if (!validLevels.includes(hipaaLevel)) {
    console.warn(`⚠️ Invalid HIPAA_COMPLIANCE_LEVEL: "${hipaaLevel}". Expected one of: ${validLevels.join(', ')}`);
  }

  // Success message in development
  if (import.meta.env.DEV) {
    console.log('✅ Environment variables validated successfully');
    console.log('📊 Configuration:', {
      environment: import.meta.env.MODE,
      apiUrl: import.meta.env.VITE_API_BASE_URL,
      hipaaLevel,
    });
  }
}

/**
 * Gets an environment variable with optional default value
 * @param {string} key - Environment variable key
 * @param {string} defaultValue - Default value if not found
 * @returns {string} Environment variable value or default
 */
export function getEnv(key, defaultValue = '') {
  return import.meta.env[key] || defaultValue;
}

/**
 * Checks if a feature flag is enabled
 * @param {string} feature - Feature flag name (without VITE_ENABLE_ prefix)
 * @returns {boolean} True if feature is enabled
 */
export function isFeatureEnabled(feature) {
  const value = import.meta.env[`VITE_ENABLE_${feature.toUpperCase()}`];
  return value === 'true' || value === true;
}

/**
 * Gets configuration object with all environment variables
 * @returns {object} Configuration object
 */
export function getConfig() {
  return {
    app: {
      name: getEnv('VITE_APP_NAME', 'GIVC Healthcare Platform'),
      version: getEnv('VITE_APP_VERSION', '1.0.0'),
      environment: import.meta.env.MODE,
    },
    api: {
      baseUrl: getEnv('VITE_API_BASE_URL'),
      timeout: parseInt(getEnv('VITE_API_TIMEOUT', '30000')),
    },
    security: {
      hipaaLevel: getEnv('VITE_HIPAA_COMPLIANCE_LEVEL', 'strict'),
      rcmAccreditation: getEnv('VITE_RCM_ACCREDITATION', 'enabled'),
      auditLogging: getEnv('VITE_AUDIT_LOGGING', 'enabled'),
      encryptionEnabled: isFeatureEnabled('encryption'),
    },
    features: {
      pwa: isFeatureEnabled('pwa'),
      analytics: isFeatureEnabled('analytics'),
      errorReporting: isFeatureEnabled('error_reporting'),
      performanceMonitoring: isFeatureEnabled('performance_monitoring'),
    },
    fileUpload: {
      maxSizeMB: parseInt(getEnv('VITE_MAX_FILE_SIZE_MB', '100')),
      allowedTypes: getEnv('VITE_ALLOWED_FILE_TYPES', 'image/*,application/pdf,application/dicom'),
    },
  };
}
