'use client';

import { useState } from 'react';
import RejectionDashboard from '@/components/RejectionDashboard';

export default function Home() {
  const [locale, setLocale] = useState<'en' | 'ar'>('en');

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50 dark:from-slate-900 dark:via-slate-800 dark:to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-slate-900 dark:text-white">
              {locale === 'ar' ? 'لوحة التحكم - إدارة المطالبات' : 'BrainSAIT RCM Dashboard'}
            </h1>
            <p className="text-slate-600 dark:text-slate-300 mt-2">
              {locale === 'ar' ? 'نظام إدارة دورة الإيرادات الطبية' : 'Healthcare Revenue Cycle Management System'}
            </p>
          </div>
          
          {/* Language Toggle */}
          <button
            onClick={() => setLocale(locale === 'en' ? 'ar' : 'en')}
            className="px-4 py-2 bg-white dark:bg-slate-800 rounded-lg shadow-md hover:shadow-lg transition-all"
          >
            {locale === 'en' ? '🇸🇦 العربية' : '🇬🇧 English'}
          </button>
        </div>

        {/* Dashboard Component */}
        <RejectionDashboard locale={locale} />
      </div>
    </main>
  );
}
