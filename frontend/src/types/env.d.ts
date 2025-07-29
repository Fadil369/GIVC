/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_NAME: string;
  readonly VITE_APP_VERSION: string;
  readonly VITE_APP_ENVIRONMENT: string;
  readonly VITE_API_BASE_URL: string;
  readonly VITE_API_TIMEOUT: string;
  readonly VITE_CLOUDFLARE_ACCOUNT_ID: string;
  readonly VITE_CLOUDFLARE_ZONE_ID: string;
  readonly VITE_JWT_EXPIRY_HOURS: string;
  readonly VITE_SESSION_TIMEOUT_MINUTES: string;
  readonly VITE_ENABLE_PWA: string;
  readonly VITE_ENABLE_ANALYTICS: string;
  readonly VITE_ENABLE_ERROR_REPORTING: string;
  readonly VITE_ENABLE_PERFORMANCE_MONITORING: string;
  readonly VITE_HIPAA_COMPLIANCE_LEVEL: string;
  readonly VITE_RCM_ACCREDITATION: string;
  readonly VITE_AUDIT_LOGGING: string;
  readonly VITE_MAX_FILE_SIZE_MB: string;
  readonly VITE_ALLOWED_FILE_TYPES: string;
  readonly VITE_CSP_ENABLED: string;
  readonly VITE_ENCRYPTION_ENABLED: string;
  readonly VITE_DEBUG_MODE: string;
  readonly VITE_SHOW_PERFORMANCE_METRICS: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare global {
  interface Window {
    // Analytics tracking
    gtag?: (...args: any[]) => void;
    dataLayer?: any[];
    
    // Error reporting
    Sentry?: {
      captureException: (error: Error) => void;
      captureMessage: (message: string) => void;
    };
    
    // Performance monitoring
    webVitals?: {
      getCLS: (callback: (metric: any) => void) => void;
      getFID: (callback: (metric: any) => void) => void;
      getFCP: (callback: (metric: any) => void) => void;
      getLCP: (callback: (metric: any) => void) => void;
      getTTFB: (callback: (metric: any) => void) => void;
    };
  }
}

export { };

