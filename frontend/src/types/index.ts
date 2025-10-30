// Central export point for all type definitions and enums
// GIVC Healthcare Platform Type System

// Export all enums
export * from './enums';

// Export all insurance types
export * from './insurance';

// Re-export constants for backward compatibility
export const USER_ROLES = ['admin', 'physician', 'nurse', 'technician', 'billing_specialist', 'compliance_officer', 'patient'] as const;
export const PERMISSIONS = ['read_medical_data', 'write_medical_data', 'delete_medical_data', 'access_ai_agents', 'manage_users', 'view_compliance', 'manage_billing', 'export_data'] as const;
export const MEDICAL_FILE_TYPES = ['dicom', 'lab_result', 'clinical_note', 'prescription', 'insurance_document', 'patient_record', 'imaging_report', 'pathology_report'] as const;
export const FILE_CATEGORIES = ['radiology', 'laboratory', 'clinical', 'administrative', 'billing', 'insurance'] as const;
export const PROCESSING_STATUSES = ['uploading', 'queued', 'processing', 'completed', 'failed', 'requires_review'] as const;
export const URGENCY_LEVELS = ['emergency', 'urgent', 'semi_urgent', 'standard', 'non_urgent'] as const;
export const COMPLIANCE_STATUSES = ['compliant', 'non_compliant', 'under_review', 'requires_action'] as const;
