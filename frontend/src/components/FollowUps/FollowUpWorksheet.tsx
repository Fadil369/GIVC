import { useMemo, useState } from 'react';
import { Transition } from '@headlessui/react';
import { useFollowUpSnapshot } from '@/hooks/useFollowUpSnapshot';
import type { FollowUpRecord, FollowUpSummary, TeamsPriority } from '@/types/followUp';

const priorityBadges: Record<TeamsPriority, string> = {
  critical: 'bg-red-100 text-red-700 border-red-200',
  high: 'bg-orange-100 text-orange-700 border-orange-200',
  medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
  low: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  info: 'bg-blue-100 text-blue-700 border-blue-200',
};

const priorityLabels: { label: string; value: TeamsPriority }[] = [
  { value: 'critical', label: 'Critical' },
  { value: 'high', label: 'High' },
  { value: 'medium', label: 'Medium' },
  { value: 'low', label: 'Low' },
  { value: 'info', label: 'Info' },
];

const formatCurrency = (value?: number | null) => {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return '—';
  }

  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'SAR',
    maximumFractionDigits: 2,
  }).format(value);
};

const formatDate = (value?: string | null) => {
  if (!value) return '—';
  try {
    return new Intl.DateTimeFormat('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    }).format(new Date(value));
  } catch (error) {
    return value;
  }
};

const formatDays = (value?: number | null) => {
  if (value === undefined || value === null) return '—';
  if (value === 0) return 'Due Today';
  if (value < 0) return `${Math.abs(value)} day${Math.abs(value) === 1 ? '' : 's'} overdue`;
  return `${value} day${value === 1 ? '' : 's'}`;
};

const highlightMetrics: Array<{ key: keyof FollowUpSummary; label: string; accent: string }> = [
  { key: 'actionable_rows', label: 'Actionable Alerts', accent: 'text-red-600' },
  { key: 'critical', label: 'Critical', accent: 'text-red-500' },
  { key: 'high', label: 'High', accent: 'text-orange-500' },
  { key: 'medium', label: 'Medium', accent: 'text-yellow-500' },
  { key: 'low', label: 'Low', accent: 'text-emerald-500' },
  { key: 'due_soon', label: 'Due Soon', accent: 'text-blue-500' },
];

function deriveUniqueValues(records: FollowUpRecord[], key: 'branch' | 'status') {
  return Array.from(new Set(records.map((record) => record[key]).filter(Boolean))).sort((a, b) =>
    a.localeCompare(b, undefined, { sensitivity: 'base' })
  );
}

function filterRecords(records: FollowUpRecord[], search: string) {
  const query = search.trim().toLowerCase();
  if (!query) return records;

  return records.filter((record) => {
    const haystack = [
      record.correlation_id,
      record.branch,
      record.insurance_company,
      record.status_display,
      record.processor ?? '',
    ]
      .join(' ')
      .toLowerCase();

    return haystack.includes(query);
  });
}

const loadingRows = Array.from({ length: 6 }, (_, index) => index);

const AlertBanner = ({ message }: { message: string }) => (
  <div className="rounded-xl border border-red-200 bg-red-50/80 px-4 py-3 text-sm text-red-700 shadow-sm">
    <div className="flex items-center gap-3">
      <span className="text-lg">⚠️</span>
      <p>{message}</p>
    </div>
  </div>
);

export default function FollowUpWorksheet() {
  const [searchTerm, setSearchTerm] = useState('');
  const { data, filters, setFilters, refresh, status, isLoading, isRefreshing, error, lastUpdated } =
    useFollowUpSnapshot({ autoRefreshInterval: 120_000 });

  const records = useMemo(() => {
    if (!data) return [];
    const filtered = filterRecords(data.records, searchTerm);
    return filtered;
  }, [data, searchTerm]);

  const branchOptions = useMemo(() => (data ? deriveUniqueValues(data.records, 'branch') : []), [data]);
  const statusOptions = useMemo(() => (data ? deriveUniqueValues(data.records, 'status') : []), [data]);

  const actionableRate = useMemo(() => {
    if (!data || data.summary.total_rows === 0) return 0;
    return Math.round((data.summary.actionable_rows / data.summary.total_rows) * 100);
  }, [data]);

  const handleResetFilters = () => {
    setFilters({
      includeNonAlerts: true,
      priority: '',
      status: '',
      branch: '',
      shouldAlert: '',
    });
  };

  const handleManualRefresh = () => {
    refresh().catch(() => undefined);
  };

  return (
    <div className="space-y-6 pb-12">
      <header className="flex flex-col gap-4 border-b border-gray-200 pb-6 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-medium uppercase tracking-[0.35em] text-blue-600">Follow-Up Operations</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">Worksheet Command Center</h1>
          <p className="mt-1 text-sm text-slate-500">
            Monitor actionable batches, understand workload distribution, and surface priority rejects across all
            branches instantly.
          </p>
        </div>
        <div className="flex flex-col gap-2 md:items-end">
          <button
            type="button"
            onClick={handleManualRefresh}
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-blue-200 bg-white px-4 py-2 text-sm font-medium text-blue-700 transition-all hover:border-blue-300 hover:bg-blue-50"
            disabled={status === 'loading'}
          >
            <span className="text-lg">🔄</span>
            {isRefreshing || status === 'loading' ? 'Refreshing...' : 'Refresh Snapshot'}
          </button>
          <p className="text-xs text-slate-400">
            Last updated:
            <span className="ml-1 font-medium text-slate-600">
              {lastUpdated ? lastUpdated.toLocaleString() : 'Fetching...' }
            </span>
          </p>
        </div>
      </header>

      {error && <AlertBanner message={error} />}

      <section className="grid gap-4 rounded-3xl border border-slate-200 bg-white p-6 shadow-lg shadow-blue-100/20 lg:grid-cols-4">
        <div className="rounded-2xl bg-gradient-to-br from-blue-600 via-blue-500 to-indigo-500 p-5 text-white">
          <p className="text-sm font-medium uppercase tracking-widest text-blue-50/80">Total Rows</p>
          <p className="mt-3 text-4xl font-bold">
            {data?.summary.total_rows ?? (isLoading ? '—' : 0)}
          </p>
          <p className="mt-2 text-sm text-blue-100">
            {actionableRate}% actionable
          </p>
        </div>

        {highlightMetrics.map((metric) => {
          const metricValue = data ? data.summary[metric.key] : undefined;
          return (
            <div key={metric.key} className="rounded-2xl border border-slate-100 bg-slate-50/80 p-5">
              <p className="text-xs font-semibold uppercase tracking-widest text-slate-400">{metric.label}</p>
              <p className={`mt-4 text-3xl font-bold ${metric.accent}`}>
                {metricValue ?? (isLoading ? '—' : 0)}
              </p>
              <p className="mt-2 text-xs text-slate-500">Worksheet snapshot</p>
            </div>
          );
        })}
      </section>

      <section className="rounded-3xl border border-slate-200 bg-white p-6 shadow-lg shadow-purple-100/20">
        <div className="grid gap-4 lg:grid-cols-5">
          <label className="flex flex-col gap-2 text-sm font-medium text-slate-600">
            Priority
            <select
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:border-blue-400 focus:outline-none"
              value={filters.priority ?? ''}
              onChange={(event) =>
                setFilters({ priority: (event.target.value || '') as TeamsPriority | '' })
              }
            >
              <option value="">All priorities</option>
              {priorityLabels.map((item) => (
                <option key={item.value} value={item.value}>
                  {item.label}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-2 text-sm font-medium text-slate-600">
            Branch
            <select
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:border-blue-400 focus:outline-none"
              value={filters.branch ?? ''}
              onChange={(event) => setFilters({ branch: event.target.value })}
            >
              <option value="">All branches</option>
              {branchOptions.map((branch) => (
                <option key={branch} value={branch}>
                  {branch}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-2 text-sm font-medium text-slate-600">
            Status
            <select
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:border-blue-400 focus:outline-none"
              value={filters.status ?? ''}
              onChange={(event) => setFilters({ status: event.target.value })}
            >
              <option value="">All statuses</option>
              {statusOptions.map((status) => (
                <option key={status} value={status}>
                  {status.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
                </option>
              ))}
            </select>
          </label>

          <label className="flex flex-col gap-2 text-sm font-medium text-slate-600">
            Alert Mode
            <select
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 focus:border-blue-400 focus:outline-none"
              value={filters.shouldAlert === '' ? '' : String(filters.shouldAlert)}
              onChange={(event) => {
                const value = event.target.value;
                setFilters({ shouldAlert: value === '' ? '' : value === 'true' });
              }}
            >
              <option value="">All rows</option>
              <option value="true">Actionable only</option>
              <option value="false">Non-actionable</option>
            </select>
          </label>

          <div className="flex flex-col gap-2">
            <span className="text-sm font-medium text-slate-600">Include Non-Alerts</span>
            <label className="inline-flex items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-sm font-medium">
              <input
                type="checkbox"
                className="h-5 w-5 rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                checked={filters.includeNonAlerts !== false}
                onChange={(event) => setFilters({ includeNonAlerts: event.target.checked })}
              />
              <span className="text-slate-600">Show monitoring rows</span>
            </label>
          </div>
        </div>

        <div className="mt-4 flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
          <label className="flex w-full items-center gap-3 rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 md:max-w-md">
            <span className="text-lg">🔍</span>
            <input
              type="search"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Search correlation ID, insurance, processor..."
              className="flex-1 bg-transparent text-sm font-medium text-slate-700 placeholder:text-slate-400 focus:outline-none"
            />
          </label>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleResetFilters}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 transition hover:border-slate-300 hover:bg-slate-50"
            >
              Reset filters
            </button>
          </div>
        </div>
      </section>

      <section className="rounded-3xl border border-slate-200 bg-white shadow-xl shadow-slate-100">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200">
            <thead className="bg-slate-50">
              <tr className="text-left text-xs font-semibold uppercase tracking-wider text-slate-500">
                <th scope="col" className="px-6 py-4">Correlation ID</th>
                <th scope="col" className="px-6 py-4">Priority</th>
                <th scope="col" className="px-6 py-4">Branch</th>
                <th scope="col" className="px-6 py-4">Insurance</th>
                <th scope="col" className="px-6 py-4">Status</th>
                <th scope="col" className="px-6 py-4">Due</th>
                <th scope="col" className="px-6 py-4">Processor</th>
                <th scope="col" className="px-6 py-4">Recovery</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm text-slate-700">
              {isLoading && (
                <tr>
                  <td colSpan={8} className="px-6 py-8">
                    <div className="space-y-3">
                      {loadingRows.map((row) => (
                        <div key={row} className="h-12 animate-pulse rounded-xl bg-slate-100" />
                      ))}
                    </div>
                  </td>
                </tr>
              )}

              {!isLoading && records.length === 0 && (
                <tr>
                  <td colSpan={8} className="px-6 py-16 text-center text-sm text-slate-500">
                    <div className="flex flex-col items-center gap-3">
                      <span className="text-3xl">📄</span>
                      <p className="font-semibold">No records match your filters</p>
                      <p className="text-xs text-slate-400">Adjust filters to see more follow-up alerts.</p>
                    </div>
                  </td>
                </tr>
              )}

              {!isLoading &&
                records.map((record) => (
                  <tr key={record.correlation_id} className="hover:bg-blue-50/40">
                    <td className="whitespace-nowrap px-6 py-4 font-semibold text-slate-900">{record.correlation_id}</td>
                    <td className="px-6 py-4">
                      <span
                        className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold ${
                          priorityBadges[record.priority]
                        }`}
                      >
                        <span>{record.priority_icon}</span>
                        {record.priority_label}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col text-xs">
                        <span className="font-semibold text-slate-800">{record.branch}</span>
                        <span className="text-slate-400 uppercase tracking-widest">{record.branch_key}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <p className="font-medium">{record.insurance_company}</p>
                      {record.batch_no && (
                        <p className="text-xs text-slate-400">Batch {record.batch_no}</p>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col text-xs">
                        <span className="font-semibold text-slate-800">{record.status_display}</span>
                        <span className="text-slate-400">{record.should_alert ? 'Action required' : 'Monitoring'}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col text-xs">
                        <span className="font-semibold text-slate-800">{formatDate(record.due_date)}</span>
                        <span className="text-slate-400">{formatDays(record.days_until_due)}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col text-xs">
                        <span className="font-semibold text-slate-800">{record.processor ?? '—'}</span>
                        <span className="text-slate-400">{record.rework_type ?? '—'}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col text-xs">
                        <span className="font-semibold text-slate-800">{formatCurrency(record.recovery_amount)}</span>
                        <span className="text-slate-400">Rejection {formatCurrency(record.final_rejection_amount)}</span>
                      </div>
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>

        <Transition
          show={isRefreshing && !isLoading}
          enter="transition ease-out duration-300"
          enterFrom="opacity-0 translate-y-2"
          enterTo="opacity-100 translate-y-0"
          leave="transition ease-in duration-200"
          leaveFrom="opacity-100 translate-y-0"
          leaveTo="opacity-0 translate-y-2"
        >
          <div className="border-t border-slate-100 bg-blue-50/60 px-6 py-3 text-sm text-blue-700">
            Updating snapshot&hellip;
          </div>
        </Transition>
      </section>
    </div>
  );
}
