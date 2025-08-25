import { motion } from 'framer-motion';
import React, { useEffect, useState } from 'react';
import { useAuth } from '../../hooks/useAuth.jsx';

// 🔧 ENHANCED DEBUG SYSTEM
const DEBUG_LEVELS = {
  DEBUG: 'DEBUG',
  INFO: 'INFO',
  WARN: 'WARN',
  ERROR: 'ERROR',
  CRITICAL: 'CRITICAL'
};

// Debug log structure (JSDoc for IDE support)
/**
 * @typedef {Object} DebugLog
 * @property {Date} timestamp
 * @property {string} level
 * @property {string} message
 * @property {*} [data]
 * @property {string} [stackTrace]
 */

class DebugLogger {
  private logs= [];
  private maxLogs = 1000;

  log(level: DEBUG_LEVELS, message: string, data?: any) {
    const stackTrace = level === DEBUG_LEVELS.ERROR || level === DEBUG_LEVELS.CRITICAL 
      ? new Error().stack 
      : undefined;
    
    const log= {
      timestamp: new Date(),
      level,
      message,
      data,
      ...(stackTrace && { stackTrace })
    };

    this.logs.push(log);
    if (this.logs.length > this.maxLogs) {
      this.logs.shift();
    }

    const style = this.getConsoleStyle(level);
    console.log(`%c[${level}] ${message}`, style, data || '');

    if (level === DEBUG_LEVELS.CRITICAL) {
      this.sendToMonitoring(log);
    }
  }

  private getConsoleStyle(level: DEBUG_LEVELS): string {
    const styles = {
      [DEBUG_LEVELS.DEBUG]: 'color: #6B7280; font-weight: normal;',
      [DEBUG_LEVELS.INFO]: 'color: #3B82F6; font-weight: bold;',
      [DEBUG_LEVELS.WARN]: 'color: #F59E0B; font-weight: bold;',
      [DEBUG_LEVELS.ERROR]: 'color: #EF4444; font-weight: bold; background: #FEE2E2;',
      [DEBUG_LEVELS.CRITICAL]: 'color: #FFFFFF; font-weight: bold; background: #DC2626; padding: 2px 4px;'
    };
    return styles[level];
  }

  private sendToMonitoring(log: DebugLog) {
    if (process.env.NODE_ENV === 'production') {
      console.error('CRITICAL ERROR - Sending to monitoring:', log);
    }
  }

  getLogs(level?: DEBUG_LEVELS): DebugLog[] {
    return level ? this.logs.filter(log => log.level === level) : this.logs;
  }

  clearLogs() {
    this.logs = [];
  }

  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }
}

const debugLogger = new DebugLogger();

// 🔧 TOAST HOOK
const useToast = () => {
  return {
    showToast: (message=> {
      debugLogger.log(DEBUG_LEVELS.INFO, `Toast: ${type.toUpperCase()} - ${message}`);
      
      const toast = document.createElement('div');
      toast.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg text-white font-semibold transform transition-all duration-300 ${
        type === 'success' ? 'bg-green-500' :
        type === 'error' ? 'bg-red-500' :
        type === 'warning' ? 'bg-yellow-500' :
        'bg-blue-500'
      }`;
      toast.textContent = message;
      toast.style.transform = 'translateX(100%)';
      
      document.body.appendChild(toast);
      
      setTimeout(() => {
        toast.style.transform = 'translateX(0)';
      }, 10);
      
      setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
          if (document.body.contains(toast)) {
            document.body.removeChild(toast);
          }
        }, 300);
      }, 3000);
    }
  };
};

// 🎯 INTERFACE DEFINITIONS
interface HealthcareMetric {
  id: string;
  title: string;
  value: string;
  change: string;
  changeType: 'positive' | 'negative' | 'neutral';
  icon: string;
  status: 'normal' | 'warning' | 'critical';
  lastUpdated: Date;
  trend: number[];
}

interface QuickAction {
  id: string;
  title: string;
  icon: string;
  shortcut?: string;
  onClick: () => void;
  disabled?: boolean;
  category: 'primary' | 'secondary';
}

interface SystemAlert {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: Date;
  dismissed: boolean;
  actionable?: boolean;
}

interface ActivityItem {
  id: number;
  type: 'claim' | 'approval' | 'eligibility' | 'lab' | 'alert' | 'system';
  message: string;
  time: string;
  status: 'pending' | 'success' | 'warning' | 'error';
  urgent: boolean;
  priority: 'low' | 'medium' | 'high' | 'critical';
}

const DashboardEnhanced= () => {
  const { user } = useAuth();
  const { showToast } = useToast();
  
  // 🎯 STATE MANAGEMENT
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [metrics, setMetrics] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [activities, setActivities] = useState([]);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [refreshing, setRefreshing] = useState(false);
  const [debugMode, setDebugMode] = useState(process.env.NODE_ENV === 'development');

  // 🔄 DATA INITIALIZATION
  const initializeData = async () => {
    try {
      debugLogger.log(DEBUG_LEVELS.INFO, 'Initializing dashboard data');
      setLoading(true);
      setError(null);
      
      // Simulate realistic API delay
      await new Promise(resolve => setTimeout(resolve, 1200));
      
      // Enhanced healthcare metrics with trends
      const healthcareMetrics= [
        {
          id: 'claims-total',
          title: 'Total Claims',
          value: '2,847',
          change: '+18.5% from last month',
          changeType: 'positive',
          icon: '📊',
          status: 'normal',
          lastUpdated: new Date(),
          trend: [2400, 2500, 2650, 2750, 2847]
        },
        {
          id: 'approval-rate',
          title: 'Approval Rate',
          value: '96.2%',
          change: '+3.1% improvement',
          changeType: 'positive',
          icon: '✅',
          status: 'normal',
          lastUpdated: new Date(),
          trend: [93.1, 94.5, 95.2, 95.8, 96.2]
        },
        {
          id: 'revenue',
          title: 'Monthly Revenue',
          value: 'SAR 4.2M',
          change: '+24.8% growth',
          changeType: 'positive',
          icon: '💰',
          status: 'normal',
          lastUpdated: new Date(),
          trend: [3.2, 3.5, 3.8, 4.0, 4.2]
        },
        {
          id: 'processing-time',
          title: 'Avg Processing',
          value: '1.4 days',
          change: '-0.6 days faster',
          changeType: 'positive',
          icon: '⏱️',
          status: 'normal',
          lastUpdated: new Date(),
          trend: [2.0, 1.8, 1.6, 1.5, 1.4]
        },
        {
          id: 'pending-claims',
          title: 'Pending Claims',
          value: '127',
          change: '-23 from yesterday',
          changeType: 'positive',
          icon: '📋',
          status: 'warning',
          lastUpdated: new Date(),
          trend: [180, 165, 150, 135, 127]
        },
        {
          id: 'compliance-score',
          title: 'Compliance Score',
          value: '98.9%',
          change: '+0.3% improvement',
          changeType: 'positive',
          icon: '🛡️',
          status: 'normal',
          lastUpdated: new Date(),
          trend: [98.2, 98.4, 98.6, 98.7, 98.9]
        }
      ];

      // System alerts
      const systemAlerts= [
        {
          id: 'maint-1',
          type: 'info',
          message: 'Scheduled maintenance tonight 2:00-4:00 AM for NPHIES integration upgrade',
          timestamp: new Date(Date.now() - 1000 * 60 * 15),
          dismissed: false,
          actionable: true
        },
        {
          id: 'success-1',
          type: 'success',
          message: 'Insurance eligibility API performance improved by 40%',
          timestamp: new Date(Date.now() - 1000 * 60 * 60),
          dismissed: false
        }
      ];

      // Recent activities
      const recentActivities= [
        {
          id: 1,
          type: 'claim',
          message: 'High-value claim (SAR 45,000) submitted for Patient ID: PAT-2024-2847',
          time: '2 minutes ago',
          status: 'pending',
          urgent: true,
          priority: 'high'
        },
        {
          id: 2,
          type: 'approval',
          message: 'Insurance pre-authorization approved for cardiac surgery (SAR 125,000)',
          time: '8 minutes ago',
          status: 'success',
          urgent: false,
          priority: 'high'
        },
        {
          id: 3,
          type: 'eligibility',
          message: 'Bulk eligibility check completed for 45 patients',
          time: '15 minutes ago',
          status: 'success',
          urgent: false,
          priority: 'medium'
        },
        {
          id: 4,
          type: 'alert',
          message: 'CRITICAL: Claim rejection rate spike detected in oncology department',
          time: '23 minutes ago',
          status: 'error',
          urgent: true,
          priority: 'critical'
        },
        {
          id: 5,
          type: 'lab',
          message: 'AI analysis completed: 12 lab results processed with 98.5% accuracy',
          time: '35 minutes ago',
          status: 'success',
          urgent: false,
          priority: 'medium'
        }
      ];

      setMetrics(healthcareMetrics);
      setAlerts(systemAlerts);
      setActivities(recentActivities);
      setLastRefresh(new Date());
      
      debugLogger.log(DEBUG_LEVELS.INFO, 'Dashboard data loaded successfully', {
        metrics: healthcareMetrics.length,
        alerts: systemAlerts.length,
        activities: recentActivities.length
      });

      showToast('Dashboard data refreshed successfully', 'success');
      
    } catch (err) {
      const error = err as Error;
      debugLogger.log(DEBUG_LEVELS.ERROR, 'Failed to initialize dashboard', error);
      setError('Failed to load dashboard. Please try refreshing or contact support.');
      showToast('Failed to load dashboard data', 'error');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  // 🔄 REFRESH HANDLER
  const handleRefresh = async () => {
    debugLogger.log(DEBUG_LEVELS.INFO, 'Manual refresh triggered by user');
    setRefreshing(true);
    await initializeData();
  };

  // 🌐 ONLINE/OFFLINE DETECTION
  useEffect(() => {
    const handleOnline = () => {
      debugLogger.log(DEBUG_LEVELS.INFO, 'Connection restored - refreshing data');
      setIsOnline(true);
      showToast('Connection restored', 'success');
      initializeData();
    };

    const handleOffline = () => {
      debugLogger.log(DEBUG_LEVELS.WARN, 'Connection lost - entering offline mode');
      setIsOnline(false);
      showToast('Connection lost - working offline', 'warning');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  // 🚀 INITIALIZE ON MOUNT
  useEffect(() => {
    debugLogger.log(DEBUG_LEVELS.INFO, 'Dashboard component mounted', { user: user?.name });
    initializeData();
  }, []);

  // ⏰ AUTO-REFRESH
  useEffect(() => {
    if (!isOnline) return;

    const interval = setInterval(() => {
      debugLogger.log(DEBUG_LEVELS.DEBUG, 'Auto-refresh triggered');
      initializeData();
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [isOnline]);

  // ⌨️ KEYBOARD SHORTCUTS
  useEffect(() => {
    const handleKeyPress = (event=> {
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'r':
            event.preventDefault();
            handleRefresh();
            break;
          case 'd':
            if (event.shiftKey) {
              event.preventDefault();
              setDebugMode(!debugMode);
              debugLogger.log(DEBUG_LEVELS.INFO, `Debug mode ${debugMode ? 'disabled' : 'enabled'}`);
            }
            break;
          case '1':
            event.preventDefault();
            debugLogger.log(DEBUG_LEVELS.INFO, 'Quick action: Check Eligibility');
            showToast('Navigating to eligibility check...', 'info');
            break;
          case '2':
            event.preventDefault();
            debugLogger.log(DEBUG_LEVELS.INFO, 'Quick action: Submit Claim');
            showToast('Opening claim submission form...', 'info');
            break;
        }
      }
    };

    document.addEventListener('keydown', handleKeyPress);
    return () => document.removeEventListener('keydown', handleKeyPress);
  }, [debugMode]);

  // 🎯 QUICK ACTIONS
  const quickActions= [
    {
      id: 'check-eligibility',
      title: 'Check Eligibility',
      icon: '🔍',
      shortcut: 'Ctrl+1',
      category: 'primary',
      onClick: () => {
        debugLogger.log(DEBUG_LEVELS.INFO, 'Quick action: Check Eligibility triggered');
        showToast('Opening eligibility verification...', 'info');
      }
    },
    {
      id: 'submit-claim',
      title: 'Submit Claim',
      icon: '📄',
      shortcut: 'Ctrl+2',
      category: 'primary',
      onClick: () => {
        debugLogger.log(DEBUG_LEVELS.INFO, 'Quick action: Submit Claim triggered');
        showToast('Opening claim submission...', 'info');
      }
    },
    {
      id: 'lab-results',
      title: 'AI Lab Analysis',
      icon: '🧪',
      category: 'primary',
      onClick: () => {
        debugLogger.log(DEBUG_LEVELS.INFO, 'Quick action: Lab Analysis triggered');
        showToast('Opening AI lab analysis...', 'info');
      }
    },
    {
      id: 'analytics',
      title: 'Analytics Dashboard',
      icon: '📈',
      category: 'secondary',
      onClick: () => {
        debugLogger.log(DEBUG_LEVELS.INFO, 'Quick action: Analytics triggered');
        showToast('Opening analytics dashboard...', 'info');
      }
    },
    {
      id: 'triage',
      title: 'AI Triage',
      icon: '🤖',
      category: 'secondary',
      onClick: () => {
        debugLogger.log(DEBUG_LEVELS.INFO, 'Quick action: AI Triage triggered');
        showToast('Opening AI triage system...', 'info');
      }
    },
    {
      id: 'compliance',
      title: 'Compliance Monitor',
      icon: '🛡️',
      category: 'secondary',
      onClick: () => {
        debugLogger.log(DEBUG_LEVELS.INFO, 'Quick action: Compliance Monitor triggered');
        showToast('Opening compliance dashboard...', 'info');
      }
    }
  ];

  const dismissAlert = (alertId=> {
    setAlerts(prev => prev.map(alert => 
      alert.id === alertId ? { ...alert, dismissed: true } : alert
    ));
    debugLogger.log(DEBUG_LEVELS.INFO, 'Alert dismissed', { alertId });
  };

  // 🎨 LOADING STATE
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <motion.div 
          className="text-center"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
        >
          <div className="loading-spinner w-20 h-20 mx-auto mb-6"></div>
          <div className="text-2xl font-bold text-gray-700 mb-3">
            🏥 Loading GIVC Healthcare Dashboard
          </div>
          <div className="text-lg text-gray-500 mb-2">
            Initializing secure healthcare environment...
          </div>
          <div className="text-sm text-gray-400">
            Connecting to NPHIES • Verifying credentials • Loading patient data
          </div>
        </motion.div>
      </div>
    );
  }

  // ❌ ERROR STATE
  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <motion.div 
          className="text-center p-8 max-w-md"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="text-8xl mb-6">🚨</div>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Dashboard Error</h2>
          <p className="text-gray-600 mb-6 text-lg">{error}</p>
          <div className="flex gap-4 justify-center">
            <button
              onClick={handleRefresh}
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg text-lg font-semibold transition-colors"
              disabled={refreshing}
            >
              {refreshing ? 'Retrying...' : 'Try Again'}
            </button>
            <button
              onClick={() => window.location.reload()}
              className="border-2 border-gray-300 hover:border-gray-400 text-gray-700 px-6 py-3 rounded-lg text-lg font-semibold transition-colors"
            >
              Full Reload
            </button>
          </div>
          {debugMode && (
            <div className="mt-6 p-4 bg-red-50 rounded-lg text-left">
              <div className="text-sm font-mono text-red-800">
                Debug Info: Check console for detailed error logs
              </div>
            </div>
          )}
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-6xl mx-auto px-3 sm:px-4 lg:px-6 py-2 lg:py-4">
        {/* 🎯 HEADER WITH STATUS */}
        <motion.div 
          className="mb-4 lg:mb-6"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="flex flex-col lg:flex-row lg:justify-between lg:items-start mb-3 lg:mb-4 gap-4">
            <div className="flex-1">
              <h1 className="text-2xl lg:text-4xl font-bold text-gray-900 mb-2 lg:mb-3">
                Welcome back, {user?.name || 'Healthcare Professional'} 👋
              </h1>
              <p className="text-lg lg:text-xl text-gray-600">
                GIVC Healthcare Dashboard - Real-time clinical insights & AI-powered tools
              </p>
            </div>
            
            <div className="flex flex-wrap items-center gap-3 lg:gap-4">
              {/* Connection Status */}
              <motion.div 
                className={`flex items-center gap-2 px-3 py-2 rounded-full text-sm font-medium ${
                  isOnline 
                    ? 'bg-green-100 text-green-800 border border-green-200' 
                    : 'bg-red-100 text-red-800 border border-red-200'
                }`}
                animate={{ scale: isOnline ? 1 : [1, 1.05, 1] }}
                transition={{ duration: 0.3 }}
              >
                <div className={`w-2 h-2 lg:w-3 lg:h-3 rounded-full ${
                  isOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                }`} />
                <span className="hidden sm:inline">{isOnline ? '🟢 Online' : '🔴 Offline'}</span>
              </motion.div>
              
              {/* Last Update */}
              <div className="text-xs lg:text-sm text-gray-500 text-center">
                <div className="hidden lg:block">Last updated</div>
                <div className="font-medium">{lastRefresh.toLocaleTimeString()}</div>
              </div>
              
              {/* Refresh Button */}
              <motion.button
                onClick={handleRefresh}
                disabled={refreshing}
                className={`p-2 lg:p-3 rounded-full hover:bg-gray-100 transition-colors ${refreshing ? 'animate-spin' : ''}`}
                title="Refresh Dashboard (Ctrl+R)"
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
              >
                <span className="text-xl lg:text-2xl">{refreshing ? '⏳' : '🔄'}</span>
              </motion.button>

              {/* Debug Toggle */}
              {process.env.NODE_ENV === 'development' && (
                <button
                  onClick={() => setDebugMode(!debugMode)}
                  className={`p-1 lg:p-2 text-xs rounded ${debugMode ? 'bg-yellow-100' : 'bg-gray-100'} hover:bg-gray-200 transition-colors`}
                  title="Toggle Debug Mode (Ctrl+Shift+D)"
                >
                  🔧 <span className="hidden lg:inline">{debugMode ? 'ON' : 'OFF'}</span>
                </button>
              )}
            </div>
          </div>

          {/* 🚨 SYSTEM ALERTS */}
          {alerts.filter(alert => !alert.dismissed).map((alert) => (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className={`mb-3 lg:mb-4 p-4 lg:p-5 rounded-lg border-l-4 ${
                alert.type === 'error' ? 'bg-red-50 border-red-400 text-red-800' :
                alert.type === 'warning' ? 'bg-yellow-50 border-yellow-400 text-yellow-800' :
                alert.type === 'success' ? 'bg-green-50 border-green-400 text-green-800' :
                'bg-blue-50 border-blue-400 text-blue-800'
              }`}
            >
              <div className="flex justify-between items-start gap-3">
                <div className="flex items-start gap-3">
                  <span className="text-xl lg:text-2xl">
                    {alert.type === 'error' ? '🚨' :
                     alert.type === 'warning' ? '⚠️' :
                     alert.type === 'success' ? '✅' : 'ℹ️'}
                  </span>
                  <div>
                    <p className="font-semibold text-base lg:text-lg">{alert.message}</p>
                    <p className="text-xs lg:text-sm opacity-75 mt-1">
                      {alert.timestamp.toLocaleString()}
                    </p>
                    {alert.actionable && (
                      <button className="mt-2 text-xs lg:text-sm underline hover:no-underline">
                        Take Action →
                      </button>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => dismissAlert(alert.id)}
                  className="text-gray-400 hover:text-gray-600 text-lg lg:text-xl flex-shrink-0"
                  title="Dismiss alert"
                >
                  ✕
                </button>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* 📊 HEALTHCARE METRICS GRID */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 lg:gap-6 mb-4 lg:mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          {metrics.map((metric, index) => (
            <motion.div
              key={metric.id}
              className={`relative overflow-hidden bg-white rounded-xl p-4 lg:p-6 shadow-lg border-2 ${
                metric.status === 'critical' ? 'border-red-300 bg-red-50 shadow-red-100' :
                metric.status === 'warning' ? 'border-yellow-300 bg-yellow-50 shadow-yellow-100' :
                'border-gray-200 bg-white shadow-gray-100'
              }`}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{ scale: 1.02, y: -4 }}
            >
              {/* Trend Background */}
              <div className="absolute inset-0 opacity-5">
                <svg className="w-full h-full" viewBox="0 0 100 50">
                  <polyline
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    points={metric.trend.map((value, i) => 
                      `${(i / (metric.trend.length - 1)) * 100},${50 - (value / Math.max(...metric.trend)) * 40}`
                    ).join(' ')}
                  />
                </svg>
              </div>

              <div className="relative z-10">
                <div className="flex items-center justify-between mb-3 lg:mb-4">
                  <span className="text-2xl lg:text-3xl">{metric.icon}</span>
                  <div className="text-right">
                    <span className="text-base lg:text-lg font-semibold">{metric.title}</span>
                    {metric.status !== 'normal' && (
                      <span className={`ml-2 lg:ml-3 px-2 py-1 rounded-full text-xs font-bold ${
                        metric.status === 'critical' ? 'bg-red-200 text-red-900' :
                        'bg-yellow-200 text-yellow-900'
                      }`}>
                        {metric.status.toUpperCase()}
                      </span>
                    )}
                  </div>
                </div>
                
                <div className="text-2xl lg:text-3xl font-bold mb-2 text-gray-800">{metric.value}</div>
                
                <div className={`text-sm font-medium ${
                  metric.changeType === 'positive' ? 'text-green-600' :
                  metric.changeType === 'negative' ? 'text-red-600' :
                  'text-gray-600'
                }`}>
                  {metric.changeType === 'positive' ? '📈' : 
                   metric.changeType === 'negative' ? '📉' : '➡️'} {metric.change}
                </div>
                
                <div className="text-xs text-gray-400 mt-2 lg:mt-3 flex justify-between">
                  <span>Updated: {metric.lastUpdated.toLocaleTimeString()}</span>
                  <span>Real-time</span>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* ⚡ QUICK ACTIONS GRID */}
        <motion.div
          className="mb-4 lg:mb-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <h2 className="text-xl lg:text-2xl font-bold text-gray-900 mb-3 lg:mb-4">⚡ Quick Actions</h2>
          
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 lg:gap-4">
            {quickActions.map((action, index) => (
              <motion.button
                key={action.id}
                className={`relative bg-white rounded-xl p-4 lg:p-6 shadow-lg border-2 transition-all duration-200 hover:shadow-xl ${action.disabled ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-50'} ${
                  action.category === 'primary' ? 'ring-2 ring-blue-200' : ''
                }`}
                onClick={action.onClick}
                disabled={action.disabled}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4, delay: 0.5 + index * 0.1 }}
                whileHover={!action.disabled ? { scale: 1.03, y: -3 } : {}}
                whileTap={!action.disabled ? { scale: 0.97 } : {}}
              >
                <span className="text-2xl lg:text-4xl block mb-2 lg:mb-3">{action.icon}</span>
                <div>
                  <span className="font-semibold text-sm lg:text-lg block text-gray-800 leading-tight">{action.title}</span>
                  {action.shortcut && (
                    <div className="text-xs text-gray-500 mt-1 bg-gray-100 px-2 py-1 rounded inline-block">
                      <span className="hidden lg:inline">{action.shortcut}</span>
                    </div>
                  )}
                  {action.category === 'primary' && (
                    <div className="absolute top-2 right-2 w-2 h-2 lg:w-3 lg:h-3 bg-blue-500 rounded-full"></div>
                  )}
                </div>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* 📋 RECENT ACTIVITY */}
        <motion.div
          className="bg-white rounded-xl p-4 lg:p-8 shadow-lg border border-gray-200"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-3 lg:mb-4 gap-2">
            <h2 className="text-xl lg:text-2xl font-bold text-gray-900">📋 Recent Activity</h2>
            <button className="text-blue-600 hover:text-blue-700 font-medium text-sm lg:text-base self-start sm:self-center">
              View All Activity →
            </button>
          </div>
          
          <div className="space-y-3 lg:space-y-4">
            {activities.map((activity, index) => (
              <motion.div
                key={activity.id}
                className={`flex flex-col sm:flex-row sm:items-center sm:justify-between p-4 lg:p-5 rounded-lg transition-all duration-200 gap-3 ${
                  activity.urgent 
                    ? 'bg-red-50 border-2 border-red-200 shadow-red-100' 
                    : 'bg-gray-50 hover:bg-gray-100 border border-gray-200'
                } ${activity.priority === 'critical' ? 'animate-pulse' : ''}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.7 + index * 0.1 }}
              >
                <div className="flex items-start gap-3 flex-1">
                  <div className={`w-3 h-3 lg:w-4 lg:h-4 rounded-full mt-1 flex-shrink-0 ${
                    activity.status === 'success' ? 'bg-green-500' :
                    activity.status === 'pending' ? 'bg-yellow-500 animate-pulse' :
                    activity.status === 'error' ? 'bg-red-500 animate-pulse' :
                    'bg-gray-400'
                  }`} />
                  
                  <div className="flex-1 min-w-0">
                    <p className={`font-medium text-sm lg:text-base ${
                      activity.urgent ? 'text-red-900' : 'text-gray-900'
                    }`}>
                      {activity.message}
                    </p>
                    <p className="text-xs lg:text-sm text-gray-500 mt-1">{activity.time}</p>
                  </div>
                </div>
                
                <div className="flex flex-wrap items-center gap-2 sm:flex-shrink-0">
                  {activity.urgent && (
                    <span className="px-2 py-1 bg-red-200 text-red-900 text-xs font-bold rounded-full animate-pulse">
                      🚨 <span className="hidden sm:inline">URGENT</span>
                    </span>
                  )}
                  {activity.priority === 'critical' && (
                    <span className="px-2 py-1 bg-purple-200 text-purple-900 text-xs font-bold rounded-full">
                      🔥 <span className="hidden sm:inline">CRITICAL</span>
                    </span>
                  )}
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    activity.status === 'success' ? 'bg-green-200 text-green-800' :
                    activity.status === 'pending' ? 'bg-yellow-200 text-yellow-800' :
                    activity.status === 'error' ? 'bg-red-200 text-red-800' :
                    'bg-gray-200 text-gray-800'
                  }`}>
                    {activity.status.toUpperCase()}
                  </span>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* 🔧 DEBUG PANEL */}
        {debugMode && (
          <motion.div
            className="mt-6 lg:mt-8 p-4 lg:p-6 bg-gray-900 text-green-400 rounded-lg font-mono text-xs lg:text-sm shadow-2xl"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1 }}
          >
            <div className="mb-3 lg:mb-4 font-bold text-base lg:text-lg text-green-300">🔧 GIVC Debug Panel</div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 lg:gap-4">
              <div>
                <div className="text-green-300 font-semibold mb-2">System Status:</div>
                <div>User: {user?.name} ({user?.role})</div>
                <div>Connection: {isOnline ? '🟢 Online' : '🔴 Offline'}</div>
                <div>Metrics loaded: {metrics.length}</div>
                <div>Active alerts: {alerts.filter(a => !a.dismissed).length}</div>
                <div>Recent activities: {activities.length}</div>
              </div>
              <div>
                <div className="text-green-300 font-semibold mb-2">Performance:</div>
                <div>Last refresh: {lastRefresh.toISOString()}</div>
                <div>Memory usage: {(performance as any).memory ? `${Math.round((performance as any).memory.usedJSHeapSize / 1024 / 1024)}MB` : 'N/A'}</div>
                <div>Load time: {performance.now().toFixed(2)}ms</div>
              </div>
            </div>
            <div className="mt-3 lg:mt-4 text-xs text-gray-400">
              Shortcuts: Ctrl+R (refresh) | Ctrl+Shift+D (debug) | Ctrl+1 (eligibility) | Ctrl+2 (claims)
            </div>
            <button
              onClick={() => console.log('Debug logs:', debugLogger.getLogs())}
              className="mt-2 px-3 py-1 bg-green-800 text-green-100 rounded text-xs hover:bg-green-700"
            >
              Export Debug Logs
            </button>
          </motion.div>
        )}

        {/* 📱 MOBILE OPTIMIZATION MESSAGE */}
        <div className="md:hidden mt-6 lg:mt-8 p-3 lg:p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center gap-3">
            <span className="text-xl lg:text-2xl">📱</span>
            <div>
              <div className="font-semibold text-blue-900 text-sm lg:text-base">Mobile Optimized</div>
              <div className="text-xs lg:text-sm text-blue-700">
                Dashboard fully optimized for mobile healthcare workflows
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardEnhanced;
