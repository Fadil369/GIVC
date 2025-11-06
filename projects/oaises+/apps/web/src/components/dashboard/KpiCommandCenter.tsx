import type { DashboardAnalytics, LocaleMessages } from '@/types/dashboard';

interface KpiCommandCenterProps {
  messages: LocaleMessages;
  analytics: DashboardAnalytics;
  locale: 'en' | 'ar';
}

const barConfigs = [
  { label: 'Payer A', value: 0.15 },
  { label: 'Payer B', value: 0.75 },
  { label: 'Payer C', value: 0.4 },
];

const branchPerformance = [
  { label: 'Branch 1', value: 0.8 },
  { label: 'Branch 2', value: 0.5 },
  { label: 'Branch 3', value: 0.3 },
  { label: 'Branch 4', value: 0.6 },
];

const reimbursementSegments = [
  { label: 'Category A', value: 0.3 },
  { label: 'Category B', value: 0.2 },
  { label: 'Category C', value: 0.5 },
  { label: 'Category D', value: 0.35 },
];

const widthPercentClasses = [
  'w-0',
  'w-[5%]',
  'w-[10%]',
  'w-[15%]',
  'w-[20%]',
  'w-[25%]',
  'w-[30%]',
  'w-[35%]',
  'w-[40%]',
  'w-[45%]',
  'w-1/2',
  'w-[55%]',
  'w-[60%]',
  'w-[65%]',
  'w-[70%]',
  'w-[75%]',
  'w-[80%]',
  'w-[85%]',
  'w-[90%]',
  'w-[95%]',
  'w-full',
];

const heightPercentClasses = [
  'h-0',
  'h-[5%]',
  'h-[10%]',
  'h-[15%]',
  'h-[20%]',
  'h-[25%]',
  'h-[30%]',
  'h-[35%]',
  'h-[40%]',
  'h-[45%]',
  'h-1/2',
  'h-[55%]',
  'h-[60%]',
  'h-[65%]',
  'h-[70%]',
  'h-[75%]',
  'h-[80%]',
  'h-[85%]',
  'h-[90%]',
  'h-[95%]',
  'h-full',
];

const clampIndex = (value: number, total: number) => {
  const percent = Math.round(value * 100);
  const stepIndex = Math.round(percent / 5);
  return Math.min(total - 1, Math.max(0, stepIndex));
};

export function KpiCommandCenter({ messages, analytics, locale }: KpiCommandCenterProps) {
  const denialRate = (analytics.denial_rate_by_payer ?? 12.5).toFixed(1);
  const avgAppeal = (analytics.avg_appeal_cycle_time ?? 7.2).toFixed(1);
  const reimbursement = (analytics.reimbursement_success_rate ?? 85.3).toFixed(1);

  const direction = locale === 'ar' ? 'rtl' : 'ltr';

  return (
    <section dir={direction} className="space-y-6">
      <header className="space-y-1">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{messages.kpiCommandCenter}</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">{messages.last30Days}</p>
      </header>

      <div className="grid gap-4 md:grid-cols-3">
        <KpiSummaryCard title={messages.denialRateByPayer} value={`${denialRate}%`} direction={direction} trend={{ value: -2.1, positive: true }} />
        <KpiSummaryCard title={messages.appealCycleTime} value={`${avgAppeal} ${messages.days}`} direction={direction} trend={{ value: 1.5, positive: false }} />
        <KpiSummaryCard title={messages.reimbursementSuccess} value={`${reimbursement}%`} direction={direction} trend={{ value: 3.2, positive: true }} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <article className="space-y-4 rounded-2xl bg-white p-6 shadow-lg ring-1 ring-slate-100 dark:bg-slate-900 dark:ring-slate-800">
          <header className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{messages.denialRateByPayer}</h3>
              <p className="text-xs uppercase tracking-wide text-slate-400">{messages.last30Days}</p>
            </div>
            <span className="material-symbols-outlined text-rose-500" aria-hidden>arrow_downward</span>
          </header>

          <div className="space-y-3 pt-4">
            {barConfigs.map((config) => (
              <div key={config.label} className="space-y-2">
                <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wide text-slate-400">
                  <span>{config.label}</span>
                  <span>{Math.round(config.value * 100)}%</span>
                </div>
                <div className="h-2 rounded-full bg-slate-200 dark:bg-slate-700">
                  <div className={`h-2 rounded-full bg-sky-500 ${widthPercentClasses[clampIndex(config.value, widthPercentClasses.length)]}`} />
                </div>
              </div>
            ))}
          </div>
        </article>

        <article className="space-y-4 rounded-2xl bg-white p-6 shadow-lg ring-1 ring-slate-100 dark:bg-slate-900 dark:ring-slate-800">
          <header className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{messages.appealCycleTime}</h3>
              <p className="text-xs uppercase tracking-wide text-slate-400">{messages.last30Days}</p>
            </div>
            <span className="material-symbols-outlined text-emerald-500" aria-hidden>arrow_upward</span>
          </header>

          <div className="flex h-48 items-end justify-around gap-3">
            {branchPerformance.map((branch) => (
              <div key={branch.label} className="flex flex-col items-center">
                <div className="flex h-40 w-12 items-end justify-center rounded-t-xl bg-slate-100 dark:bg-slate-800">
                  <div className={`w-full rounded-t-xl bg-sky-500 ${heightPercentClasses[clampIndex(branch.value, heightPercentClasses.length)]}`} />
                </div>
                <span className="mt-2 text-xs font-semibold uppercase tracking-wide text-slate-400">{branch.label}</span>
              </div>
            ))}
          </div>
        </article>

        <article className="space-y-4 rounded-2xl bg-white p-6 shadow-lg ring-1 ring-slate-100 dark:bg-slate-900 dark:ring-slate-800">
          <header className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{messages.reimbursementSuccess}</h3>
              <p className="text-xs uppercase tracking-wide text-slate-400">{messages.last30Days}</p>
            </div>
            <span className="material-symbols-outlined text-emerald-500" aria-hidden>insights</span>
          </header>

          <div className="flex h-48 items-end justify-around gap-3">
            {reimbursementSegments.map((segment) => (
              <div key={segment.label} className="flex flex-col items-center">
                <div className="flex h-40 w-12 items-end justify-center rounded-t-xl bg-slate-100 dark:bg-slate-800">
                  <div className={`w-full rounded-t-xl bg-emerald-500 ${heightPercentClasses[clampIndex(segment.value, heightPercentClasses.length)]}`} />
                </div>
                <span className="mt-2 text-xs font-semibold uppercase tracking-wide text-slate-400">{segment.label}</span>
              </div>
            ))}
          </div>
        </article>
      </div>
    </section>
  );
}

interface KpiSummaryCardProps {
  title: string;
  value: string;
  trend: { value: number; positive: boolean };
  direction: string;
}

function KpiSummaryCard({ title, value, trend, direction }: KpiSummaryCardProps) {
  const trendColor = trend.positive ? 'text-emerald-500' : 'text-rose-500';
  const trendIcon = trend.positive ? 'arrow_upward' : 'arrow_downward';

  return (
    <article className="rounded-2xl bg-white p-6 shadow-lg ring-1 ring-slate-100 dark:bg-slate-900 dark:ring-slate-800">
      <header className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-500 dark:text-slate-400">{title}</h3>
        <span className={`flex items-center gap-1 text-xs font-semibold ${trendColor}`}>
          <span className="material-symbols-outlined text-base" aria-hidden>{trendIcon}</span>
          {trend.value}%
        </span>
      </header>
      <p className="mt-4 text-3xl font-bold text-slate-900 dark:text-white" dir={direction}>{value}</p>
      <p className="mt-2 text-xs uppercase tracking-wide text-slate-400">{direction === 'rtl' ? 'مقارنة بالأسبوع الماضي' : 'vs previous period'}</p>
    </article>
  );
}
