import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../hooks/useAuth';
import { NavLink } from 'react-router-dom';

const DashboardProfessional = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({});
  const [recentActivity, setRecentActivity] = useState([]);

  useEffect(() => {
    // Professional healthcare metrics with SAR currency
    setStats({
      totalPatients: 12847,
      processedToday: 189,
      pendingClaims: 42,
      systemUptime: 99.8,
      costSavings: 2450280, // In SAR
      satisfaction: 94.8,
      aiAccuracy: 97.3,
      complianceScore: 99.2
    });

    setRecentActivity([
      {
        id: 1,
        title: 'معالجة المطالبات بالذكاء الاصطناعي',
        description: 'تم الموافقة التلقائية على 23 مطالبة عبر التحليل الذكي',
        time: 'منذ دقيقتين',
        type: 'success',
        icon: '🤖',
        value: '+45,280 ر.س'
      },
      {
        id: 2,
        title: 'تنبيه تقييم المخاطر',
        description: 'تم اكتشاف نمط مريض عالي الخطورة يتطلب الانتباه',
        time: 'منذ 15 دقيقة',
        type: 'warning',
        icon: '⚠️',
        value: 'أولوية عالية'
      },
      {
        id: 3,
        title: 'حل دعم العملاء',
        description: 'روبوت الدردشة الذكي حل 12 استفسار مريض معقد',
        time: 'منذ 30 دقيقة',
        type: 'info',
        icon: '💬',
        value: 'رضا 95%'
      },
      {
        id: 4,
        title: 'معالجة الوثائق',
        description: 'خزينة الطب عالجت 67 وثيقة طبية مع التشفير',
        time: 'منذ ساعة',
        type: 'success',
        icon: '📄',
        value: 'آمن 100%'
      }
    ]);
  }, []);

  const quickActions = [
    {
      name: 'دعم العملاء الذكي',
      href: '/support',
      icon: '🤖',
      gradient: 'from-blue-500 to-blue-600',
      description: 'مساعدة المرضى الذكية',
      stats: 'متاح 24/7'
    },
    {
      name: 'معالجة المطالبات',
      href: '/claims',
      icon: '📋',
      gradient: 'from-green-500 to-green-600',
      description: 'مراجعة المطالبات التلقائية',
      stats: '42 معلقة'
    },
    {
      name: 'تقييم المخاطر',
      href: '/risk-assessment',
      icon: '⚖️',
      gradient: 'from-purple-500 to-purple-600',
      description: 'تحليلات الصحة التنبؤية',
      stats: 'مدعوم بالذكاء الاصطناعي'
    },
    {
      name: 'خزينة الطب',
      href: '/medivault',
      icon: '🗂️',
      gradient: 'from-indigo-500 to-indigo-600',
      description: 'تخزين الوثائق الآمن',
      stats: 'متوافق مع HIPAA'
    }
  ];

  const statCards = [
    {
      title: 'إجمالي المرضى',
      value: stats.totalPatients?.toLocaleString(),
      icon: '👥',
      change: '+12%',
      changeType: 'positive',
      gradient: 'from-blue-500 to-blue-600'
    },
    {
      title: 'معالج اليوم',
      value: stats.processedToday,
      icon: '⚡',
      change: '+8%',
      changeType: 'positive',
      gradient: 'from-green-500 to-green-600'
    },
    {
      title: 'المطالبات المعلقة',
      value: stats.pendingClaims,
      icon: '📋',
      change: '-15%',
      changeType: 'positive',
      gradient: 'from-yellow-500 to-yellow-600'
    },
    {
      title: 'وقت تشغيل النظام',
      value: `${stats.systemUptime}%`,
      icon: '🔧',
      change: '+0.2%',
      changeType: 'positive',
      gradient: 'from-purple-500 to-purple-600'
    },
    {
      title: 'توفير التكاليف',
      value: `${(stats.costSavings / 1000).toFixed(0)}K ر.س`,
      icon: '💰',
      change: '+23%',
      changeType: 'positive',
      gradient: 'from-emerald-500 to-emerald-600'
    },
    {
      title: 'رضا المرضى',
      value: `${stats.satisfaction}%`,
      icon: '😊',
      change: '+3%',
      changeType: 'positive',
      gradient: 'from-pink-500 to-pink-600'
    },
    {
      title: 'دقة الذكاء الاصطناعي',
      value: `${stats.aiAccuracy}%`,
      icon: '🎯',
      change: '+1.5%',
      changeType: 'positive',
      gradient: 'from-orange-500 to-orange-600'
    },
    {
      title: 'نقاط الامتثال',
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
    <div className="min-h-screen bg-white relative overflow-hidden">
      <div className="p-8 lg:p-12 max-w-7xl mx-auto">
        {/* Welcome Section - Clean & Simple */}
        <div className="mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center lg:text-left"
          >
            <motion.h1 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.2 }}
              className="text-4xl lg:text-5xl font-bold text-gray-900 mb-4 leading-tight"
            >
              أهلاً وسهلاً، د. {user?.name?.split(' ')[0] || 'أحمد'} 👋
              <span className="text-2xl lg:text-3xl font-normal text-gray-600 block mt-2">
                Welcome, Dr. {user?.name?.split(' ')[0] || 'Ahmed'}
              </span>
            </motion.h1>
            <motion.p 
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-xl text-gray-700 max-w-2xl font-medium"
            >
              لوحة التحكم الشاملة لمنصة الرعاية الصحية والتأمين
              <span className="text-lg text-gray-500 block mt-1">
                Comprehensive Healthcare & Insurance Platform Dashboard
              </span>
            </motion.p>
          </motion.div>
        </div>

        {/* Key Metrics Grid - Clean & Professional */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8 mb-12">
          {statCards.map((card, index) => (
            <motion.div
              key={card.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="group bg-white rounded-2xl p-6 lg:p-8 shadow-lg border border-gray-200 hover:shadow-xl hover:scale-105 transition-all duration-300"
            >
              {/* Icon - Clean & Simple */}
              <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${card.gradient} flex items-center justify-center mb-6 shadow-md`}>
                <span className="text-2xl text-white">{card.icon}</span>
              </div>

              {/* Value - Clear Typography */}
              <div className="mb-4">
                <p className="text-3xl lg:text-4xl font-bold text-gray-900 mb-2">
                  {card.value}
                </p>
                <p className="text-base lg:text-lg font-semibold text-gray-700 mb-1">
                  {card.title}
                </p>
                <p className="text-sm text-gray-600">
                  {/* Add English translations for stat cards */}
                  {card.title === 'إجمالي المرضى' && 'Total Patients'}
                  {card.title === 'معالج اليوم' && 'Processed Today'}
                  {card.title === 'المطالبات المعلقة' && 'Pending Claims'}
                  {card.title === 'وقت تشغيل النظام' && 'System Uptime'}
                  {card.title === 'توفير التكاليف' && 'Cost Savings'}
                  {card.title === 'رضا المرضى' && 'Patient Satisfaction'}
                  {card.title === 'دقة الذكاء الاصطناعي' && 'AI Accuracy'}
                  {card.title === 'نقاط الامتثال' && 'Compliance Score'}
                </p>
              </div>

              {/* Change Indicator - Clean */}
              <div className={`inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold ${
                card.changeType === 'positive' 
                  ? 'bg-green-100 text-green-700 border border-green-200' 
                  : 'bg-red-100 text-red-700 border border-red-200'
              }`}>
                <span className="mr-1 text-base">
                  {card.changeType === 'positive' ? '↗' : '↘'}
                </span>
                {card.change}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Quick Actions - Clean Professional Design */}
        <div className="bg-white rounded-2xl p-8 lg:p-12 shadow-lg border border-gray-200 mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-2 text-center lg:text-left">
            الإجراءات السريعة
          </h2>
          <p className="text-lg text-gray-600 mb-8 text-center lg:text-left">
            Quick Actions
          </p>
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
                  className="group block p-6 bg-gray-50 rounded-2xl border border-gray-200 hover:border-gray-300 hover:shadow-lg transition-all duration-300 hover:bg-white"
                >
                  {/* Icon */}
                  <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${action.gradient} flex items-center justify-center mb-4 shadow-md`}>
                    <span className="text-2xl text-white">{action.icon}</span>
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {action.name}
                  </h3>
                  <p className="text-sm text-gray-600 mb-1">
                    {/* Add English names for quick actions */}
                    {action.name === 'دعم العملاء الذكي' && 'AI Customer Support'}
                    {action.name === 'معالجة المطالبات' && 'Claims Processing'}
                    {action.name === 'تقييم المخاطر' && 'Risk Assessment'}
                    {action.name === 'خزينة الطب' && 'MediVault'}
                  </p>
                  <p className="text-base text-gray-700 mb-4">
                    {action.description}
                  </p>
                  
                  {/* Stats Badge */}
                  <div className="inline-flex items-center px-3 py-1.5 bg-blue-100 text-blue-700 rounded-lg text-sm font-semibold">
                    {action.stats}
                  </div>
                </NavLink>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Recent Activity - Clean Professional Design */}
        <div className="bg-white rounded-2xl p-8 lg:p-12 shadow-lg border border-gray-200">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="text-3xl font-bold text-gray-900">النشاط الأخير</h2>
              <p className="text-lg text-gray-600 mt-1">Recent Activity</p>
            </div>
            <button className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-semibold">
              عرض الكل
              <span className="text-sm ml-2">View All</span>
            </button>
          </div>

          <div className="space-y-6">
            {recentActivity.map((activity, index) => (
              <motion.div
                key={activity.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.8 + index * 0.1 }}
                className="flex items-start space-x-6 p-6 bg-gray-50 rounded-xl border border-gray-200 hover:shadow-md transition-all duration-300"
              >
                {/* Activity Icon */}
                <div className={`w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0 border ${getActivityIcon(activity.type)}`}>
                  <span className="text-xl">{activity.icon}</span>
                </div>

                {/* Activity Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-lg font-bold text-gray-900 mb-2">
                        {activity.title}
                      </h3>
                      <p className="text-base text-gray-700 leading-relaxed mb-3">
                        {activity.description}
                      </p>
                      <p className="text-sm text-gray-600">
                        {activity.time}
                      </p>
                    </div>
                    
                    {/* Value Badge */}
                    <div className="ml-4 flex-shrink-0">
                      <span className="inline-flex items-center px-4 py-2 bg-white text-gray-700 rounded-xl text-sm font-semibold border border-gray-200">
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
