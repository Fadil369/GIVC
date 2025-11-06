import { useMemo, useState } from 'react';
import type { LocaleMessages, NphiesUpdateItem } from '@/types/dashboard';

interface NphiesUpdatesPanelProps {
  messages: LocaleMessages;
  locale: 'en' | 'ar';
  updates?: NphiesUpdateItem[];
}

const defaultUpdates: NphiesUpdateItem[] = [
  { id: 'update-201', title: 'NPHIES Code Update', version: '2.0.1', timestamp: '2024-01-18T08:30:00Z', status: 'success' },
  { id: 'update-195', title: 'NPHIES Code Update', version: '1.9.5', timestamp: '2024-01-12T11:00:00Z', status: 'success' },
];

const defaultTransactions: NphiesUpdateItem[] = [
  { id: 'txn-987654321', title: 'Transaction ID: 987654321', timestamp: '2024-01-20T10:30:00Z', status: 'success', claimReference: 'Claim #123456789' },
  { id: 'txn-123456789', title: 'Transaction ID: 123456789', timestamp: '2024-01-20T11:45:00Z', status: 'success', claimReference: 'Claim #987654321' },
  { id: 'txn-654321987', title: 'Transaction ID: 654321987', timestamp: '2024-01-20T12:10:00Z', status: 'failed', claimReference: 'Claim #456789123' },
];

export function NphiesUpdatesPanel({ messages, locale, updates = defaultUpdates }: NphiesUpdatesPanelProps) {
  const [search, setSearch] = useState('');
  const [activeTab, setActiveTab] = useState<'success' | 'failed'>('success');

  const transactions = useMemo(() => defaultTransactions, []);

  const filteredTransactions = transactions.filter((transaction) => {
    const matchesStatus = transaction.status === activeTab;
    const matchesSearch = transaction.title.toLowerCase().includes(search.toLowerCase()) || transaction.claimReference?.toLowerCase().includes(search.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const direction = locale === 'ar' ? 'rtl' : 'ltr';

  return (
    <section dir={direction} className="space-y-6 rounded-2xl bg-white p-8 shadow-lg ring-1 ring-slate-100 dark:bg-slate-900 dark:ring-slate-800">
      <header className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
        <div>
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{messages.nphiesUpdates}</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">{messages.latestUpdates}</p>
        </div>
        <button
          type="button"
          onClick={() => setSearch('')}
          className="self-start rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
        >
          {messages.refresh}
        </button>
      </header>

      <div className="relative">
        <span className="material-symbols-outlined pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" aria-hidden>search</span>
        <input
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder={messages.search}
          className="w-full rounded-lg border border-slate-200 bg-slate-50 py-3 pl-10 pr-4 text-slate-700 focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:focus:border-sky-400 dark:focus:ring-sky-500/40"
        />
      </div>

      <section>
        <h3 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">{messages.latestUpdates}</h3>
        <div className="space-y-3">
          {updates.map((update) => (
            <article key={update.id} className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800">
              <div>
                <p className="font-semibold text-slate-900 dark:text-white">{update.title}</p>
                {update.version && <p className="text-sm text-slate-500 dark:text-slate-400">Version {update.version}</p>}
              </div>
              <time className="text-sm text-slate-400 dark:text-slate-500">{new Date(update.timestamp).toLocaleString(locale === 'ar' ? 'ar-SA' : 'en-US')}</time>
            </article>
          ))}
        </div>
      </section>

      <section>
        <h3 className="mb-4 text-lg font-semibold text-slate-900 dark:text-white">{messages.transactionLog}</h3>
        <div className="mb-4 flex rounded-lg border border-slate-200 bg-slate-100 p-1 dark:border-slate-700 dark:bg-slate-800">
          {(['success', 'failed'] as const).map((tab) => (
            <button
              key={tab}
              type="button"
              onClick={() => setActiveTab(tab)}
              className={`flex-1 rounded-md px-4 py-2 text-sm font-semibold transition ${
                activeTab === tab
                  ? 'bg-white text-sky-600 shadow-sm dark:bg-slate-700'
                  : 'text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200'
              }`}
            >
              {tab === 'success' ? messages.successful : messages.failed}
            </button>
          ))}
        </div>

        <div className="space-y-3">
          {filteredTransactions.length === 0 && (
            <p className="rounded-xl border border-dashed border-slate-300 p-6 text-center text-slate-500 dark:border-slate-700 dark:text-slate-400">{messages.noResults}</p>
          )}
          {filteredTransactions.map((transaction) => (
            <article key={transaction.id} className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50 p-4 dark:border-slate-700 dark:bg-slate-800">
              <div>
                <p className="font-medium text-slate-900 dark:text-white">{transaction.title}</p>
                {transaction.claimReference && <p className="text-sm text-slate-500 dark:text-slate-400">{transaction.claimReference}</p>}
              </div>
              <time className="text-sm text-slate-400 dark:text-slate-500">{new Date(transaction.timestamp).toLocaleTimeString(locale === 'ar' ? 'ar-SA' : 'en-US', { hour: '2-digit', minute: '2-digit' })}</time>
            </article>
          ))}
        </div>
      </section>
    </section>
  );
}
