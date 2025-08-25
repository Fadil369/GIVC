import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../../hooks/useAuth.jsx';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    totalFiles: 0,
    filesProcessedToday: 0,
    aiProcessingQueue: 0,
    complianceScore: 0,
    activeUsers: 0,
    systemUptime: 0,
    averageProcessingTime: 0,
    criticalAlerts: 0
  });

  useEffect(() => {
    // Mock data for demonstration
    setStats({
      totalFiles: 1247,
      filesProcessedToday: 84,
      aiProcessingQueue: 12,
      complianceScore: 98.5,
      activeUsers: 45,
      systemUptime: 99.8,
      averageProcessingTime: 2.3,
      criticalAlerts: 2
    });
  }, []);

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.name || 'Healthcare Professional'}
        </h1>
        <p className="text-gray-600 mt-2">
          Here's what's happening with your GIVC platform today.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <motion.div
          className="bg-white rounded-lg shadow p-6"
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.2 }}
        >
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <div className="w-6 h-6 text-blue-600">📄</div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Files</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.totalFiles}</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="bg-white rounded-lg shadow p-6"
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.2 }}
        >
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <div className="w-6 h-6 text-green-600">✅</div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Processed Today</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.filesProcessedToday}</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="bg-white rounded-lg shadow p-6"
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.2 }}
        >
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <div className="w-6 h-6 text-yellow-600">⏳</div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">AI Queue</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.aiProcessingQueue}</p>
            </div>
          </div>
        </motion.div>

        <motion.div
          className="bg-white rounded-lg shadow p-6"
          whileHover={{ scale: 1.02 }}
          transition={{ duration: 0.2 }}
        >
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <div className="w-6 h-6 text-purple-600">🛡️</div>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Compliance Score</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.complianceScore}%</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow mb-8">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="flex items-center p-4 bg-blue-50 rounded-lg hover:bg-blue-100 transition-colors">
              <div className="w-8 h-8 bg-blue-600 text-white rounded-lg flex items-center justify-center mr-3">
                📤
              </div>
              <div className="text-left">
                <h3 className="font-medium text-gray-900">Upload Files</h3>
                <p className="text-sm text-gray-600">Add new medical files</p>
              </div>
            </button>

            <button className="flex items-center p-4 bg-green-50 rounded-lg hover:bg-green-100 transition-colors">
              <div className="w-8 h-8 bg-green-600 text-white rounded-lg flex items-center justify-center mr-3">
                🤖
              </div>
              <div className="text-left">
                <h3 className="font-medium text-gray-900">AI Analysis</h3>
                <p className="text-sm text-gray-600">Process with AI agents</p>
              </div>
            </button>

            <button className="flex items-center p-4 bg-purple-50 rounded-lg hover:bg-purple-100 transition-colors">
              <div className="w-8 h-8 bg-purple-600 text-white rounded-lg flex items-center justify-center mr-3">
                📊
              </div>
              <div className="text-left">
                <h3 className="font-medium text-gray-900">View Reports</h3>
                <p className="text-sm text-gray-600">Analytics & insights</p>
              </div>
            </button>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="flex items-center p-4 bg-gray-50 rounded-lg">
              <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center mr-3">
                📄
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">DICOM file analyzed</h4>
                <p className="text-sm text-gray-600">Chest X-ray processed by AI agent</p>
              </div>
              <span className="text-sm text-gray-500">2 minutes ago</span>
            </div>

            <div className="flex items-center p-4 bg-gray-50 rounded-lg">
              <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center mr-3">
                ✅
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">Lab results processed</h4>
                <p className="text-sm text-gray-600">Blood work analysis completed</p>
              </div>
              <span className="text-sm text-gray-500">15 minutes ago</span>
            </div>

            <div className="flex items-center p-4 bg-gray-50 rounded-lg">
              <div className="w-8 h-8 bg-yellow-600 text-white rounded-full flex items-center justify-center mr-3">
                ⚠️
              </div>
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">Compliance alert</h4>
                <p className="text-sm text-gray-600">Access log requires review</p>
              </div>
              <span className="text-sm text-gray-500">1 hour ago</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
