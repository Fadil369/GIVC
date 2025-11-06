import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { NavLink, useLocation } from 'react-router-dom';
import { useAuth } from '../../hooks/useAuth.jsx';

const SidebarProfessional = ({ isOpen, onToggle, isMobile }) => {
  const { user } = useAuth();
  const location = useLocation();
  const [activeSubmenu, setActiveSubmenu] = useState(null);

  // Clean, professional navigation structure
  const navigationItems = [
    {
      id: 'dashboard',
      name: 'Dashboard',
      path: '/dashboard',
      icon: '📊',
      description: 'Overview & Analytics',
      color: 'from-blue-500 to-blue-600'
    },
    {
      id: 'support',
      name: 'AI Support',
      path: '/support',
      icon: '🤖',
      description: '24/7 Customer Care',
      color: 'from-green-500 to-green-600',
      badge: 'AI'
    },
    {
      id: 'claims',
      name: 'Claims Center',
      path: '/claims',
      icon: '📋',
      description: 'Process & Review',
      color: 'from-purple-500 to-purple-600',
      badge: '42'
    },
    {
      id: 'risk',
      name: 'Risk Engine',
      path: '/risk-assessment',
      icon: '⚖️',
      description: 'Predictive Analysis',
      color: 'from-red-500 to-red-600',
      badge: 'NEW'
    },
    {
      id: 'vault',
      name: 'MediVault',
      path: '/medivault',
      icon: '🗂️',
      description: 'Secure Documents',
      color: 'from-indigo-500 to-indigo-600'
    },
    {
      id: 'triage',
      name: 'AI Triage',
      path: '/triage',
      icon: '🩺',
      description: 'Emergency Assessment',
      color: 'from-pink-500 to-pink-600',
      badge: 'BETA'
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

      {/* Sidebar Container */}
      <motion.aside
        initial={false}
        animate={{
          x: isMobile ? (isOpen ? 0 : '-100%') : 0,
          width: isMobile ? '320px' : '280px'
        }}
        transition={{ 
          type: 'spring', 
          damping: 25, 
          stiffness: 200,
          duration: 0.3
        }}
        className={`
          fixed top-0 left-0 h-full bg-white/95 backdrop-blur-xl border-r border-gray-200/50 shadow-2xl z-50
          ${isMobile ? 'lg:relative lg:translate-x-0' : 'relative'}
          flex flex-col
        `}
      >
        {/* Header Section - Clean & Professional */}
        <div className="px-6 py-8 border-b border-gray-100/80">
          <div className="flex items-center space-x-4">
            {/* Logo */}
            <div className="w-12 h-12 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 rounded-2xl flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-xl">G</span>
            </div>
            
            {/* Brand & User Info */}
            <div className="flex-1 min-w-0">
              <h1 className="text-xl font-bold text-gray-900 tracking-tight">
                GIVC Platform
              </h1>
              <p className="text-sm text-gray-600 mt-0.5 truncate">
                {user?.name || 'Healthcare Professional'}
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
                    group relative flex items-center px-4 py-4 rounded-2xl transition-all duration-300
                    ${isActive 
                      ? 'bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200/50 shadow-md' 
                      : 'hover:bg-gray-50/80 hover:shadow-sm'
                    }
                  `}
                >
                  {/* Active Indicator */}
                  {isActive && (
                    <motion.div
                      layoutId="activeTab"
                      className="absolute left-0 top-1/2 transform -translate-y-1/2 w-1 h-8 bg-gradient-to-b from-blue-500 to-purple-600 rounded-r-full"
                      transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                    />
                  )}

                  {/* Icon Container */}
                  <div className={`
                    w-12 h-12 rounded-xl flex items-center justify-center text-xl transition-all duration-300
                    ${isActive 
                      ? `bg-gradient-to-br ${item.color} text-white shadow-lg scale-110` 
                      : 'bg-gray-100 text-gray-600 group-hover:bg-gray-200'
                    }
                  `}>
                    {item.icon}
                  </div>

                  {/* Content */}
                  <div className="ml-4 flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h3 className={`
                        text-lg font-semibold tracking-tight truncate
                        ${isActive ? 'text-gray-900' : 'text-gray-700 group-hover:text-gray-900'}
                      `}>
                        {item.name}
                      </h3>
                      
                      {/* Badge */}
                      {item.badge && (
                        <span className={`
                          ml-2 px-2.5 py-1 text-xs font-bold rounded-full flex-shrink-0
                          ${item.badge === 'AI' ? 'bg-green-100 text-green-700' :
                            item.badge === 'NEW' ? 'bg-red-100 text-red-700' :
                            item.badge === 'BETA' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-blue-100 text-blue-700'
                          }
                        `}>
                          {item.badge}
                        </span>
                      )}
                    </div>
                    
                    <p className={`
                      text-sm mt-1 truncate
                      ${isActive ? 'text-gray-600' : 'text-gray-500 group-hover:text-gray-600'}
                    `}>
                      {item.description}
                    </p>
                  </div>

                  {/* Hover Arrow */}
                  <div className={`
                    ml-2 opacity-0 transform translate-x-2 transition-all duration-300
                    ${isActive ? 'opacity-100 translate-x-0' : 'group-hover:opacity-100 group-hover:translate-x-0'}
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
        <div className="px-6 py-6 border-t border-gray-100/80">
          {/* System Status */}
          <div className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-2xl border border-green-200/50">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse shadow-sm"></div>
              <div>
                <p className="text-sm font-semibold text-gray-900">All Systems Active</p>
                <p className="text-xs text-gray-600">99.9% Uptime</p>
              </div>
            </div>
            <div className="text-green-600">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>

          {/* Help & Support */}
          <button className="w-full mt-4 flex items-center justify-center space-x-2 py-3 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-xl transition-all duration-200">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192L5.636 18.364M12 2.25a9.75 9.75 0 100 19.5 9.75 9.75 0 000-19.5z" />
            </svg>
            <span className="font-medium">Help & Support</span>
          </button>
        </div>
      </motion.aside>
    </>
  );
};

export default SidebarProfessional;
