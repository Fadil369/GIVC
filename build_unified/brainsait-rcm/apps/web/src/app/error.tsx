'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background-light dark:bg-background-dark">
      <div className="text-center max-w-md">
        <h1 className="text-6xl font-bold text-red-600 dark:text-red-400 mb-4">
          500
        </h1>
        <p className="text-xl text-muted-light dark:text-muted-dark mb-4">
          Something went wrong!
        </p>
        {error.message && (
          <p className="text-sm text-muted-light dark:text-muted-dark mb-8 font-mono bg-slate-100 dark:bg-slate-800 p-3 rounded">
            {error.message}
          </p>
        )}
        <button
          onClick={reset}
          className="px-6 py-3 bg-primary-light dark:bg-primary-dark text-white rounded-lg hover:opacity-90 transition-opacity"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
