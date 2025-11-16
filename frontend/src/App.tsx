/**
 * GIVC Healthcare Platform - Main Application Component
 *  Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Consolidated App component with TypeScript, enhanced routing,
 * lazy loading, and comprehensive error handling
 */

import { Suspense, lazy } from 'react';
import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import ErrorBoundary from '@/components/ErrorBoundary/ErrorBoundary';
import { ToastProvider } from '@/components/UI/Toast';
import { AuthProvider } from '@/hooks/useAuth';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { LanguageProvider } from '@/contexts/LanguageContext';

// Loading Component with beautiful skeleton UI
import LoadingFallback from '@/components/UI/LoadingFallback';

// Critical components - load immediately (no lazy loading)
import Login from '@/components/Auth/Login';
import ProtectedRoute from '@/components/Auth/ProtectedRoute';
import Layout from '@/components/Layout/Layout';

// Lazy-loaded components for better initial load performance
const Dashboard = lazy(() => import('@/components/Dashboard/Dashboard'));
const MediVault = lazy(() => import('@/components/MediVault/MediVault'));
const AITriage = lazy(() => import('@/components/AITriage/AITriage'));
const MedicalAgents = lazy(() => import('@/components/MedicalAgents/MedicalAgents'));
const CustomerSupportHub = lazy(() => import('@/components/CustomerSupport/CustomerSupportHub'));
const ClaimsProcessingCenter = lazy(() => import('@/components/ClaimsProcessing/ClaimsProcessingCenter'));
const RiskAssessmentEngine = lazy(() => import('@/components/RiskAssessment/RiskAssessmentEngine'));
const FollowUpWorksheet = lazy(() => import('@/components/FollowUps/FollowUpWorksheet'));
const EligibilityVerification = lazy(() => import('@/components/EligibilityVerification/EligibilityVerification'));

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <LanguageProvider>
          <ToastProvider>
            <Router>
              <AuthProvider>
                <div className="min-h-screen bg-gray-50 dark:bg-slate-900 transition-colors duration-300">
                  <Suspense fallback={<LoadingFallback />}>
                    <Routes>
                      <Route path="/login" element={<Login />} />
                      <Route path="/" element={<Navigate to="/dashboard" replace />} />
                      <Route path="/dashboard-direct" element={<Dashboard />} />
                      <Route
                        path="/"
                        element={
                          <ProtectedRoute>
                            <ErrorBoundary>
                              <Layout />
                            </ErrorBoundary>
                          </ProtectedRoute>
                        }
                      >
                        <Route path="dashboard" element={<ErrorBoundary><Dashboard /></ErrorBoundary>} />
                        <Route path="medivault" element={<ErrorBoundary><MediVault /></ErrorBoundary>} />
                        <Route path="triage" element={<ErrorBoundary><AITriage /></ErrorBoundary>} />
                        <Route path="agents" element={<ErrorBoundary><MedicalAgents /></ErrorBoundary>} />
                        <Route path="support" element={<ErrorBoundary><CustomerSupportHub /></ErrorBoundary>} />
                        <Route path="claims" element={<ErrorBoundary><ClaimsProcessingCenter /></ErrorBoundary>} />
                        <Route path="risk-assessment" element={<ErrorBoundary><RiskAssessmentEngine /></ErrorBoundary>} />
                        <Route path="follow-ups" element={<ErrorBoundary><FollowUpWorksheet /></ErrorBoundary>} />
                        <Route path="eligibility" element={<ErrorBoundary><EligibilityVerification /></ErrorBoundary>} />
                      </Route>
                      <Route path="*" element={<Navigate to="/dashboard" replace />} />
                    </Routes>
                  </Suspense>
                </div>
              </AuthProvider>
            </Router>
          </ToastProvider>
        </LanguageProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
