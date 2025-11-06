export type Locale = 'en' | 'ar';

export interface LocaleMessages {
  loading: string;
  error: string;
  retry: string;
  monthlyClaims: string;
  rejectionRate: string;
  recoveryRate: string;
  pendingLetters: string;
  claimsToProcess: string;
  deniedClaims: string;
  totalProcessed: string;
  avgProcessingTime: string;
  days: string;
  new: string;
  pending: string;
  kpis: string;
  denialRateByPayer: string;
  appealCycleTime: string;
  reimbursementSuccess: string;
  tasks: string;
  metrics: string;
  overview: string;
  last30Days: string;
  claimWorkspace: string;
  branchDenials: string;
  kpiCommandCenter: string;
  nphiesUpdates: string;
  submitClaim: string;
  submitToPayer: string;
  patientInformation: string;
  claimDetails: string;
  diagnosisProcedures: string;
  denialRiskAssessment: string;
  riskLow: string;
  riskMedium: string;
  riskHigh: string;
  assignedDeniedClaims: string;
  turnaround: string;
  hours: string;
  slaBreached: string;
  search: string;
  latestUpdates: string;
  transactionLog: string;
  successful: string;
  failed: string;
  noResults: string;
  refresh: string;
}

export interface DashboardAnalytics {
  period?: string;
  total_rejections?: number;
  total_appeals?: number;
  recovery_rate?: number;
  pending_appeals?: number;
  avg_appeal_cycle_time?: number;
  fraud_alerts_count?: number;
  denial_rate_by_payer?: number;
  reimbursement_success_rate?: number;
}

export interface RejectionRecord {
  _id?: string;
  claim_id: string;
  patient_id: string;
  payer?: string;
  denial_code?: string;
  denial_reason?: string;
  amount?: number;
  service_date?: string;
  branch?: string;
  status?: string;
  created_at?: string;
}

export interface ComplianceLetterRecord {
  _id?: string;
  type?: string;
  status?: string;
  created_at?: string;
}

export interface NphiesUpdateItem {
  id: string;
  title: string;
  version?: string;
  timestamp: string;
  status?: 'success' | 'failed';
  claimReference?: string;
}
