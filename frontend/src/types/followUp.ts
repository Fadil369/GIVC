export type TeamsPriority =
  | 'critical'
  | 'high'
  | 'medium'
  | 'low'
  | 'info';

export type StakeholderGroup =
  | 'Security Eng.'
  | 'CloudOps'
  | 'Runtime Eng.'
  | 'DevOps'
  | 'SRE'
  | 'Compliance Office'
  | 'NPHIES Integration'
  | 'PMO';

export interface FollowUpRecord {
  correlation_id: string;
  branch: string;
  branch_key: string;
  insurance_company: string;
  batch_no?: string | null;
  processor?: string | null;
  status: string;
  status_display: string;
  status_raw?: string | null;
  should_alert: boolean;
  priority: TeamsPriority;
  priority_label: string;
  priority_color: string;
  priority_icon: string;
  stakeholders: StakeholderGroup[];
  alerts: string[];
  due_date?: string | null;
  received_date?: string | null;
  resubmission_date?: string | null;
  days_until_due?: number | null;
  billing_amount?: number | null;
  approved_to_pay?: number | null;
  final_rejection_amount?: number | null;
  final_rejection_percent?: number | null;
  recovery_amount?: number | null;
  billing_month?: string | null;
  billing_year?: number | null;
  rework_type?: string | null;
  batch_type?: string | null;
  formatted: Record<string, unknown>;
  portal_resources: Array<Record<string, unknown>>;
}

export interface FollowUpSummary {
  total_rows: number;
  actionable_rows: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  info: number;
  overdue: number;
  due_soon: number;
  ready_to_work: number;
  not_submitted: number;
  recovery_total: number;
  billing_total: number;
  rejection_total: number;
}

export interface FollowUpSnapshot {
  generated_at: string;
  workbook_path: string;
  accounts_path?: string | null;
  summary: FollowUpSummary;
  overall_summary: FollowUpSummary;
  records: FollowUpRecord[];
}

export interface FollowUpFilters {
  includeNonAlerts?: boolean;
  priority?: TeamsPriority | '';
  branch?: string;
  status?: string;
  shouldAlert?: boolean | '';
}
