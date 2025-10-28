import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const RiskAssessmentEngine = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [riskProfiles, setRiskProfiles] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [predictiveModels, setPredictiveModels] = useState([]);
  const [riskFactors, setRiskFactors] = useState([]);
  const [assessmentHistory, setAssessmentHistory] = useState([]);
  const [filterCategory, setFilterCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  const riskCategories = {
    'chronic-disease': { 
      name: 'Chronic Disease', 
      color: 'bg-red-100 text-red-800', 
      icon: '🫀',
      description: 'Long-term conditions requiring ongoing care'
    },
    'acute-care': { 
      name: 'Acute Care', 
      color: 'bg-orange-100 text-orange-800', 
      icon: '🚨',
      description: 'Immediate medical attention needs'
    },
    'preventive': { 
      name: 'Preventive Care', 
      color: 'bg-green-100 text-green-800', 
      icon: '🛡️',
      description: 'Prevention and early detection focus'
    },
    'behavioral': { 
      name: 'Behavioral Health', 
      color: 'bg-purple-100 text-purple-800', 
      icon: '🧠',
      description: 'Mental health and substance abuse risks'
    },
    'pharmacy': { 
      name: 'Pharmacy', 
      color: 'bg-blue-100 text-blue-800', 
      icon: '💊',
      description: 'Medication adherence and drug interactions'
    }
  };

  const riskLevels = {
    low: { name: 'Low Risk', color: 'text-green-600', bgColor: 'bg-green-100', range: '0-25' },
    moderate: { name: 'Moderate Risk', color: 'text-yellow-600', bgColor: 'bg-yellow-100', range: '26-50' },
    high: { name: 'High Risk', color: 'text-orange-600', bgColor: 'bg-orange-100', range: '51-75' },
    critical: { name: 'Critical Risk', color: 'text-red-600', bgColor: 'bg-red-100', range: '76-100' }
  };

  useEffect(() => {
    loadMockData();
  }, []);

  const loadMockData = () => {
    // Mock risk profiles
    setRiskProfiles([
      {
        id: 'RP-001',
        patientId: 'P-123456',
        patientName: 'John Smith',
        age: 58,
        gender: 'Male',
        overallRiskScore: 72,
        riskLevel: 'high',
        lastAssessment: new Date('2025-01-28'),
        nextReview: new Date('2025-02-28'),
        categories: {
          'chronic-disease': { score: 85, trend: 'increasing', factors: ['Diabetes Type 2', 'Hypertension', 'High Cholesterol'] },
          'acute-care': { score: 45, trend: 'stable', factors: ['Previous ER visits', 'Chest pain episodes'] },
          'preventive': { score: 30, trend: 'improving', factors: ['Overdue screenings', 'Vaccination gaps'] },
          'behavioral': { score: 20, trend: 'stable', factors: ['Mild anxiety'] },
          'pharmacy': { score: 60, trend: 'concerning', factors: ['Poor medication adherence', 'Multiple prescriptions'] }
        },
        predictions: {
          hospitalizationRisk: { probability: 35, timeframe: '6 months', confidence: 87 },
          costProjection: { amount: 12500, period: 'annual', confidence: 92 },
          interventionOpportunity: 'High - Diabetes management program recommended'
        },
        medicalHistory: {
          conditions: ['Type 2 Diabetes', 'Hypertension', 'Hyperlipidemia'],
          medications: ['Metformin', 'Lisinopril', 'Atorvastatin'],
          allergies: ['Penicillin'],
          procedures: ['Cardiac catheterization (2023)', 'Colonoscopy (2022)']
        },
        socialDeterminants: {
          smoking: 'Former smoker (quit 2020)',
          alcohol: 'Occasional',
          exercise: 'Sedentary',
          diet: 'Poor',
          income: 'Middle',
          education: 'High school',
          transportation: 'Available'
        }
      },
      {
        id: 'RP-002',
        patientId: 'P-654321',
        patientName: 'Maria Rodriguez',
        age: 34,
        gender: 'Female',
        overallRiskScore: 28,
        riskLevel: 'moderate',
        lastAssessment: new Date('2025-01-25'),
        nextReview: new Date('2025-04-25'),
        categories: {
          'chronic-disease': { score: 15, trend: 'stable', factors: ['Family history of diabetes'] },
          'acute-care': { score: 25, trend: 'improving', factors: ['Occasional migraines'] },
          'preventive': { score: 45, trend: 'needs-attention', factors: ['Overdue mammogram', 'Pap smear due'] },
          'behavioral': { score: 35, trend: 'concerning', factors: ['Work stress', 'Sleep issues'] },
          'pharmacy': { score: 10, trend: 'excellent', factors: ['Good medication adherence'] }
        },
        predictions: {
          hospitalizationRisk: { probability: 8, timeframe: '12 months', confidence: 94 },
          costProjection: { amount: 3200, period: 'annual', confidence: 89 },
          interventionOpportunity: 'Moderate - Stress management and preventive care scheduling'
        },
        medicalHistory: {
          conditions: ['Migraines', 'Anxiety'],
          medications: ['Sumatriptan PRN', 'Sertraline'],
          allergies: ['None known'],
          procedures: ['None recent']
        },
        socialDeterminants: {
          smoking: 'Never',
          alcohol: 'Social',
          exercise: 'Moderate',
          diet: 'Good',
          income: 'Upper middle',
          education: 'College',
          transportation: 'Available'
        }
      },
      {
        id: 'RP-003',
        patientId: 'P-789012',
        patientName: 'Ahmed Al-Hassan',
        age: 67,
        gender: 'Male',
        overallRiskScore: 89,
        riskLevel: 'critical',
        lastAssessment: new Date('2025-01-29'),
        nextReview: new Date('2025-02-05'),
        categories: {
          'chronic-disease': { score: 95, trend: 'worsening', factors: ['COPD', 'Heart failure', 'Diabetes'] },
          'acute-care': { score: 85, trend: 'concerning', factors: ['Recent hospitalizations', 'ER visits'] },
          'preventive': { score: 70, trend: 'poor', factors: ['Multiple missed appointments'] },
          'behavioral': { score: 40, trend: 'stable', factors: ['Depression'] },
          'pharmacy': { score: 80, trend: 'critical', factors: ['Non-adherence', 'Complex regimen'] }
        },
        predictions: {
          hospitalizationRisk: { probability: 78, timeframe: '3 months', confidence: 91 },
          costProjection: { amount: 45000, period: 'annual', confidence: 88 },
          interventionOpportunity: 'Critical - Immediate care management and medication adherence program'
        },
        medicalHistory: {
          conditions: ['COPD', 'CHF', 'Type 2 Diabetes', 'Depression'],
          medications: ['Albuterol', 'Furosemide', 'Insulin', 'Sertraline', 'Metformin'],
          allergies: ['Sulfa drugs'],
          procedures: ['Cardiac stent (2024)', 'Multiple hospitalizations']
        },
        socialDeterminants: {
          smoking: 'Current smoker',
          alcohol: 'None',
          exercise: 'Unable',
          diet: 'Poor',
          income: 'Low',
          education: 'Elementary',
          transportation: 'Limited'
        }
      }
    ]);

    // Mock predictive models
    setPredictiveModels([
      {
        id: 'PM-001',
        name: 'Chronic Disease Progression Model',
        type: 'regression',
        accuracy: 94.2,
        lastTrained: new Date('2025-01-15'),
        features: ['Age', 'BMI', 'HbA1c', 'Blood pressure', 'Medication adherence', 'Social factors'],
        predictions: 'Hospital readmission within 30 days',
        performance: {
          precision: 92.1,
          recall: 89.5,
          f1Score: 90.8,
          auc: 94.2
        }
      },
      {
        id: 'PM-002',
        name: 'Emergency Care Predictor',
        type: 'classification',
        accuracy: 87.6,
        lastTrained: new Date('2025-01-20'),
        features: ['Previous ER visits', 'Chronic conditions', 'Medication count', 'Age', 'Social determinants'],
        predictions: 'Emergency department utilization risk',
        performance: {
          precision: 85.3,
          recall: 88.9,
          f1Score: 87.1,
          auc: 87.6
        }
      },
      {
        id: 'PM-003',
        name: 'Cost Prediction Engine',
        type: 'ensemble',
        accuracy: 91.8,
        lastTrained: new Date('2025-01-25'),
        features: ['Historical costs', 'Risk scores', 'Utilization patterns', 'Demographic factors'],
        predictions: 'Annual healthcare cost estimation',
        performance: {
          precision: 90.2,
          recall: 92.1,
          f1Score: 91.1,
          auc: 91.8
        }
      }
    ]);

    // Mock risk factors
    setRiskFactors([
      {
        category: 'Clinical',
        factors: [
          { name: 'Diabetes', impact: 'High', prevalence: 12.3, coefficient: 2.4 },
          { name: 'Hypertension', impact: 'High', prevalence: 24.1, coefficient: 1.8 },
          { name: 'COPD', impact: 'Critical', prevalence: 6.2, coefficient: 3.2 },
          { name: 'Heart Disease', impact: 'Critical', prevalence: 8.9, coefficient: 2.9 }
        ]
      },
      {
        category: 'Behavioral',
        factors: [
          { name: 'Smoking', impact: 'High', prevalence: 18.7, coefficient: 2.1 },
          { name: 'Obesity', impact: 'High', prevalence: 31.2, coefficient: 1.6 },
          { name: 'Sedentary lifestyle', impact: 'Moderate', prevalence: 45.3, coefficient: 1.3 },
          { name: 'Poor diet', impact: 'Moderate', prevalence: 38.9, coefficient: 1.4 }
        ]
      },
      {
        category: 'Social',
        factors: [
          { name: 'Low income', impact: 'High', prevalence: 15.2, coefficient: 1.9 },
          { name: 'Limited transportation', impact: 'Moderate', prevalence: 8.7, coefficient: 1.5 },
          { name: 'Low health literacy', impact: 'High', prevalence: 22.1, coefficient: 1.7 },
          { name: 'Social isolation', impact: 'Moderate', prevalence: 12.4, coefficient: 1.4 }
        ]
      }
    ]);

    // Mock assessment history
    setAssessmentHistory([
      {
        id: 'AH-001',
        date: new Date('2025-01-29'),
        type: 'Automated Assessment',
        patientsAssessed: 1247,
        avgRiskScore: 34.2,
        highRiskIdentified: 89,
        interventionsTriggered: 156,
        processingTime: '2.3 hours'
      },
      {
        id: 'AH-002',
        date: new Date('2025-01-28'),
        type: 'Scheduled Review',
        patientsAssessed: 892,
        avgRiskScore: 36.8,
        highRiskIdentified: 67,
        interventionsTriggered: 134,
        processingTime: '1.8 hours'
      }
    ]);
  };

  const getRiskLevelInfo = (score) => {
    if (score <= 25) return riskLevels.low;
    if (score <= 50) return riskLevels.moderate;
    if (score <= 75) return riskLevels.high;
    return riskLevels.critical;
  };

  const getRiskTrendIcon = (trend) => {
    const icons = {
      improving: '📈',
      stable: '➡️',
      concerning: '📊',
      worsening: '📉',
      increasing: '⬆️',
      'needs-attention': '⚠️',
      excellent: '✅',
      poor: '❌',
      critical: '🚨'
    };
    return icons[trend] || '➡️';
  };

  const filteredProfiles = riskProfiles.filter(profile => {
    const matchesCategory = filterCategory === 'all' || profile.riskLevel === filterCategory;
    const matchesSearch = profile.patientName.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         profile.patientId.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const RiskProfileModal = ({ profile, onClose }) => {
    if (!profile) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95 }}
          className="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-y-auto"
        >
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Risk Assessment Detail</h2>
                <p className="text-sm text-gray-500">{profile.patientName} ({profile.patientId})</p>
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
            {/* Overall Risk Summary */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-4 border border-blue-200">
                <h3 className="text-sm font-medium text-gray-900 mb-2">Overall Risk Score</h3>
                <div className="flex items-center space-x-2">
                  <div className="text-3xl font-bold text-gray-900">{profile.overallRiskScore}</div>
                  <div className="flex-1">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${getRiskLevelInfo(profile.overallRiskScore).color.replace('text-', 'bg-')}`}
                        style={{ width: `${profile.overallRiskScore}%` }}
                      ></div>
                    </div>
                    <span className={`text-xs font-medium mt-1 ${getRiskLevelInfo(profile.overallRiskScore).color}`}>
                      {getRiskLevelInfo(profile.overallRiskScore).name}
                    </span>
                  </div>
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">Demographics</h3>
                <div className="space-y-1 text-sm">
                  <div>Age: {profile.age}</div>
                  <div>Gender: {profile.gender}</div>
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">Assessment Dates</h3>
                <div className="space-y-1 text-sm">
                  <div>Last: {profile.lastAssessment.toLocaleDateString()}</div>
                  <div>Next: {profile.nextReview.toLocaleDateString()}</div>
                </div>
              </div>
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="text-sm font-medium text-gray-900 mb-2">Predictions</h3>
                <div className="space-y-1 text-sm">
                  <div>Hospitalization: {profile.predictions.hospitalizationRisk.probability}%</div>
                  <div>Cost: ${profile.predictions.costProjection.amount.toLocaleString()}</div>
                </div>
              </div>
            </div>

            {/* Risk Categories Breakdown */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Categories Analysis</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(profile.categories).map(([categoryKey, categoryData]) => {
                  const categoryInfo = riskCategories[categoryKey];
                  return (
                    <div key={categoryKey} className="bg-white border border-gray-200 rounded-lg p-4">
                      <div className="flex items-center space-x-3 mb-3">
                        <span className="text-2xl">{categoryInfo.icon}</span>
                        <div>
                          <h4 className="text-sm font-semibold text-gray-900">{categoryInfo.name}</h4>
                          <p className="text-xs text-gray-600">{categoryInfo.description}</p>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-600">Risk Score</span>
                          <div className="flex items-center space-x-2">
                            <span className="text-sm font-medium">{categoryData.score}</span>
                            <span className="text-sm">{getRiskTrendIcon(categoryData.trend)}</span>
                          </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${getRiskLevelInfo(categoryData.score).color.replace('text-', 'bg-')}`}
                            style={{ width: `${categoryData.score}%` }}
                          ></div>
                        </div>
                        <div className="space-y-1">
                          {categoryData.factors.map((factor, idx) => (
                            <div key={idx} className="text-xs text-gray-600">
                              • {factor}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Predictive Analytics */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Predictive Insights</h3>
                <div className="space-y-4">
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <h4 className="text-sm font-semibold text-red-900 mb-2">Hospitalization Risk</h4>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-red-700">
                        {profile.predictions.hospitalizationRisk.probability}% probability
                      </span>
                      <span className="text-xs text-red-600">
                        Confidence: {profile.predictions.hospitalizationRisk.confidence}%
                      </span>
                    </div>
                    <div className="w-full bg-red-100 rounded-full h-2">
                      <div 
                        className="bg-red-600 h-2 rounded-full"
                        style={{ width: `${profile.predictions.hospitalizationRisk.probability}%` }}
                      ></div>
                    </div>
                    <p className="text-xs text-red-700 mt-2">
                      Within {profile.predictions.hospitalizationRisk.timeframe}
                    </p>
                  </div>
                  
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h4 className="text-sm font-semibold text-blue-900 mb-2">Cost Projection</h4>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-blue-700">
                        ${profile.predictions.costProjection.amount.toLocaleString()} {profile.predictions.costProjection.period}
                      </span>
                      <span className="text-xs text-blue-600">
                        Confidence: {profile.predictions.costProjection.confidence}%
                      </span>
                    </div>
                    <div className="w-full bg-blue-100 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${(profile.predictions.costProjection.amount / 50000) * 100}%` }}
                      ></div>
                    </div>
                  </div>

                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <h4 className="text-sm font-semibold text-green-900 mb-2">Intervention Opportunity</h4>
                    <p className="text-sm text-green-700">{profile.predictions.interventionOpportunity}</p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Medical History</h3>
                <div className="space-y-3">
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-1">Conditions</h4>
                    <div className="flex flex-wrap gap-1">
                      {profile.medicalHistory.conditions.map((condition, idx) => (
                        <span key={idx} className="px-2 py-1 text-xs bg-red-100 text-red-800 rounded-full">
                          {condition}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-1">Medications</h4>
                    <div className="flex flex-wrap gap-1">
                      {profile.medicalHistory.medications.map((medication, idx) => (
                        <span key={idx} className="px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded-full">
                          {medication}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="text-sm font-medium text-gray-900 mb-1">Allergies</h4>
                    <div className="flex flex-wrap gap-1">
                      {profile.medicalHistory.allergies.map((allergy, idx) => (
                        <span key={idx} className="px-2 py-1 text-xs bg-yellow-100 text-yellow-800 rounded-full">
                          {allergy}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Social Determinants */}
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Social Determinants of Health</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {Object.entries(profile.socialDeterminants).map(([key, value]) => (
                  <div key={key} className="bg-gray-50 rounded-lg p-3">
                    <h4 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-1">
                      {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                    </h4>
                    <p className="text-sm font-medium text-gray-900">{value}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="flex space-x-3 pt-4 border-t border-gray-200">
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                Update Assessment
              </button>
              <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                Create Care Plan
              </button>
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                Schedule Follow-up
              </button>
              <button className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors">
                Export Report
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    );
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Risk Assessment Engine</h1>
        <p className="text-gray-600">
          AI-powered predictive analytics combining medical data with insurance risk models
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'overview', name: 'Risk Overview', icon: '📊' },
              { id: 'profiles', name: 'Patient Profiles', icon: '👥' },
              { id: 'models', name: 'Predictive Models', icon: '🤖' },
              { id: 'factors', name: 'Risk Factors', icon: '⚠️' },
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
        {/* Risk Overview */}
        {activeTab === 'overview' && (
          <motion.div
            key="overview"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {/* Risk Level Distribution */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {Object.entries(riskLevels).map(([level, info]) => {
                const count = riskProfiles.filter(p => p.riskLevel === level).length;
                return (
                  <div key={level} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="flex items-center">
                      <div className={`p-3 rounded-lg ${info.bgColor}`}>
                        <span className="text-2xl">
                          {level === 'low' ? '🟢' : level === 'moderate' ? '🟡' : level === 'high' ? '🟠' : '🔴'}
                        </span>
                      </div>
                      <div className="ml-4">
                        <p className="text-sm font-medium text-gray-600">{info.name}</p>
                        <p className="text-2xl font-bold text-gray-900">{count}</p>
                        <p className="text-xs text-gray-500">Score: {info.range}</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* High Risk Patients Alert */}
            <div className="bg-gradient-to-r from-red-50 to-orange-50 border border-red-200 rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-4">
                <span className="text-3xl">🚨</span>
                <div>
                  <h3 className="text-lg font-semibold text-red-900">High Risk Patients Requiring Immediate Attention</h3>
                  <p className="text-sm text-red-700">Patients with critical risk scores need immediate care management intervention</p>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {riskProfiles.filter(p => p.riskLevel === 'critical' || p.riskLevel === 'high').slice(0, 3).map((profile) => (
                  <div key={profile.id} className="bg-white border border-red-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="text-sm font-semibold text-gray-900">{profile.patientName}</h4>
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getRiskLevelInfo(profile.overallRiskScore).bgColor} ${getRiskLevelInfo(profile.overallRiskScore).color}`}>
                        {profile.overallRiskScore}
                      </span>
                    </div>
                    <p className="text-xs text-gray-600 mb-2">{profile.patientId} • Age {profile.age}</p>
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-600">Hospitalization Risk:</span>
                        <span className="font-medium text-red-600">{profile.predictions.hospitalizationRisk.probability}%</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-600">Projected Cost:</span>
                        <span className="font-medium text-gray-900">${profile.predictions.costProjection.amount.toLocaleString()}</span>
                      </div>
                    </div>
                    <button
                      onClick={() => setSelectedProfile(profile)}
                      className="w-full mt-3 px-3 py-1 text-xs bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                    >
                      View Details
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Assessments */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Recent Assessment Activity</h3>
              </div>
              <div className="divide-y divide-gray-200">
                {assessmentHistory.map((assessment) => (
                  <div key={assessment.id} className="p-6">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h4 className="text-sm font-semibold text-gray-900">{assessment.type}</h4>
                        <p className="text-xs text-gray-500">{assessment.date.toLocaleString()}</p>
                      </div>
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                        {assessment.processingTime}
                      </span>
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="text-gray-600">Patients Assessed:</span>
                        <span className="ml-2 font-medium text-gray-900">{assessment.patientsAssessed}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Avg Risk Score:</span>
                        <span className="ml-2 font-medium text-gray-900">{assessment.avgRiskScore}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">High Risk ID'd:</span>
                        <span className="ml-2 font-medium text-red-600">{assessment.highRiskIdentified}</span>
                      </div>
                      <div>
                        <span className="text-gray-600">Interventions:</span>
                        <span className="ml-2 font-medium text-green-600">{assessment.interventionsTriggered}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        )}

        {/* Patient Profiles */}
        {activeTab === 'profiles' && (
          <motion.div
            key="profiles"
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
                    value={filterCategory}
                    onChange={(e) => setFilterCategory(e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="all">All Risk Levels</option>
                    {Object.entries(riskLevels).map(([level, info]) => (
                      <option key={level} value={level}>{info.name}</option>
                    ))}
                  </select>
                </div>
                <div className="flex items-center space-x-4">
                  <input
                    type="text"
                    placeholder="Search patients..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>

            {/* Patient Profiles Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredProfiles.map((profile) => (
                <div key={profile.id} className="bg-white rounded-lg shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{profile.patientName}</h3>
                        <p className="text-sm text-gray-600">{profile.patientId} • Age {profile.age} • {profile.gender}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-gray-900">{profile.overallRiskScore}</div>
                        <span className={`text-xs font-medium ${getRiskLevelInfo(profile.overallRiskScore).color}`}>
                          {getRiskLevelInfo(profile.overallRiskScore).name}
                        </span>
                      </div>
                    </div>

                    <div className="space-y-3">
                      {Object.entries(profile.categories).slice(0, 3).map(([categoryKey, categoryData]) => {
                        const categoryInfo = riskCategories[categoryKey];
                        return (
                          <div key={categoryKey} className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <span className="text-sm">{categoryInfo.icon}</span>
                              <span className="text-xs text-gray-600">{categoryInfo.name}</span>
                            </div>
                            <div className="flex items-center space-x-2">
                              <div className="w-12 bg-gray-200 rounded-full h-1">
                                <div 
                                  className={`h-1 rounded-full ${getRiskLevelInfo(categoryData.score).color.replace('text-', 'bg-')}`}
                                  style={{ width: `${categoryData.score}%` }}
                                ></div>
                              </div>
                              <span className="text-xs font-medium text-gray-900">{categoryData.score}</span>
                              <span className="text-xs">{getRiskTrendIcon(categoryData.trend)}</span>
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="flex justify-between text-xs text-gray-600 mb-2">
                        <span>Next Review:</span>
                        <span>{profile.nextReview.toLocaleDateString()}</span>
                      </div>
                      <button
                        onClick={() => setSelectedProfile(profile)}
                        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                      >
                        View Full Assessment
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Predictive Models */}
        {activeTab === 'models' && (
          <motion.div
            key="models"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
              {predictiveModels.map((model) => (
                <div key={model.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">{model.name}</h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                      model.type === 'regression' ? 'bg-blue-100 text-blue-800' :
                      model.type === 'classification' ? 'bg-green-100 text-green-800' :
                      'bg-purple-100 text-purple-800'
                    }`}>
                      {model.type}
                    </span>
                  </div>

                  <div className="space-y-3 mb-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-600">Accuracy</span>
                        <span className="font-medium text-gray-900">{model.accuracy}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-600 h-2 rounded-full"
                          style={{ width: `${model.accuracy}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="text-sm">
                      <span className="text-gray-600">Predicts:</span>
                      <p className="font-medium text-gray-900 mt-1">{model.predictions}</p>
                    </div>

                    <div className="text-sm">
                      <span className="text-gray-600">Last Trained:</span>
                      <p className="font-medium text-gray-900">{model.lastTrained.toLocaleDateString()}</p>
                    </div>
                  </div>

                  <div className="border-t border-gray-200 pt-4">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Performance Metrics</h4>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Precision:</span>
                        <span className="font-medium">{model.performance.precision}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Recall:</span>
                        <span className="font-medium">{model.performance.recall}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">F1-Score:</span>
                        <span className="font-medium">{model.performance.f1Score}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">AUC:</span>
                        <span className="font-medium">{model.performance.auc}%</span>
                      </div>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <h4 className="text-sm font-medium text-gray-900 mb-2">Key Features</h4>
                    <div className="flex flex-wrap gap-1">
                      {model.features.slice(0, 4).map((feature, idx) => (
                        <span key={idx} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full">
                          {feature}
                        </span>
                      ))}
                      {model.features.length > 4 && (
                        <span className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded-full">
                          +{model.features.length - 4} more
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="mt-4 flex space-x-2">
                    <button className="flex-1 px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200 transition-colors">
                      View Details
                    </button>
                    <button className="flex-1 px-3 py-1 text-xs bg-green-100 text-green-700 rounded hover:bg-green-200 transition-colors">
                      Retrain Model
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Risk Factors */}
        {activeTab === 'factors' && (
          <motion.div
            key="factors"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="space-y-6"
          >
            {riskFactors.map((category) => (
              <div key={category.category} className="bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">{category.category} Risk Factors</h3>
                </div>
                <div className="p-6">
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead>
                        <tr className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          <th className="pb-3">Risk Factor</th>
                          <th className="pb-3">Impact Level</th>
                          <th className="pb-3">Prevalence</th>
                          <th className="pb-3">Model Coefficient</th>
                          <th className="pb-3">Visual</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {category.factors.map((factor, idx) => (
                          <tr key={idx}>
                            <td className="py-3 text-sm font-medium text-gray-900">{factor.name}</td>
                            <td className="py-3">
                              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                factor.impact === 'Critical' ? 'bg-red-100 text-red-800' :
                                factor.impact === 'High' ? 'bg-orange-100 text-orange-800' :
                                'bg-yellow-100 text-yellow-800'
                              }`}>
                                {factor.impact}
                              </span>
                            </td>
                            <td className="py-3 text-sm text-gray-600">{factor.prevalence}%</td>
                            <td className="py-3 text-sm font-medium text-gray-900">{factor.coefficient}</td>
                            <td className="py-3">
                              <div className="w-16 bg-gray-200 rounded-full h-2">
                                <div 
                                  className={`h-2 rounded-full ${
                                    factor.impact === 'Critical' ? 'bg-red-600' :
                                    factor.impact === 'High' ? 'bg-orange-600' :
                                    'bg-yellow-600'
                                  }`}
                                  style={{ width: `${factor.prevalence}%` }}
                                ></div>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ))}
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
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Score Distribution</h3>
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">📊</div>
                  <p>Interactive risk distribution chart</p>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Prediction Accuracy Trends</h3>
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">📈</div>
                  <p>Model performance over time</p>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Impact Analysis</h3>
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">💰</div>
                  <p>Risk-based cost projections</p>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Intervention Effectiveness</h3>
                <div className="text-center py-8 text-gray-500">
                  <div className="text-4xl mb-2">🎯</div>
                  <p>Outcome tracking dashboard</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Risk Profile Detail Modal */}
      <AnimatePresence>
        {selectedProfile && (
          <RiskProfileModal 
            profile={selectedProfile} 
            onClose={() => setSelectedProfile(null)} 
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default RiskAssessmentEngine;
