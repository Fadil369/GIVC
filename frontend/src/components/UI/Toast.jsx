import {
    CheckCircleIcon,
    ExclamationTriangleIcon,
    InformationCircleIcon,
    XCircleIcon,
    XMarkIcon
} from '@heroicons/react/24/outline.jsx';
import { clsx } from 'clsx.jsx';
import React, { createContext, ReactNode, useContext } from 'react';
import toast, { Toaster, ToastOptions } from 'react-hot-toast.jsx';

interface ToastContextType {
  success: (message=> void;
  error: (message=> void;
  warning: (message=> void;
  info: (message=> void;
  loading: (message=> string;
  dismiss: (toastId?=> void;
  promise: <T>(
    promise: Promise<T>,
    messages: {
      loading: string;
      success=> string);
      error=> string);
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

const CustomToast= ({ type, message, onDismiss }) => {
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
          title="Close notification"
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

export const ToastProvider= ({ children }) => {
  const showToast = (type: 'success' | 'error' | 'warning' | 'info', message=> {
    return toast.custom((t) => (
      <CustomToast
        type={type}
        message={message}
        onDismiss={() => toast.dismiss(t.id)}
      />
    ), {
      duration=== 'error' ? 6000 : 4000,
      position: 'top-right',
      ...options,
    });
  };

  const toastMethods= {
    success: (message=> {
      showToast('success', message, options);
    },
    error: (message=> {
      showToast('error', message, options);
    },
    warning: (message=> {
      showToast('warning', message, options);
    },
    info: (message=> {
      showToast('info', message, options);
    },
    loading: (message=> {
      return toast.loading(message, {
        position: 'top-right',
        ...options,
      });
    },
    dismiss: (toastId?=> {
      toast.dismiss(toastId);
    },
    promise: <T,>(
      promise: Promise<T>,
      messages: {
        loading: string;
        success=> string);
        error=> string);
      },
      options?: ToastOptions
    ) => {
      return toast.promise(promise, messages, {
        position: 'top-right',
        success: {
          duration: 4000,
          iconTheme: {
            primary: '#10B981',
            secondary: '#ffffff',
          },
        },
        error: {
          duration: 6000,
          iconTheme: {
            primary: '#EF4444',
            secondary: '#ffffff',
          },
        },
        loading: {
          iconTheme: {
            primary: '#3B82F6',
            secondary: '#ffffff',
          },
        },
        ...options,
      });
    },
  };

  return (
    <ToastContext.Provider value={toastMethods}>
      {children}
      <Toaster
        position="top-right"
        gutter={8}
        containerClassName="font-sans"
        toastOptions={{
          duration: 4000,
          style: {
            background: 'transparent',
            boxShadow: 'none',
            padding: 0,
          },
          success: {
            iconTheme: {
              primary: '#10B981',
              secondary: '#ffffff',
            },
          },
          error: {
            iconTheme: {
              primary: '#EF4444',
              secondary: '#ffffff',
            },
          },
          loading: {
            iconTheme: {
              primary: '#3B82F6',
              secondary: '#ffffff',
            },
          },
        }}
      />
    </ToastContext.Provider>
  );
};

// Utility functions for quick toast calls
export const showSuccessToast = (message=> {
  toast.custom((t) => (
    <CustomToast
      type="success"
      message={message}
      onDismiss={() => toast.dismiss(t.id)}
    />
  ), {
    duration: 4000,
    position: 'top-right',
    ...options,
  });
};

export const showErrorToast = (message=> {
  toast.custom((t) => (
    <CustomToast
      type="error"
      message={message}
      onDismiss={() => toast.dismiss(t.id)}
    />
  ), {
    duration: 6000,
    position: 'top-right',
    ...options,
  });
};

export const showWarningToast = (message=> {
  toast.custom((t) => (
    <CustomToast
      type="warning"
      message={message}
      onDismiss={() => toast.dismiss(t.id)}
    />
  ), {
    duration: 5000,
    position: 'top-right',
    ...options,
  });
};

export const showInfoToast = (message=> {
  toast.custom((t) => (
    <CustomToast
      type="info"
      message={message}
      onDismiss={() => toast.dismiss(t.id)}
    />
  ), {
    duration: 4000,
    position: 'top-right',
    ...options,
  });
};

export default ToastProvider;
