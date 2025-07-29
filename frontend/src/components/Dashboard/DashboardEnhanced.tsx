import { NoDataFound } from '@/components/UI/EmptyState';
import { SkeletonCard } from '@/components/UI/LoadingSkeleton';
import { useToast } from '@/components/UI/Toast';
import { GIVC_BRANDING } from '@/config/branding';
import { useAuth } from '@/hooks/useAuth';
import {
    ArrowDownIcon,
    ArrowPathIcon,
    ArrowUpIcon,
    BellIcon,
    CpuChipIcon,
    DocumentTextIcon,
    ExclamationTriangleIcon,
    EyeIcon,
    ShieldCheckIcon,
    UserGroupIcon,
} from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';
import React, { useEffect, useState } from 'react';

interface DashboardStats {
  totalFiles: number;
  filesProcessedToday: number;
  aiProcessingQueue: number;
  complianceScore: number;
  activeUsers: number;
  systemUptime: number;
  averageProcessingTime: number;
  criticalAlerts: number;
  trends: {
    files: number;
    processing: number;
    users: number;
  };
}

interface RecentActivity {
  id: number;
  type: 'file_upload' | 'ai_analysis' | 'compliance' | 'triage';
  description: string;
  time: string;
  status: 'processing' | 'completed' | 'failed';
  icon: React.ComponentType<any>;
}

interface Alert {
  id: number;
  type: 'critical' | 'warning' | 'info';
  title: string;
  description: string;
  time: string;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const toast = useToast();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadDashboardData = async (showToast = false) => {
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockStats: DashboardStats = {
        totalFiles: 1247,
        filesProcessedToday: 23,
        aiProcessingQueue: 5,
        complianceScore: 98.5,
        activeUsers: 42,
        systemUptime: 99.9,
        averageProcessingTime: 2.3,
        criticalAlerts: 1,
        trends: {
          files: 12.5,
          processing: -3.2,
          users: 8.1,
        },
      };

      const mockActivity: RecentActivity[] = [
        {
          id: 1,
          type: 'file_upload',
          description: 'DICOM image uploaded for analysis',
          time: '2 minutes ago',
          status: 'processing',
          icon: DocumentTextIcon,
        },
        {
          id: 2,
          type: 'ai_analysis',
          description: 'Lab results analysis completed',
          time: '5 minutes ago',
          status: 'completed',
          icon: CpuChipIcon,
        },
        {
          id: 3,
          type: 'compliance',
          description: 'HIPAA audit log generated',
          time: '15 minutes ago',
          status: 'completed',
          icon: ShieldCheckIcon,
        },
        {
          id: 4,
          type: 'triage',
          description: 'Patient triage assessment completed',
          time: '23 minutes ago',
          status: 'completed',
          icon: UserGroupIcon,
        },
      ];

      const mockAlerts: Alert[] = [
        {
          id: 1,
          type: 'critical',
          title: 'High Priority Patient Alert',
          description: 'Patient requires immediate attention based on AI triage assessment',
          time: '5 minutes ago',
        },
        {
          id: 2,
          type: 'warning',
          title: 'Processing Queue Backup',
          description: 'AI processing queue has 5 pending items',
          time: '10 minutes ago',
        },
        {
          id: 3,
          type: 'info',
          title: 'System Maintenance Scheduled',
          description: 'Scheduled maintenance window tonight 2:00 AM - 4:00 AM EST',
          time: '1 hour ago',
        },
      ];

      setStats(mockStats);
      setRecentActivity(mockActivity);
      setAlerts(mockAlerts);
      
      if (showToast) {
        toast.success('Dashboard data refreshed successfully');
      }
    } catch (error) {
      toast.error('Failed to load dashboard data');
      console.error('Dashboard data loading error:', error);
    }
  };

  useEffect(() => {
    const initializeData = async () => {
      setIsLoading(true);
      await loadDashboardData();
      setIsLoading(false);
    };

    initializeData();
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadDashboardData(true);
    setIsRefreshing(false);
  };

  const getTrendIcon = (trend: number) => {
    if (trend > 0) {
      return <ArrowUpIcon className="h-4 w-4 text-green-600" />;
    } else if (trend < 0) {
      return <ArrowDownIcon className="h-4 w-4 text-red-600" />;
    }
    return null;
  };

  const getTrendColor = (trend: number) => {
    if (trend > 0) return 'text-green-600';
    if (trend < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'processing':
        return 'text-blue-600 bg-blue-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'critical':
        return 'border-red-200 bg-red-50';
      case 'warning':
        return 'border-yellow-200 bg-yellow-50';
      case 'info':
        return 'border-blue-200 bg-blue-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case 'critical':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-600" />;
      case 'info':
        return <BellIcon className="h-5 w-5 text-blue-600" />;
      default:
        return <BellIcon className="h-5 w-5 text-gray-600" />;
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6 animate-fade-in">
        {/* Header Skeleton */}
        <SkeletonCard />

        {/* Stats Grid Skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, index) => (
            <SkeletonCard key={index} />
          ))}
        </div>

        {/* Charts and Activity Skeleton */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      className="space-y-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Welcome Header */}
      <motion.div
        className="card-interactive"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back, {user?.name?.split(' ')[0] || 'Doctor'}! 👋
            </h1>
            <p className="text-gray-600 mt-1">
              Here's what's happening with your GIVC healthcare platform today.
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="btn-ghost"
              title="Refresh dashboard"
            >
              <ArrowPathIcon className={`h-5 w-5 ${isRefreshing ? 'animate-spin' : ''}`} />
              {isRefreshing ? 'Refreshing...' : 'Refresh'}
            </button>
            <div className="text-right">
              <div className="text-sm text-gray-500">
                {new Date().toLocaleDateString('en-US', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </div>
              <div className="text-sm font-medium text-primary-600">
                {GIVC_BRANDING.company.accreditation}
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Key Metrics */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        {stats && [
          {
            title: 'Total Files',
            value: stats.totalFiles.toLocaleString(),
            subtitle: `+${stats.filesProcessedToday} processed today`,
            icon: DocumentTextIcon,
            color: 'text-primary-600',
            bgColor: 'bg-primary-100',
            trend: stats.trends.files,
          },
          {
            title: 'AI Processing',
            value: stats.aiProcessingQueue.toString(),
            subtitle: `${stats.averageProcessingTime}s avg time`,
            icon: CpuChipIcon,
            color: 'text-secondary-600',
            bgColor: 'bg-secondary-100',
            trend: stats.trends.processing,
          },
          {
            title: 'Active Users',
            value: stats.activeUsers.toString(),
            subtitle: 'Currently online',
            icon: UserGroupIcon,
            color: 'text-green-600',
            bgColor: 'bg-green-100',
            trend: stats.trends.users,
          },
          {
            title: 'System Uptime',
            value: `${stats.systemUptime}%`,
            subtitle: `${stats.criticalAlerts} critical alerts`,
            icon: ShieldCheckIcon,
            color: 'text-blue-600',
            bgColor: 'bg-blue-100',
          },
        ].map((metric, index) => (
          <motion.div
            key={metric.title}
            className="card-interactive"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + index * 0.1 }}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-gray-500">{metric.title}</p>
                  {metric.trend !== undefined && (
                    <div className={`flex items-center space-x-1 ${getTrendColor(metric.trend)}`}>
                      {getTrendIcon(metric.trend)}
                      <span className="text-sm font-medium">
                        {Math.abs(metric.trend)}%
                      </span>
                    </div>
                  )}
                </div>
                <p className="text-2xl font-bold text-gray-900 mt-2">{metric.value}</p>
                <p className="text-sm text-gray-600 mt-1">{metric.subtitle}</p>
              </div>
              <div className={`p-3 rounded-lg ${metric.bgColor} ml-4`}>
                <metric.icon className={`h-6 w-6 ${metric.color}`} />
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Activity and Alerts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <motion.div
          className="card"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
            <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View All
            </button>
          </div>
          
          {recentActivity.length === 0 ? (
            <NoDataFound 
              title="No recent activity"
              description="Activity will appear here as you use the system."
            />
          ) : (
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <motion.div
                  key={activity.id}
                  className="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition-colors"
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + index * 0.1 }}
                >
                  <div className={`p-2 rounded-lg ${getStatusColor(activity.status)}`}>
                    <activity.icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">
                      {activity.description}
                    </p>
                    <p className="text-sm text-gray-500">{activity.time}</p>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(activity.status)}`}>
                    {activity.status}
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>

        {/* System Alerts */}
        <motion.div
          className="card"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">System Alerts</h2>
            <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              Manage Alerts
            </button>
          </div>
          
          {alerts.length === 0 ? (
            <NoDataFound 
              title="No active alerts"
              description="System alerts will appear here when attention is needed."
            />
          ) : (
            <div className="space-y-4">
              {alerts.map((alert, index) => (
                <motion.div
                  key={alert.id}
                  className={`border rounded-lg p-4 ${getAlertColor(alert.type)}`}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 + index * 0.1 }}
                >
                  <div className="flex items-start space-x-3">
                    {getAlertIcon(alert.type)}
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium text-gray-900">
                        {alert.title}
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">
                        {alert.description}
                      </p>
                      <p className="text-xs text-gray-500 mt-2">{alert.time}</p>
                    </div>
                    <button 
                      className="text-gray-400 hover:text-gray-600"
                      title="View alert details"
                      aria-label="View alert details"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>

      {/* Quick Actions */}
      <motion.div
        className="card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7 }}
      >
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: 'Upload File', href: '/medivault', icon: DocumentTextIcon, color: 'bg-blue-100 text-blue-600' },
            { label: 'Run Triage', href: '/triage', icon: UserGroupIcon, color: 'bg-green-100 text-green-600' },
            { label: 'View Agents', href: '/agents', icon: CpuChipIcon, color: 'bg-purple-100 text-purple-600' },
            { label: 'Check Compliance', href: '/compliance', icon: ShieldCheckIcon, color: 'bg-orange-100 text-orange-600' },
          ].map((action, index) => (
            <motion.button
              key={action.label}
              className="flex flex-col items-center p-4 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-md transition-all"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.8 + index * 0.1 }}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className={`p-3 rounded-lg ${action.color} mb-3`}>
                <action.icon className="h-6 w-6" />
              </div>
              <span className="text-sm font-medium text-gray-900">{action.label}</span>
            </motion.button>
          ))}
        </div>
      </motion.div>
    </motion.div>
  );
};

export default Dashboard;
