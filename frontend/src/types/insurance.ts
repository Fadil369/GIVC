// Insurance System Types for GIVC Healthcare Platform
import {
  InsurancePlanType,
  SmokingStatus,
  BudgetPreference,
  CommunicationChannel,
  Severity,
  MedicalConditionStatus,
  ClaimType,
  ClaimStatus,
  ClaimDocumentType,
  MessageSender,
  MessageType,
  ChatSessionStatus,
  ChatCategory,
  Priority,
  RiskAssessmentType,
  RiskLevel,
  Impact,
  RiskFactorSource,
  FraudAlertType,
  FraudAlertStatus,
  ComplianceType,
  ComplianceStatus,
  ComplianceFindingStatus,
  ContentType,
  ContentCategory,
  ReadingLevel,
  Trend,
  AnalyticsCategory,
  SortOrder,
  FilterOperator,
} from './enums';

export interface InsurancePlan {
  id: string;
  name: string;
  type: InsurancePlanType;
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
    smokingStatus: SmokingStatus;
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
    budgetPreference: BudgetPreference;
  };
  preferences: {
    communicationChannel: CommunicationChannel;
    language: string;
    accessibilityNeeds: string[];
  };
}

export interface MedicalCondition {
  id: string;
  name: string;
  severity: Severity;
  diagnosedDate: string;
  status: MedicalConditionStatus;
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
  type: ClaimType;
  status: ClaimStatus;
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
  type: ClaimDocumentType;
  filename: string;
  uploadDate: string;
  extractedData: Record<string, any>;
  aiProcessed: boolean;
}

export interface ChatMessage {
  id: string;
  sender: MessageSender;
  content: string;
  timestamp: string;
  type: MessageType;
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
  status: ChatSessionStatus;
  category: ChatCategory;
  priority: Priority;
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
  type: RiskAssessmentType;
  riskScore: number; // 0-100
  riskLevel: RiskLevel;
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
  impact: Impact;
  weight: number;
  confidence: number;
  source: RiskFactorSource;
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
  severity: RiskLevel;
  type: FraudAlertType;
  description: string;
  detectedDate: string;
  status: FraudAlertStatus;
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
  type: ComplianceType;
  generatedDate: string;
  period: {
    startDate: string;
    endDate: string;
  };
  status: ComplianceStatus;
  findings: ComplianceFinding[];
  recommendations: string[];
  nextReviewDate: string;
}

export interface ComplianceFinding {
  regulation: string;
  requirement: string;
  status: ComplianceFindingStatus;
  evidence: string[];
  remediation?: string[];
  deadline?: string;
}

export interface EducationalContent {
  id: string;
  title: string;
  content: string;
  type: ContentType;
  category: ContentCategory;
  targetAudience: string[];
  readingLevel: ReadingLevel;
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
  trend: Trend;
  period: string;
  comparison: {
    previousPeriod: number;
    change: number;
    changePercent: number;
  };
  category: AnalyticsCategory;
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

// Common utility types (now imported from enums)
// export type SortOrder - using enum from enums.ts
// export type FilterOperator - using enum from enums.ts

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
