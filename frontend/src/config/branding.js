// GIVC Healthcare Platform Branding Configuration
// © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited

export const GIVC_BRANDING = {
  // Company Information
  company: {
    name: "GIVC",
    fullName: "Global Integrated Virtual Care",
    tagline: "Advanced Healthcare Technology Solutions",
    owner: "Dr. Al Fadil",
    organization: "BRAINSAIT LTD",
    accreditation: "RCM Accredited Healthcare Technology Provider",
  },

  // Domain & URLs
  domain: {
    primary: "givc.thefadil.site",
    api: "givc.thefadil.site/api",
    cdn: "givc.thefadil.site/assets",
  },

  // Brand Colors (matching Tailwind config)
  colors: {
    primary: {
      main: "#3b82f6",      // GIVC Blue
      light: "#93c5fd",
      dark: "#1d4ed8",
      gradient: "linear-gradient(135deg, #3b82f6 0%, #22c55e 100%)",
    },
    secondary: {
      main: "#22c55e",      // GIVC Green
      light: "#86efac",
      dark: "#15803d",
    },
    medical: {
      critical: "#ef4444",   // Critical/Emergency
      high: "#f97316",       // High Priority
      medium: "#eab308",     // Medium Priority
      info: "#3b82f6",       // Information
      success: "#22c55e",    // Success/Normal
    },
    compliance: {
      secure: "#10b981",     // HIPAA Compliant
      warning: "#f59e0b",    // Compliance Warning
      violation: "#ef4444",  // Compliance Violation
    },
  },

  // Typography
  fonts: {
    primary: "Inter, system-ui, sans-serif",
    mono: "Fira Code, monospace",
    medical: "Inter, system-ui, sans-serif", // Professional medical font
  },

  // Logo & Assets
  assets: {
    logo: {
      text: "GIVC",
      icon: "🏥", // Temporary - replace with actual logo
      tagline: "Global Integrated Virtual Care",
    },
    badges: {
      rcm: "RCM Accredited",
      hipaa: "HIPAA Compliant",
      iso: "ISO 27001 Certified",
      fda: "FDA Validated AI",
    },
  },

  // UI Configuration
  ui: {
    borderRadius: "8px",
    shadowMedical: "0 4px 6px -1px rgba(59, 130, 246, 0.1)",
    shadowCompliance: "0 4px 6px -1px rgba(16, 185, 129, 0.1)",
    animations: {
      transition: "200ms",
      pulse: "3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
    },
  },

  // Medical Specialties
  specialties: [
    "Radiology & Medical Imaging",
    "Laboratory Medicine",
    "Clinical Decision Support",
    "Revenue Cycle Management",
    "Compliance & Audit",
    "Telemedicine & Virtual Care",
    "AI-Powered Diagnostics",
    "Electronic Health Records",
  ],

  // AI Agents Configuration
  agents: {
    dicom: {
      name: "DICOM Analysis Agent",
      description: "AI-powered medical imaging analysis with ResNet-50",
      capabilities: ["Image Analysis", "Measurement Extraction", "Report Generation"],
      confidence: 0.85,
    },
    labParser: {
      name: "Lab Results Parser",
      description: "OCR and text extraction for laboratory results",
      capabilities: ["OCR Processing", "Value Extraction", "Clinical Alerts"],
      confidence: 0.90,
    },
    clinicalDecision: {
      name: "Clinical Decision Support",
      description: "Differential diagnosis and treatment recommendations",
      capabilities: ["Diagnosis Generation", "Treatment Plans", "Clinical Guidelines"],
      confidence: 0.88,
    },
    compliance: {
      name: "Compliance Monitor",
      description: "Real-time HIPAA compliance and audit monitoring",
      capabilities: ["HIPAA Monitoring", "Audit Logging", "Violation Detection"],
      confidence: 0.95,
    },
  },

  // Compliance Standards
  compliance: {
    hipaa: {
      enabled: true,
      auditRetention: "7 years",
      encryption: "AES-256",
      accessControls: "Role-based",
    },
    rcm: {
      accredited: true,
      billingCodes: ["ICD-10", "CPT", "HCPCS"],
      claimsProcessing: true,
    },
    iso27001: {
      certified: true,
      securityFramework: "ISO 27001:2013",
      riskAssessment: "Annual",
    },
  },

  // Performance Requirements
  performance: {
    pageLoad: "< 3 seconds",
    aiProcessing: "< 5 seconds",
    uptime: "99.9%",
    concurrentUsers: "1000+",
  },

  // API Configuration
  api: {
    version: "v1",
    baseUrl: "/api/v1",
    endpoints: {
      auth: "/auth",
      medivault: "/medivault",
      triage: "/triage",
      agents: "/agents",
      compliance: "/compliance",
      analytics: "/analytics",
    },
  },

  // File Management
  fileTypes: {
    medical: [".dcm", ".jpg", ".png", ".pdf", ".hl7", ".xml"],
    documents: [".pdf", ".doc", ".docx", ".txt"],
    images: [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
    maxSize: "100MB",
    encryption: "AES-256-GCM",
  },
};

// Environment-specific overrides
export const getEnvironmentConfig = () => {
  const env = 'development'; // Default for client-side usage
  
  return {
    ...GIVC_BRANDING,
    environment: env,
    debug: env === 'development',
    apiUrl: env === 'production' 
      ? `https://${GIVC_BRANDING.domain.primary}/api`
      : 'http://localhost:8787/api',
  };
};

export default GIVC_BRANDING;
