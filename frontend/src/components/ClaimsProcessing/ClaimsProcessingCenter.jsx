import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const ClaimsProcessingCenter = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [claims, setClaims] = useState([]);
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [processingStats, setProcessingStats] = useState({});
  const [fraudAlerts, setFraudAlerts] = useState([]);
  const [automationSettings, setAutomationSettings] = useState({});

  const claimStatuses = {
    submitted: { label: 'Submitted', color: 'bg-blue-100 text-blue-800', count: 42 },
    'under-review': { label: 'Under Review', color: 'bg-yellow-100 text-yellow-800', count: 28 },
    'ai-approved': { label: 'AI Approved', color: 'bg-green-100 text-green-800', count: 156 },
    'needs-review': { label: 'Needs Review', color: 'bg-orange-100 text-orange-800', count: 15 },
    approved: { label: 'Approved', color: 'bg-green-100 text-green-800', count: 234 },
    denied: { label: 'Denied', color: 'bg-red-100 text-red-800', count: 12 },
    'fraud-flagged': { label: 'Fraud Flagged', color: 'bg-red-100 text-red-800', count: 3 }
  };

  const processingRules = [
    {
      id: 1,
      name: 'Routine Checkup Auto-Approval',
      type: 'auto-approve',
      criteria: 'Preventive care claims under $500 with verified provider',
      enabled: true,
      accuracy: 98.5,
      processed: 1247
    },
    {
      id: 2,
      name: 'Duplicate Claim Detection',
      type: 'fraud-detection',
      criteria: 'Same service, date, and provider within 24 hours',
      enabled: true,
      accuracy: 99.2,
      processed: 89
    },
    {
      id: 3,
      name: 'High-Value Claim Review',
      type: 'manual-review',
      criteria: 'Claims over $10,000 require human review',
      enabled: true,
      accuracy: 95.8,
      processed: 156
    },
    {
      id: 4,
      name: 'Provider Network Verification',
      type: 'validation',
      criteria: 'Verify provider is in-network and certified',
      enabled: true,
      accuracy: 99.8,
      processed: 2341
    }
  ];

  useEffect(() => {
    loadMockData();
  }, []);

  const loadMockData = () => {
    // Mock claims data
    setClaims([
      {
        id: 'CLM-2025-001',
        patientName: 'John Smith',
        patientId: 'P-123456',
        serviceDate: '2025-01-28',
        submittedDate: '2025-01-29',
        provider: 'Dr. Sarah Wilson - Cardiology',
        providerId: 'PRV-789',
        serviceType: 'Consultation',
        amount: 285.00,
        status: 'ai-approved',
        aiConfidence: 94.2,
        processingTime: '2 minutes',
        diagnosis: 'Routine cardiac checkup',
        procedureCodes: ['99213', '93306'],
        priority: 'normal',
        fraudScore: 12, // Low risk
        autoApproved: true,
        reviewNotes: 'Standard consultation within normal parameters. Provider verified, patient history consistent.'
      },
      {
        id: 'CLM-2025-002',
        patientName: 'Maria Rodriguez',
        patientId: 'P-654321',
        serviceDate: '2025-01-27',
        submittedDate: '2025-01-28',
        provider: 'City General Hospital - Emergency',
        providerId: 'PRV-456',
        serviceType: 'Emergency Room Visit',
        amount: 1847.50,
        status: 'under-review',
        aiConfidence: 76.8,
        processingTime: 'Pending',
        diagnosis: 'Chest pain evaluation',
        procedureCodes: ['99284', '71045', '80053'],
        priority: 'high',
        fraudScore: 23, // Medium risk
        autoApproved: false,
        reviewNotes: 'Higher than average cost for similar procedures. Requires manual review for cost justification.'
      },
      {
        id: 'CLM-2025-003',
        patientName: 'Ahmed Al-Hassan',
        patientId: 'P-789012',
        serviceDate: '2025-01-26',
        submittedDate: '2025-01-29',
        provider: 'Quick Care Clinic',
        providerId: 'PRV-999',
        serviceType: 'Multiple Procedures',
        amount: 3250.00,
        status: 'fraud-flagged',
        aiConfidence: 15.3,
        processingTime: 'Flagged',
        diagnosis: 'Various conditions',
        procedureCodes: ['99213', '99214', '99215', '87426', '36415'],
        priority: 'urgent',
        fraudScore: 87, // High risk
        autoApproved: false,
        reviewNotes: 'FRAUD ALERT: Same patient, multiple high-level consultations on same day. Provider has previous fraud indicators.'
      },
      {
        id: 'CLM-2025-004',
        patientName: 'Lisa Chen',
        patientId: 'P-345678',
        serviceDate: '2025-01-25',
        submittedDate: '2025-01-25',
        provider: 'Premier Vision Center',
        providerId: 'PRV-567',
        serviceType: 'Eye Examination',
        amount: 165.00,
        status: 'approved',
        aiConfidence: 98.7,
        processingTime: '45 seconds',
        diagnosis: 'Routine eye exam',
        procedureCodes: ['92014'],
        priority: 'normal',
        fraudScore: 8, // Very low risk
        autoApproved: true,
        reviewNotes: 'Standard preventive care. All parameters within normal ranges.'
      }
    ]);

    // Mock processing stats
    setProcessingStats({
      totalClaims: 2847,
      processedToday: 189,
      avgProcessingTime: '3.2 minutes',
      autoApprovalRate: 78.4,
      fraudDetectionRate: 2.1,
      costSavings: 145280,
      accuracy: 96.8
    });

    // Mock fraud alerts
    setFraudAlerts([
      {
        id: 'FA-001',
        claimId: 'CLM-2025-003',
        type: 'Pattern Anomaly',
        severity: 'high',
        description: 'Multiple high-level consultations same day',
        confidence: 89.2,
        timestamp: new Date('2025-01-29T10:15:00')
      },
      {
        id: 'FA-002',
        claimId: 'CLM-2025-018',
        type: 'Provider Risk',
        severity: 'medium',
        description: 'Provider exceeded normal billing patterns',
        confidence: 67.5,
        timestamp: new Date('2025-01-29T09:30:00')
      }
    ]);

    // Mock automation settings
    setAutomationSettings({
      autoApprovalThreshold: 85,
      fraudDetectionSensitivity: 'high',
      manualReviewThreshold: 10000,
      maxProcessingTime: 24,
      enableRealTimeProcessing: true,
      enablePredictiveAnalytics: true
    });
  };

  const getStatusBadge = (status) => {
    const statusInfo = claimStatuses[status];
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${statusInfo.color}`}>
        {statusInfo.label}
      </span>
    );
  };

  const getPriorityBadge = (priority) => {
    const colors = {
      normal: 'bg-gray-100 text-gray-800',
      high: 'bg-yellow-100 text-yellow-800',
      urgent: 'bg-red-100 text-red-800'
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[priority]}`}>
        {priority.toUpperCase()}
      </span>
    );
  };

  const getFraudScoreColor = (score) => {
    if (score < 30) return 'text-green-600';
    if (score < 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 70) return 'text-yellow-600';
    return 'text-red-600';
  };

  const filteredClaims = claims.filter(claim => {
    const matchesStatus = filterStatus === 'all' || claim.status === filterStatus;
    const matchesSearch = claim.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         claim.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         claim.provider.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  const handleClaimAction = (claimId, action) => {
    setClaims(prev => prev.map(claim => 
      claim.id === claimId 
        ? { ...claim, status: action, processingTime: 'Just now' }
        : claim
    ));
  };

  const ClaimDetailModal = ({ claim, onClose }) => {
    if (!claim) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto"
        >
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Claim Details</h2>
                <p className="text-sm text-gray-500">{claim.id}</p>
              </div>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Status and AI Analysis */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">Status</h3>
                <div className="space-y-2">
                  {getStatusBadge(claim.status)}
                  {getPriorityBadge(claim.priority)}
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">AI Confidence</h3>
                <div className="flex items-center space-x-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${getConfidenceColor(claim.aiConfidence).replace('text-', 'bg-')}`}
                      style={{ width: `${claim.aiConfidence}%` }}
                    ></div>
                  </div>
                  <span className={`text-sm font-medium ${getConfidenceColor(claim.aiConfidence)}`}>
                    {claim.aiConfidence}%
                  </span>
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">Fraud Risk</h3>
                <div className="flex items-center space-x-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${getFraudScoreColor(claim.fraudScore).replace('text-', 'bg-')}`}
                      style={{ width: `${claim.fraudScore}%` }}
                    ></div>
                  </div>
                  <span className={`text-sm font-medium ${getFraudScoreColor(claim.fraudScore)}`}>
                    {claim.fraudScore}
                  </span>
                </div>
              </div>
            </div>

            {/* Patient and Provider Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Patient Information</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Name:</span>
                    <span className="text-sm font-medium text-gray-900">{claim.patientName}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Patient ID:</span>
                    <span className="text-sm font-medium text-gray-900">{claim.patientId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Service Date:</span>
                    <span className="text-sm font-medium text-gray-900">{claim.serviceDate}</span>
                  </div>
                </div>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Provider Information</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Provider:</span>
                    <span className="text-sm font-medium text-gray-900">{claim.provider}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Provider ID:</span>
                    <span className="text-sm font-medium text-gray-900">{claim.providerId}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Service Type:</span>
                    <span className="text-sm font-medium text-gray-900">{claim.serviceType}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Claim Details */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Claim Details</h3>
              <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Diagnosis:</span>
                  <span className="text-sm font-medium text-gray-900">{claim.diagnosis}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Procedure Codes:</span>
                  <span className="text-sm font-medium text-gray-900">{claim.procedureCodes.join(', ')}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Claim Amount:</span>
                  <span className="text-lg font-bold text-gray-900">${claim.amount.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Processing Time:</span>
                  <span className="text-sm font-medium text-gray-900">{claim.processingTime}</span>
                </div>
              </div>
            </div>

            {/* AI Review Notes */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">AI Analysis & Notes</h3>
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <p className="text-sm text-gray-700">{claim.reviewNotes}</p>
              </div>
            </div>

            {/* Actions */}
            {(claim.status === 'under-review' || claim.status === 'needs-review') && (
              <div className="flex space-x-3 pt-4 border-t border-gray-200">
                <button
                  onClick={() => {
                    handleClaimAction(claim.id, 'approved');
                    onClose();
                  }}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  Approve Claim
                </button>
                <button
                  onClick={() => {
                    handleClaimAction(claim.id, 'denied');
                    onClose();
                  }}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  Deny Claim
                </button>
                <button
                  onClick={() => {
                    handleClaimAction(claim.id, 'needs-review');
                    onClose();
                  }}
                  className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                >
                  Request More Info
                </button>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    );
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Claims Processing Center</h1>
        <p className="text-gray-600">
          AI-powered automated claims review with fraud detection and intelligent routing
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'dashboard', name: 'Processing Dashboard', icon: '📊' },
              { id: 'claims', name: 'Claims Queue', icon: '📋' },
              { id: 'fraud', name: 'Fraud Detection', icon: '🛡️' },
              { id: 'automation', name: 'AI Rules Engine', icon: '⚙️' },
              { id: 'analytics', name: 'Analytics', icon: '📈' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="text-lg">{tab.icon}</span>
                <span>{tab.name}</span>
              </button>
            ))}
          </nav>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {/* Processing Dashboard */}
        {activeTab === 'dashboard' && (
          <motion.div
            key="dashboard"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <span className="text-2xl">📊</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Total Claims</p>
                    <p className="text-2xl font-bold text-gray-900">{processingStats.totalClaims?.toLocaleString()}</p>
                  </div>
                </div>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <span className="text-2xl">⚡</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Processed Today</p>
                    <p className="text-2xl font-bold text-gray-900">{processingStats.processedToday}</p>
                  </div>
                </div>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-purple-100 rounded-lg">
                    <span className="text-2xl">🤖</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Auto-Approval Rate</p>
                    <p className="text-2xl font-bold text-gray-900">{processingStats.autoApprovalRate}%</p>
                  </div>
                </div>
              </div>
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center">
                  <div className="p-2 bg-yellow-100 rounded-lg">
                    <span className="text-2xl">💰</span>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-600">Cost Savings</p>
                    <p className="text-2xl font-bold text-gray-900">${processingStats.costSavings?.toLocaleString()}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Status Overview */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">Claims by Status</h3>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    {Object.entries(claimStatuses).map(([status, info]) => (
                      <div key={status} className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${info.color}`}>
                            {info.label}
                          </span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm font-medium text-gray-900">{info.count}</span>
                          <div className="w-20 bg-gray-200 rounded-full h-2">
                            <div 
                              className="bg-blue-600 h-2 rounded-full"
                              style={{ width: `${(info.count / 500) * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">Recent Fraud Alerts</h3>
                </div>
                <div className="p-6">
                  <div className="space-y-4">
                    {fraudAlerts.slice(0, 3).map((alert) => (
                      <div key={alert.id} className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg border border-red-200">
                        <div className="flex-shrink-0">
                          <span className="text-red-600">⚠️</span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-red-900">{alert.type}</p>
                          <p className="text-xs text-red-700">{alert.description}</p>
                          <p className="text-xs text-red-600 mt-1">
                            Confidence: {alert.confidence}% • {alert.timestamp.toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Claims Queue */}
        {activeTab === 'claims' && (
          <motion.div
            key="claims"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Filters */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
                <div className="flex items-center space-x-4">
                  <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="all">All Status</option>
                    {Object.entries(claimStatuses).map(([status, info]) => (
                      <option key={status} value={status}>{info.label}</option>
                    ))}
                  </select>
                </div>
                <div className="flex items-center space-x-4">
                  <input
                    type="text"
                    placeholder="Search claims..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Claims Table */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Claim ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Patient
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Provider
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Amount
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        AI Score
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {filteredClaims.map((claim) => (
                      <tr key={claim.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {claim.id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div>
                            <div className="text-sm font-medium text-gray-900">{claim.patientName}</div>
                            <div className="text-sm text-gray-500">{claim.patientId}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{claim.provider.split(' - ')[0]}</div>
                          <div className="text-sm text-gray-500">{claim.serviceType}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          ${claim.amount.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="space-y-1">
                            {getStatusBadge(claim.status)}
                            {getPriorityBadge(claim.priority)}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="flex items-center space-x-2">
                            <span className={`text-sm font-medium ${getConfidenceColor(claim.aiConfidence)}`}>
                              {claim.aiConfidence}%
                            </span>
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${getConfidenceColor(claim.aiConfidence).replace('text-', 'bg-')}`}
                                style={{ width: `${claim.aiConfidence}%` }}
                              ></div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <button
                            onClick={() => setSelectedClaim(claim)}
                            className="text-blue-600 hover:text-blue-900 mr-3"
                          >
                            View Details
                          </button>
                          {(claim.status === 'under-review' || claim.status === 'needs-review') && (
                            <>
                              <button
                                onClick={() => handleClaimAction(claim.id, 'approved')}
                                className="text-green-600 hover:text-green-900 mr-3"
                              >
                                Approve
                              </button>
                              <button
                                onClick={() => handleClaimAction(claim.id, 'denied')}
                                className="text-red-600 hover:text-red-900"
                              >
                                Deny
                              </button>
                            </>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </motion.div>
        )}

        {/* Fraud Detection */}
        {activeTab === 'fraud' && (
          <motion.div
            key="fraud"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900">Fraud Alerts</h3>
                  </div>
                  <div className="divide-y divide-gray-200">
                    {fraudAlerts.map((alert) => (
                      <div key={alert.id} className="p-6">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-3">
                            <div className={`flex-shrink-0 p-2 rounded-lg ${
                              alert.severity === 'high' ? 'bg-red-100' : 'bg-yellow-100'
                            }`}>
                              <span className="text-lg">
                                {alert.severity === 'high' ? '🚨' : '⚠️'}
                              </span>
                            </div>
                            <div>
                              <h4 className="text-sm font-semibold text-gray-900">{alert.type}</h4>
                              <p className="text-sm text-gray-600 mt-1">{alert.description}</p>
                              <div className="flex items-center space-x-4 mt-2">
                                <span className="text-xs text-gray-500">
                                  Claim: {alert.claimId}
                                </span>
                                <span className="text-xs text-gray-500">
                                  Confidence: {alert.confidence}%
                                </span>
                                <span className="text-xs text-gray-500">
                                  {alert.timestamp.toLocaleString()}
                                </span>
                              </div>
                            </div>
                          </div>
                          <div className="flex space-x-2">
                            <button className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors">
                              Investigate
                            </button>
                            <button className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors">
                              Dismiss
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Fraud Detection Stats</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Detection Rate:</span>
                      <span className="text-sm font-medium text-gray-900">2.1%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">False Positives:</span>
                      <span className="text-sm font-medium text-gray-900">0.3%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Prevented Loss:</span>
                      <span className="text-sm font-medium text-gray-900">$89,450</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Accuracy:</span>
                      <span className="text-sm font-medium text-gray-900">97.8%</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* AI Rules Engine */}
        {activeTab === 'automation' && (
          <motion.div
            key="automation"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Processing Rules</h3>
                <p className="text-sm text-gray-600">Configure AI-powered automated processing rules</p>
              </div>
              <div className="divide-y divide-gray-200">
                {processingRules.map((rule) => (
                  <div key={rule.id} className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h4 className="text-sm font-semibold text-gray-900">{rule.name}</h4>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            rule.type === 'auto-approve' ? 'bg-green-100 text-green-800' :
                            rule.type === 'fraud-detection' ? 'bg-red-100 text-red-800' :
                            rule.type === 'manual-review' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-blue-100 text-blue-800'
                          }`}>
                            {rule.type.replace('-', ' ')}
                          </span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{rule.criteria}</p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span>Accuracy: {rule.accuracy}%</span>
                          <span>Processed: {rule.processed}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input 
                            type="checkbox" 
                            checked={rule.enabled} 
                            className="sr-only peer"
                            onChange={() => {
                              // Toggle rule enabled state
                            }}
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                        </label>
                        <button className="px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded-full hover:bg-gray-200 transition-colors">
                          Edit
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Analytics */}
        {activeTab === 'analytics' && (
          <motion.div
            key="analytics"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Processing Efficiency</h3>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Average Processing Time</span>
                      <span className="font-medium">3.2 minutes</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-600 h-2 rounded-full" style={{width: '78%'}}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>AI Accuracy Rate</span>
                      <span className="font-medium">96.8%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-green-600 h-2 rounded-full" style={{width: '96.8%'}}></div>
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span>Cost Reduction</span>
                      <span className="font-medium">$145,280</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div className="bg-purple-600 h-2 rounded-full" style={{width: '85%'}}></div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Trends</h3>
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">📈</div>
                  <p>Interactive charts coming soon</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Claim Detail Modal */}
      <AnimatePresence>
        {selectedClaim && (
          <ClaimDetailModal 
            claim={selectedClaim} 
            onClose={() => setSelectedClaim(null)} 
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default ClaimsProcessingCenter;
