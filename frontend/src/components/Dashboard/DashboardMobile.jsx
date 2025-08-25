import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../hooks/useAuth.jsx';
import { NavLink } from 'react-router-dom';

const DashboardMobile = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({});
  const [activeTab, setActiveTab] = useState('overview');
  const [notifications, setNotifications] = useState([]);
  const [recentActivity, setRecentActivity] = useState([]);

  useEffect(() => {
    // Mock data with realistic healthcare insurance metrics
    setStats({
      totalClaims: 2847,
      processedToday: 189,
      pendingReview: 42,
      fraudDetected: 3,
      customerSupport: 156,
      avgProcessingTime: '3.2 min',
      satisfaction: 94.8,
      complianceScore: 99.2,
      costSavings: 145280,
      activePolicies: 12450,
      riskAssessments: 89,
      systemUptime: 99.8
    });

    setNotifications([
      { id: 1, type: 'urgent', title: 'High Risk Patient Alert', message: 'Patient #P-789012 requires immediate attention', time: '5 min ago' },
      { id: 2, type: 'info', title: 'Claims Processing Update', message: '15 claims auto-approved via AI', time: '12 min ago' },
      { id: 3, type: 'success', title: 'Fraud Prevention', message: 'Suspicious activity blocked automatically', time: '1 hour ago' }
    ]);

    setRecentActivity([
      { id: 1, icon: '🤖', title: 'AI Claims Auto-Approval', description: '23 routine claims processed automatically', time: '2 min ago', status: 'success' },
      { id: 2, icon: '🔍', title: 'Fraud Detection Alert', description: 'Suspicious pattern detected in claim CLM-2025-003', time: '15 min ago', status: 'warning' },
      { id: 3, icon: '📞', title: 'Customer Support Session', description: 'AI chatbot resolved 12 customer inquiries', time: '30 min ago', status: 'info' },
      { id: 4, icon: '⚖️', title: 'Risk Assessment Completed', description: 'High-risk patient profile updated with new data', time: '1 hour ago', status: 'info' },
      { id: 5, icon: '📋', title: 'Claims Batch Processed', description: '67 claims processed in latest batch run', time: '2 hours ago', status: 'success' }
    ]);
  }, []);

  const quickActions = [
    { name: 'Customer Support', href: '/support', icon: '🎧', color: 'bg-blue-500', description: 'AI-powered assistance' },
    { name: 'Process Claims', href: '/claims', icon: '📋', color: 'bg-green-500', description: 'Review pending claims' },
    { name: 'Risk Assessment', href: '/risk-assessment', icon: '⚖️', color: 'bg-purple-500', description: 'Analyze patient risk' },
    { name: 'AI Triage', href: '/triage', icon: '🩺', color: 'bg-red-500', description: 'Emergency assessment' },
    { name: 'MediVault', href: '/medivault', icon: '🗂️', color: 'bg-yellow-500', description: 'Secure file storage' },
    { name: 'Medical Agents', href: '/agents', icon: '🤖', color: 'bg-indigo-500', description: 'AI medical analysis' }
  ];

  const statCards = [
    { title: 'Total Claims', value: stats.totalClaims?.toLocaleString(), icon: '📋', color: 'bg-blue-50 text-blue-600', change: '+12%' },
    { title: 'Processed Today', value: stats.processedToday, icon: '⚡', color: 'bg-green-50 text-green-600', change: '+8%' },
    { title: 'Pending Review', value: stats.pendingReview, icon: '⏳', color: 'bg-yellow-50 text-yellow-600', change: '-15%' },
    { title: 'Fraud Detected', value: stats.fraudDetected, icon: '🛡️', color: 'bg-red-50 text-red-600', change: '-22%' },
    { title: 'Support Tickets', value: stats.customerSupport, icon: '🎧', color: 'bg-purple-50 text-purple-600', change: '+5%' },
    { title: 'Avg Process Time', value: stats.avgProcessingTime, icon: '⏱️', color: 'bg-indigo-50 text-indigo-600', change: '-18%' },
    { title: 'Satisfaction Score', value: `${stats.satisfaction}%`, icon: '😊', color: 'bg-green-50 text-green-600', change: '+3%' },
    { title: 'Compliance Score', value: `${stats.complianceScore}%`, icon: '✅', color: 'bg-blue-50 text-blue-600', change: '+1%' }
  ];

  const getNotificationIcon = (type) => {
    const icons = {
      urgent: '🚨',
      warning: '⚠️',
      info: 'ℹ️',
      success: '✅'
    };
    return icons[type] || 'ℹ️';
  };

  const getNotificationColor = (type) => {
    const colors = {
      urgent: 'bg-red-50 border-red-200 text-red-800',
      warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
      info: 'bg-blue-50 border-blue-200 text-blue-800',
      success: 'bg-green-50 border-green-200 text-green-800'
    };
    return colors[type] || 'bg-gray-50 border-gray-200 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-purple-50">
      {/* Mobile-First Container */}
      <div className="px-4 py-6 lg:px-8 lg:py-8 max-w-7xl mx-auto">
        {/* Header Section - Mobile Optimized */}
        <div className="mb-6 lg:mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div className="mb-4 lg:mb-0">
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900">
                Welcome back, {user?.name?.split(' ')[0] || 'Professional'} 👋
              </h1>
              <p className="text-sm lg:text-base text-gray-600 mt-1">
                Your unified healthcare & insurance platform dashboard
              </p>
            </div>
            <div className="flex items-center space-x-2 lg:space-x-4">
              <div className="flex items-center space-x-2 px-3 py-2 bg-green-50 border border-green-200 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs lg:text-sm font-medium text-green-700">All Systems Operational</span>
              </div>
            </div>
          </div>
        </div>

        {/* Tab Navigation - Mobile First */}
        <div className="mb-6 lg:mb-8">
          <div className="flex overflow-x-auto pb-2 lg:pb-0 scrollbar-hide">
            <div className="flex space-x-2 lg:space-x-4 min-w-max lg:min-w-0">
              {[
                { id: 'overview', name: 'Overview', icon: '📊' },
                { id: 'claims', name: 'Claims', icon: '📋' },
                { id: 'patients', name: 'Patients', icon: '👥' },
                { id: 'analytics', name: 'Analytics', icon: '📈' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 py-2 lg:px-6 lg:py-3 rounded-lg font-medium text-sm lg:text-base transition-all duration-200 whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'bg-white text-blue-700 shadow-md border border-blue-200'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
                  }`}
                >
                  <span className="text-lg">{tab.icon}</span>
                  <span>{tab.name}</span>
                </button>
              ))}</div>
          </div>
        </div>

        <AnimatePresence mode="wait">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <motion.div
              key="overview"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6 lg:space-y-8"
            >
              {/* Stats Grid - Mobile First Responsive */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-6">
                {statCards.map((stat, index) => (
                  <motion.div
                    key={stat.title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-white/80 backdrop-blur-sm rounded-xl lg:rounded-2xl p-4 lg:p-6 shadow-sm border border-gray-200/50 hover:shadow-lg hover:border-gray-300/50 transition-all"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className={`p-2 lg:p-3 rounded-lg lg:rounded-xl ${stat.color}`}>
                        <span className="text-lg lg:text-xl">{stat.icon}</span>
                      </div>
                      <span className={`text-xs lg:text-sm font-medium px-2 py-1 rounded-full ${
                        stat.change.startsWith('+') ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                      }`}>
                        {stat.change}
                      </span>
                    </div>
                    <div>
                      <p className="text-xs lg:text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                      <p className="text-lg lg:text-2xl font-bold text-gray-900">{stat.value}</p>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Quick Actions - Mobile Optimized Grid */}
              <div className="bg-white/80 backdrop-blur-sm rounded-xl lg:rounded-2xl p-4 lg:p-6 shadow-sm border border-gray-200/50">
                <h2 className="text-lg lg:text-xl font-semibold text-gray-900 mb-4 lg:mb-6">Quick Actions</h2>
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-3 lg:gap-4">
                  {quickActions.map((action) => (
                    <NavLink
                      key={action.name}
                      to={action.href}
                      className="group flex flex-col items-center p-4 lg:p-6 bg-gray-50 hover:bg-white rounded-xl lg:rounded-2xl transition-all duration-200 hover:shadow-md border border-transparent hover:border-gray-200"
                    >
                      <div className={`w-12 h-12 lg:w-16 lg:h-16 ${action.color} rounded-xl lg:rounded-2xl flex items-center justify-center mb-3 group-hover:scale-110 transition-transform shadow-lg`}>
                        <span className="text-xl lg:text-2xl text-white">{action.icon}</span>
                      </div>
                      <h3 className="font-semibold text-gray-900 text-sm lg:text-base text-center mb-1">{action.name}</h3>
                      <p className="text-xs lg:text-sm text-gray-600 text-center">{action.description}</p>
                    </NavLink>
                  ))}
                </div>
              </div>

              {/* Notifications & Activity - Mobile Stacked Layout */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
                {/* Notifications */}
                <div className="bg-white/80 backdrop-blur-sm rounded-xl lg:rounded-2xl p-4 lg:p-6 shadow-sm border border-gray-200/50">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg lg:text-xl font-semibold text-gray-900">Notifications</h2>
                    <span className="bg-red-500 text-white text-xs px-2 py-1 rounded-full">{notifications.length}</span>
                  </div>
                  <div className="space-y-3">
                    {notifications.slice(0, 3).map((notification) => (
                      <div
                        key={notification.id}
                        className={`p-3 lg:p-4 rounded-lg lg:rounded-xl border ${getNotificationColor(notification.type)}`}
                      >
                        <div className="flex items-start space-x-3">
                          <span className="text-lg flex-shrink-0">{getNotificationIcon(notification.type)}</span>
                          <div className="min-w-0 flex-1">
                            <h4 className="font-medium text-sm lg:text-base">{notification.title}</h4>
                            <p className="text-xs lg:text-sm opacity-90 mt-1">{notification.message}</p>
                            <p className="text-xs opacity-75 mt-2">{notification.time}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <button className="w-full mt-4 px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors">
                    View All Notifications
                  </button>
                </div>

                {/* Recent Activity */}
                <div className="bg-white/80 backdrop-blur-sm rounded-xl lg:rounded-2xl p-4 lg:p-6 shadow-sm border border-gray-200/50">
                  <h2 className="text-lg lg:text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
                  <div className="space-y-3">
                    {recentActivity.slice(0, 4).map((activity) => (
                      <div key={activity.id} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg lg:rounded-xl">
                        <span className="text-lg flex-shrink-0">{activity.icon}</span>
                        <div className="min-w-0 flex-1">
                          <h4 className="font-medium text-sm lg:text-base text-gray-900">{activity.title}</h4>
                          <p className="text-xs lg:text-sm text-gray-600 mt-1">{activity.description}</p>
                          <p className="text-xs text-gray-500 mt-2">{activity.time}</p>
                        </div>
                        <div className={`w-2 h-2 rounded-full flex-shrink-0 mt-2 ${
                          activity.status === 'success' ? 'bg-green-500' :
                          activity.status === 'warning' ? 'bg-yellow-500' :
                          'bg-blue-500'
                        }`}></div>
                      </div>
                    ))}
                  </div>
                  <button className="w-full mt-4 px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition-colors">
                    View Activity Log
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {/* Other tabs content placeholder */}
          {activeTab !== 'overview' && (
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="bg-white/80 backdrop-blur-sm rounded-xl lg:rounded-2xl p-8 lg:p-12 shadow-sm border border-gray-200/50 text-center"
            >
              <div className="text-6xl lg:text-8xl mb-4">
                {activeTab === 'claims' ? '📋' : activeTab === 'patients' ? '👥' : '📈'}
              </div>
              <h2 className="text-xl lg:text-2xl font-bold text-gray-900 mb-2">
                {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Dashboard
              </h2>
              <p className="text-gray-600 mb-6">
                Detailed {activeTab} management interface coming soon
              </p>
              <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                Explore {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default DashboardMobile;
