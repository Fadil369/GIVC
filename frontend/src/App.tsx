import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';

import AITriage from '@/components/AITriage/AITriage';
import Login from '@/components/Auth/Login';
import ProtectedRoute from '@/components/Auth/ProtectedRoute';
import ClaimsProcessing from '@/components/ClaimsProcessing/ClaimsProcessing';
import CustomerSupport from '@/components/CustomerSupport/CustomerSupport';
import Dashboard from '@/components/Dashboard/Dashboard';
import ErrorBoundary from '@/components/ErrorBoundary/ErrorBoundary';
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
                <Route path="/login" element={<Login />} />
                
                {/* Protected Routes */}
                <Route path="/" element={
                  <ProtectedRoute>
                    <ErrorBoundary>
                      <Layout />
                    </ErrorBoundary>
                  </ProtectedRoute>
                }>
                  {/* Default redirect to dashboard */}
                  <Route index element={<Navigate to="/dashboard" replace />} />
                  
                  {/* Main Application Routes */}
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
                  
                  {/* Catch-all redirect */}
                  <Route path="*" element={<Navigate to="/dashboard" replace />} />
                </Route>
              </Routes>
            </div>
          </AuthProvider>
        </Router>
      </ToastProvider>
    </ErrorBoundary>
  );
}

export default App;