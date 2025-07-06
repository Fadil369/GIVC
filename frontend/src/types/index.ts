// Type definitions for GIVC Healthcare Platform

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  permissions: Permission[];
  lastLogin?: Date;
  avatar?: string;
  organization?: string;
  specialty?: string;
}

export type UserRole = 
  | 'admin' 
  | 'physician' 
  | 'nurse' 
  | 'technician' 
  | 'billing_specialist' 
  | 'compliance_officer' 
  | 'patient';

export type Permission = 
  | 'read_medical_data'
  | 'write_medical_data'
  | 'delete_medical_data'
  | 'access_ai_agents'
  | 'manage_users'
  | 'view_compliance'
  | 'manage_billing'
  | 'export_data';

// Medical File Types
export interface MedicalFile {
  id: string;
  name: string;
  type: MedicalFileType;
  size: number;
  uploadedAt: Date;
  uploadedBy: string;
  category: FileCategory;
  status: ProcessingStatus;
  url?: string;
  metadata?: MedicalFileMetadata;
  analysisResults?: AnalysisResult[];
  complianceStatus: ComplianceStatus;
}

export type MedicalFileType = 
  | 'dicom'
  | 'lab_result'
  | 'clinical_note'
  | 'prescription'
  | 'insurance_document'
  | 'patient_record'
  | 'imaging_report'
  | 'pathology_report';

export type FileCategory = 
  | 'radiology'
  | 'laboratory'
  | 'clinical'
  | 'administrative'
  | 'billing'
  | 'insurance';

export type ProcessingStatus = 
  | 'uploading'
  | 'queued'
  | 'processing'
  | 'completed'
  | 'failed'
  | 'requires_review';

export interface MedicalFileMetadata {
  patientId?: string;
  studyDate?: Date;
  modality?: string;
  bodyPart?: string;
  physician?: string;
  institution?: string;
  studyDescription?: string;
  seriesDescription?: string;
  imageCount?: number;
  pixelSpacing?: number[];
  sliceThickness?: number;
}

// AI Analysis Results
export interface AnalysisResult {
  id: string;
  fileId: string;
  agentType: AIAgentType;
  confidence: number;
  findings: Finding[];
  recommendations: Recommendation[];
  processedAt: Date;
  processingTime: number;
  version: string;
}

export type AIAgentType = 
  | 'dicom_analysis'
  | 'lab_parser'
  | 'clinical_decision'
  | 'compliance_monitor';

export interface Finding {
  type: FindingType;
  description: string;
  severity: Severity;
  location?: AnatomicalLocation;
  measurements?: Measurement[];
  confidence: number;
  icd10Code?: string;
  snomedCode?: string;
}

export type FindingType = 
  | 'abnormality'
  | 'normal'
  | 'critical'
  | 'incidental'
  | 'artifact'
  | 'measurement';

export type Severity = 
  | 'critical'
  | 'high'
  | 'medium'
  | 'low'
  | 'normal';

export interface AnatomicalLocation {
  region: string;
  laterality?: 'left' | 'right' | 'bilateral';
  coordinates?: {
    x: number;
    y: number;
    z?: number;
  };
}

export interface Measurement {
  type: string;
  value: number;
  unit: string;
  normalRange?: {
    min: number;
    max: number;
  };
}

export interface Recommendation {
  type: RecommendationType;
  description: string;
  priority: Priority;
  timeframe?: string;
  followUp?: string;
  references?: string[];
}

export type RecommendationType = 
  | 'immediate_action'
  | 'follow_up'
  | 'additional_testing'
  | 'specialist_referral'
  | 'medication_adjustment'
  | 'lifestyle_modification';

export type Priority = 
  | 'emergency'
  | 'urgent'
  | 'routine'
  | 'when_convenient';

// Triage Assessment
export interface TriageAssessment {
  id: string;
  patientId: string;
  symptoms: Symptom[];
  urgencyLevel: UrgencyLevel;
  recommendations: TriageRecommendation[];
  estimatedWaitTime?: number;
  specialtyRequired?: string;
  createdAt: Date;
  completedAt?: Date;
}

export interface Symptom {
  name: string;
  severity: number; // 1-10 scale
  duration: string;
  onset: 'sudden' | 'gradual' | 'chronic';
  location?: string;
  character?: string;
  aggravatingFactors?: string[];
  relievingFactors?: string[];
}

export type UrgencyLevel = 
  | 'emergency'     // Level 1 - Immediate
  | 'urgent'        // Level 2 - Within 15 minutes
  | 'semi_urgent'   // Level 3 - Within 30 minutes
  | 'standard'      // Level 4 - Within 60 minutes
  | 'non_urgent';   // Level 5 - Within 120 minutes

export interface TriageRecommendation {
  type: 'immediate_care' | 'scheduled_appointment' | 'self_care' | 'emergency_services';
  description: string;
  timeframe: string;
  department?: string;
  provider?: string;
}

// Compliance & Audit
export type ComplianceStatus = 
  | 'compliant'
  | 'non_compliant'
  | 'under_review'
  | 'requires_action';

export interface ComplianceEvent {
  id: string;
  type: ComplianceEventType;
  severity: ComplianceSeverity;
  description: string;
  userId: string;
  resourceId?: string;
  timestamp: Date;
  resolved: boolean;
  resolution?: string;
  resolvedAt?: Date;
  resolvedBy?: string;
}

export type ComplianceEventType = 
  | 'unauthorized_access'
  | 'data_export'
  | 'failed_authentication'
  | 'policy_violation'
  | 'data_breach'
  | 'audit_log_access'
  | 'encryption_failure'
  | 'retention_violation';

export type ComplianceSeverity = 
  | 'critical'
  | 'high'
  | 'medium'
  | 'low'
  | 'informational';

// Billing & RCM
export interface BillingRecord {
  id: string;
  patientId: string;
  serviceDate: Date;
  provider: string;
  icd10Codes: string[];
  cptCodes: string[];
  chargeAmount: number;
  paidAmount: number;
  insuranceClaim?: InsuranceClaim;
  status: BillingStatus;
  createdAt: Date;
  updatedAt: Date;
}

export type BillingStatus = 
  | 'draft'
  | 'submitted'
  | 'in_process'
  | 'paid'
  | 'denied'
  | 'appealed'
  | 'written_off';

export interface InsuranceClaim {
  id: string;
  payerId: string;
  submittedDate: Date;
  claimAmount: number;
  approvedAmount?: number;
  denialReason?: string;
  status: ClaimStatus;
}

export type ClaimStatus = 
  | 'pending'
  | 'approved'
  | 'denied'
  | 'under_review'
  | 'appealed';

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  timestamp: Date;
  requestId: string;
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
}

// Dashboard Analytics
export interface DashboardMetrics {
  totalFiles: number;
  filesProcessedToday: number;
  aiProcessingQueue: number;
  complianceScore: number;
  activeUsers: number;
  systemUptime: number;
  averageProcessingTime: number;
  criticalAlerts: number;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
    borderWidth?: number;
  }[];
}

// Error Types
export interface AppError {
  code: string;
  message: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: Date;
  userId?: string;
  context?: Record<string, any>;
}

// Notification Types
export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  severity: NotificationSeverity;
  read: boolean;
  createdAt: Date;
  actionUrl?: string;
  actionText?: string;
  expiresAt?: Date;
}

export type NotificationType = 
  | 'system'
  | 'security'
  | 'compliance'
  | 'processing'
  | 'billing'
  | 'user_action';

export type NotificationSeverity = 
  | 'info'
  | 'warning'
  | 'error'
  | 'success';