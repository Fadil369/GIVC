import type { DashboardAnalytics, LocaleMessages, RejectionRecord } from '@/types/dashboard';

interface MainDashboardProps {
  locale: 'en' | 'ar';
  messages: LocaleMessages;
  analytics: DashboardAnalytics;
  rejections: RejectionRecord[];
  pendingLettersCount: number;
}

const gradientStops = ['from-sky-500 to-sky-600', 'from-rose-500 to-rose-600', 'from-emerald-500 to-emerald-600', 'from-amber-500 to-amber-600'];

export function MainDashboard({ locale, messages, analytics, rejections, pendingLettersCount }: MainDashboardProps) {
  const recentRejections = rejections.slice(0, 4);
  const totalProcessed = analytics.total_rejections ?? rejections.length;
  const avgProcessingTime = analytics.avg_appeal_cycle_time ?? 2.5;

  const trendData = [
    { label: 'Jan', value: 24 },
    { label: 'Feb', value: 32 },
    { label: 'Mar', value: 28 },
    { label: 'Apr', value: 36 },
    { label: 'May', value: 40 },
  ];

  const metricCards = [
    {
      key: 'claims',
      title: messages.monthlyClaims,
      value: totalProcessed.toLocaleString(locale === 'ar' ? 'ar-SA' : 'en-US'),
      icon: '📊',
      gradient: gradientStops[0],
    },
    {
      key: 'rejectionRate',
      title: messages.rejectionRate,
      value: `${(analytics.denial_rate_by_payer ?? 12.5).toFixed(1)}%`,
      icon: '⚠️',
      gradient: gradientStops[1],
    },
    {
      key: 'recovery',
      title: messages.recoveryRate,
      value: `${(analytics.recovery_rate ?? 85.3).toFixed(1)}%`,
      icon: '✅',
      gradient: gradientStops[2],
    },
    {
      key: 'letters',
      title: messages.pendingLetters,
      value: pendingLettersCount.toString(),
      icon: '📝',
      gradient: gradientStops[3],
    },
  ];

  return (
    <div className="space-y-8">
      <section className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {metricCards.map((card) => (
          <article key={card.key} className={`rounded-2xl bg-gradient-to-br ${card.gradient} p-6 text-white shadow-lg transition-all hover:translate-y-[-2px]`}>
            <div className="flex items-start justify-between">
              <span className="text-4xl" aria-hidden>{card.icon}</span>
              <span className="rounded-full bg-white/20 px-3 py-1 text-xs font-semibold uppercase tracking-wide">{messages.last30Days}</span>
            </div>
            <h3 className="mt-6 text-sm font-medium opacity-90">{card.title}</h3>
            <p className="mt-2 text-3xl font-bold">{card.value}</p>
          </article>
        ))}
      </section>

      <section className="grid gap-6 lg:grid-cols-[2fr,1fr]">
        <article className="rounded-2xl bg-white p-6 shadow-md ring-1 ring-slate-100 dark:bg-slate-900 dark:ring-slate-800">
          <header className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-slate-900 dark:text-white">{messages.overview}</h2>
              <p className="text-sm text-slate-500 dark:text-slate-400">{messages.last30Days}</p>
            </div>
            <div className="flex items-center gap-2 text-sm text-green-500">
              <span aria-hidden>▲</span>
              <span>+15%</span>
            </div>
          </header>

          <div className="mt-6 h-56 rounded-xl bg-gradient-to-tr from-sky-50 to-white p-4 dark:from-slate-800 dark:to-slate-900">
            <svg viewBox="0 0 500 160" className="h-full w-full">
              <defs>
                <linearGradient id="dashboardGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#0ea5e9" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#0ea5e9" stopOpacity="0" />
                </linearGradient>
              </defs>
              <path
                d="M0 140 C40 60 80 100 120 70 C160 40 200 115 240 90 C280 60 320 110 360 80 C400 50 440 140 480 100 L500 160 L0 160 Z"
                fill="url(#dashboardGradient)"
              />
              <polyline
                fill="none"
                stroke="#0284c7"
                strokeWidth="4"
                strokeLinecap="round"
                points="0,140 40,60 80,100 120,70 160,40 200,115 240,90 280,60 320,110 360,80 400,50 440,140 480,100"
              />
            </svg>
          </div>

          <footer className="mt-4 flex justify-between text-xs font-semibold uppercase tracking-wide text-slate-400">
            {trendData.map((item) => (
              <span key={item.label}>{item.label}</span>
            ))}
          </footer>
        </article>

        <article className="rounded-2xl bg-white p-6 shadow-md ring-1 ring-slate-100 dark:bg-slate-900 dark:ring-slate-800">
          <header className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-900 dark:text-white">{messages.tasks}</h2>
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">{messages.pending}</span>
          </header>
          <div className="mt-6 space-y-4">
            <TaskRow
              color="primary"
              title={messages.claimsToProcess}
              subtitle={`12 ${messages.pending.toLowerCase()}`}
              icon="description"
            />
            <TaskRow
              color="rose"
              title={messages.deniedClaims}
              subtitle={`3 ${messages.new.toLowerCase()}`}
              icon="thumb_down"
            />
            <TaskRow
              color="amber"
              title={messages.pendingLetters}
              subtitle={`${pendingLettersCount} ${messages.pending.toLowerCase()}`}
              icon="mail"
            />
          </div>
        </article>
      </section>

      <section className="rounded-2xl bg-white p-6 shadow-md ring-1 ring-slate-100 dark:bg-slate-900 dark:ring-slate-800">
        <header className="flex items-center justify-between">
          <h2 className="text-xl font-semibold text-slate-900 dark:text-white">{messages.assignedDeniedClaims}</h2>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-500 dark:bg-slate-800 dark:text-slate-300">{messages.last30Days}</span>
        </header>
        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {recentRejections.map((item, index) => (
            <DenialCard key={item._id ?? `${item.claim_id}-${index}`} record={item} messages={messages} />
          ))}
          {recentRejections.length === 0 && (
            <p className="col-span-full rounded-xl border border-dashed border-slate-300 p-8 text-center text-slate-500 dark:border-slate-700 dark:text-slate-400">{messages.noResults}</p>
          )}
        </div>
      </section>
    </div>
  );
}

interface TaskRowProps {
  title: string;
  subtitle: string;
  icon: string;
  color: 'primary' | 'rose' | 'amber';
}

function TaskRow({ title, subtitle, icon, color }: TaskRowProps) {
  const colorMap: Record<TaskRowProps['color'], string> = {
    primary: 'bg-sky-100 text-sky-600 dark:bg-sky-900/40 dark:text-sky-300',
    rose: 'bg-rose-100 text-rose-600 dark:bg-rose-900/40 dark:text-rose-300',
    amber: 'bg-amber-100 text-amber-600 dark:bg-amber-900/40 dark:text-amber-300',
  };

  return (
    <div className="flex items-center justify-between rounded-xl border border-slate-100 p-4 transition-colors hover:border-slate-200 dark:border-slate-700 dark:hover:border-slate-600">
      <div className={`flex h-12 w-12 items-center justify-center rounded-full ${colorMap[color]}`}>
        <span className="material-symbols-outlined" aria-hidden>{icon}</span>
      </div>
      <div className="ml-4 flex-1">
        <p className="font-semibold text-slate-900 dark:text-white">{title}</p>
        <p className="text-sm text-slate-500 dark:text-slate-400">{subtitle}</p>
      </div>
      <span className="material-symbols-outlined text-slate-400" aria-hidden>chevron_right</span>
    </div>
  );
}

interface DenialCardProps {
  record: RejectionRecord;
  messages: LocaleMessages;
}

function DenialCard({ record, messages }: DenialCardProps) {
  const hoursRemaining = (() => {
    if (!record.created_at) return 48;
    const created = new Date(record.created_at).getTime();
    const deadline = created + 48 * 60 * 60 * 1000;
    const diff = Math.max(deadline - Date.now(), 0);
    return Math.round(diff / (60 * 60 * 1000));
  })();

  const severityClass = hoursRemaining <= 8 ? 'bg-rose-100 text-rose-700 border-rose-200 dark:bg-rose-900/40 dark:text-rose-300 dark:border-rose-800' : hoursRemaining <= 24 ? 'bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-900/40 dark:text-amber-300 dark:border-amber-800' : 'bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-900/40 dark:text-emerald-300 dark:border-emerald-800';

  return (
    <article className="rounded-xl border border-slate-100 p-4 shadow-sm transition-all hover:-translate-y-1 hover:border-slate-200 dark:border-slate-800 dark:hover:border-slate-700">
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="text-sm text-slate-500 dark:text-slate-400">Claim ID: {record.claim_id}</p>
          <p className="font-semibold text-slate-900 dark:text-white">Patient: {record.patient_id}</p>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            Denial:
            <span className="font-medium"> {record.denial_reason ?? 'Pending review'}</span>
          </p>
        </div>
        <div className={`flex h-20 w-20 flex-col items-center justify-center rounded-full border-4 ${severityClass}`}>
          <p className="text-2xl font-bold">{hoursRemaining}</p>
          <p className="text-xs font-semibold uppercase tracking-wide">{messages.hours}</p>
        </div>
      </div>
      {hoursRemaining <= 4 && (
        <p className="mt-3 text-sm font-semibold text-rose-600 dark:text-rose-300">{messages.slaBreached}</p>
      )}
    </article>
  );
}
