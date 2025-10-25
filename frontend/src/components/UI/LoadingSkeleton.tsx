import { clsx } from 'clsx';
import React from 'react';

interface LoadingSkeletonProps {
  variant?: 'text' | 'rectangular' | 'circular' | 'card' | 'table' | 'chart' | 'avatar';
  lines?: number;
  className?: string;
  animated?: boolean;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = 'text',
  lines = 1,
  className,
  animated = true,
}) => {
  const baseClasses = clsx(
    'bg-gray-200 rounded',
    {
      'animate-pulse': animated,
    },
    className
  );

  switch (variant) {
    case 'text':
      return (
        <div className="space-y-2">
          {Array.from({ length: lines }).map((_, index) => (
            <div
              key={index}
              className={clsx(
                baseClasses, 
                'h-4',
                index === lines - 1 && lines > 1 ? 'w-3/4' : 'w-full'
              )}
            />
          ))}
        </div>
      );

    case 'rectangular':
      return <div className={clsx(baseClasses, 'h-20')} />;

    case 'circular':
      return <div className={clsx(baseClasses, 'rounded-full w-10 h-10')} />;

    case 'avatar':
      return (
        <div className="flex items-center space-x-3">
          <div className={clsx(baseClasses, 'rounded-full w-10 h-10')} />
          <div className="flex-1 space-y-2">
            <div className={clsx(baseClasses, 'h-4 w-3/4')} />
            <div className={clsx(baseClasses, 'h-3 w-1/2')} />
          </div>
        </div>
      );

    case 'card':
      return (
        <div className={clsx('p-4 border border-gray-200 rounded-lg', className)}>
          <div className={clsx(baseClasses, 'h-48 mb-4')} />
          <div className="space-y-2">
            <div className={clsx(baseClasses, 'h-4 w-3/4')} />
            <div className={clsx(baseClasses, 'h-4 w-full')} />
            <div className={clsx(baseClasses, 'h-4 w-5/6')} />
          </div>
        </div>
      );

    case 'table':
      return (
        <div className="space-y-3">
          {Array.from({ length: lines }).map((_, index) => (
            <div key={index} className="flex space-x-4">
              <div className={clsx(baseClasses, 'h-8 w-1/4')} />
              <div className={clsx(baseClasses, 'h-8 w-1/4')} />
              <div className={clsx(baseClasses, 'h-8 w-1/4')} />
              <div className={clsx(baseClasses, 'h-8 w-1/4')} />
            </div>
          ))}
        </div>
      );

    case 'chart':
      return (
        <div className="space-y-4">
          <div className="flex items-end space-x-2 h-48">
            {Array.from({ length: 7 }).map((_, index) => (
              <div
                key={index}
                className={clsx(baseClasses, 'w-full')}
                style={{ height: `${Math.random() * 100}%` }}
              />
            ))}
          </div>
          <div className="flex justify-between">
            {Array.from({ length: 7 }).map((_, index) => (
              <div key={index} className={clsx(baseClasses, 'h-4 w-12')} />
            ))}
          </div>
        </div>
      );

    default:
      return <div className={clsx(baseClasses, 'h-4')} />;
  }
};

export default LoadingSkeleton;
