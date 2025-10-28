import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../hooks/useAuth.jsx';
import { NavLink } from 'react-router-dom';

const DashboardProfessional = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({});
  const [recentActivity, setRecentActivity] = useState([]);

  useEffect(() => {
    // Professional healthcare metrics
    setStats({
      totalPatients: 12847,
      processedToday: 189,
      pendingClaims: 42,
      systemUptime: 99.8,
      costSavings: 2450280,
      satisfaction: 94.8,
      aiAccuracy: 97.3,
      complianceScore: 99.2
    });

    setRecentActivity([
      {
        id: 1,
        title: 'AI Claims Processing',
        description: '23 claims auto-approved via intelligent analysis',
        time: '2 minutes ago',
        type: 'success',
        icon: '🤖',
        value: '+$45,280'
      },
      {
        id: 2,
        title: 'Risk Assessment Alert',
        description: 'High-risk patient pattern detected requiring attention',
        time: '15 minutes ago',
        type: 'warning',
        icon: '⚠️',
        value: 'Priority'
      },
      {
        id: 3,
        title: 'Customer Support Resolution',
        description: 'AI chatbot resolved 12 complex patient inquiries',
        time: '30 minutes ago',
        type: 'info',
        icon: '💬',
        value: '95% satisfaction'
      },
      {
        id: 4,
        title: 'Document Processing',
        description: 'MediVault processed 67 medical documents with encryption',
        time: '1 hour ago',
        type: 'success',
        icon: '📄',
        value: '100% secure'
      }
    ]);
  }, []);

  const quickActions = [
    {
      name: 'AI Customer Support',
      href: '/support',
      icon: '🤖',
      gradient: 'from-blue-500 to-blue-600',
      description: 'Intelligent patient assistance',
      stats: '24/7 Available'
    },
    {
      name: 'Claims Processing',
      href: '/claims',
      icon: '📋',
      gradient: 'from-green-500 to-green-600',
      description: 'Automated claim reviews',
      stats: '42 Pending'
    },
    {
      name: 'Risk Assessment',
      href: '/risk-assessment',
      icon: '⚖️',
      gradient: 'from-purple-500 to-purple-600',
      description: 'Predictive health analytics',
      stats: 'AI Powered'
    },
    {
      name: 'MediVault',
      href: '/medivault',
      icon: '🗂️',
      gradient: 'from-indigo-500 to-indigo-600',
      description: 'Secure document storage',
      stats: 'HIPAA Compliant'
    }
  ];

  const statCards = [
    {
      title: 'Total Patients',
      value: stats.totalPatients?.toLocaleString(),
      icon: '👥',
      change: '+12%',
      changeType: 'positive',
      gradient: 'from-blue-500 to-blue-600'
    },
    {
      title: 'Processed Today',
      value: stats.processedToday,
      icon: '⚡',
      change: '+8%',
      changeType: 'positive',
      gradient: 'from-green-500 to-green-600'
    },
    {
      title: 'Pending Claims',
      value: stats.pendingClaims,
      icon: '📋',
      change: '-15%',
      changeType: 'positive',
      gradient: 'from-yellow-500 to-yellow-600'
    },
    {
      title: 'System Uptime',
      value: `${stats.systemUptime}%`,
      icon: '🔧',
      change: '+0.2%',
      changeType: 'positive',
      gradient: 'from-purple-500 to-purple-600'
    },
    {
      title: 'Cost Savings',
      value: `$${(stats.costSavings / 1000).toFixed(0)}K`,
      icon: '💰',
      change: '+23%',
      changeType: 'positive',
      gradient: 'from-emerald-500 to-emerald-600'
    },
    {
      title: 'Patient Satisfaction',
      value: `${stats.satisfaction}%`,
      icon: '😊',
      change: '+3%',
      changeType: 'positive',
      gradient: 'from-pink-500 to-pink-600'
    },
    {
      title: 'AI Accuracy',
      value: `${stats.aiAccuracy}%`,
      icon: '🎯',
      change: '+1.5%',
      changeType: 'positive',
      gradient: 'from-orange-500 to-orange-600'
    },
    {
      title: 'Compliance Score',
      value: `${stats.complianceScore}%`,
      icon: '✅',
      change: '+0.8%',
      changeType: 'positive',
      gradient: 'from-cyan-500 to-cyan-600'
    }
  ];

  const getActivityIcon = (type) => {
    const styles = {
      success: 'bg-green-100 text-green-600 border-green-200',
      warning: 'bg-yellow-100 text-yellow-600 border-yellow-200',
      info: 'bg-blue-100 text-blue-600 border-blue-200',
      error: 'bg-red-100 text-red-600 border-red-200'
    };
    return styles[type] || styles.info;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
      <div className="p-8 lg:p-12 max-w-7xl mx-auto">
        {/* Welcome Section - Clean & Professional */}
        <div className="mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center lg:text-left"
          >
            <h1 className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4">
              Welcome back, {user?.name?.split(' ')[0] || 'Doctor'} 👋
            </h1>
            <p className="text-xl text-gray-600 max-w-2xl">
              Your comprehensive healthcare & insurance platform dashboard
            </p>
          </motion.div>
        </div>

        {/* Key Metrics Grid - Professional Layout */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 mb-12">
          {statCards.map((card, index) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white/80 backdrop-blur-sm rounded-3xl p-6 lg:p-8 shadow-xl border border-white/50 hover:shadow-2xl hover:scale-105 transition-all duration-300"
            >
              {/* Icon with Gradient */}
              <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${card.gradient} flex items-center justify-center mb-6 shadow-lg`}>
                <span className="text-2xl text-white">{card.icon}</span>
              </div>

              {/* Value */}
              <div className="mb-4">
                <p className="text-3xl lg:text-4xl font-bold text-gray-900 mb-2">{card.value}</p>
                <p className="text-base lg:text-lg font-medium text-gray-600">{card.title}</p>
              </div>

              {/* Change Indicator */}
              <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${
                card.changeType === 'positive' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
              }`}>
                <span className="mr-1">
                  {card.changeType === 'positive' ? '↗' : '↘'}
                </span>
                {card.change}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Quick Actions - Enhanced Professional Design */}
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 lg:p-12 shadow-xl border border-white/50 mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center lg:text-left">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-6 lg:gap-8">
            {quickActions.map((action, index) => (
              <motion.div
                key={action.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 + index * 0.1 }}
              >
                <NavLink
                  to={action.href}
                  className="group block p-8 bg-gradient-to-br from-white to-gray-50/50 rounded-3xl border border-gray-200/50 hover:border-gray-300 hover:shadow-2xl transition-all duration-300 transform hover:scale-105"
                >
                  {/* Icon */}
                  <div className={`w-20 h-20 rounded-3xl bg-gradient-to-br ${action.gradient} flex items-center justify-center mb-6 shadow-xl group-hover:shadow-2xl transition-all duration-300`}>
                    <span className="text-3xl text-white">{action.icon}</span>
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-gray-700 transition-colors">
                    {action.name}
                  </h3>
                  <p className="text-base text-gray-600 mb-4 leading-relaxed">
                    {action.description}
                  </p>
                  
                  {/* Stats Badge */}
                  <div className="inline-flex items-center px-4 py-2 bg-blue-50 text-blue-700 rounded-2xl text-sm font-semibold">
                    {action.stats}
                  </div>
                </NavLink>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Recent Activity - Clean Professional Design */}
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 lg:p-12 shadow-xl border border-white/50">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-3xl font-bold text-gray-900">Recent Activity</h2>
            <button className="px-6 py-3 bg-blue-600 text-white rounded-2xl hover:bg-blue-700 transition-colors font-semibold">
              View All
            </button>
          </div>

          <div className="space-y-6">
            {recentActivity.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.8 + index * 0.1 }}
                className="flex items-start space-x-6 p-6 bg-gradient-to-r from-gray-50 to-white rounded-2xl border border-gray-100 hover:shadow-lg transition-all duration-300"
              >
                {/* Activity Icon */}
                <div className={`w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0 border ${getActivityIcon(activity.type)}`}>
                  <span className="text-xl">{activity.icon}</span>
                </div>

                {/* Activity Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-gray-900 mb-2">
                        {activity.title}
                      </h3>
                      <p className="text-base text-gray-600 leading-relaxed mb-3">
                        {activity.description}
                      </p>
                      <p className="text-sm text-gray-500">
                        {activity.time}
                      </p>
                    </div>
                    
                    {/* Value Badge */}
                    <div className="ml-4 flex-shrink-0">
                      <span className="inline-flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-2xl text-sm font-semibold">
                        {activity.value}
                      </span>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardProfessional;
