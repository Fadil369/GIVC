import { clsx } from 'clsx';
import React from 'react';

interface LoadingSkeletonProps {
  variant?: 'text' | 'rectangular' | 'circular' | 'card' | 'table' | 'chart' | 'avatar';
  lines?: number;
  className?: string | undefined;
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
          <div className="space-y-2 flex-1">
            <div className={clsx(baseClasses, 'h-4 w-3/5')} />
            <div className={clsx(baseClasses, 'h-3 w-2/5')} />
          </div>
        </div>
      );

    case 'card':
      return (
        <div className={clsx(baseClasses, 'p-6')}>
          <div className="space-y-4">
            <div className={clsx(baseClasses, 'h-6 w-3/5')} />
            <div className="space-y-2">
              <div className={clsx(baseClasses, 'h-4 w-full')} />
              <div className={clsx(baseClasses, 'h-4 w-4/5')} />
              <div className={clsx(baseClasses, 'h-4 w-3/5')} />
            </div>
            <div className="flex space-x-2 pt-4">
              <div className={clsx(baseClasses, 'h-8 w-20')} />
              <div className={clsx(baseClasses, 'h-8 w-20')} />
            </div>
          </div>
        </div>
      );

    case 'table':
      return (
        <div className="space-y-3">
          {/* Table Header */}
          <div className="grid grid-cols-4 gap-4">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className={clsx(baseClasses, 'h-4')} />
            ))}
          </div>
          {/* Table Rows */}
          {Array.from({ length: lines || 5 }).map((_, rowIndex) => (
            <div key={rowIndex} className="grid grid-cols-4 gap-4">
              {Array.from({ length: 4 }).map((_, colIndex) => (
                <div key={colIndex} className={clsx(baseClasses, 'h-4')} />
              ))}
            </div>
          ))}
        </div>
      );

    case 'chart':
      return (
        <div className={clsx('space-y-4', className)}>
          <div className={clsx(baseClasses, 'h-6 w-2/5')} />
          <div className="flex items-end space-x-2 h-48">
            {Array.from({ length: 8 }).map((_, index) => {
              const heights = ['h-16', 'h-20', 'h-24', 'h-32', 'h-36', 'h-40', 'h-44', 'h-48'];
              const randomHeight = heights[Math.floor(Math.random() * heights.length)];
              return (
                <div
                  key={index}
                  className={clsx(baseClasses, 'flex-1', randomHeight)}
                />
              );
            })}
          </div>
          <div className="flex justify-between">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className={clsx(baseClasses, 'h-3 w-12')} />
            ))}
          </div>
        </div>
      );

    default:
      return <div className={clsx(baseClasses, 'h-4 w-full')} />;
  }
};

// Pre-built skeleton components for common use cases
export const SkeletonCard: React.FC<{ className?: string | undefined }> = ({ className }) => (
  <LoadingSkeleton variant="card" className={className} />
);

export const SkeletonText: React.FC<{ lines?: number; className?: string | undefined }> = ({ 
  lines = 3, 
  className 
}) => (
  <LoadingSkeleton variant="text" lines={lines} className={className} />
);

export const SkeletonAvatar: React.FC<{ className?: string | undefined }> = ({ 
  className 
}) => (
  <LoadingSkeleton variant="avatar" className={className} />
);

export const SkeletonChart: React.FC<{ className?: string | undefined }> = ({ 
  className 
}) => (
  <LoadingSkeleton variant="chart" className={className} />
);

export const SkeletonTable: React.FC<{ rows?: number; className?: string | undefined }> = ({ 
  rows = 5, 
  className 
}) => (
  <LoadingSkeleton variant="table" lines={rows} className={className} />
);

export const SkeletonButton: React.FC<{ className?: string | undefined }> = ({ 
  className 
}) => (
  <LoadingSkeleton variant="rectangular" className={clsx('rounded-md h-10 w-24', className)} />
);

export default LoadingSkeleton;
