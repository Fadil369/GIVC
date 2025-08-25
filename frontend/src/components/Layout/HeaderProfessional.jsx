import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../hooks/useAuth.jsx';
import { useTheme } from '../../contexts/ThemeContext.jsx';
import { useLanguage } from '../../contexts/LanguageContext.jsx';
import { NavLink, useLocation } from 'react-router-dom';
import ThemeLanguageToggle from '../Settings/ThemeLanguageToggle.jsx';

const HeaderProfessional = ({ onToggleSidebar, isMobile }) => {
  const { user, logout } = useAuth();
  const { theme } = useTheme();
  const { t, language, isRTL } = useLanguage();
  const location = useLocation();
  const [searchTerm, setSearchTerm] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [notifications] = useState([
    { id: 1, title: 'High Priority Patient Alert', message: 'Patient requires immediate attention', type: 'urgent', unread: true },
    { id: 2, title: 'Claims Processing Complete', message: '15 claims auto-approved successfully', type: 'success', unread: true },
    { id: 3, title: 'System Update', message: 'New AI features available', type: 'info', unread: false }
  ]);
  const [showNotifications, setShowNotifications] = useState(false);
  const userMenuRef = useRef();
  const notificationsRef = useRef();

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target)) {
        setShowUserMenu(false);
      }
      if (notificationsRef.current && !notificationsRef.current.contains(event.target)) {
        setShowNotifications(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const getPageTitle = () => {
    const pathTitles = {
      '/dashboard': t('dashboard'),
      '/support': t('support'),
      '/claims': t('claims'),
      '/risk-assessment': t('riskAssessment'),
      '/medivault': t('medivault'),
      '/triage': t('triage'),
      '/agents': t('agents')
    };
    return pathTitles[location.pathname] || t('platform');
  };

  const unreadCount = notifications.filter(n => n.unread).length;

  return (
    <motion.header
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white/98 dark:bg-slate-900/98 backdrop-blur-xl border-b border-gray-100/50 dark:border-slate-800/50"
      dir={isRTL ? 'rtl' : 'ltr'}
    >
      <div className="px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          {/* Left Section - Menu & Title */}
          <div className="flex items-center space-x-6">
            {/* Mobile Menu Button */}
            <button
              onClick={onToggleSidebar}
              className="lg:hidden p-3 rounded-xl text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-slate-800 transition-all duration-200"
              aria-label="Toggle navigation"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>

            {/* Page Title - Clean Typography */}
            <div className="hidden md:block">
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">
                {getPageTitle()}
              </h1>
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">
                {new Date().toLocaleDateString(language === 'ar' ? 'ar-SA' : 'en-US', { 
                  weekday: 'long', 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </p>
            </div>
          </div>

          {/* Center Section - Search (Desktop Only) */}
          <div className="hidden lg:flex flex-1 max-w-xl mx-8">
            <div className="relative w-full">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder={t('searchPlaceholder')}
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-6 py-4 text-base bg-gray-50/80 dark:bg-slate-800/80 border border-gray-200/50 dark:border-slate-700/50 rounded-2xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 dark:focus:border-blue-500 focus:bg-white dark:focus:bg-slate-800 transition-all duration-200 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white"
              />
            </div>
          </div>

          {/* Right Section - Actions & User */}
          <div className="flex items-center space-x-4">
            {/* System Status - Desktop Only */}
            <div className="hidden xl:flex items-center space-x-3 px-4 py-3 bg-green-50/80 dark:bg-green-900/20 border border-green-200/50 dark:border-green-700/30 rounded-2xl">
              <div className="w-2.5 h-2.5 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-medium text-green-700 dark:text-green-400">{t('systemOperational')}</span>
            </div>

            {/* Theme & Language Toggle */}
            <ThemeLanguageToggle />

            {/* Notifications */}
            <div ref={notificationsRef} className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="relative p-3 rounded-xl text-gray-600 hover:text-gray-900 hover:bg-gray-50 transition-all duration-200"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-3-3.5a7 7 0 01-14 0L1 17h5a7 7 0 0114 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 21a1.5 1.5 0 003 0" />
                </svg>
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center">
                    {unreadCount}
                  </span>
                )}
              </button>

              {/* Notifications Dropdown */}
              <AnimatePresence>
                {showNotifications && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                    className="absolute right-0 top-full mt-3 w-96 bg-white rounded-2xl shadow-2xl border border-gray-100 z-50"
                  >
                    <div className="p-6 border-b border-gray-100">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-bold text-gray-900">Notifications</h3>
                        <span className="text-sm text-gray-500">{unreadCount} unread</span>
                      </div>
                    </div>
                    
                    <div className="max-h-80 overflow-y-auto">
                      {notifications.map((notification) => (
                        <div
                          key={notification.id}
                          className={`p-6 hover:bg-gray-50/50 transition-colors border-b border-gray-50 last:border-b-0 ${
                            notification.unread ? 'bg-blue-50/30' : ''
                          }`}
                        >
                          <div className="flex items-start space-x-4">
                            <div className={`w-3 h-3 rounded-full mt-2 flex-shrink-0 ${
                              notification.type === 'urgent' ? 'bg-red-500' :
                              notification.type === 'success' ? 'bg-green-500' :
                              'bg-blue-500'
                            }`}></div>
                            <div className="flex-1 min-w-0">
                              <h4 className="text-base font-semibold text-gray-900 mb-1">
                                {notification.title}
                              </h4>
                              <p className="text-sm text-gray-600 leading-relaxed">
                                {notification.message}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    <div className="p-4 bg-gray-50/50 rounded-b-2xl">
                      <button className="w-full text-center text-base font-medium text-blue-600 hover:text-blue-700 py-2">
                        View All Notifications
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* User Menu */}
            <div ref={userMenuRef} className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-4 p-2 rounded-2xl hover:bg-gray-50 transition-all duration-200"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 rounded-2xl flex items-center justify-center shadow-lg">
                  <span className="text-white font-bold text-lg">
                    {user?.name?.charAt(0) || 'H'}
                  </span>
                </div>
                <div className="hidden lg:block text-left">
                  <p className="text-base font-semibold text-gray-900">
                    {user?.name || 'Healthcare Professional'}
                  </p>
                  <p className="text-sm text-gray-500">
                    {user?.role || 'Medical Director'}
                  </p>
                </div>
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* User Dropdown */}
              <AnimatePresence>
                {showUserMenu && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                    className="absolute right-0 top-full mt-3 w-72 bg-white rounded-2xl shadow-2xl border border-gray-100 z-50"
                  >
                    <div className="p-6 border-b border-gray-100">
                      <div className="flex items-center space-x-4">
                        <div className="w-14 h-14 bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-700 rounded-2xl flex items-center justify-center shadow-lg">
                          <span className="text-white font-bold text-xl">
                            {user?.name?.charAt(0) || 'H'}
                          </span>
                        </div>
                        <div>
                          <p className="text-lg font-bold text-gray-900">
                            {user?.name || 'Dr. Healthcare Professional'}
                          </p>
                          <p className="text-sm text-gray-600">
                            {user?.email || 'professional@givc.com'}
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="py-3">
                      {[
                        { icon: '👤', label: 'Profile Settings', action: () => {} },
                        { icon: '🔔', label: 'Notifications', action: () => {} },
                        { icon: '🔒', label: 'Security & Privacy', action: () => {} },
                        { icon: '⚙️', label: 'System Preferences', action: () => {} },
                        { icon: '❓', label: 'Help & Documentation', action: () => {} }
                      ].map((item, index) => (
                        <button
                          key={index}
                          onClick={item.action}
                          className="w-full text-left px-6 py-3 text-base text-gray-700 hover:bg-gray-50 hover:text-gray-900 transition-colors flex items-center space-x-4"
                        >
                          <span className="text-lg">{item.icon}</span>
                          <span className="font-medium">{item.label}</span>
                        </button>
                      ))}
                    </div>
                    
                    <div className="border-t border-gray-100 p-3">
                      <button
                        onClick={logout}
                        className="w-full text-left px-6 py-3 text-base text-red-600 hover:bg-red-50 hover:text-red-700 transition-colors flex items-center space-x-4 rounded-xl"
                      >
                        <span className="text-lg">🚪</span>
                        <span className="font-medium">Sign Out</span>
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* Mobile Search - Clean & Spacious */}
        <div className="lg:hidden pb-6">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="Search patients, claims, documents..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-6 py-4 text-base bg-gray-50/80 border border-gray-200/50 rounded-2xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 focus:bg-white transition-all duration-200 placeholder-gray-500"
            />
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default HeaderProfessional;
