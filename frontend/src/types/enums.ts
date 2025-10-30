// Enumeration Types for GIVC Healthcare Platform
// Use these enums instead of hard-coded string literals to prevent type mismatches

// Insurance Plan Types
export enum InsurancePlanType {
  Individual = 'individual',
  Family = 'family',
  Group = 'group',
  Medicare = 'medicare',
  Medicaid = 'medicaid',
}

// Smoking Status
export enum SmokingStatus {
  Never = 'never',
  Former = 'former',
  Current = 'current',
}

// Budget Preferences
export enum BudgetPreference {
  Low = 'low',
  Medium = 'medium',
  High = 'high',
}

// Communication Channels
export enum CommunicationChannel {
  Email = 'email',
  Phone = 'phone',
  Chat = 'chat',
  App = 'app',
}

// Medical Condition Severity
export enum Severity {
  Mild = 'mild',
  Moderate = 'moderate',
  Severe = 'severe',
}

// Medical Condition Status
export enum MedicalConditionStatus {
  Active = 'active',
  Resolved = 'resolved',
  Chronic = 'chronic',
}

// Claim Types
export enum ClaimType {
  Medical = 'medical',
  Prescription = 'prescription',
  Dental = 'dental',
  Vision = 'vision',
  MentalHealth = 'mental_health',
}

// Claim Status
export enum ClaimStatus {
  Submitted = 'submitted',
  Processing = 'processing',
  Approved = 'approved',
  Denied = 'denied',
  PendingInfo = 'pending_info',
}

// Claim Document Types
export enum ClaimDocumentType {
  MedicalRecord = 'medical_record',
  Receipt = 'receipt',
  Prescription = 'prescription',
  Referral = 'referral',
  PriorAuth = 'prior_auth',
}

// Chat Message Sender
export enum MessageSender {
  User = 'user',
  AI = 'ai',
  Agent = 'agent',
}

// Chat Message Type
export enum MessageType {
  Text = 'text',
  File = 'file',
  Form = 'form',
  QuickReply = 'quick_reply',
}

// Chat Session Status
export enum ChatSessionStatus {
  Active = 'active',
  Resolved = 'resolved',
  Escalated = 'escalated',
  Abandoned = 'abandoned',
}

// Chat Session Category
export enum ChatCategory {
  General = 'general',
  Claims = 'claims',
  Enrollment = 'enrollment',
  Billing = 'billing',
  Benefits = 'benefits',
  Emergency = 'emergency',
}

// Priority Levels
export enum Priority {
  Low = 'low',
  Medium = 'medium',
  High = 'high',
  Urgent = 'urgent',
}

// Risk Assessment Types
export enum RiskAssessmentType {
  Enrollment = 'enrollment',
  Renewal = 'renewal',
  ClaimsAnalysis = 'claims_analysis',
  FraudDetection = 'fraud_detection',
}

// Risk Levels
export enum RiskLevel {
  Low = 'low',
  Medium = 'medium',
  High = 'high',
  Critical = 'critical',
}

// Risk Factor Impact
export enum Impact {
  Positive = 'positive',
  Negative = 'negative',
}

// Risk Factor Source
export enum RiskFactorSource {
  MedicalHistory = 'medical_history',
  ClaimsData = 'claims_data',
  Demographics = 'demographics',
  Lifestyle = 'lifestyle',
}

// Fraud Alert Types
export enum FraudAlertType {
  BillingAnomaly = 'billing_anomaly',
  ProviderPattern = 'provider_pattern',
  PatientBehavior = 'patient_behavior',
  DuplicateClaims = 'duplicate_claims',
}

// Fraud Alert Status
export enum FraudAlertStatus {
  Open = 'open',
  Investigating = 'investigating',
  Resolved = 'resolved',
  FalsePositive = 'false_positive',
}

// Compliance Report Types
export enum ComplianceType {
  HIPAA = 'hipaa',
  ADA = 'ada',
  StateRegulation = 'state_regulation',
  FederalRegulation = 'federal_regulation',
}

// Compliance Status
export enum ComplianceStatus {
  Compliant = 'compliant',
  NonCompliant = 'non_compliant',
  RequiresAttention = 'requires_attention',
}

// Compliance Finding Status
export enum ComplianceFindingStatus {
  Met = 'met',
  NotMet = 'not_met',
  PartiallyMet = 'partially_met',
}

// Educational Content Types
export enum ContentType {
  Article = 'article',
  Video = 'video',
  Infographic = 'infographic',
  Interactive = 'interactive',
  Checklist = 'checklist',
}

// Educational Content Categories
export enum ContentCategory {
  Benefits = 'benefits',
  Wellness = 'wellness',
  Claims = 'claims',
  PreventiveCare = 'preventive_care',
  CostManagement = 'cost_management',
}

// Reading Levels
export enum ReadingLevel {
  Basic = 'basic',
  Intermediate = 'intermediate',
  Advanced = 'advanced',
}

// Analytics Trends
export enum Trend {
  Increasing = 'increasing',
  Decreasing = 'decreasing',
  Stable = 'stable',
}

// Analytics Categories
export enum AnalyticsCategory {
  CustomerSatisfaction = 'customer_satisfaction',
  ClaimsProcessing = 'claims_processing',
  CostManagement = 'cost_management',
  FraudDetection = 'fraud_detection',
}

// Sort Order
export enum SortOrder {
  Asc = 'asc',
  Desc = 'desc',
}

// Filter Operators
export enum FilterOperator {
  Equals = 'equals',
  Contains = 'contains',
  GreaterThan = 'greater_than',
  LessThan = 'less_than',
  Between = 'between',
}
