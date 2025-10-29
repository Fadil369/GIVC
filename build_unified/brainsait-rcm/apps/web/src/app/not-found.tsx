'use client';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background-light dark:bg-background-dark">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-primary-light dark:text-primary-dark mb-4">
          404
        </h1>
        <p className="text-xl text-muted-light dark:text-muted-dark mb-8">
          Page not found
        </p>
        <a
          href="/"
          className="px-6 py-3 bg-primary-light dark:bg-primary-dark text-white rounded-lg hover:opacity-90 transition-opacity"
        >
          Go back home
        </a>
      </div>
    </div>
  );
}
