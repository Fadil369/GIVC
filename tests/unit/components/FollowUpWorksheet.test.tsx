import { describe, expect, it, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, within } from '@testing-library/react';
import FollowUpWorksheet from '@/components/FollowUps/FollowUpWorksheet';
import { useFollowUpSnapshot } from '@/hooks/useFollowUpSnapshot';
import type { FollowUpSnapshot } from '@/types/followUp';

vi.mock('@/hooks/useFollowUpSnapshot');

const mockUseFollowUpSnapshot = vi.mocked(useFollowUpSnapshot);

const sampleSnapshot: FollowUpSnapshot = {
  generated_at: '2025-11-06T12:00:00Z',
  workbook_path: '/tmp/follow-up.xlsx',
  accounts_path: null,
  summary: {
    total_rows: 2,
    actionable_rows: 1,
    critical: 1,
    high: 0,
    medium: 0,
    low: 1,
    info: 0,
    overdue: 1,
    due_soon: 0,
    ready_to_work: 1,
    not_submitted: 0,
    recovery_total: 15000,
    billing_total: 50000,
    rejection_total: 35000,
  },
  overall_summary: {
    total_rows: 2,
    actionable_rows: 1,
    critical: 1,
    high: 0,
    medium: 0,
    low: 1,
    info: 0,
    overdue: 1,
    due_soon: 0,
    ready_to_work: 1,
    not_submitted: 0,
    recovery_total: 15000,
    billing_total: 50000,
    rejection_total: 35000,
  },
  records: [
    {
      correlation_id: 'corr-abc',
      branch: 'Riyadh',
      branch_key: 'riyadh',
      insurance_company: 'Insurance Co A',
      batch_no: 'B123',
      processor: 'Ahmed',
      status: 'ready_to_work',
      status_display: 'Ready to Work',
      status_raw: 'READY',
      should_alert: true,
      priority: 'critical',
      priority_label: 'Critical',
      priority_color: 'attention',
      priority_icon: '🚨',
      stakeholders: ['Compliance Office'],
      alerts: ['Overdue by 3 days'],
      due_date: '2025-11-10',
      received_date: '2025-11-01',
      resubmission_date: null,
      days_until_due: -3,
      billing_amount: 25000,
      approved_to_pay: 10000,
      final_rejection_amount: 15000,
      final_rejection_percent: 60,
      recovery_amount: 5000,
      billing_month: 'November',
      billing_year: 2025,
      rework_type: 'Appeal',
      batch_type: 'Follow-up',
      formatted: {},
      portal_resources: [],
    },
    {
      correlation_id: 'corr-def',
      branch: 'Jeddah',
      branch_key: 'jeddah',
      insurance_company: 'Insurance Co B',
      batch_no: null,
      processor: 'Sara',
      status: 'monitoring',
      status_display: 'Monitoring',
      status_raw: 'MONITORING',
      should_alert: false,
      priority: 'low',
      priority_label: 'Low',
      priority_color: 'good',
      priority_icon: '📝',
      stakeholders: ['Runtime Eng.'],
      alerts: [],
      due_date: '2025-11-20',
      received_date: '2025-11-03',
      resubmission_date: null,
      days_until_due: 4,
      billing_amount: 25000,
      approved_to_pay: null,
      final_rejection_amount: 20000,
      final_rejection_percent: 40,
      recovery_amount: 10000,
      billing_month: 'November',
      billing_year: 2025,
      rework_type: null,
      batch_type: 'Follow-up',
      formatted: {},
      portal_resources: [],
    },
  ],
};

const defaultHookReturn = {
  data: sampleSnapshot,
  filters: {
    includeNonAlerts: true,
    priority: '',
    status: '',
    branch: '',
    shouldAlert: '',
  },
  setFilters: vi.fn(),
  refresh: vi.fn().mockResolvedValue(undefined),
  status: 'success' as const,
  isLoading: false,
  isRefreshing: false,
  error: null,
  lastUpdated: new Date('2025-11-06T12:00:00Z'),
};

beforeEach(() => {
  mockUseFollowUpSnapshot.mockReturnValue({ ...defaultHookReturn });
});

describe('FollowUpWorksheet', () => {
  it('renders summary metrics and records', () => {
    render(<FollowUpWorksheet />);

    expect(screen.getByText('Worksheet Command Center')).toBeInTheDocument();
    expect(screen.getByText('corr-abc')).toBeInTheDocument();
    expect(screen.getByText('Follow-Up Operations')).toBeInTheDocument();

    const actionableCard = screen.getByText('Actionable Alerts').closest('div');
    expect(actionableCard).toBeTruthy();
    if (actionableCard) {
      expect(within(actionableCard).getByText('1')).toBeInTheDocument();
    }
  });

  it('invokes filter updates when priority changes', () => {
    const setFilters = vi.fn();
    mockUseFollowUpSnapshot.mockReturnValueOnce({ ...defaultHookReturn, setFilters });

    render(<FollowUpWorksheet />);

    const prioritySelect = screen.getByLabelText('Priority');
    fireEvent.change(prioritySelect, { target: { value: 'high' } });

    expect(setFilters).toHaveBeenCalledWith({ priority: 'high' });
  });

  it('shows skeleton rows when loading', () => {
    mockUseFollowUpSnapshot.mockReturnValueOnce({
      ...defaultHookReturn,
      data: null,
      isLoading: true,
      status: 'loading',
    });

    render(<FollowUpWorksheet />);

    expect(screen.getByText('Refreshing...')).toBeInTheDocument();
    const loaders = document.querySelectorAll('.animate-pulse');
    expect(loaders.length).toBeGreaterThan(0);
    expect(screen.queryByText('corr-abc')).not.toBeInTheDocument();
  });
});
