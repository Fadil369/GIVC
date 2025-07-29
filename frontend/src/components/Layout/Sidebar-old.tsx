import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { GIVC_BRANDING } from '@/config/branding';
import {
  HomeIcon,
  DocumentIcon,
  UserGroupIcon,
  CpuChipIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  Cog6ToothIcon,
} from '@heroicons/react/24/outline';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
  { name: 'MediVault', href: '/medivault', icon: DocumentIcon },
  { name: 'AI Triage', href: '/triage', icon: UserGroupIcon },
  { name: 'Medical Agents', href: '/agents', icon: CpuChipIcon },
  { name: 'Compliance', href: '/compliance', icon: ShieldCheckIcon },
  { name: 'Analytics', href: '/analytics', icon: ChartBarIcon },
  { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
];

const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose }) => {
  const location = useLocation();
  const { user } = useAuth();

  return (
    <>
      {/* Mobile sidebar overlay */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-40 lg:hidden"
          onClick={onClose}
        >
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
        </div>
      )}

      {/* Sidebar */}
      <div className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center h-16 px-6 border-b border-gray-200">
            <div className="flex items-center">
              <div className="text-2xl mr-3">🏥</div>
              <div>
                <h1 className="text-xl font-bold givc-text-gradient">
                  {GIVC_BRANDING.company.name}
                </h1>
                <p className="text-xs text-gray-500">
                  Healthcare Platform
                </p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-4 space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={onClose}
                  className={`
                    group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200
                    ${isActive
                      ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600'
                      : 'text-gray-700 hover:bg-gray-50 hover:text-gray-900'
                    }
                  `}
                >
                  <item.icon
                    className={`
                      mr-3 h-5 w-5 transition-colors duration-200
                      ${isActive ? 'text-primary-600' : 'text-gray-400 group-hover:text-gray-500'}
                    `}
                    aria-hidden="true"
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>

          {/* User info */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-primary-600 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-white">
                    {user?.name?.charAt(0) || 'U'}
                  </span>
                </div>
              </div>
              <div className="ml-3 flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {user?.name || 'User'}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {user?.role || 'Healthcare Professional'}
                </p>
              </div>
            </div>

            {/* Compliance Status */}
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="flex items-center justify-between text-xs">
                <span className="text-gray-500">System Status</span>
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span className="text-green-600 font-medium">Compliant</span>
                </div>
              </div>
              <div className="mt-1 text-xs text-gray-400">
                HIPAA • RCM • ISO 27001
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Sidebar;