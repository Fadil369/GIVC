import { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error boundary caught an error:', error, errorInfo);
    
    // Log error to monitoring service
    this.logErrorToService(error, errorInfo);
    
    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    this.setState({
      error,
      errorInfo,
    });
  }

  private logErrorToService = (error: Error, errorInfo: ErrorInfo) => {
    // Integration with error monitoring service (e.g., Sentry)
    try {
      const errorData = {
        message: error.message,
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        userAgent: navigator.userAgent,
        url: window.location.href,
      };

      // Log to console in development
      if (import.meta.env.MODE === 'development') {
        console.group('🚨 Error Boundary');
        console.error('Error:', error);
        console.error('Error Info:', errorInfo);
        console.error('Error Data:', errorData);
        console.groupEnd();
      }

      // Send to monitoring service in production
      if (import.meta.env.MODE === 'production') {
        // Replace with your error monitoring service
        fetch('/api/v1/errors', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(errorData),
        }).catch(err => {
          console.error('Failed to log error to service:', err);
        });
      }
    } catch (loggingError) {
      console.error('Error occurred while logging error:', loggingError);
    }
  };

  private handleRetry = () => {
    this.setState({ hasError: false });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-md w-full space-y-8">
            <div>
              <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-red-100">
                <svg
                  className="h-6 w-6 text-red-600"
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.99-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
                Something went wrong
              </h2>
              <p className="mt-2 text-center text-sm text-gray-600">
                We encountered an unexpected error. Our team has been notified.
              </p>
            </div>

            {import.meta.env.MODE === 'development' && this.state.error && (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <h3 className="text-sm font-medium text-red-800 mb-2">
                  Error Details (Development Mode)
                </h3>
                <pre className="text-xs text-red-700 overflow-auto max-h-32">
                  {this.state.error.message}
                  {this.state.error.stack}
                </pre>
              </div>
            )}

            <div className="flex space-x-4">
              <button
                onClick={this.handleRetry}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Try Again
              </button>
              <button
                onClick={() => window.location.reload()}
                className="group relative w-full flex justify-center py-2 px-4 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Reload Page
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
