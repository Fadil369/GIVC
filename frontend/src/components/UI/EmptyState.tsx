import {
  ChartBarIcon,
  CloudArrowUpIcon,
  DocumentIcon,
  ExclamationTriangleIcon,
  InboxIcon,
  MagnifyingGlassIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';
import React, { ReactNode } from 'react';

interface EmptyStateProps {
  variant?: 'default' | 'search' | 'error' | 'upload' | 'data' | 'users' | 'files';
  title: string;
  description?: string;
  icon?: ReactNode;
  action?: {
    label: string;
    onClick: () => void;
    variant?: 'primary' | 'secondary';
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
  };
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  variant = 'default',
  title,
  description,
  icon,
  action,
  secondaryAction,
  className,
  size = 'md',
}) => {
  const getDefaultIcon = () => {
    switch (variant) {
      case 'search':
        return <MagnifyingGlassIcon className="h-12 w-12 text-gray-400" />;
      case 'error':
        return <ExclamationTriangleIcon className="h-12 w-12 text-red-400" />;
      case 'upload':
        return <CloudArrowUpIcon className="h-12 w-12 text-gray-400" />;
      case 'data':
        return <ChartBarIcon className="h-12 w-12 text-gray-400" />;
      case 'users':
        return <UserGroupIcon className="h-12 w-12 text-gray-400" />;
      case 'files':
        return <DocumentIcon className="h-12 w-12 text-gray-400" />;
      default:
        return <InboxIcon className="h-12 w-12 text-gray-400" />;
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'py-8';
      case 'md':
        return 'py-12';
      case 'lg':
        return 'py-16';
      default:
        return 'py-12';
    }
  };

  return (
    <div className={clsx(
      'text-center',
      getSizeClasses(),
      className
    )}>
      {/* Icon */}
      <div className="flex justify-center mb-4">
        {icon || getDefaultIcon()}
      </div>

      {/* Title */}
      <h3 className={clsx(
        'font-semibold text-gray-900',
        size === 'sm' ? 'text-base' : size === 'lg' ? 'text-xl' : 'text-lg'
      )}>
        {title}
      </h3>

      {/* Description */}
      {description && (
        <p className={clsx(
          'mt-2 text-gray-500',
          size === 'sm' ? 'text-sm' : 'text-base',
          'max-w-md mx-auto'
        )}>
          {description}
        </p>
      )}

      {/* Actions */}
      {(action || secondaryAction) && (
        <div className="mt-6 flex flex-col sm:flex-row gap-3 justify-center">
          {action && (
            <button
              onClick={action.onClick}
              className={clsx(
                'inline-flex items-center px-4 py-2 border rounded-md shadow-sm text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors',
                action.variant === 'secondary'
                  ? 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50 focus:ring-blue-500'
                  : 'border-transparent text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500'
              )}
            >
              {action.label}
            </button>
          )}
          {secondaryAction && (
            <button
              onClick={secondaryAction.onClick}
              className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              {secondaryAction.label}
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default EmptyState;
