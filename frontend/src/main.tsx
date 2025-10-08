/**
 * GIVC Healthcare Platform - Application Entry Point
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Main entry point with environment validation, enhanced error handling,
 * and HIPAA-compliant logging integration
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

// Import environment validation and logger
import { validateEnvironment, getConfig } from './config/validateEnv';
import logger from './services/logger';

// Environment Validation Error UI Component
const EnvironmentError: React.FC<{ errors: string[] }> = ({ errors }) => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 via-white to-orange-50">
      <div className="max-w-2xl w-full bg-white rounded-2xl shadow-2xl p-8 border-4 border-red-500">
        <div className="text-center mb-6">
          <div className="w-20 h-20 mx-auto bg-red-100 rounded-full flex items-center justify-center mb-4">
            <svg className="w-12 h-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-red-600 mb-2">
            ⚠️ Environment Configuration Error
          </h1>
          <p className="text-gray-600 mb-6">
            GIVC Healthcare Platform cannot start due to missing or invalid environment configuration.
            This is critical for HIPAA compliance and security.
          </p>
        </div>

        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-6 rounded">
          <h3 className="text-lg font-semibold text-red-800 mb-3">Missing Configuration:</h3>
          <ul className="space-y-2">
            {errors.map((error, index) => (
              <li key={index} className="flex items-start gap-2 text-red-700">
                <svg className="w-5 h-5 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="font-mono text-sm">{error}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
          <h4 className="font-semibold text-blue-800 mb-2">📝 How to Fix:</h4>
          <ol className="list-decimal list-inside space-y-1 text-sm text-blue-700">
            <li>Create a <code className="bg-blue-100 px-2 py-0.5 rounded">.env</code> file in the project root</li>
            <li>Copy the required variables from <code className="bg-blue-100 px-2 py-0.5 rounded">.env.example</code></li>
            <li>Fill in the missing values</li>
            <li>Restart the development server</li>
          </ol>
        </div>

        <div className="mt-6 text-center text-sm text-gray-500">
          <p>🔒 HIPAA Compliance Requirement</p>
          <p>All environment variables must be properly configured for PHI protection</p>
        </div>
      </div>
    </div>
  );
};

// Enhanced Error Boundary with HIPAA logging
class ApplicationErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log to HIPAA-compliant logger instead of console
    logger.error('Application crashed', {
      error: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
    });

    // In production, send to monitoring service
    if (import.meta.env.PROD) {
      // TODO: Send to Sentry/Cloudflare Workers analytics
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 via-white to-orange-50">
          <div className="max-w-md w-full bg-white rounded-2xl shadow-2xl p-8 border-t-4 border-red-500">
            <div className="text-center">
              <div className="w-20 h-20 mx-auto bg-red-100 rounded-full flex items-center justify-center mb-4">
                <svg className="w-12 h-12 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                System Error
              </h1>
              
              <p className="text-gray-600 mb-6">
                We apologize for the inconvenience. Our technical team has been notified
                and is working on a solution.
              </p>

              {import.meta.env.DEV && this.state.error && (
                <div className="mb-6 text-left">
                  <details className="bg-red-50 border border-red-200 rounded p-4">
                    <summary className="cursor-pointer font-semibold text-red-800 mb-2">
                      Error Details (Development Only)
                    </summary>
                    <pre className="text-xs text-red-700 overflow-auto">
                      {this.state.error.message}
                      {'\n\n'}
                      {this.state.error.stack}
                    </pre>
                  </details>
                </div>
              )}

              <div className="space-y-3">
                <button
                  onClick={() => window.location.reload()}
                  className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-200 shadow-lg"
                >
                  🔄 Reload Application
                </button>
                
                <button
                  onClick={() => {
                    this.setState({ hasError: false, error: undefined });
                    window.location.href = '/dashboard';
                  }}
                  className="w-full bg-gray-100 text-gray-700 font-semibold py-3 px-6 rounded-lg hover:bg-gray-200 transition-all duration-200"
                >
                  🏠 Return to Dashboard
                </button>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200 text-sm text-gray-500">
                <p>🔒 HIPAA Compliant Platform</p>
                <p className="text-xs mt-1">Error logged securely with PHI protection</p>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Initialize application with environment validation
async function initializeApp() {
  const rootElement = document.getElementById('root');
  
  if (!rootElement) {
    throw new Error('Root element not found');
  }

  const root = ReactDOM.createRoot(rootElement);

  try {
    // Validate environment before starting app
    logger.info('🚀 Initializing GIVC Healthcare Platform...');
    const validation = validateEnvironment();

    if (!validation.isValid) {
      logger.error('Environment validation failed', {
        errors: validation.errors,
        warnings: validation.warnings,
      });

      // Show environment error UI
      root.render(<EnvironmentError errors={validation.errors} />);
      return;
    }

    // Log warnings but continue
    if (validation.warnings.length > 0) {
      logger.warn('Environment validation warnings', {
        warnings: validation.warnings,
      });
    }

    // Get configuration
    const config = getConfig();
    logger.info('✅ Environment validated successfully', {
      environment: import.meta.env.MODE,
      hipaaLevel: config.VITE_HIPAA_COMPLIANCE_LEVEL,
      features: {
        aiAgents: config.VITE_ENABLE_AI_AGENTS === 'true',
        medivault: config.VITE_ENABLE_MEDIVAULT === 'true',
      },
    });

    // Render application with full error handling
    root.render(
      <React.StrictMode>
        <ApplicationErrorBoundary>
          <App />
        </ApplicationErrorBoundary>
      </React.StrictMode>
    );

    logger.info('✅ GIVC Healthcare Platform started successfully');
  } catch (error) {
    logger.error('Failed to initialize application', { error });
    
    // Show generic error UI
    root.render(
      <EnvironmentError
        errors={[
          'Failed to initialize application',
          error instanceof Error ? error.message : 'Unknown error',
        ]}
      />
    );
  }
}

// Start the application
initializeApp();
