import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../hooks/useAuth.jsx';
import { NavLink, useLocation } from 'react-router-dom';

const Header = ({ onToggleSidebar, isMobile }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [searchTerm, setSearchTerm] = useState('');
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [notifications] = useState([
    { id: 1, title: 'تنبيه مريض عالي الأولوية', message: 'المريض يحتاج اهتمام فوري', type: 'urgent', unread: true },
    { id: 2, title: 'اكتمال معالجة المطالبات', message: 'تم الموافقة تلقائياً على 15 مطالبة بنجاح', type: 'success', unread: true },
    { id: 3, title: 'تحديث النظام', message: 'ميزات ذكاء اصطناعي جديدة متاحة', type: 'info', unread: false }
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
      '/dashboard': 'لوحة التحكم',
      '/support': 'الدعم الذكي',
      '/claims': 'مركز المطالبات',
      '/risk-assessment': 'تقييم المخاطر',
      '/medivault': 'خزينة الطب',
      '/triage': 'الفرز الذكي',
      '/agents': 'الوكلاء الطبيون'
    };
    return pathTitles[location.pathname] || 'منصة GIVC';
  };

  const unreadCount = notifications.filter(n => n.unread).length;

  return (
    <motion.header
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white border-b border-gray-100"
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

            {/* Page Title - Arabic with small English */}
            <div className="hidden md:block">
              <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
                {getPageTitle()}
                <span className="text-sm font-normal text-gray-500 ml-2">
                  {location.pathname === '/dashboard' && 'Dashboard'}
                  {location.pathname === '/support' && 'AI Support'}
                  {location.pathname === '/claims' && 'Claims Center'}
                  {location.pathname === '/risk-assessment' && 'Risk Assessment'}
                  {location.pathname === '/medivault' && 'MediVault'}
                  {location.pathname === '/triage' && 'AI Triage'}
                  {location.pathname === '/agents' && 'Medical Agents'}
                </span>
              </h1>
              <p className="text-sm text-gray-500 mt-0.5">
                {new Date().toLocaleDateString('ar-SA', { 
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
                placeholder="البحث في المرضى، المطالبات، الوثائق... | Search patients, claims, documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-12 pr-6 py-4 text-base bg-gray-50 border border-gray-200 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-blue-400 focus:bg-white transition-all duration-200 placeholder-gray-500 text-gray-900"
              />
            </div>
          </div>

          {/* Right Section - Actions & User */}
          <div className="flex items-center space-x-4">
            {/* System Status - Simple */}
            <div className="hidden xl:flex items-center space-x-3 px-4 py-2 bg-green-50 border border-green-200 rounded-2xl">
              <div className="w-2.5 h-2.5 bg-green-500 rounded-full"></div>
              <span className="text-sm font-medium text-green-700">
                النظام يعمل <span className="text-xs text-green-600">System Operational</span>
              </span>
            </div>

            {/* Notifications - Simple */}
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
                    className="absolute right-0 top-full mt-3 w-96 art-notification rounded-3xl shadow-2xl border border-gray-100/50 dark:border-slate-700/50 z-50 overflow-hidden"
                  >
                    {/* Enhanced Header */}
                    <div className="p-6 border-b border-gray-100/50 dark:border-slate-700/50 bg-gradient-to-r from-blue-50/50 to-purple-50/50 dark:from-slate-800/50 dark:to-slate-700/50">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-bold bg-gradient-to-r from-gray-900 to-blue-800 dark:from-white dark:to-blue-200 bg-clip-text text-transparent">الإشعارات</h3>
                        <span className="text-sm text-gray-500 dark:text-gray-400 bg-gray-100/50 dark:bg-slate-700/50 px-3 py-1 rounded-full">{unreadCount} غير مقروء</span>
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
                        عرض جميع الإشعارات
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* User Menu - Enhanced Artistic */}
            <div ref={userMenuRef} className="relative">
              <motion.button
                onClick={() => setShowUserMenu(!showUserMenu)}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="flex items-center space-x-4 p-2 rounded-3xl art-card artistic-hover transition-all duration-300"
              >
                <div className="relative">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-600 via-purple-600 via-indigo-600 to-cyan-600 rounded-3xl flex items-center justify-center shadow-2xl overflow-hidden">
                    {/* Animated background */}
                    <motion.div 
                      animate={{ 
                        background: [
                          'linear-gradient(45deg, #2563EB, #8B5CF6)',
                          'linear-gradient(45deg, #8B5CF6, #4F46E5)', 
                          'linear-gradient(45deg, #4F46E5, #0891B2)',
                          'linear-gradient(45deg, #0891B2, #2563EB)'
                        ]
                      }}
                      transition={{ duration: 4, repeat: Infinity, ease: "easeInOut" }}
                      className="absolute inset-0"
                    />
                    <span className="text-white font-bold text-lg relative z-10 filter drop-shadow-lg">
                      {user?.name?.charAt(0) || 'H'}
                    </span>
                  </div>
                  {/* Online indicator */}
                  <motion.div
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    className="absolute -bottom-1 -right-1 w-4 h-4 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full border-2 border-white dark:border-slate-800 shadow-lg"
                  />
                </div>
                <div className="hidden lg:block text-left">
                  <p className="text-base font-semibold bg-gradient-to-r from-gray-900 to-blue-800 dark:from-white dark:to-blue-200 bg-clip-text text-transparent">
                    {user?.name || 'مختص الرعاية الصحية'}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    {user?.role || 'مدير طبي'}
                  </p>
                </div>
                <motion.svg 
                  animate={{ rotate: showUserMenu ? 180 : 0 }}
                  transition={{ duration: 0.3 }}
                  className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </motion.svg>
              </motion.button>

              {/* User Dropdown */}
              <AnimatePresence>
                {showUserMenu && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                    className="absolute right-0 top-full mt-3 w-72 art-notification rounded-3xl shadow-2xl border border-gray-100/50 dark:border-slate-700/50 z-50 overflow-hidden"
                  >
                    {/* Enhanced User Header */}
                    <div className="p-6 border-b border-gray-100/50 dark:border-slate-700/50 bg-gradient-to-r from-blue-50/50 to-purple-50/50 dark:from-slate-800/50 dark:to-slate-700/50">
                      <div className="flex items-center space-x-4">
                        <div className="relative">
                          <div className="w-16 h-16 bg-gradient-to-br from-blue-600 via-purple-600 via-indigo-600 to-cyan-600 rounded-3xl flex items-center justify-center shadow-2xl overflow-hidden">
                            <motion.div 
                              animate={{ 
                                background: [
                                  'linear-gradient(45deg, #2563EB, #8B5CF6)',
                                  'linear-gradient(45deg, #8B5CF6, #4F46E5)', 
                                  'linear-gradient(45deg, #4F46E5, #0891B2)',
                                  'linear-gradient(45deg, #0891B2, #2563EB)'
                                ]
                              }}
                              transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
                              className="absolute inset-0"
                            />
                            <span className="text-white font-bold text-2xl relative z-10 filter drop-shadow-lg">
                              {user?.name?.charAt(0) || 'H'}
                            </span>
                          </div>
                        </div>
                        <div>
                          <p className="text-lg font-bold bg-gradient-to-r from-gray-900 to-blue-800 dark:from-white dark:to-blue-200 bg-clip-text text-transparent">
                            {user?.name || 'د. مختص الرعاية الصحية'}
                          </p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            {user?.email || 'professional@givc.com'}
                          </p>
                        </div>
                      </div>
                    </div>
                    
                    <div className="py-3">
                      {[
                        { icon: '👤', label: 'إعدادات الملف الشخصي', action: () => {} },
                        { icon: '🔔', label: 'الإشعارات', action: () => {} },
                        { icon: '🔒', label: 'الأمان والخصوصية', action: () => {} },
                        { icon: '⚙️', label: 'تفضيلات النظام', action: () => {} },
                        { icon: '❓', label: 'المساعدة والوثائق', action: () => {} }
                      ].map((item, index) => (
                        <motion.button
                          key={index}
                          onClick={item.action}
                          initial={{ opacity: 0, x: -10 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.1 }}
                          className="w-full text-left px-6 py-4 text-base text-gray-700 dark:text-gray-300 hover:bg-gradient-to-r hover:from-blue-50 hover:to-purple-50 dark:hover:from-slate-700 dark:hover:to-slate-600 hover:text-gray-900 dark:hover:text-white transition-all duration-300 flex items-center space-x-4 rounded-2xl mx-2 artistic-hover"
                        >
                          <span className="text-xl">{item.icon}</span>
                          <span className="font-medium">{item.label}</span>
                        </motion.button>
                      ))}
                    </div>
                    
                    <div className="border-t border-gray-100/50 dark:border-slate-700/50 p-3">
                      <motion.button
                        onClick={logout}
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="w-full text-left px-6 py-4 text-base bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white transition-all duration-300 flex items-center space-x-4 rounded-2xl mx-2 shadow-lg artistic-hover"
                      >
                        <span className="text-xl">🚪</span>
                        <span className="font-semibold">تسجيل الخروج</span>
                      </motion.button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* Mobile Search - Enhanced Artistic */}
        <div className="lg:hidden pb-6 relative z-10">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
            <input
              type="text"
              placeholder="البحث في المرضى، المطالبات، الوثائق..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-6 py-4 text-base art-card border-0 rounded-3xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400 transition-all duration-300 placeholder-gray-500 dark:placeholder-gray-400 shimmer-effect"
            />
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;
