import { GIVC_BRANDING } from '../../config/branding.js';
import { useAuth } from '../../hooks/useAuth.jsx';
import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';

const Login = () => {
  const { login, isAuthenticated, isLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const success = await login(email, password);
      if (!success) {
        setError('Invalid credentials. Please try again.');
      }
    } catch (err) {
      setError('Login failed. Please check your connection and try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="loading-spinner w-8 h-8"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex">
      {/* Left side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 givc-gradient">
        <div className="flex flex-col justify-center items-center w-full text-white p-12">
          <div className="max-w-md text-center">
            {/* GIVC Logo */}
            <div className="text-6xl mb-6">🏥</div>
            <h1 className="text-4xl font-bold mb-4">
              {GIVC_BRANDING.company.name}
            </h1>
            <p className="text-xl mb-6">
              {GIVC_BRANDING.company.fullName}
            </p>
            <p className="text-lg opacity-90 mb-8">
              {GIVC_BRANDING.company.tagline}
            </p>
            
            {/* Features */}
            <div className="space-y-4 text-left">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-white rounded-full"></div>
                <span>HIPAA Compliant Platform</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-white rounded-full"></div>
                <span>AI-Powered Medical Analysis</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-white rounded-full"></div>
                <span>RCM Accredited Solutions</span>
              </div>
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-white rounded-full"></div>
                <span>Real-time Compliance Monitoring</span>
              </div>
            </div>
            
            {/* Accreditation Badges */}
            <div className="mt-8 pt-8 border-t border-white/20">
              <div className="text-sm opacity-75 mb-2">Accredited & Certified</div>
              <div className="flex flex-wrap gap-2 justify-center">
                <span className="px-3 py-1 bg-white/20 rounded-full text-xs">
                  {GIVC_BRANDING.assets.badges.rcm}
                </span>
                <span className="px-3 py-1 bg-white/20 rounded-full text-xs">
                  {GIVC_BRANDING.assets.badges.hipaa}
                </span>
                <span className="px-3 py-1 bg-white/20 rounded-full text-xs">
                  {GIVC_BRANDING.assets.badges.iso}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right side - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        <div className="max-w-md w-full">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="text-4xl mb-2">🏥</div>
            <h2 className="text-2xl font-bold givc-text-gradient">
              {GIVC_BRANDING.company.name}
            </h2>
          </div>

          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-gray-900">
              Welcome Back
            </h2>
            <p className="mt-2 text-gray-600">
              Sign in to access your GIVC healthcare platform
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="form-input mt-1"
                placeholder="Enter your email"
                disabled={isSubmitting}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="form-input mt-1"
                placeholder="Enter your password"
                disabled={isSubmitting}
              />
            </div>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting}
              className={`w-full btn-primary ${isSubmitting ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {isSubmitting ? (
                <span className="flex items-center justify-center">
                  <div className="loading-spinner w-4 h-4 mr-2"></div>
                  Signing In...
                </span>
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          {/* Demo Credentials */}
          <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-md">
            <div className="text-sm text-blue-800">
              <strong>Demo Credentials:</strong>
              <br />
              Email: dr.fadil@givc.thefadil.site
              <br />
              Password: demo123
            </div>
          </div>

          {/* Footer */}
          <div className="mt-8 text-center text-sm text-gray-500">
            <p>
              © {new Date().getFullYear()} {GIVC_BRANDING.company.owner} - {GIVC_BRANDING.company.organization}
            </p>
            <p className="mt-1">
              {GIVC_BRANDING.company.accreditation}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
