'use client';

import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '@/lib/api';
import { MainDashboard } from '@/components/dashboard/MainDashboard';
import { ClaimSubmissionWorkspace } from '@/components/dashboard/ClaimSubmissionWorkspace';
import { BranchDenialsBoard } from '@/components/dashboard/BranchDenialsBoard';
import { KpiCommandCenter } from '@/components/dashboard/KpiCommandCenter';
import { NphiesUpdatesPanel } from '@/components/dashboard/NphiesUpdatesPanel';
import type { LocaleMessages, DashboardAnalytics, RejectionRecord, ComplianceLetterRecord } from '@/types/dashboard';

interface RejectionDashboardProps {
  locale: 'en' | 'ar';
}

export default function RejectionDashboard({ locale }: RejectionDashboardProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [rejections, setRejections] = useState<RejectionRecord[]>([]);
  const [letters, setLetters] = useState<ComplianceLetterRecord[]>([]);
  const [analytics, setAnalytics] = useState<DashboardAnalytics>({});
  const [activeTab, setActiveTab] = useState<'main' | 'claim' | 'denials' | 'kpi' | 'nphies'>('main');

  const isRTL = locale === 'ar';

  const translations: Record<'en' | 'ar', LocaleMessages> = {
    en: {
      loading: 'Loading dashboard...',
      error: 'Failed to load data',
      retry: 'Retry',
      monthlyClaims: 'Monthly Claims',
      rejectionRate: 'Rejection Rate',
      recoveryRate: 'Recovery Rate',
      pendingLetters: 'Pending Letters',
      claimsToProcess: 'Claims to Process',
      deniedClaims: 'Denied Claims',
      totalProcessed: 'Total Claims Processed',
      avgProcessingTime: 'Avg. Processing Time',
      days: 'days',
      new: 'new',
      pending: 'pending',
      kpis: 'Key Performance Indicators',
      denialRateByPayer: 'Denial Rate % by Payer',
      appealCycleTime: 'Avg. Appeal Cycle Time',
      reimbursementSuccess: 'Reimbursement Success %',
      tasks: 'Tasks',
      metrics: 'Metrics',
      overview: 'Overview',
      last30Days: 'Last 30 Days',
      claimWorkspace: 'Claims Oasis Workspace',
      branchDenials: 'Branch Denial Command Center',
      kpiCommandCenter: 'Denial Analytics & KPIs',
      nphiesUpdates: 'NPHIES Updates & Transaction Log',
      submitClaim: 'Submit compliant claims with real-time risk scoring.',
      submitToPayer: 'Submit to Payer via NPHIES',
      patientInformation: 'Patient Information',
      claimDetails: 'Claim Details',
      diagnosisProcedures: 'Diagnosis & Procedures (NPHIES)',
      denialRiskAssessment: 'Denial Risk Assessment',
      riskLow: 'Low',
      riskMedium: 'Medium',
      riskHigh: 'High',
      assignedDeniedClaims: 'Assigned Denied Claims',
      turnaround: 'Turnaround',
      hours: 'Hours',
      slaBreached: 'SLA breached – escalate immediately',
      search: 'Search NPHIES codes, claims, or transactions',
      latestUpdates: 'Latest Updates',
      transactionLog: 'Transaction Log',
      successful: 'Successful',
      failed: 'Failed',
      noResults: 'No matching records right now.',
      refresh: 'Refresh feed',
    },
    ar: {
      loading: 'جاري تحميل لوحة التحكم...',
      error: 'فشل تحميل البيانات',
      retry: 'إعادة المحاولة',
      monthlyClaims: 'المطالبات الشهرية',
      rejectionRate: 'معدل الرفض',
      recoveryRate: 'معدل الاسترداد',
      pendingLetters: 'الخطابات المعلقة',
      claimsToProcess: 'المطالبات للمعالجة',
      deniedClaims: 'المطالبات المرفوضة',
      totalProcessed: 'إجمالي المطالبات المعالجة',
      avgProcessingTime: 'متوسط وقت المعالجة',
      days: 'أيام',
      new: 'جديد',
      pending: 'معلق',
      kpis: 'مؤشرات الأداء الرئيسية',
      denialRateByPayer: 'معدل الرفض حسب شركة التأمين',
      appealCycleTime: 'متوسط زمن معالجة الاستئناف',
      reimbursementSuccess: 'نسبة نجاح التعويض',
      tasks: 'المهام',
      metrics: 'المقاييس',
      overview: 'نظرة عامة',
      last30Days: 'آخر 30 يومًا',
      claimWorkspace: 'مساحة عمل مطالبات الواحة',
      branchDenials: 'مركز قيادة الرفض للفروع',
      kpiCommandCenter: 'تحليلات الرفض ومؤشرات الأداء',
      nphiesUpdates: 'تحديثات نافييس وسجل المعاملات',
      submitClaim: 'أرسل المطالبات المتوافقة مع تقييم المخاطر الفوري.',
      submitToPayer: 'إرسال إلى شركة التأمين عبر نافييس',
      patientInformation: 'بيانات المريض',
      claimDetails: 'تفاصيل المطالبة',
      diagnosisProcedures: 'التشخيص والإجراءات (نافييس)',
      denialRiskAssessment: 'تقييم مخاطر الرفض',
      riskLow: 'منخفض',
      riskMedium: 'متوسط',
      riskHigh: 'مرتفع',
      assignedDeniedClaims: 'المطالبات المرفوضة المخصصة',
      turnaround: 'المدة المتاحة',
      hours: 'ساعات',
      slaBreached: 'تم تجاوز اتفاقية مستوى الخدمة - يلزم التصعيد',
      search: 'ابحث في رموز نافييس أو المطالبات أو المعاملات',
      latestUpdates: 'أحدث التحديثات',
      transactionLog: 'سجل المعاملات',
      successful: 'ناجح',
      failed: 'فشل',
      noResults: 'لا توجد سجلات مطابقة الآن.',
      refresh: 'تحديث القائمة',
    },
  };

  const messages = translations[locale];

  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [rejectionsResponse, lettersResponse, analyticsResponse] = await Promise.all([
        apiClient.getCurrentMonthRejections(),
        apiClient.getPendingComplianceLetters(),
        apiClient.getDashboardAnalytics(),
      ]);

      setRejections(rejectionsResponse as RejectionRecord[]);
      setLetters(lettersResponse as ComplianceLetterRecord[]);
      setAnalytics(analyticsResponse as DashboardAnalytics);
    } catch (err) {
      setError((err as Error).message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-b-2 border-blue-600" />
          <p className="text-slate-600 dark:text-slate-300">{messages.loading}</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="mb-4 rounded-lg border border-red-400 bg-red-100 px-6 py-4 text-red-700 dark:border-red-700 dark:bg-red-900/20 dark:text-red-300">
            <p className="font-semibold">{messages.error}</p>
            <p className="text-sm mt-1">{error}</p>
          </div>
          <button
            onClick={fetchDashboardData}
            className="rounded-lg bg-blue-600 px-6 py-2 text-white transition-colors hover:bg-blue-700"
          >
            {messages.retry}
          </button>
        </div>
      </div>
    );
  }

  const tabs: Array<{ id: typeof activeTab; label: string; icon: string }> = [
    { id: 'main', label: messages.overview, icon: 'dashboard' },
    { id: 'claim', label: messages.claimWorkspace, icon: 'description' },
    { id: 'denials', label: messages.branchDenials, icon: 'cancel' },
    { id: 'kpi', label: messages.kpiCommandCenter, icon: 'analytics' },
    { id: 'nphies', label: messages.nphiesUpdates, icon: 'update' },
  ];

  return (
    <div className={`space-y-8 ${isRTL ? 'rtl' : 'ltr'}`} dir={isRTL ? 'rtl' : 'ltr'}>
      <nav className="flex flex-wrap gap-2 rounded-2xl bg-white p-2 shadow-md ring-1 ring-slate-100 dark:bg-slate-900 dark:ring-slate-800">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-semibold transition ${
              activeTab === tab.id
                ? 'bg-sky-500 text-white shadow-sm'
                : 'text-slate-500 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800'
            }`}
          >
            <span className="material-symbols-outlined text-base" aria-hidden>{tab.icon}</span>
            <span className="max-w-[10rem] truncate text-left">{tab.label}</span>
          </button>
        ))}
      </nav>

      {activeTab === 'main' && (
        <MainDashboard
          locale={locale}
          messages={messages}
          analytics={analytics}
          rejections={rejections}
          pendingLettersCount={letters.length}
        />
      )}
      {activeTab === 'claim' && <ClaimSubmissionWorkspace locale={locale} messages={messages} />}
      {activeTab === 'denials' && <BranchDenialsBoard locale={locale} messages={messages} records={rejections} />}
      {activeTab === 'kpi' && <KpiCommandCenter locale={locale} messages={messages} analytics={analytics} />}
      {activeTab === 'nphies' && <NphiesUpdatesPanel locale={locale} messages={messages} />}
    </div>
  );
}
