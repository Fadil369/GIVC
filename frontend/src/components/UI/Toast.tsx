import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';
import React, { createContext, ReactNode, useContext } from 'react';
import toast, { Toaster, ToastOptions } from 'react-hot-toast';

interface ToastContextType {
  success: (message: string) => void;
  error: (message: string) => void;
  warning: (message: string) => void;
  info: (message: string) => void;
  loading: (message: string) => string;
  dismiss: (toastId?: string) => void;
  promise: <T>(
    promise: Promise<T>,
    messages: {
      loading: string;
      success: (data: T) => string;
      error: (err: any) => string;
    },
    options?: ToastOptions
  ) => Promise<T>;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

interface CustomToastProps {
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  onDismiss: () => void;
}

const CustomToast: React.FC<CustomToastProps> = ({ type, message, onDismiss }) => {
  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircleIcon className="h-5 w-5 text-green-400" />;
      case 'error':
        return <XCircleIcon className="h-5 w-5 text-red-400" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-400" />;
      case 'info':
        return <InformationCircleIcon className="h-5 w-5 text-blue-400" />;
    }
  };

  const getStyles = () => {
    switch (type) {
      case 'success':
        return 'bg-white border-l-4 border-green-400 shadow-lg';
      case 'error':
        return 'bg-white border-l-4 border-red-400 shadow-lg';
      case 'warning':
        return 'bg-white border-l-4 border-yellow-400 shadow-lg';
      case 'info':
        return 'bg-white border-l-4 border-blue-400 shadow-lg';
    }
  };

  return (
    <div className={clsx(
      'flex items-center p-4 rounded-lg max-w-md w-full',
      'animate-in slide-in-from-top-5 duration-300',
      getStyles()
    )}>
      <div className="flex items-center flex-1">
        <div className="flex-shrink-0">
          {getIcon()}
        </div>
        <div className="ml-3">
          <p className="text-sm font-medium text-gray-900">
            {message}
          </p>
        </div>
      </div>
      <div className="ml-4 flex-shrink-0">
        <button
          className="inline-flex text-gray-400 hover:text-gray-500 focus:outline-none focus:text-gray-500 transition ease-in-out duration-150"
          onClick={onDismiss}
          aria-label="Close notification"
        >
          <XMarkIcon className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
};

interface ToastProviderProps {
  children: ReactNode;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
  const showToast = (type: 'success' | 'error' | 'warning' | 'info', message: string) => {
    toast.custom((t) => (
      <CustomToast
        type={type}
        message={message}
        onDismiss={() => toast.dismiss(t.id)}
      />
    ), {
      duration: 4000,
      position: 'top-right',
    });
  };

  const toastContext: ToastContextType = {
    success: (message: string) => showToast('success', message),
    error: (message: string) => showToast('error', message),
    warning: (message: string) => showToast('warning', message),
    info: (message: string) => showToast('info', message),
    loading: (message: string) => {
      return toast.loading(message, {
        position: 'top-right',
      });
    },
    dismiss: (toastId?: string) => {
      if (toastId) {
        toast.dismiss(toastId);
      } else {
        toast.dismiss();
      }
    },
    promise: <T,>(
      promise: Promise<T>,
      messages: {
        loading: string;
        success: (data: T) => string;
        error: (err: any) => string;
      },
      options?: ToastOptions
    ) => {
      return toast.promise(
        promise,
        messages,
        { ...options, position: 'top-right' }
      );
    },
  };

  return (
    <ToastContext.Provider value={toastContext}>
      {children}
      <Toaster
        position="top-right"
        reverseOrder={false}
        gutter={8}
        toastOptions={{
          duration: 4000,
          style: {
            background: 'transparent',
            boxShadow: 'none',
            padding: 0,
          },
        }}
      />
    </ToastContext.Provider>
  );
};

export default ToastProvider;
