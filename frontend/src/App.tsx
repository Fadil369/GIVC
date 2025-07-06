import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from '@/hooks/useAuth';
import Layout from '@/components/Layout/Layout';
import Dashboard from '@/components/Dashboard/Dashboard';
import MediVault from '@/components/MediVault/MediVault';
import AITriage from '@/components/AITriage/AITriage';
import MedicalAgents from '@/components/MedicalAgents/MedicalAgents';
import Login from '@/components/Auth/Login';
import ProtectedRoute from '@/components/Auth/ProtectedRoute';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={<Login />} />
            
            {/* Protected Routes */}
            <Route path="/" element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }>
              {/* Default redirect to dashboard */}
              <Route index element={<Navigate to="/dashboard" replace />} />
              
              {/* Main Application Routes */}
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="medivault" element={<MediVault />} />
              <Route path="triage" element={<AITriage />} />
              <Route path="agents" element={<MedicalAgents />} />
              
              {/* Catch-all redirect */}
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Route>
          </Routes>
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;