import { motion } from 'framer-motion';
import React from 'react';
import { Link } from 'react-router-dom';

const LandingPage= () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-green-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">G</span>
              </div>
              <span className="text-2xl font-bold givc-text-gradient">GIVC Healthcare</span>
            </div>
            <Link
              to="/login"
              className="btn-primary"
            >
              Sign In
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-8">
            Revolutionizing
            <span className="block givc-text-gradient">Healthcare Management</span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-12 max-w-3xl mx-auto">
            Integrated NPHIES compliance solutions with AI-powered workflows for Saudi healthcare providers.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link to="/login" className="btn-primary text-lg px-8 py-4">
              Access Platform
            </Link>
            <button className="btn-outline text-lg px-8 py-4">
              Learn More
            </button>
          </div>
        </motion.div>

        {/* Dashboard Preview */}
        <motion.div
          className="mb-16"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
        >
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">Healthcare Dashboard</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[
              { icon: '📊', title: 'Claims Processed', value: '98.2%', change: '+2.4% from last month' },
              { icon: '🔍', title: 'Eligibility Checks', value: '87', change: '+12% from last week' },
              { icon: '💰', title: 'Monthly Revenue', value: 'SAR 256K', change: '+8.1% from last month' },
              { icon: '👥', title: 'Active Patients', value: '348', change: '+5.2% from last month' }
            ].map((metric, index) => (
              <motion.div
                key={metric.title}
                className="metric-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.3 + index * 0.1 }}
              >
                <div className="metric-title">
                  <span className="text-2xl">{metric.icon}</span>
                  {metric.title}
                </div>
                <div className="metric-value">{metric.value}</div>
                <div className="metric-change metric-change-positive">
                  {metric.change}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div
          className="mb-16"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
        >
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-8">Quick Actions</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { icon: '🧪', title: 'Lab Results Parser' },
              { icon: '🔍', title: 'Check Eligibility' },
              { icon: '📄', title: 'Submit Claim' },
              { icon: '📈', title: 'View Analytics' }
            ].map((action, index) => (
              <motion.div
                key={action.title}
                className="quick-action"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: 0.5 + index * 0.1 }}
                whileHover={{ scale: 1.02 }}
              >
                <span className="quick-action-icon">{action.icon}</span>
                <span>{action.title}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Features */}
        <motion.div
          className="mb-16"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">Platform Features</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                icon: '🤖',
                title: 'AI-Powered Analytics',
                description: 'Advanced machine learning algorithms for predictive healthcare insights and automated decision support.'
              },
              {
                icon: '🏥',
                title: 'NPHIES Compliance',
                description: 'Fully compliant with Saudi NPHIES standards for seamless insurance claim processing and eligibility verification.'
              },
              {
                icon: '🔒',
                title: 'HIPAA Security',
                description: 'Enterprise-grade security with end-to-end encryption ensuring complete patient data protection and privacy.'
              }
            ].map((feature, index) => (
              <motion.div
                key={feature.title}
                className="card text-center"
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.7 + index * 0.1 }}
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-green-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">G</span>
                </div>
                <span className="text-xl font-bold">GIVC Healthcare Platform</span>
              </div>
              <p className="text-gray-400">
                Advanced NPHIES-compliant healthcare management platform for Saudi healthcare providers.
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Quick Links</h3>
              <ul className="space-y-2 text-gray-400">
                <li><Link to="/login" className="hover:text-white transition-colors">Dashboard</Link></li>
                <li><a href="#" className="hover:text-white transition-colors">Eligibility Check</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Claims Management</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Analytics</a></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold mb-4">Contact</h3>
              <div className="space-y-2 text-gray-400">
                <p className="flex items-center gap-2">
                  <span>📞</span>
                  +966 55 123 4567
                </p>
                <p className="flex items-center gap-2">
                  <span>📧</span>
                  contact@givc-healthcare.sa
                </p>
                <p className="flex items-center gap-2">
                  <span>📍</span>
                  Riyadh, Saudi Arabia
                </p>
              </div>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 GIVC Healthcare Platform. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
