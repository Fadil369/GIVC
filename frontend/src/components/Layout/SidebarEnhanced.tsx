import { GIVC_BRANDING } from '@/config/branding';
import { useAuth } from '@/hooks/useAuth';
import {
    ArrowLeftOnRectangleIcon,
    BellIcon,
    ChartBarIcon,
    ChatBubbleLeftRightIcon,
    CogIcon,
    CpuChipIcon,
    DocumentCheckIcon,
    FolderOpenIcon,
    QuestionMarkCircleIcon,
    UserGroupIcon,
    XMarkIcon,
} from '@heroicons/react/24/outline';
import { clsx } from 'clsx';
import { AnimatePresence, motion } from 'framer-motion';
import React, { useEffect, useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

interface NavigationItem {
  name: string;
  href: string;
  icon: React.ComponentType<any>;
  badge?: number;
  description?: string;
  shortcut?: string;
}

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onToggle }) => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [hoveredItem, setHoveredItem] = useState<string | null>(null);

  // Close sidebar on route change (mobile)
  useEffect(() => {
    if (window.innerWidth < 1024) {
      onToggle();
    }
  }, [location.pathname]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.metaKey || event.ctrlKey) {
        switch (event.key) {
          case '1':
            event.preventDefault();
            window.location.href = '/dashboard';
            break;
          case '2':
            event.preventDefault();
            window.location.href = '/medivault';
            break;
          case '3':
            event.preventDefault();
            window.location.href = '/triage';
            break;
          case '4':
            event.preventDefault();
            window.location.href = '/agents';
            break;
          case '5':
            event.preventDefault();
            window.location.href = '/support';
            break;
          case '6':
            event.preventDefault();
            window.location.href = '/claims';
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  const navigation: NavigationItem[] = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: ChartBarIcon,
      description: 'Overview and analytics',
      shortcut: '⌘1',
    },
    {
      name: 'MediVault',
      href: '/medivault',
      icon: FolderOpenIcon,
      description: 'Medical file management',
      shortcut: '⌘2',
    },
    {
      name: 'AI Triage',
      href: '/triage',
      icon: UserGroupIcon,
      description: 'Patient assessment system',
      shortcut: '⌘3',
    },
    {
      name: 'Medical Agents',
      href: '/agents',
      icon: CpuChipIcon,
      description: 'AI-powered analysis tools',
      shortcut: '⌘4',
    },
    {
      name: 'Customer Support',
      href: '/support',
      icon: ChatBubbleLeftRightIcon,
      badge: 3,
      description: 'Patient communication',
      shortcut: '⌘5',
    },
    {
      name: 'Claims Processing',
      href: '/claims',
      icon: DocumentCheckIcon,
      badge: 12,
      description: 'Insurance claims management',
      shortcut: '⌘6',
    },
  ];

  const secondaryNavigation = [
    {
      name: 'Settings',
      href: '/settings',
      icon: CogIcon,
    },
    {
      name: 'Notifications',
      href: '/notifications',
      icon: BellIcon,
      badge: 5,
    },
    {
      name: 'Help & Support',
      href: '/help',
      icon: QuestionMarkCircleIcon,
    },
  ];

  const isActiveRoute = (href: string) => {
    if (href === '/dashboard') {
      return location.pathname === '/' || location.pathname === '/dashboard';
    }
    return location.pathname.startsWith(href);
  };

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="givc-gradient w-8 h-8 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">G</span>
          </div>
          <div className="min-w-0">
            <h1 className="text-lg font-bold givc-text-gradient truncate">
              {GIVC_BRANDING.company.name}
            </h1>
            <p className="text-xs text-gray-500 truncate">
              {GIVC_BRANDING.company.tagline}
            </p>
          </div>
        </div>
        <button
          onClick={onToggle}
          className="lg:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500"
          aria-label="Close sidebar"
        >
          <XMarkIcon className="h-5 w-5" />
        </button>
      </div>

      {/* User Profile */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
            <span className="text-primary-600 font-semibold text-sm">
              {user?.name?.charAt(0) || 'U'}
            </span>
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.name || 'Unknown User'}
            </p>
            <p className="text-xs text-gray-500 truncate">
              {user?.role || 'Healthcare Professional'}
            </p>
          </div>
          <div className="flex items-center">
            <div className="status-indicator status-online"></div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        <div className="space-y-1">
          {navigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                clsx(
                  'group flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-all duration-200 relative',
                  isActive || isActiveRoute(item.href)
                    ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )
              }
              onMouseEnter={() => setHoveredItem(item.name)}
              onMouseLeave={() => setHoveredItem(null)}
            >
              <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
              <span className="flex-1 truncate">{item.name}</span>
              {item.badge && (
                <span className="notification-badge">
                  {item.badge}
                </span>
              )}
              {item.shortcut && (
                <span className="hidden lg:block text-xs text-gray-400 ml-2">
                  {item.shortcut}
                </span>
              )}
              
              {/* Tooltip for collapsed state */}
              <AnimatePresence>
                {hoveredItem === item.name && !isOpen && (
                  <motion.div
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -10 }}
                    className="absolute left-full top-1/2 transform -translate-y-1/2 ml-2 z-50"
                  >
                    <div className="bg-gray-900 text-white text-sm rounded-lg py-2 px-3 shadow-lg">
                      <div className="font-medium">{item.name}</div>
                      {item.description && (
                        <div className="text-xs text-gray-300 mt-1">
                          {item.description}
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </NavLink>
          ))}
        </div>

        {/* Divider */}
        <div className="border-t border-gray-200 my-4"></div>

        {/* Secondary Navigation */}
        <div className="space-y-1">
          {secondaryNavigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                clsx(
                  'group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200',
                  isActive
                    ? 'bg-gray-100 text-gray-900'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )
              }
            >
              <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
              <span className="flex-1 truncate">{item.name}</span>
              {'badge' in item && item.badge && (
                <span className="notification-badge">
                  {item.badge}
                </span>
              )}
            </NavLink>
          ))}
        </div>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={logout}
          className="w-full flex items-center px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50 hover:text-red-700 rounded-lg transition-all duration-200"
        >
          <ArrowLeftOnRectangleIcon className="mr-3 h-5 w-5" />
          <span>Sign Out</span>
        </button>
        
        <div className="mt-4 text-center">
          <p className="text-xs text-gray-500">
            Version 1.0.0
          </p>
          <p className="text-xs text-gray-400 mt-1">
            © 2024 {GIVC_BRANDING.company.name}
          </p>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 lg:hidden"
            onClick={onToggle}
          >
            <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <div className="flex">
        {/* Desktop Sidebar */}
        <div className="hidden lg:flex lg:flex-shrink-0">
          <div className="flex flex-col w-64">
            <div className="flex flex-col h-full bg-white border-r border-gray-200 shadow-sm">
              <SidebarContent />
            </div>
          </div>
        </div>

        {/* Mobile Sidebar */}
        <AnimatePresence>
          {isOpen && (
            <motion.div
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'spring', damping: 25, stiffness: 200 }}
              className="fixed inset-y-0 left-0 z-50 flex w-72 lg:hidden"
            >
              <div className="flex flex-col flex-1 bg-white border-r border-gray-200 shadow-xl">
                <SidebarContent />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  );
};

export default Sidebar;
