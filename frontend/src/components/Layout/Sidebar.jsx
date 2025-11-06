import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth.jsx';

const Sidebar = ({ isOpen, onToggle, isMobile }) => {
  const { user } = useAuth();
  const location = useLocation();
  const [activeSubmenu, setActiveSubmenu] = useState(null);

  // Clean, professional navigation structure
  const navigationItems = [
    {
      id: 'dashboard',
      name: 'لوحة التحكم',
      englishName: 'Dashboard',
      path: '/dashboard',
      icon: '📊',
      description: 'النظرة العامة والتحليلات',
      englishDescription: 'Overview & Analytics'
    },
    {
      id: 'support',
      name: 'الدعم الذكي',
      englishName: 'AI Support',
      path: '/support',
      icon: '🤖',
      description: 'خدمة العملاء على مدار الساعة',
      englishDescription: '24/7 Customer Care',
      badge: 'AI'
    },
    {
      id: 'claims',
      name: 'مركز المطالبات',
      englishName: 'Claims Center',
      path: '/claims',
      icon: '📋',
      description: 'المعالجة والمراجعة',
      englishDescription: 'Process & Review',
      badge: '42'
    },
    {
      id: 'risk',
      name: 'محرك المخاطر',
      englishName: 'Risk Engine',
      path: '/risk-assessment',
      icon: '⚖️',
      description: 'التحليل التنبؤي',
      englishDescription: 'Predictive Analysis',
      badge: 'جديد'
    },
    {
      id: 'follow-ups',
      name: 'متابعة المطالبات',
      englishName: 'Follow-Ups',
      path: '/follow-ups',
      icon: '🧾',
      description: 'إدارة حالات المتابعة',
      englishDescription: 'Follow-up Management',
      badge: 'Live'
    },
    {
      id: 'vault',
      name: 'خزينة الطب',
      englishName: 'MediVault',
      path: '/medivault',
      icon: '🗂️',
      description: 'الوثائق الآمنة',
      englishDescription: 'Secure Documents'
    },
    {
      id: 'triage',
      name: 'فرز ذكي',
      englishName: 'AI Triage',
      path: '/triage',
      icon: '🩺',
      description: 'تقييم الطوارئ',
      englishDescription: 'Emergency Assessment',
      badge: 'تجريبي'
    }
  ];

  // Close sidebar when clicking on mobile nav item
  const handleNavClick = () => {
    if (isMobile) {
      onToggle();
    }
  };

  // Determine if current path matches nav item
  const isActiveRoute = (path) => {
    return location.pathname === path;
  };

  return (
    <>
      {/* Mobile Overlay */}
      <AnimatePresence>
        {isMobile && isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onToggle}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 lg:hidden"
          />
        )}
      </AnimatePresence>

      {/* Sidebar Container - Clean White */}
      <motion.aside
        initial={false}
        animate={{
          x: isMobile ? (isOpen ? 0 : '-100%') : 0,
          width: isMobile ? '320px' : '320px'
        }}
        transition={{ 
          type: 'spring', 
          damping: 25, 
          stiffness: 200,
          duration: 0.3
        }}
        className={`
          fixed top-0 left-0 h-full bg-white border-r border-gray-200 shadow-lg z-50
          ${isMobile ? 'lg:relative lg:translate-x-0' : 'relative'}
          flex flex-col
        `}
      >
        {/* Header Section - Clean & Simple */}
        <div className="px-6 py-8 border-b border-gray-100">
          <div className="flex items-center space-x-4">
            {/* Simple Logo */}
            <div className="w-12 h-12 bg-blue-600 rounded-2xl flex items-center justify-center shadow-md">
              <span className="text-white font-bold text-xl">G</span>
            </div>
            
            {/* Brand & User Info - Clean */}
            <div className="flex-1 min-w-0">
              <h1 className="text-xl font-bold text-gray-900 tracking-tight">
                منصة GIVC
                <span className="text-sm font-normal text-gray-500 ml-2">Platform</span>
              </h1>
              <p className="text-sm text-gray-600 mt-0.5 truncate">
                {user?.name || 'مختص رعاية صحية'}
                <span className="text-xs text-gray-500 ml-1">Healthcare Professional</span>
              </p>
            </div>
          </div>
        </div>

        {/* Navigation - Clean & Spacious */}
        <nav className="flex-1 px-4 py-6 overflow-y-auto">
          <div className="space-y-3">
            {navigationItems.map((item) => {
              const isActive = isActiveRoute(item.path);
              
              return (
                <NavLink
                  key={item.id}
                  to={item.path}
                  onClick={handleNavClick}
                  className={`
                    group relative flex items-center px-4 py-4 rounded-lg transition-all duration-200
                    ${isActive 
                      ? 'bg-blue-50 border border-blue-200 shadow-sm' 
                      : 'hover:bg-gray-50'
                    }
                  `}
                >
                  {/* Active Indicator */}
                  {isActive && (
                    <div className="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-8 bg-blue-600 rounded-r-full" />
                  )}

                  {/* Icon Container */}
                  <div className={`
                    w-10 h-10 rounded-lg flex items-center justify-center text-lg transition-all duration-200
                    ${isActive 
                      ? 'bg-blue-600 text-white shadow-sm' 
                      : 'bg-gray-100 text-gray-600 group-hover:bg-gray-200'
                    }
                  `}>
                    {item.icon}
                  </div>

                  {/* Content - Complete Text Display */}
                  <div className="ml-4 flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <h3 className={`
                          text-lg font-semibold text-gray-900
                          ${isActive ? 'text-blue-900' : 'group-hover:text-gray-900'}
                        `}>
                          {item.name}
                          <span className="text-sm font-normal text-gray-500 ml-2">
                            {item.englishName}
                          </span>
                        </h3>
                      </div>
                      
                      {/* Badge */}
                      {item.badge && (
                        <span className={`
                          ml-2 px-2 py-1 text-xs font-medium rounded-full flex-shrink-0
                          ${item.badge === 'AI' || item.badge === '42' ? 'bg-green-100 text-green-700' :
                            item.badge === 'جديد' || item.badge === 'NEW' ? 'bg-red-100 text-red-700' :
                            item.badge === 'تجريبي' || item.badge === 'BETA' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-blue-100 text-blue-700'
                          }
                        `}>
                          {item.badge}
                        </span>
                      )}
                    </div>
                    
                    <p className={`
                      text-sm mt-1 text-gray-600
                      ${isActive ? 'text-gray-700' : 'group-hover:text-gray-600'}
                    `}>
                      {item.description}
                      <span className="text-xs text-gray-500 ml-1">
                        • {item.englishDescription}
                      </span>
                    </p>
                  </div>

                  {/* Simple Arrow */}
                  <div className={`
                    ml-2 transition-opacity duration-200
                    ${isActive ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}
                  `}>
                    <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </NavLink>
              );
            })}
          </div>
        </nav>

        {/* Footer Section - System Status */}
        <div className="px-6 py-6 border-t border-gray-100">
          {/* System Status */}
          <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg border border-green-200">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <div>
                <p className="text-sm font-semibold text-gray-900">
                  جميع الأنظمة نشطة
                  <span className="text-xs text-gray-600 ml-1">All Systems Active</span>
                </p>
                <p className="text-xs text-gray-600">
                  99.9% وقت التشغيل
                  <span className="text-gray-500 ml-1">• Uptime</span>
                </p>
              </div>
            </div>
            <div className="text-green-600">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>

          {/* Help & Support */}
          <button className="w-full mt-4 flex items-center justify-center space-x-2 py-3 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="font-medium">
              المساعدة والدعم
              <span className="text-sm text-gray-500 ml-1">Help & Support</span>
            </span>
          </button>
        </div>
      </motion.aside>
    </>
  );
};

export default Sidebar;
