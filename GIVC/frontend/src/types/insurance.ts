// Insurance System Types for GIVC Healthcare Platform

export interface InsurancePlan {
  id: string;
  name: string;
  type: 'individual' | 'family' | 'group' | 'medicare' | 'medicaid';
  premium: {
    monthly: number;
    annual: number;
    currency: string;
  };
  deductible: number;
  outOfPocketMax: number;
  copay: {
    primaryCare: number;
    specialist: number;
    emergency: number;
    urgentCare: number;
  };
  coverage: {
    preventiveCare: number; // percentage
    prescriptionDrugs: number;
    mentalHealth: number;
    dentalVision: boolean;
    maternityNewborn: boolean;
    rehabilitationServices: boolean;
  };
  network: string[];
  restrictions: string[];
  benefits: string[];
  rating: number;
  customerSatisfaction: number;
}

export interface Customer {
  id: string;
  personalInfo: {
    firstName: string;
    lastName: string;
    dateOfBirth: string;
    ssn: string;
    email: string;
    phone: string;
    address: {
      street: string;
      city: string;
      state: string;
      zipCode: string;
    };
  };
  medicalHistory: {
    conditions: MedicalCondition[];
    medications: Medication[];
    allergies: string[];
    familyHistory: string[];
    smokingStatus: 'never' | 'former' | 'current';
    riskFactors: string[];
  };
  insuranceInfo: {
    currentPlan?: InsurancePlan;
    previousPlans: InsurancePlan[];
    preferredProviders: string[];
    specialNeeds: string[];
  };
  financialInfo: {
    income: number;
    dependents: number;
    budgetPreference: 'low' | 'medium' | 'high';
  };
  preferences: {
    communicationChannel: 'email' | 'phone' | 'chat' | 'app';
    language: string;
    accessibilityNeeds: string[];
  };
}

export interface MedicalCondition {
  id: string;
  name: string;
  severity: 'mild' | 'moderate' | 'severe';
  diagnosedDate: string;
  status: 'active' | 'resolved' | 'chronic';
  treatments: string[];
  estimatedAnnualCost: number;
}

export interface Medication {
  id: string;
  name: string;
  dosage: string;
  frequency: string;
  prescribed: string;
  monthlyCost: number;
  generic: boolean;
}

export interface Claim {
  id: string;
  customerId: string;
  planId: string;
  type: 'medical' | 'prescription' | 'dental' | 'vision' | 'mental_health';
  status: 'submitted' | 'processing' | 'approved' | 'denied' | 'pending_info';
  submittedDate: string;
  processedDate?: string;
  provider: {
    name: string;
    npi: string;
    address: string;
    specialty: string;
  };
  services: ClaimService[];
  totalAmount: number;
  coveredAmount: number;
  patientResponsibility: number;
  deductibleApplied: number;
  copayAmount: number;
  denialReason?: string;
  documents: ClaimDocument[];
  fraudRisk: {
    score: number; // 0-100
    flags: string[];
    reasons: string[];
  };
  aiAnalysis: {
    processed: boolean;
    confidence: number;
    recommendations: string[];
    flaggedAnomalies: string[];
  };
}

export interface ClaimService {
  id: string;
  cptCode: string;
  description: string;
  quantity: number;
  unitPrice: number;
  totalPrice: number;
  dateOfService: string;
  diagnosis: string[];
  medicalNecessity: boolean;
}

export interface ClaimDocument {
  id: string;
  type: 'medical_record' | 'receipt' | 'prescription' | 'referral' | 'prior_auth';
  filename: string;
  uploadDate: string;
  extractedData: Record<string, any>;
  aiProcessed: boolean;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'ai' | 'agent';
  content: string;
  timestamp: string;
  type: 'text' | 'file' | 'form' | 'quick_reply';
  metadata?: {
    intent?: string;
    confidence?: number;
    entities?: Record<string, any>;
    attachments?: string[];
  };
}

export interface ChatSession {
  id: string;
  customerId: string;
  startTime: string;
  endTime?: string;
  status: 'active' | 'resolved' | 'escalated' | 'abandoned';
  category: 'general' | 'claims' | 'enrollment' | 'billing' | 'benefits' | 'emergency';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  messages: ChatMessage[];
  aiAgent: {
    name: string;
    version: string;
    capabilities: string[];
  };
  humanAgent?: {
    id: string;
    name: string;
    specialty: string;
  };
  resolution: {
    resolved: boolean;
    satisfactionRating?: number;
    feedback?: string;
    resolutionTime?: number;
  };
}

export interface RiskAssessment {
  id: string;
  customerId: string;
  assessmentDate: string;
  type: 'enrollment' | 'renewal' | 'claims_analysis' | 'fraud_detection';
  riskScore: number; // 0-100
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  factors: RiskFactor[];
  recommendations: string[];
  predictedCosts: {
    annual: number;
    confidence: number;
    breakdown: {
      category: string;
      amount: number;
      probability: number;
    }[];
  };
  aiModel: {
    name: string;
    version: string;
    accuracy: number;
    lastTrained: string;
  };
}

export interface RiskFactor {
  type: string;
  description: string;
  impact: 'positive' | 'negative';
  weight: number;
  confidence: number;
  source: 'medical_history' | 'claims_data' | 'demographics' | 'lifestyle';
}

export interface PlanRecommendation {
  id: string;
  customerId: string;
  recommendedPlans: RecommendedPlan[];
  generatedDate: string;
  reasoning: string;
  customerProfile: {
    ageGroup: string;
    healthStatus: string;
    budgetCategory: string;
    usagePattern: string;
  };
  aiAnalysis: {
    matchingScore: number;
    confidence: number;
    methodology: string;
    dataPoints: string[];
  };
}

export interface RecommendedPlan {
  plan: InsurancePlan;
  matchScore: number; // 0-100
  estimatedAnnualCost: number;
  savings: number;
  pros: string[];
  cons: string[];
  suitabilityReasons: string[];
  scenarioAnalysis: {
    lowUsage: number;
    averageUsage: number;
    highUsage: number;
  };
}

export interface FraudAlert {
  id: string;
  claimId: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  type: 'billing_anomaly' | 'provider_pattern' | 'patient_behavior' | 'duplicate_claims';
  description: string;
  detectedDate: string;
  status: 'open' | 'investigating' | 'resolved' | 'false_positive';
  confidence: number;
  evidencePoints: string[];
  investigation: {
    assignedTo?: string;
    notes: string[];
    actions: string[];
    resolution?: string;
  };
}

export interface ComplianceReport {
  id: string;
  type: 'hipaa' | 'ada' | 'state_regulation' | 'federal_regulation';
  generatedDate: string;
  period: {
    startDate: string;
    endDate: string;
  };
  status: 'compliant' | 'non_compliant' | 'requires_attention';
  findings: ComplianceFinding[];
  recommendations: string[];
  nextReviewDate: string;
}

export interface ComplianceFinding {
  regulation: string;
  requirement: string;
  status: 'met' | 'not_met' | 'partially_met';
  evidence: string[];
  remediation?: string[];
  deadline?: string;
}

export interface EducationalContent {
  id: string;
  title: string;
  content: string;
  type: 'article' | 'video' | 'infographic' | 'interactive' | 'checklist';
  category: 'benefits' | 'wellness' | 'claims' | 'preventive_care' | 'cost_management';
  targetAudience: string[];
  readingLevel: 'basic' | 'intermediate' | 'advanced';
  personalizedFor?: string; // customer ID
  tags: string[];
  createdDate: string;
  lastUpdated: string;
  engagement: {
    views: number;
    ratings: number[];
    completionRate: number;
    shareCount: number;
  };
}

export interface AnalyticsMetric {
  id: string;
  name: string;
  value: number;
  trend: 'increasing' | 'decreasing' | 'stable';
  period: string;
  comparison: {
    previousPeriod: number;
    change: number;
    changePercent: number;
  };
  category: 'customer_satisfaction' | 'claims_processing' | 'cost_management' | 'fraud_detection';
  drillDown?: AnalyticsMetric[];
}

// API Response Types
export interface APIResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  metadata?: {
    timestamp: string;
    requestId: string;
    version: string;
  };
}

// Chat Bot Intents
export interface ChatIntent {
  name: string;
  confidence: number;
  entities: Record<string, any>;
  responses: string[];
  actions: string[];
}

// Common utility types
export type SortOrder = 'asc' | 'desc';
export type FilterOperator = 'equals' | 'contains' | 'greater_than' | 'less_than' | 'between';

export interface Filter {
  field: string;
  operator: FilterOperator;
  value: any;
}

export interface Sort {
  field: string;
  order: SortOrder;
}

export interface PaginationParams {
  page: number;
  limit: number;
  sort?: Sort[];
  filters?: Filter[];
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}
