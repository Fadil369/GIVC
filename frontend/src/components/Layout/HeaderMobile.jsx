import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../../hooks/useAuth.jsx';
import { NavLink, useLocation } from 'react-router-dom';

const HeaderMobile = ({ onToggleSidebar, isMobile }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [searchTerm, setSearchTerm] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showSearch, setShowSearch] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [showNotifications, setShowNotifications] = useState(false);
  const searchRef = useRef();
  const userMenuRef = useRef();
  const notificationsRef = useRef();

  // Mock search results for demonstration
  const mockSearchResults = [
    { id: 1, title: 'Patient: John Smith', type: 'patient', path: '/dashboard', icon: '👤' },
    { id: 2, title: 'Claim: CLM-2025-001', type: 'claim', path: '/claims', icon: '📋' },
    { id: 3, title: 'Risk Assessment Report', type: 'document', path: '/risk-assessment', icon: '📊' },
    { id: 4, title: 'Customer Support Ticket', type: 'support', path: '/support', icon: '🎧' },
    { id: 5, title: 'MediVault Files', type: 'files', path: '/medivault', icon: '🗂️' }
  ];

  // Mock notifications
  useEffect(() => {
    setNotifications([
      { id: 1, title: 'New Claim Submitted', message: 'Claim CLM-2025-005 requires review', time: '5 min ago', type: 'info', unread: true },
      { id: 2, title: 'High Risk Patient Alert', message: 'Patient P-789012 flagged for attention', time: '12 min ago', type: 'urgent', unread: true },
      { id: 3, title: 'AI Analysis Complete', message: '15 documents processed successfully', time: '1 hour ago', type: 'success', unread: false }
    ]);
  }, []);

  // Handle search
  useEffect(() => {
    if (searchTerm.trim()) {
      const filtered = mockSearchResults.filter(item =>
        item.title.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setSearchResults(filtered);
    } else {
      setSearchResults([]);
    }
  }, [searchTerm]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSearch(false);
      }
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
      '/dashboard': 'Dashboard',
      '/support': 'Customer Support',
      '/claims': 'Claims Processing',
      '/risk-assessment': 'Risk Assessment',
      '/medivault': 'MediVault',
      '/triage': 'AI Triage',
      '/agents': 'Medical Agents'
    };
    return pathTitles[location.pathname] || 'GIVC Platform';
  };

  const getNotificationIcon = (type) => {
    const icons = {
      urgent: '🚨',
      warning: '⚠️',
      info: 'ℹ️',
      success: '✅'
    };
    return icons[type] || 'ℹ️';
  };

  const unreadCount = notifications.filter(n => n.unread).length;

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-gray-200/50 shadow-sm"
    >
      <div className="px-4 lg:px-6">
        <div className="flex items-center justify-between h-16 lg:h-20">
          {/* Left Section - Mobile Menu & Logo */}
          <div className="flex items-center space-x-3 lg:space-x-4">
            {/* Mobile Sidebar Toggle */}
            <button
              onClick={onToggleSidebar}
              className="lg:hidden p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
              aria-label="Toggle sidebar"
            >
              <motion.div
                transition={{ duration: 0.2 }}
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </motion.div>
            </button>

            {/* Logo & Title */}
            <div className="flex items-center space-x-3 lg:space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 lg:w-10 lg:h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg lg:rounded-xl flex items-center justify-center shadow-lg">
                  <span className="text-white font-bold text-sm lg:text-lg">G</span>
                </div>
                <div className="hidden sm:block">
                  <h1 className="text-lg lg:text-xl font-bold text-gray-900">GIVC</h1>
                  <p className="text-xs lg:text-sm text-gray-600 -mt-1">Healthcare Platform</p>
                </div>
              </div>
              
              {/* Page Title - Hidden on small mobile */}
              <div className="hidden md:block">
                <div className="w-px h-6 bg-gray-300 mx-4"></div>
                <h2 className="text-lg font-semibold text-gray-900">{getPageTitle()}</h2>
              </div>
            </div>
          </div>

          {/* Center Section - Search (Hidden on small mobile) */}
          <div ref={searchRef} className="hidden md:block flex-1 max-w-md mx-4 lg:mx-8 relative">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Search patients, claims, documents..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onFocus={() => setShowSearch(true)}
                className="w-full pl-10 pr-4 py-2 lg:py-3 border border-gray-300 rounded-lg lg:rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white/80 backdrop-blur-sm text-sm lg:text-base"
              />
            </div>

            {/* Search Results Dropdown */}
            <AnimatePresence>
              {showSearch && (searchResults.length > 0 || searchTerm.trim()) && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-lg border border-gray-200 py-2 max-h-64 overflow-y-auto z-50"
                >
                  {searchResults.length > 0 ? (
                    searchResults.map((result) => (
                      <NavLink
                        key={result.id}
                        to={result.path}
                        onClick={() => {
                          setShowSearch(false);
                          setSearchTerm('');
                        }}
                        className="flex items-center space-x-3 px-4 py-3 hover:bg-gray-50 transition-colors"
                      >
                        <span className="text-lg">{result.icon}</span>
                        <div>
                          <p className="font-medium text-gray-900">{result.title}</p>
                          <p className="text-sm text-gray-600 capitalize">{result.type}</p>
                        </div>
                      </NavLink>
                    ))
                  ) : (
                    <div className="px-4 py-3 text-sm text-gray-600">
                      No results found for "{searchTerm}"
                    </div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Right Section - Actions & User Menu */}
          <div className="flex items-center space-x-2 lg:space-x-4">
            {/* Mobile Search Toggle */}
            <button
              className="md:hidden p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
              onClick={() => setShowSearch(!showSearch)}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>

            {/* System Status */}
            <div className="hidden lg:flex items-center space-x-2 px-3 py-2 bg-green-50 border border-green-200 rounded-full">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs font-medium text-green-700">All Systems Active</span>
            </div>

            {/* Notifications */}
            <div ref={notificationsRef} className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="relative p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors"
              >
                <svg className="w-5 h-5 lg:w-6 lg:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-3-3.5a7 7 0 01-14 0L1 17h5a7 7 0 0114 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 21a1.5 1.5 0 003 0" />
                </svg>
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
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
                    className="absolute right-0 top-full mt-2 w-80 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50"
                  >
                    <div className="px-4 py-2 border-b border-gray-100">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold text-gray-900">Notifications</h3>
                        <span className="text-xs text-gray-600">{unreadCount} unread</span>
                      </div>
                    </div>
                    <div className="max-h-64 overflow-y-auto">
                      {notifications.map((notification) => (
                        <div
                          key={notification.id}
                          className={`px-4 py-3 hover:bg-gray-50 transition-colors ${notification.unread ? 'bg-blue-50/50' : ''}`}
                        >
                          <div className="flex items-start space-x-3">
                            <span className="text-lg flex-shrink-0">{getNotificationIcon(notification.type)}</span>
                            <div className="min-w-0 flex-1">
                              <p className="text-sm font-medium text-gray-900">{notification.title}</p>
                              <p className="text-xs text-gray-600 mt-1">{notification.message}</p>
                              <p className="text-xs text-gray-500 mt-2">{notification.time}</p>
                            </div>
                            {notification.unread && (
                              <div className="w-2 h-2 bg-blue-500 rounded-full flex-shrink-0 mt-2"></div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                    <div className="px-4 py-2 border-t border-gray-100">
                      <button className="text-sm text-blue-600 hover:text-blue-700 font-medium">
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
                className="flex items-center space-x-2 lg:space-x-3 p-2 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="w-8 h-8 lg:w-10 lg:h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-full flex items-center justify-center shadow-md">
                  <span className="text-white font-bold text-sm lg:text-base">
                    {user?.name?.charAt(0) || 'U'}
                  </span>
                </div>
                <div className="hidden lg:block text-left">
                  <p className="text-sm font-medium text-gray-900">{user?.name || 'User'}</p>
                  <p className="text-xs text-gray-600">{user?.role || 'Healthcare Professional'}</p>
                </div>
                <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                    className="absolute right-0 top-full mt-2 w-56 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50"
                  >
                    <div className="px-4 py-3 border-b border-gray-100">
                      <p className="font-medium text-gray-900">{user?.name || 'User'}</p>
                      <p className="text-sm text-gray-600">{user?.email || 'user@givc.com'}</p>
                    </div>
                    
                    <div className="py-2">
                      <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors flex items-center space-x-3">
                        <span>👤</span>
                        <span>Profile Settings</span>
                      </button>
                      <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors flex items-center space-x-3">
                        <span>�</span>
                        <span>Notification Preferences</span>
                      </button>
                      <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors flex items-center space-x-3">
                        <span>🔒</span>
                        <span>Security Settings</span>
                      </button>
                      <button className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors flex items-center space-x-3">
                        <span>❓</span>
                        <span>Help & Support</span>
                      </button>
                    </div>
                    
                    <div className="border-t border-gray-100 py-2">
                      <button
                        onClick={logout}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors flex items-center space-x-3"
                      >
                        <span>🚪</span>
                        <span>Sign Out</span>
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {/* Mobile Search Expansion */}
        <AnimatePresence>
          {showSearch && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden border-t border-gray-200 py-4"
            >
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <input
                  type="text"
                  placeholder="Search patients, claims, documents..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white/80 backdrop-blur-sm"
                />
              </div>
              
              {/* Mobile Search Results */}
              {searchResults.length > 0 && (
                <div className="mt-3 space-y-2">
                  {searchResults.slice(0, 3).map((result) => (
                    <NavLink
                      key={result.id}
                      to={result.path}
                      onClick={() => {
                        setShowSearch(false);
                        setSearchTerm('');
                      }}
                      className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <span className="text-lg">{result.icon}</span>
                      <div>
                        <p className="font-medium text-gray-900">{result.title}</p>
                        <p className="text-sm text-gray-600 capitalize">{result.type}</p>
                      </div>
                    </NavLink>
                  ))}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.header>
  );
};

export default HeaderMobile;
