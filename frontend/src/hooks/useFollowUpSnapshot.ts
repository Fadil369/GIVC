import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { logger } from '@/services/logger';
import { getFollowUpSnapshot } from '@/services/followUpApi';
import type { FollowUpFilters, FollowUpSnapshot } from '@/types/followUp';

type Status = 'idle' | 'loading' | 'success' | 'error';

const DEFAULT_FILTERS: FollowUpFilters = {
  includeNonAlerts: true,
  priority: '',
  status: '',
  branch: '',
  shouldAlert: '',
};

export interface UseFollowUpSnapshotOptions {
  autoRefreshInterval?: number;
  initialFilters?: FollowUpFilters;
}

export interface UseFollowUpSnapshotResult {
  data: FollowUpSnapshot | null;
  filters: FollowUpFilters;
  setFilters: (filters: FollowUpFilters | ((prev: FollowUpFilters) => FollowUpFilters)) => void;
  refresh: (nextFilters?: FollowUpFilters) => Promise<void>;
  status: Status;
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

export function useFollowUpSnapshot(
  options: UseFollowUpSnapshotOptions = {}
): UseFollowUpSnapshotResult {
  const { autoRefreshInterval, initialFilters } = options;
  const [data, setData] = useState<FollowUpSnapshot | null>(null);
  const [filters, setFiltersState] = useState<FollowUpFilters>({
    ...DEFAULT_FILTERS,
    ...initialFilters,
  });
  const [status, setStatus] = useState<Status>('idle');
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const intervalRef = useRef<number | null>(null);
  const hasLoadedRef = useRef(false);

  const isLoading = status === 'loading';

  const effectiveFilters = useMemo(() => {
    const normalized: FollowUpFilters = { ...filters };

    if (normalized.priority === '') normalized.priority = undefined;
    if (normalized.status === '') normalized.status = undefined;
    if (normalized.branch === '') normalized.branch = undefined;
    if (normalized.shouldAlert === '') normalized.shouldAlert = undefined;

    return normalized;
  }, [filters]);

  const loadSnapshot = useCallback(
    async (overrideFilters?: FollowUpFilters) => {
      const nextFilters: FollowUpFilters = {
        ...effectiveFilters,
        ...overrideFilters,
      };

      const isInitialLoad = !hasLoadedRef.current;
      setStatus('loading');
      setError(null);
      if (!isInitialLoad) {
        setIsRefreshing(true);
      }

      try {
        const snapshot = await getFollowUpSnapshot(nextFilters);
        setData(snapshot);
        setLastUpdated(new Date());
        setStatus('success');
        hasLoadedRef.current = true;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Unable to load follow-up worksheet data';
        setError(message);
        setStatus('error');
        logger.error('Failed to load follow-up snapshot', { error: message, filters: nextFilters });
      } finally {
        setIsRefreshing(false);
      }
    },
    [effectiveFilters]
  );

  const refresh = useCallback(
    async (overrideFilters?: FollowUpFilters) => {
      await loadSnapshot(overrideFilters);
    },
    [loadSnapshot]
  );

  useEffect(() => {
    loadSnapshot().catch(() => {
      /* errors handled inside loadSnapshot */
    });
  }, [loadSnapshot]);

  const setFilters = useCallback(
    (update: FollowUpFilters | ((prev: FollowUpFilters) => FollowUpFilters)) => {
      setFiltersState((prev) => {
        const next = typeof update === 'function' ? (update as (prev: FollowUpFilters) => FollowUpFilters)(prev) : update;
        return { ...prev, ...next };
      });
    },
    []
  );

  useEffect(() => {
    if (!autoRefreshInterval) {
      return () => undefined;
    }

    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }

    intervalRef.current = window.setInterval(() => {
      loadSnapshot().catch(() => undefined);
    }, autoRefreshInterval);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [autoRefreshInterval, loadSnapshot]);

  return {
    data,
    filters,
    setFilters,
    refresh,
    status,
    isLoading,
    isRefreshing,
    error,
    lastUpdated,
  };
}
