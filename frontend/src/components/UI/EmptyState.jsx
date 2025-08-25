import {
    ChartBarIcon,
    CloudArrowUpIcon,
    DocumentIcon,
    ExclamationTriangleIcon,
    InboxIcon,
    MagnifyingGlassIcon,
    UserGroupIcon
} from '@heroicons/react/24/outline.jsx';
import { clsx } from 'clsx.jsx';
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
  } | undefined;
  secondaryAction?: {
    label: string;
    onClick: () => void;
  } | undefined;
  className?: string | undefined;
  size?: 'sm' | 'md' | 'lg';
}

export const EmptyState= ({
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
        return {
          container: 'py-8',
          icon: 'h-8 w-8',
          title: 'text-lg',
          description: 'text-sm',
        };
      case 'lg':
        return {
          container: 'py-16',
          icon: 'h-16 w-16',
          title: 'text-2xl',
          description: 'text-base',
        };
      default:
        return {
          container: 'py-12',
          icon: 'h-12 w-12',
          title: 'text-xl',
          description: 'text-sm',
        };
    }
  };

  const sizeClasses = getSizeClasses();

  return (
    <div className={clsx('text-center', sizeClasses.container, className)}>
      <div className="mx-auto mb-4">
        {icon || getDefaultIcon()}
      </div>
      
      <h3 className={clsx('font-semibold text-gray-900 mb-2', sizeClasses.title)}>
        {title}
      </h3>
      
      {description && (
        <p className={clsx('text-gray-600 mb-6 max-w-sm mx-auto', sizeClasses.description)}>
          {description}
        </p>
      )}

      {(action || secondaryAction) && (
        <div className="flex flex-col sm:flex-row gap-3 justify-center items-center">
          {action && (
            <button
              onClick={action.onClick}
              className={clsx(
                'inline-flex items-center px-4 py-2 rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors',
                action.variant === 'secondary'
                  ? 'border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 focus:ring-primary-500'
                  : 'text-white bg-primary-600 hover:bg-primary-700 focus:ring-primary-500'
              )}
            >
              {action.label}
            </button>
          )}
          
          {secondaryAction && (
            <button
              onClick={secondaryAction.onClick}
              className="inline-flex items-center px-4 py-2 text-sm font-medium text-primary-600 hover:text-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-md"
            >
              {secondaryAction.label}
            </button>
          )}
        </div>
      )}
    </div>
  );
};

// Pre-built empty state components for common scenarios
export const NoDataFound: React.FC<{
  title?: string;
  description?: string;
  onRefresh?: () => void;
  className?: string | undefined;
}> = ({
  title = 'No data found',
  description = 'There is no data to display at the moment.',
  onRefresh,
  className,
}) => (
  <EmptyState
    variant="data"
    title={title}
    description={description}
    action={onRefresh ? { label: 'Refresh', onClick: onRefresh } : undefined}
    className={className}
  />
);

export const NoSearchResults: React.FC<{
  searchTerm?: string;
  onClearSearch?: () => void;
  className?: string | undefined;
}> = ({
  searchTerm,
  onClearSearch,
  className,
}) => (
  <EmptyState
    variant="search"
    title="No results found"
    description={
      searchTerm 
        ? `No results found for "${searchTerm}". Try adjusting your search terms.`
        : 'No results found. Try different search terms.'
    }
    action={onClearSearch ? { label: 'Clear search', onClick: onClearSearch, variant: 'secondary' } : undefined}
    className={className}
  />
);

export const UploadFiles: React.FC<{
  title?: string;
  description?: string;
  onUpload: () => void;
  className?: string | undefined;
}> = ({
  title = 'Upload your first file',
  description = 'Get started by uploading a file to the system.',
  onUpload,
  className,
}) => (
  <EmptyState
    variant="upload"
    title={title}
    description={description}
    action={{ label: 'Upload file', onClick: onUpload }}
    className={className}
  />
);

export const ErrorState: React.FC<{
  title?: string;
  description?: string;
  onRetry?: () => void;
  className?: string | undefined;
}> = ({
  title = 'Something went wrong',
  description = 'We encountered an error while loading this content.',
  onRetry,
  className,
}) => (
  <EmptyState
    variant="error"
    title={title}
    description={description}
    action={onRetry ? { label: 'Try again', onClick: onRetry } : undefined}
    className={className}
  />
);

export const NoUsers: React.FC<{
  title?: string;
  description?: string;
  onInvite?: () => void;
  className?: string | undefined;
}> = ({
  title = 'No users found',
  description = 'Get started by inviting team members to join.',
  onInvite,
  className,
}) => (
  <EmptyState
    variant="users"
    title={title}
    description={description}
    action={onInvite ? { label: 'Invite users', onClick: onInvite } : undefined}
    className={className}
  />
);

export const NoFiles: React.FC<{
  title?: string;
  description?: string;
  onUpload?: () => void;
  onBrowse?: () => void;
  className?: string | undefined;
}> = ({
  title = 'No files yet',
  description = 'Upload files to get started with your medical vault.',
  onUpload,
  onBrowse,
  className,
}) => (
  <EmptyState
    variant="files"
    title={title}
    description={description}
    action={onUpload ? { label: 'Upload files', onClick: onUpload } : undefined}
    secondaryAction={onBrowse ? { label: 'Browse files', onClick: onBrowse } : undefined}
    className={className}
  />
);

export default EmptyState;
