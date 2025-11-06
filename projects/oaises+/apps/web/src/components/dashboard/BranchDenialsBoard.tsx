import { useEffect, useMemo, useState } from 'react';
import type { LocaleMessages, RejectionRecord } from '@/types/dashboard';

interface BranchDenialsBoardProps {
  messages: LocaleMessages;
  records: RejectionRecord[];
  locale: 'en' | 'ar';
}

interface CountdownInfo {
  claimId: string;
  hours: number;
  status: 'critical' | 'warning' | 'ok';
}

export function BranchDenialsBoard({ messages, records, locale }: BranchDenialsBoardProps) {
  const [countdowns, setCountdowns] = useState<CountdownInfo[]>([]);

  const enrichedRecords = useMemo(() => {
    return records.slice(0, 6).map((record) => ({
      ...record,
      branch: record.branch ?? 'Unaizah',
      created_at: record.created_at ?? new Date().toISOString(),
      denial_reason: record.denial_reason ?? 'Pending review',
    }));
  }, [records]);

  useEffect(() => {
    const updateCountdowns = () => {
      const data = enrichedRecords.map<CountdownInfo>((record) => {
        const created = new Date(record.created_at ?? Date.now()).getTime();
        const deadline = created + 48 * 60 * 60 * 1000;
        const diff = Math.max(deadline - Date.now(), 0);
        const hours = Math.round(diff / (60 * 60 * 1000));
        let status: CountdownInfo['status'] = 'ok';
        if (hours <= 6) {
          status = 'critical';
        } else if (hours <= 18) {
          status = 'warning';
        }
        return { claimId: record.claim_id, hours, status };
      });
      setCountdowns(data);
    };

    updateCountdowns();
    const timer = window.setInterval(updateCountdowns, 60_000);
    return () => window.clearInterval(timer);
  }, [enrichedRecords]);

  const direction = locale === 'ar' ? 'rtl' : 'ltr';

  return (
    <section dir={direction} className="flex flex-col gap-6">
      <header className="space-y-1">
        <h2 className="text-2xl font-extrabold text-slate-900 dark:text-white">{messages.branchDenials}</h2>
        <p className="text-sm text-slate-500 dark:text-slate-400">{messages.turnaround} 48 {messages.hours.toLowerCase()}</p>
      </header>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {enrichedRecords.map((record, index) => {
          const countdown = countdowns.find((item) => item.claimId === record.claim_id);
          const state = countdown?.status ?? 'ok';
          const badgeClass = state === 'critical'
            ? 'bg-rose-100 text-rose-700 border-rose-200 dark:bg-rose-900/40 dark:text-rose-300 dark:border-rose-800'
            : state === 'warning'
            ? 'bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-900/40 dark:text-amber-300 dark:border-amber-800'
            : 'bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-900/40 dark:text-emerald-300 dark:border-emerald-800';

          return (
            <article key={record._id ?? `${record.claim_id}-${index}`} className="rounded-xl bg-white p-5 shadow-md ring-1 ring-slate-100 transition hover:-translate-y-1 hover:shadow-lg dark:bg-slate-900 dark:ring-slate-800">
              <div className="flex items-start justify-between gap-4">
                <div className="space-y-2 text-sm">
                  <p className="text-slate-500 dark:text-slate-400">Claim ID: {record.claim_id}</p>
                  <p className="font-semibold text-slate-900 dark:text-white">Patient: {record.patient_id}</p>
                  <p className="text-slate-600 dark:text-slate-300">
                    Denial:
                    <span className="font-medium"> {record.denial_reason}</span>
                  </p>
                  <p className="text-slate-500 dark:text-slate-400">Branch: {record.branch}</p>
                </div>
                <div className={`flex h-20 w-20 flex-col items-center justify-center rounded-full border-4 ${badgeClass}`}>
                  <p className="text-2xl font-bold">{countdown?.hours ?? 48}</p>
                  <p className="text-xs font-semibold uppercase tracking-wide">{messages.hours}</p>
                </div>
              </div>
              <footer className="mt-4 flex items-center justify-between text-xs text-slate-400 dark:text-slate-500">
                <span>{messages.turnaround}</span>
                <span>{record.created_at?.slice(0, 10)}</span>
              </footer>
            </article>
          );
        })}
        {enrichedRecords.length === 0 && (
          <p className="rounded-xl border border-dashed border-slate-300 p-8 text-center text-slate-500 dark:border-slate-700 dark:text-slate-400">{messages.noResults}</p>
        )}
      </div>
    </section>
  );
}
