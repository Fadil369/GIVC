import { useAuth } from '../hooks/useAuth.jsx';
import InsuranceAPIService from '../services/insuranceAPI.jsx';
import type { Claim, FraudAlert } from '../types/insurance.jsx';
import {
    ChartBarIcon,
    CheckCircleIcon,
    ClockIcon,
    CurrencyDollarIcon,
    DocumentArrowUpIcon,
    DocumentTextIcon,
    ExclamationTriangleIcon,
    MagnifyingGlassIcon,
    ShieldCheckIcon,
    XCircleIcon,
} from '@heroicons/react/24/outline.jsx';
import { AnimatePresence, motion } from 'framer-motion';
import React, { useEffect, useState } from 'react';

interface ClaimsProcessingProps {
  className?: string;
}

const ClaimsProcessing= '' }) => {
  const { user } = useAuth();
  const [claims, setClaims] = useState([]);
  const [selectedClaim, setSelectedClaim] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [fraudAlerts, setFraudAlerts] = useState([]);
  const [uploadingDocument, setUploadingDocument] = useState(false);

  const statusColors = {
    submitted: 'bg-blue-100 text-blue-800',
    processing: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    denied: 'bg-red-100 text-red-800',
    pending_info: 'bg-purple-100 text-purple-800',
  };

  const statusIcons = {
    submitted: ClockIcon,
    processing: ChartBarIcon,
    approved: CheckCircleIcon,
    denied: XCircleIcon,
    pending_info: ExclamationTriangleIcon,
  };

  useEffect(() => {
    loadClaims();
    loadFraudAlerts();
  }, []);

  const loadClaims = async () => {
    if (!user?.id) return;

    try {
      setIsLoading(true);
      const response = await InsuranceAPIService.getClaims(user.id, {
        page: 1,
        limit: 50,
        sort: [{ field: 'submittedDate', order: 'desc' }],
      });

      if (response.success && response.data) {
        setClaims(response.data.data);
      }
    } catch (error) {
      console.error('Failed to load claims:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadFraudAlerts = async () => {
    try {
      const response = await InsuranceAPIService.getFraudAlerts({
        page: 1,
        limit: 10,
        filters: [{ field: 'status', operator: 'equals', value: 'open' }],
      });

      if (response.success && response.data) {
        setFraudAlerts(response.data.data);
      }
    } catch (error) {
      console.error('Failed to load fraud alerts:', error);
    }
  };

  const processClaimWithAI = async (claimId=> {
    try {
      setIsLoading(true);
      const response = await InsuranceAPIService.processClaimWithAI(claimId);

      if (response.success && response.data) {
        // Update the claim in our state
        setClaims(prev =>
          prev.map(claim =>
            claim.id === claimId ? response.data! : claim
          )
        );

        if (selectedClaim?.id === claimId) {
          setSelectedClaim(response.data);
        }
      }
    } catch (error) {
      console.error('Failed to process claim with AI:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const runFraudDetection = async (claimId=> {
    try {
      setIsLoading(true);
      const response = await InsuranceAPIService.detectClaimFraud(claimId);

      if (response.success && response.data) {
        // Add new fraud alerts to our state
        setFraudAlerts(prev => [...response.data!, ...prev]);
      }
    } catch (error) {
      console.error('Failed to run fraud detection:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const uploadDocument = async (claimId=> {
    try {
      setUploadingDocument(true);
      const response = await InsuranceAPIService.uploadClaimDocument(claimId, file, type);

      if (response.success) {
        // Reload the claim to get updated documents
        const claimResponse = await InsuranceAPIService.getClaim(claimId);
        if (claimResponse.success && claimResponse.data) {
          setClaims(prev =>
            prev.map(claim =>
              claim.id === claimId ? claimResponse.data! : claim
            )
          );

          if (selectedClaim?.id === claimId) {
            setSelectedClaim(claimResponse.data);
          }
        }
      }
    } catch (error) {
      console.error('Failed to upload document:', error);
    } finally {
      setUploadingDocument(false);
    }
  };

  const filteredClaims = claims.filter(claim => {
    const matchesSearch = 
      claim.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      claim.provider.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      claim.type.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesStatus = statusFilter === 'all' || claim.status === statusFilter;

    return matchesSearch && matchesStatus;
  });

  const formatCurrency = (amount=> {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  const formatDate = (dateString=> {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (selectedClaim) {
    const StatusIcon = statusIcons[selectedClaim.status];
    
    return (
      <div className={`max-w-6xl mx-auto p-6 ${className}`}>
        {/* Claim Detail Header */}
        <div className="mb-6">
          <button
            onClick={() => setSelectedClaim(null)}
            className="mb-4 text-blue-600 hover:text-blue-800 font-medium"
          >
            ← Back to Claims
          </button>
          
          <div className="bg-white rounded-xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Claim #{selectedClaim.id}</h1>
                <p className="text-gray-600">Submitted on {formatDate(selectedClaim.submittedDate)}</p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <StatusIcon className="w-5 h-5 mr-2" />
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[selectedClaim.status]}`}>
                    {selectedClaim.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-gray-900">
                    {formatCurrency(selectedClaim.totalAmount)}
                  </p>
                  <p className="text-sm text-gray-600">Total Amount</p>
                </div>
              </div>
            </div>

            {/* Claim Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <CheckCircleIcon className="w-8 h-8 text-green-600 mr-3" />
                  <div>
                    <p className="text-2xl font-bold text-green-900">
                      {formatCurrency(selectedClaim.coveredAmount)}
                    </p>
                    <p className="text-sm text-green-700">Covered Amount</p>
                  </div>
                </div>
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <CurrencyDollarIcon className="w-8 h-8 text-blue-600 mr-3" />
                  <div>
                    <p className="text-2xl font-bold text-blue-900">
                      {formatCurrency(selectedClaim.patientResponsibility)}
                    </p>
                    <p className="text-sm text-blue-700">Your Responsibility</p>
                  </div>
                </div>
              </div>

              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <DocumentTextIcon className="w-8 h-8 text-purple-600 mr-3" />
                  <div>
                    <p className="text-2xl font-bold text-purple-900">
                      {formatCurrency(selectedClaim.deductibleApplied)}
                    </p>
                    <p className="text-sm text-purple-700">Deductible Applied</p>
                  </div>
                </div>
              </div>

              <div className="bg-orange-50 p-4 rounded-lg">
                <div className="flex items-center">
                  <ShieldCheckIcon className="w-8 h-8 text-orange-600 mr-3" />
                  <div>
                    <p className="text-2xl font-bold text-orange-900">
                      {selectedClaim.fraudRisk.score}%
                    </p>
                    <p className="text-sm text-orange-700">Fraud Risk</p>
                  </div>
                </div>
              </div>
            </div>

            {/* AI Analysis */}
            {selectedClaim.aiAnalysis.processed && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
                  <ChartBarIcon className="w-5 h-5 mr-2" />
                  AI Analysis Results
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-blue-700 mb-2">
                      <strong>Confidence:</strong> {(selectedClaim.aiAnalysis.confidence * 100).toFixed(1)}%
                    </p>
                    <p className="text-sm text-blue-700">
                      <strong>Recommendations:</strong>
                    </p>
                    <ul className="text-sm text-blue-700 list-disc list-inside">
                      {selectedClaim.aiAnalysis.recommendations.map((rec, index) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    {selectedClaim.aiAnalysis.flaggedAnomalies.length > 0 && (
                      <>
                        <p className="text-sm text-blue-700 mb-2">
                          <strong>Flagged Anomalies:</strong>
                        </p>
                        <ul className="text-sm text-blue-700 list-disc list-inside">
                          {selectedClaim.aiAnalysis.flaggedAnomalies.map((anomaly, index) => (
                            <li key={index}>{anomaly}</li>
                          ))}
                        </ul>
                      </>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex space-x-4 mb-6">
              {!selectedClaim.aiAnalysis.processed && (
                <button
                  onClick={() => processClaimWithAI(selectedClaim.id)}
                  disabled={isLoading}
                  className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  {isLoading ? 'Processing...' : 'Process with AI'}
                </button>
              )}

              <button
                onClick={() => runFraudDetection(selectedClaim.id)}
                disabled={isLoading}
                className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                {isLoading ? 'Scanning...' : 'Run Fraud Detection'}
              </button>

              <label className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium cursor-pointer transition-colors">
                <DocumentArrowUpIcon className="w-5 h-5 inline mr-2" />
                {uploadingDocument ? 'Uploading...' : 'Upload Document'}
                <input
                  type="file"
                  className="hidden"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) {
                      uploadDocument(selectedClaim.id, file, 'medical_record');
                    }
                  }}
                  disabled={uploadingDocument}
                />
              </label>
            </div>

            {/* Provider Information */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-3">Provider Information</h3>
                <div className="space-y-2 text-sm">
                  <p><strong>Name:</strong> {selectedClaim.provider.name}</p>
                  <p><strong>NPI:</strong> {selectedClaim.provider.npi}</p>
                  <p><strong>Specialty:</strong> {selectedClaim.provider.specialty}</p>
                  <p><strong>Address:</strong> {selectedClaim.provider.address}</p>
                </div>
              </div>

              <div className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-3">Services Provided</h3>
                <div className="space-y-3">
                  {selectedClaim.services.map((service) => (
                    <div key={service.id} className="border-b border-gray-200 pb-2 last:border-b-0">
                      <div className="flex justify-between items-start">
                        <div>
                          <p className="font-medium text-gray-900">{service.description}</p>
                          <p className="text-sm text-gray-600">CPT: {service.cptCode}</p>
                          <p className="text-sm text-gray-600">Date: {formatDate(service.dateOfService)}</p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-gray-900">
                            {formatCurrency(service.totalPrice)}
                          </p>
                          <p className="text-sm text-gray-600">Qty: {service.quantity}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`max-w-6xl mx-auto p-6 ${className}`}>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Claims Processing</h1>
        <p className="text-gray-600">
          Manage and track your insurance claims with AI-powered processing
        </p>
      </div>

      {/* Fraud Alerts */}
      {fraudAlerts.length > 0 && (
        <div className="mb-6">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center mb-3">
              <ExclamationTriangleIcon className="w-6 h-6 text-red-600 mr-2" />
              <h3 className="font-semibold text-red-900">Fraud Alerts ({fraudAlerts.length})</h3>
            </div>
            <div className="space-y-2">
              {fraudAlerts.slice(0, 3).map((alert) => (
                <div key={alert.id} className="bg-white p-3 rounded border">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{alert.description}</p>
                      <p className="text-sm text-gray-600">
                        Claim #{alert.claimId} • Confidence: {alert.confidence}%
                      </p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      alert.severity === 'critical' ? 'bg-red-100 text-red-800' :
                      alert.severity === 'high' ? 'bg-orange-100 text-orange-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {alert.severity.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Search and Filters */}
      <div className="mb-6">
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0">
            <div className="flex-1 max-w-md">
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search claims..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                aria-label="Filter claims by status"
              >
                <option value="all">All Status</option>
                <option value="submitted">Submitted</option>
                <option value="processing">Processing</option>
                <option value="approved">Approved</option>
                <option value="denied">Denied</option>
                <option value="pending_info">Pending Info</option>
              </select>

              <button
                onClick={() => console.log('New claim form - TODO')}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                New Claim
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Claims List */}
      <div className="space-y-4">
        <AnimatePresence>
          {filteredClaims.map((claim) => {
            const StatusIcon = statusIcons[claim.status];
            
            return (
              <motion.div
                key={claim.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => setSelectedClaim(claim)}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center">
                    <StatusIcon className="w-6 h-6 mr-3 text-gray-600" />
                    <div>
                      <h3 className="font-semibold text-gray-900">Claim #{claim.id}</h3>
                      <p className="text-sm text-gray-600">
                        {claim.provider.name} • {formatDate(claim.submittedDate)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusColors[claim.status]}`}>
                      {claim.status.replace('_', ' ').toUpperCase()}
                    </span>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">
                        {formatCurrency(claim.totalAmount)}
                      </p>
                      <p className="text-sm text-gray-600">
                        Your part: {formatCurrency(claim.patientResponsibility)}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Type</p>
                    <p className="font-medium text-gray-900 capitalize">{claim.type.replace('_', ' ')}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Services</p>
                    <p className="font-medium text-gray-900">{claim.services.length} service(s)</p>
                  </div>
                  <div>
                    <p className="text-gray-600">AI Processed</p>
                    <p className="font-medium text-gray-900">
                      {claim.aiAnalysis.processed ? 'Yes' : 'No'}
                    </p>
                  </div>
                </div>

                {claim.fraudRisk.score > 70 && (
                  <div className="mt-4 bg-red-50 border border-red-200 rounded p-3">
                    <div className="flex items-center">
                      <ExclamationTriangleIcon className="w-5 h-5 text-red-600 mr-2" />
                      <p className="text-sm text-red-800">
                        High fraud risk detected ({claim.fraudRisk.score}% confidence)
                      </p>
                    </div>
                  </div>
                )}
              </motion.div>
            );
          })}
        </AnimatePresence>

        {filteredClaims.length === 0 && !isLoading && (
          <div className="text-center py-12">
            <DocumentTextIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No claims found</h3>
            <p className="text-gray-600 mb-4">
              {searchTerm || statusFilter !== 'all'
                ? 'Try adjusting your search or filters'
                : 'You haven\'t submitted any claims yet'}
            </p>
            {!searchTerm && statusFilter === 'all' && (
              <button
                onClick={() => console.log('Submit first claim - TODO')}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
              >
                Submit Your First Claim
              </button>
            )}
          </div>
        )}

        {isLoading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="mt-2 text-gray-600">Loading claims...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClaimsProcessing;
