import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';

import AITriage from '@/components/AITriage/AITriage';
import Login from '@/components/Auth/Login';
import ProtectedRoute from '@/components/Auth/ProtectedRoute';
import ClaimsProcessing from '@/components/ClaimsProcessing/ClaimsProcessingCenter';
import CustomerSupport from '@/components/CustomerSupport/CustomerSupportHub';
import Dashboard from '@/components/Dashboard/Dashboard';
import ErrorBoundary from '@/components/ErrorBoundary/ErrorBoundary';
import LandingPage from '@/components/LandingPage';
import Layout from '@/components/Layout/Layout';
import MedicalAgents from '@/components/MedicalAgents/MedicalAgents';
import MediVault from '@/components/MediVault/MediVault';
import { ToastProvider } from '@/components/UI/Toast';
import { AuthProvider } from '@/hooks/useAuth';

function App() {
  return (
    <ErrorBoundary>
      <ToastProvider>
        <Router>
          <AuthProvider>
            <div className="min-h-screen bg-gray-50">
              <Routes>
                {/* Public Routes */}
                <Route path="/landing" element={<LandingPage />} />
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
                  {/* Main Application Routes - Direct Access */}
                  <Route path="dashboard" element={
                    <ErrorBoundary>
                      <Dashboard />
                    </ErrorBoundary>
                  } />
                  <Route path="medivault" element={
                    <ErrorBoundary>
                      <MediVault />
                    </ErrorBoundary>
                  } />
                  <Route path="triage" element={
                    <ErrorBoundary>
                      <AITriage />
                    </ErrorBoundary>
                  } />
                  <Route path="agents" element={
                    <ErrorBoundary>
                      <MedicalAgents />
                    </ErrorBoundary>
                  } />
                  <Route path="support" element={
                    <ErrorBoundary>
                      <CustomerSupport />
                    </ErrorBoundary>
                  } />
                  <Route path="claims" element={
                    <ErrorBoundary>
                      <ClaimsProcessing />
                    </ErrorBoundary>
                  } />
                </Route>
                
                {/* Catch-all redirect */}
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </div>
          </AuthProvider>
        </Router>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;
