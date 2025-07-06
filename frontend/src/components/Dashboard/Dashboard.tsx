import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import { GIVC_BRANDING } from '@/config/branding';
import {
  DocumentTextIcon,
  UserGroupIcon,
  CpuChipIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

const Dashboard: React.FC = () => {
  const { user } = useAuth();

  // Mock dashboard data
  const metrics = {
    totalFiles: 1247,
    filesProcessedToday: 23,
    aiProcessingQueue: 5,
    complianceScore: 98.5,
    activeUsers: 42,
    systemUptime: 99.9,
    averageProcessingTime: 2.3,
    criticalAlerts: 1,
  };

  const recentActivity = [
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

  const alerts = [
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

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Welcome back, {user?.name?.split(' ')[0] || 'Doctor'}! 👋
            </h1>
            <p className="text-gray-600 mt-1">
              Here's what's happening with your GIVC healthcare platform today.
            </p>
          </div>
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

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <DocumentTextIcon className="h-8 w-8 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Total Files</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.totalFiles.toLocaleString()}</p>
            </div>
          </div>
          <div className="mt-4 text-sm text-green-600">
            +{metrics.filesProcessedToday} processed today
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CpuChipIcon className="h-8 w-8 text-secondary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">AI Processing</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.aiProcessingQueue}</p>
            </div>
          </div>
          <div className="mt-4 text-sm text-blue-600">
            {metrics.averageProcessingTime}s avg time
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ShieldCheckIcon className="h-8 w-8 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">Compliance Score</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.complianceScore}%</p>
            </div>
          </div>
          <div className="mt-4 text-sm text-green-600">
            HIPAA Compliant
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-8 w-8 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-500">System Uptime</p>
              <p className="text-2xl font-bold text-gray-900">{metrics.systemUptime}%</p>
            </div>
          </div>
          <div className="mt-4 text-sm text-green-600">
            {metrics.activeUsers} active users
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Recent Activity</h3>
            <button className="text-sm text-primary-600 hover:text-primary-700">
              View all
            </button>
          </div>
          
          <div className="space-y-4">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3">
                <div className={`
                  flex-shrink-0 p-2 rounded-lg
                  ${activity.status === 'completed' ? 'bg-green-100' : 'bg-blue-100'}
                `}>
                  <activity.icon className={`
                    h-4 w-4
                    ${activity.status === 'completed' ? 'text-green-600' : 'text-blue-600'}
                  `} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">
                    {activity.description}
                  </p>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-xs text-gray-500">{activity.time}</span>
                    <span className={`
                      inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium
                      ${activity.status === 'completed' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-blue-100 text-blue-800'
                      }
                    `}>
                      {activity.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Alerts & Notifications */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Alerts & Notifications</h3>
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
              {alerts.filter(a => a.type === 'critical').length} Critical
            </span>
          </div>
          
          <div className="space-y-4">
            {alerts.map((alert) => (
              <div key={alert.id} className="flex items-start space-x-3">
                <div className={`
                  flex-shrink-0 p-1 rounded-full
                  ${alert.type === 'critical' ? 'bg-red-100' : 
                    alert.type === 'warning' ? 'bg-yellow-100' : 'bg-blue-100'}
                `}>
                  {alert.type === 'critical' ? (
                    <ExclamationTriangleIcon className="h-4 w-4 text-red-600" />
                  ) : alert.type === 'warning' ? (
                    <ClockIcon className="h-4 w-4 text-yellow-600" />
                  ) : (
                    <CheckCircleIcon className="h-4 w-4 text-blue-600" />
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">
                    {alert.title}
                  </p>
                  <p className="text-sm text-gray-600 mt-1">
                    {alert.description}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {alert.time}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <button className="btn-primary text-left p-4 space-y-2">
            <DocumentTextIcon className="h-6 w-6" />
            <div>
              <div className="font-medium">Upload Medical File</div>
              <div className="text-sm opacity-90">Add files to MediVault</div>
            </div>
          </button>
          
          <button className="btn-secondary text-left p-4 space-y-2">
            <UserGroupIcon className="h-6 w-6" />
            <div>
              <div className="font-medium">Start Triage Assessment</div>
              <div className="text-sm opacity-90">AI-powered patient triage</div>
            </div>
          </button>
          
          <button className="btn-outline text-left p-4 space-y-2">
            <CpuChipIcon className="h-6 w-6" />
            <div>
              <div className="font-medium">Run AI Analysis</div>
              <div className="text-sm opacity-90">Analyze medical data</div>
            </div>
          </button>
          
          <button className="btn-outline text-left p-4 space-y-2">
            <ShieldCheckIcon className="h-6 w-6" />
            <div>
              <div className="font-medium">View Compliance</div>
              <div className="text-sm opacity-90">Check HIPAA status</div>
            </div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;