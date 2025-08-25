import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';

import Login from './components/Auth/Login.jsx';
import ProtectedRoute from './components/Auth/ProtectedRoute.jsx';
import Dashboard from './components/Dashboard/Dashboard.jsx';
import ErrorBoundary from './components/ErrorBoundary/ErrorBoundary.jsx';
import Layout from './components/Layout/Layout.jsx';
import { AuthProvider } from './hooks/useAuth.jsx';
import { ThemeProvider } from './contexts/ThemeContext.jsx';
import { LanguageProvider } from './contexts/LanguageContext.jsx';

// Import our new LLM-powered insurance components
import CustomerSupportHub from './components/CustomerSupport/CustomerSupportHub.jsx';
import ClaimsProcessingCenter from './components/ClaimsProcessing/ClaimsProcessingCenter.jsx';
import RiskAssessmentEngine from './components/RiskAssessment/RiskAssessmentEngine.jsx';
import MediVault from './components/MediVault/MediVault.jsx';

// Temporary simple toast for now - we'll add full UI components back later
const SimpleToastProvider = ({ children }) => children;

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <LanguageProvider>
          <SimpleToastProvider>
            <Router>
              <AuthProvider>
                <div className="min-h-screen bg-gray-50 dark:bg-slate-900 transition-colors duration-300">
                  <Routes>
                    {/* Public Routes */}
                    <Route path="/login" element={<Login />} />
                    
                    {/* Root redirect */}
                    <Route path="/" element={<Navigate to="/dashboard" replace />} />
                    
                    {/* Direct Dashboard Test Route */}
                    <Route path="/dashboard-direct" element={<Dashboard />} />
                    
                    {/* Protected Routes with Layout */}
                    <Route path="/" element={
                      <ProtectedRoute>
                        <ErrorBoundary>
                          <Layout />
                        </ErrorBoundary>
                      </ProtectedRoute>
                    }>
                      {/* Main Application Routes - Core Dashboard and Insurance Components */}
                      <Route path="dashboard" element={
                        <ErrorBoundary>
                          <Dashboard />
                        </ErrorBoundary>
                      } />
                      
                      {/* LLM-Powered Insurance Components */}
                      <Route path="support" element={
                        <ErrorBoundary>
                          <CustomerSupportHub />
                        </ErrorBoundary>
                      } />
                      <Route path="claims" element={
                        <ErrorBoundary>
                          <ClaimsProcessingCenter />
                        </ErrorBoundary>
                      } />
                      <Route path="risk-assessment" element={
                        <ErrorBoundary>
                          <RiskAssessmentEngine />
                        </ErrorBoundary>
                      } />
                      
                      {/* Placeholder routes that redirect to dashboard */}
                      <Route path="medivault" element={
                        <ErrorBoundary>
                          <MediVault />
                        </ErrorBoundary>
                      } />
                      <Route path="triage" element={<Navigate to="/dashboard" replace />} />
                      <Route path="agents" element={<Navigate to="/dashboard" replace />} />
                    </Route>
                    
                    {/* Catch-all redirect */}
                    <Route path="*" element={<Navigate to="/dashboard" replace />} />
                  </Routes>
                </div>
              </AuthProvider>
            </Router>
          </SimpleToastProvider>
        </LanguageProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;