import { useToast } from '@/components/UI/Toast';
import { useAuth } from '@/hooks/useAuth';
import {
    ArrowLeftOnRectangleIcon,
    Bars3Icon,
    BellIcon,
    CogIcon,
    GlobeAltIcon,
    MagnifyingGlassIcon,
    MoonIcon,
    QuestionMarkCircleIcon,
    SunIcon,
    UserCircleIcon,
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';
import { AnimatePresence, motion } from 'framer-motion';
import React, { useEffect, useRef, useState } from 'react';

interface HeaderProps {
  onMenuClick: () => void;
}

interface Notification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'success' | 'error';
  time: string;
  read: boolean;
}

interface SearchResult {
  id: string;
  title: string;
  type: 'patient' | 'file' | 'agent' | 'feature';
  url: string;
  description?: string;
}

const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const { user, logout } = useAuth();
  const toast = useToast();
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [isNotificationsOpen, setIsNotificationsOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isDarkMode, setIsDarkMode] = useState(false);
  
  const profileRef = useRef<HTMLDivElement>(null);
  const notificationRef = useRef<HTMLDivElement>(null);
  const searchRef = useRef<HTMLDivElement>(null);

  // Mock notifications
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: '1',
      title: 'New Lab Results',
      message: 'Patient PT-001 lab results are ready for review',
      type: 'info',
      time: '2 min ago',
      read: false,
    },
    {
      id: '2',
      title: 'Critical Alert',
      message: 'High priority patient requires immediate attention',
      type: 'warning',
      time: '5 min ago',
      read: false,
    },
    {
      id: '3',
      title: 'Analysis Complete',
      message: 'DICOM analysis for chest X-ray completed successfully',
      type: 'success',
      time: '10 min ago',
      read: true,
    },
  ]);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setIsProfileOpen(false);
      }
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setIsNotificationsOpen(false);
      }
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsSearchOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Search functionality
  useEffect(() => {
    if (searchQuery.length > 2) {
      // Simulate search API call
      const mockResults: SearchResult[] = [
        {
          id: '1',
          title: 'Patient Dashboard',
          type: 'feature' as const,
          url: '/dashboard',
          description: 'View patient analytics and metrics',
        },
        {
          id: '2',
          title: 'Upload Medical Files',
          type: 'feature' as const,
          url: '/medivault',
          description: 'Upload and manage medical documents',
        },
        {
          id: '3',
          title: 'AI Triage System',
          type: 'feature' as const,
          url: '/triage',
          description: 'Automated patient triage assessment',
        },
        {
          id: '4',
          title: 'DICOM Analysis Agent',
          type: 'agent' as const,
          url: '/agents',
          description: 'Medical imaging analysis with AI',
        },
      ].filter(result => 
        result.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        result.description?.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setSearchResults(mockResults);
    } else {
      setSearchResults([]);
    }
  }, [searchQuery]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
        event.preventDefault();
        setIsSearchOpen(true);
      }
      if (event.key === 'Escape') {
        setIsSearchOpen(false);
        setIsProfileOpen(false);
        setIsNotificationsOpen(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;

  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    toast.success('All notifications marked as read');
  };

  const getNotificationIcon = (type: string) => {
    const baseClasses = 'w-2 h-2 rounded-full';
    switch (type) {
      case 'error':
      case 'warning':
        return <div className={clsx(baseClasses, 'bg-red-400')} />;
      case 'success':
        return <div className={clsx(baseClasses, 'bg-green-400')} />;
      case 'info':
      default:
        return <div className={clsx(baseClasses, 'bg-blue-400')} />;
    }
  };

  const getSearchIcon = (type: string) => {
    switch (type) {
      case 'patient':
        return '👤';
      case 'file':
        return '📄';
      case 'agent':
        return '🤖';
      case 'feature':
        return '⚡';
      default:
        return '📋';
    }
  };

  const handleLogout = () => {
    toast.success('Logged out successfully');
    logout();
  };

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-30">
      <div className="px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Left Section */}
          <div className="flex items-center">
            <button
              onClick={onMenuClick}
              className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors"
              aria-label="Open sidebar"
            >
              <Bars3Icon className="h-6 w-6" />
            </button>

            {/* Search */}
            <div className="ml-4 flex-1 max-w-lg" ref={searchRef}>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  placeholder="Search patients, files, or features... (⌘K)"
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onFocus={() => setIsSearchOpen(true)}
                />
              </div>

              {/* Search Results */}
              <AnimatePresence>
                {isSearchOpen && (searchResults.length > 0 || searchQuery.length > 2) && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className="absolute top-full mt-2 w-full bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50"
                  >
                    {searchResults.length > 0 ? (
                      <>
                        {searchResults.map((result, index) => (
                          <motion.a
                            key={result.id}
                            href={result.url}
                            className="flex items-center px-4 py-3 hover:bg-gray-50 transition-colors"
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.05 }}
                            onClick={() => setIsSearchOpen(false)}
                          >
                            <span className="text-lg mr-3">{getSearchIcon(result.type)}</span>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 truncate">
                                {result.title}
                              </p>
                              {result.description && (
                                <p className="text-xs text-gray-500 truncate">
                                  {result.description}
                                </p>
                              )}
                            </div>
                            <span className="text-xs text-gray-400 capitalize ml-2">
                              {result.type}
                            </span>
                          </motion.a>
                        ))}
                        <div className="border-t border-gray-100 px-4 py-2">
                          <p className="text-xs text-gray-500">
                            Press Enter to search or Escape to close
                          </p>
                        </div>
                      </>
                    ) : (
                      <div className="px-4 py-8 text-center">
                        <MagnifyingGlassIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-gray-500">No results found</p>
                        <p className="text-xs text-gray-400 mt-1">
                          Try different keywords or check spelling
                        </p>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>

          {/* Right Section */}
          <div className="flex items-center space-x-4">
            {/* Theme Toggle */}
            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
              title={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {isDarkMode ? (
                <SunIcon className="h-5 w-5" />
              ) : (
                <MoonIcon className="h-5 w-5" />
              )}
            </button>

            {/* Language Selector */}
            <button
              className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
              title="Language settings"
            >
              <GlobeAltIcon className="h-5 w-5" />
            </button>

            {/* Notifications */}
            <div className="relative" ref={notificationRef}>
              <button
                onClick={() => setIsNotificationsOpen(!isNotificationsOpen)}
                className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
                title="Notifications"
              >
                <BellIcon className="h-6 w-6" />
                {unreadCount > 0 && (
                  <span className="absolute -top-1 -right-1 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
                    {unreadCount}
                  </span>
                )}
              </button>

              <AnimatePresence>
                {isNotificationsOpen && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                    className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50"
                  >
                    <div className="px-4 py-3 border-b border-gray-200">
                      <div className="flex items-center justify-between">
                        <h3 className="text-sm font-semibold text-gray-900">
                          Notifications
                        </h3>
                        {unreadCount > 0 && (
                          <button
                            onClick={markAllAsRead}
                            className="text-xs text-primary-600 hover:text-primary-700 font-medium"
                          >
                            Mark all read
                          </button>
                        )}
                      </div>
                    </div>
                    
                    <div className="max-h-96 overflow-y-auto">
                      {notifications.length > 0 ? (
                        notifications.map((notification, index) => (
                          <motion.div
                            key={notification.id}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className={clsx(
                              'px-4 py-3 hover:bg-gray-50 cursor-pointer transition-colors border-l-4',
                              notification.read 
                                ? 'border-transparent' 
                                : 'border-primary-500 bg-primary-50'
                            )}
                            onClick={() => markAsRead(notification.id)}
                          >
                            <div className="flex items-start space-x-3">
                              {getNotificationIcon(notification.type)}
                              <div className="flex-1 min-w-0">
                                <p className="text-sm font-medium text-gray-900 truncate">
                                  {notification.title}
                                </p>
                                <p className="text-sm text-gray-600 mt-1">
                                  {notification.message}
                                </p>
                                <p className="text-xs text-gray-500 mt-2">
                                  {notification.time}
                                </p>
                              </div>
                            </div>
                          </motion.div>
                        ))
                      ) : (
                        <div className="px-4 py-8 text-center">
                          <BellIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                          <p className="text-sm text-gray-500">No notifications</p>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Profile Dropdown */}
            <div className="relative" ref={profileRef}>
              <button
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="flex items-center space-x-3 p-2 rounded-lg hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                  <span className="text-primary-600 font-semibold text-sm">
                    {user?.name?.charAt(0) || 'U'}
                  </span>
                </div>
                <div className="hidden md:block text-left">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.name || 'Unknown User'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {user?.role || 'User'}
                  </p>
                </div>
              </button>

              <AnimatePresence>
                {isProfileOpen && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                    className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50"
                  >
                    <div className="px-4 py-3 border-b border-gray-200">
                      <p className="text-sm font-medium text-gray-900">
                        {user?.name || 'Unknown User'}
                      </p>
                      <p className="text-xs text-gray-500">
                        {user?.email || 'user@example.com'}
                      </p>
                    </div>
                    
                    <div className="py-2">
                      <a
                        href="/profile"
                        className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                      >
                        <UserCircleIcon className="h-4 w-4 mr-3" />
                        Your Profile
                      </a>
                      <a
                        href="/settings"
                        className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                      >
                        <CogIcon className="h-4 w-4 mr-3" />
                        Settings
                      </a>
                      <a
                        href="/help"
                        className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors"
                      >
                        <QuestionMarkCircleIcon className="h-4 w-4 mr-3" />
                        Help & Support
                      </a>
                    </div>
                    
                    <div className="border-t border-gray-200 py-2">
                      <button
                        onClick={handleLogout}
                        className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                      >
                        <ArrowLeftOnRectangleIcon className="h-4 w-4 mr-3" />
                        Sign Out
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
