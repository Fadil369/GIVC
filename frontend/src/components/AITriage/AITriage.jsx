import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const AITriage = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [patientData, setPatientData] = useState({
    name: '',
    age: '',
    gender: '',
    emergencyContact: '',
    chiefComplaint: ''
  });
  const [symptoms, setSymptoms] = useState([]);
  const [assessment, setAssessment] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [triageHistory, setTriageHistory] = useState([]);

  const urgencyLevels = {
    emergency: {
      color: 'bg-red-100 text-red-800 border-red-300',
      priority: 1,
      waitTime: 'Immediate',
      description: 'Life-threatening condition requiring immediate attention'
    },
    urgent: {
      color: 'bg-orange-100 text-orange-800 border-orange-300',
      priority: 2,
      waitTime: '< 15 min',
      description: 'Serious condition requiring prompt medical attention'
    },
    semi_urgent: {
      color: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      priority: 3,
      waitTime: '< 30 min',
      description: 'Urgent but stable condition'
    },
    standard: {
      color: 'bg-blue-100 text-blue-800 border-blue-300',
      priority: 4,
      waitTime: '< 60 min',
      description: 'Non-urgent condition requiring medical attention'
    },
    non_urgent: {
      color: 'bg-green-100 text-green-800 border-green-300',
      priority: 5,
      waitTime: '< 120 min',
      description: 'Routine care or consultation needed'
    }
  };

  const commonSymptoms = [
    { name: 'Chest Pain', category: 'cardiac', severity: 8 },
    { name: 'Shortness of Breath', category: 'respiratory', severity: 7 },
    { name: 'Severe Headache', category: 'neurological', severity: 6 },
    { name: 'Abdominal Pain', category: 'gastrointestinal', severity: 5 },
    { name: 'Fever', category: 'general', severity: 4 },
    { name: 'Nausea/Vomiting', category: 'gastrointestinal', severity: 3 },
    { name: 'Dizziness', category: 'neurological', severity: 3 },
    { name: 'Fatigue', category: 'general', severity: 2 },
    { name: 'Cough', category: 'respiratory', severity: 2 },
    { name: 'Joint Pain', category: 'musculoskeletal', severity: 2 }
  ];

  useEffect(() => {
    // Load triage history
    const mockHistory = [
      {
        id: 1,
        patientName: 'John Smith',
        timestamp: new Date('2024-01-15T14:30:00'),
        urgency: 'urgent',
        chiefComplaint: 'Chest pain and shortness of breath',
        disposition: 'Emergency Department'
      },
      {
        id: 2,
        patientName: 'Sarah Johnson',
        timestamp: new Date('2024-01-15T13:15:00'),
        urgency: 'standard',
        chiefComplaint: 'Mild fever and cough',
        disposition: 'Primary Care'
      }
    ];
    setTriageHistory(mockHistory);
  }, []);

  const steps = [
    'Patient Information',
    'Chief Complaint',
    'Symptom Assessment',
    'AI Analysis',
    'Triage Results'
  ];

  const addSymptom = (symptomName) => {
    const existingSymptom = symptoms.find(s => s.name === symptomName);
    if (!existingSymptom) {
      const symptomData = commonSymptoms.find(s => s.name === symptomName);
      const newSymptom = {
        id: Date.now(),
        name: symptomName,
        severity: symptomData?.severity || 5,
        duration: '',
        onset: 'gradual',
        location: '',
        character: '',
        aggravatingFactors: [],
        relievingFactors: []
      };
      setSymptoms([...symptoms, newSymptom]);
    }
  };

  const updateSymptom = (id, updates) => {
    setSymptoms(symptoms.map(symptom =>
      symptom.id === id ? { ...symptom, ...updates } : symptom
    ));
  };

  const removeSymptom = (id) => {
    setSymptoms(symptoms.filter(symptom => symptom.id !== id));
  };

  const performTriageAnalysis = () => {
    setIsProcessing(true);

    // Simulate AI analysis
    setTimeout(() => {
      const maxSeverity = Math.max(...symptoms.map(s => s.severity), 0);
      const hasEmergencyKeywords = patientData.chiefComplaint.toLowerCase().includes('chest pain') ||
        patientData.chiefComplaint.toLowerCase().includes('can\'t breathe') ||
        patientData.chiefComplaint.toLowerCase().includes('severe');

      let urgencyLevel;
      let estimatedWaitTime;
      let recommendations = [];

      if (maxSeverity >= 8 || hasEmergencyKeywords) {
        urgencyLevel = 'emergency';
        estimatedWaitTime = 0;
        recommendations = [
          { type: 'immediate_care', description: 'Direct to Emergency Department immediately', timeframe: 'Now' },
          { type: 'monitoring', description: 'Continuous vital signs monitoring', timeframe: 'Ongoing' }
        ];
      } else if (maxSeverity >= 6) {
        urgencyLevel = 'urgent';
        estimatedWaitTime = 15;
        recommendations = [
          { type: 'urgent_care', description: 'See physician within 15 minutes', timeframe: '< 15 min' },
          { type: 'diagnostic', description: 'Consider ECG and chest X-ray', timeframe: 'ASAP' }
        ];
      } else if (maxSeverity >= 4) {
        urgencyLevel = 'semi_urgent';
        estimatedWaitTime = 30;
        recommendations = [
          { type: 'standard_care', description: 'Schedule with available physician', timeframe: '< 30 min' }
        ];
      } else {
        urgencyLevel = 'standard';
        estimatedWaitTime = 60;
        recommendations = [
          { type: 'routine_care', description: 'Standard appointment scheduling', timeframe: '< 60 min' }
        ];
      }

      const newAssessment = {
        id: Date.now(),
        patientId: `P-${Date.now()}`,
        symptoms,
        urgencyLevel,
        estimatedWaitTime,
        recommendations,
        aiConfidence: 0.85 + Math.random() * 0.1,
        createdAt: new Date(),
        disposition: urgencyLevel === 'emergency' ? 'Emergency Department' :
          urgencyLevel === 'urgent' ? 'Urgent Care' : 'Primary Care'
      };

      setAssessment(newAssessment);
      setIsProcessing(false);
      setCurrentStep(4);
    }, 3000);
  };

  const resetTriage = () => {
    setCurrentStep(0);
    setPatientData({
      name: '',
      age: '',
      gender: '',
      emergencyContact: '',
      chiefComplaint: ''
    });
    setSymptoms([]);
    setAssessment(null);
    setIsProcessing(false);
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Triage System</h1>
        <p className="text-gray-600">
          Intelligent patient triage using AI-powered symptom analysis
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Main Triage Form */}
        <div className="lg:col-span-3">
          <div className="bg-white rounded-lg shadow-sm">
            {/* Progress Bar */}
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">
                  {steps[currentStep]}
                </h2>
                <span className="text-sm text-gray-500">
                  Step {currentStep + 1} of {steps.length}
                </span>
              </div>

              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
                />
              </div>
            </div>

            <div className="p-6">
              <AnimatePresence mode="wait">
                {/* Step 0: Patient Information */}
                {currentStep === 0 && (
                  <motion.div
                    key="patient-info"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-6"
                  >
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Patient Name *
                        </label>
                        <input
                          type="text"
                          value={patientData.name}
                          onChange={(e) => setPatientData({ ...patientData, name: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          placeholder="Enter patient name"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Age *
                        </label>
                        <input
                          type="number"
                          value={patientData.age}
                          onChange={(e) => setPatientData({ ...patientData, age: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          placeholder="Age"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Gender
                        </label>
                        <select
                          value={patientData.gender}
                          onChange={(e) => setPatientData({ ...patientData, gender: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        >
                          <option value="">Select gender</option>
                          <option value="male">Male</option>
                          <option value="female">Female</option>
                          <option value="other">Other</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Emergency Contact
                        </label>
                        <input
                          type="tel"
                          value={patientData.emergencyContact}
                          onChange={(e) => setPatientData({ ...patientData, emergencyContact: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                          placeholder="Phone number"
                        />
                      </div>
                    </div>
                  </motion.div>
                )}

                {/* Step 1: Chief Complaint */}
                {currentStep === 1 && (
                  <motion.div
                    key="chief-complaint"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-6"
                  >
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Chief Complaint *
                      </label>
                      <textarea
                        value={patientData.chiefComplaint}
                        onChange={(e) => setPatientData({ ...patientData, chiefComplaint: e.target.value })}
                        rows={4}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                        placeholder="Describe the main reason for the visit in the patient's own words..."
                      />
                    </div>

                    <div className="bg-blue-50 rounded-lg p-4">
                      <h4 className="font-medium text-blue-900 mb-2">Guidelines for Chief Complaint</h4>
                      <ul className="text-sm text-blue-800 space-y-1">
                        <li>• Use the patient's exact words when possible</li>
                        <li>• Include duration (e.g., "for 3 days")</li>
                        <li>• Note severity if mentioned (e.g., "severe pain")</li>
                        <li>• Keep it concise but descriptive</li>
                      </ul>
                    </div>
                  </motion.div>
                )}

                {/* Step 2: Symptom Assessment */}
                {currentStep === 2 && (
                  <motion.div
                    key="symptoms"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-6"
                  >
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Select Symptoms</h3>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                        {commonSymptoms.map((symptom) => (
                          <button
                            key={symptom.name}
                            onClick={() => addSymptom(symptom.name)}
                            className={`p-3 text-left rounded-lg border transition-colors ${symptoms.find(s => s.name === symptom.name)
                                ? 'bg-blue-100 border-blue-300 text-blue-800'
                                : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                              }`}
                          >
                            <div className="font-medium">{symptom.name}</div>
                            <div className="text-xs text-gray-600 capitalize">{symptom.category}</div>
                          </button>
                        ))}
                      </div>
                    </div>

                    {symptoms.length > 0 && (
                      <div>
                        <h4 className="text-md font-medium text-gray-900 mb-4">Selected Symptoms</h4>
                        <div className="space-y-4">
                          {symptoms.map((symptom) => (
                            <div key={symptom.id} className="bg-gray-50 rounded-lg p-4">
                              <div className="flex items-center justify-between mb-3">
                                <h5 className="font-medium text-gray-900">{symptom.name}</h5>
                                <button
                                  onClick={() => removeSymptom(symptom.id)}
                                  className="text-red-600 hover:text-red-800"
                                >
                                  ✕
                                </button>
                              </div>

                              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                  <label className="block text-xs font-medium text-gray-700 mb-1">
                                    Severity (1-10)
                                  </label>
                                  <input
                                    type="range"
                                    min="1"
                                    max="10"
                                    value={symptom.severity}
                                    onChange={(e) => updateSymptom(symptom.id, { severity: parseInt(e.target.value) })}
                                    className="w-full"
                                  />
                                  <div className="text-center text-sm text-gray-600">{symptom.severity}</div>
                                </div>

                                <div>
                                  <label className="block text-xs font-medium text-gray-700 mb-1">
                                    Duration
                                  </label>
                                  <input
                                    type="text"
                                    value={symptom.duration}
                                    onChange={(e) => updateSymptom(symptom.id, { duration: e.target.value })}
                                    className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                                    placeholder="e.g., 2 days"
                                  />
                                </div>

                                <div>
                                  <label className="block text-xs font-medium text-gray-700 mb-1">
                                    Onset
                                  </label>
                                  <select
                                    value={symptom.onset}
                                    onChange={(e) => updateSymptom(symptom.id, { onset: e.target.value })}
                                    className="w-full px-2 py-1 text-sm border border-gray-300 rounded"
                                  >
                                    <option value="sudden">Sudden</option>
                                    <option value="gradual">Gradual</option>
                                    <option value="chronic">Chronic</option>
                                  </select>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </motion.div>
                )}

                {/* Step 3: AI Analysis */}
                {currentStep === 3 && (
                  <motion.div
                    key="analysis"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="text-center py-12"
                  >
                    {isProcessing ? (
                      <div>
                        <div className="text-6xl mb-6">🤖</div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-4">
                          AI Analysis in Progress
                        </h3>
                        <p className="text-gray-600 mb-6">
                          Analyzing symptoms and determining triage level...
                        </p>
                        <div className="w-64 mx-auto bg-gray-200 rounded-full h-2">
                          <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '70%' }} />
                        </div>
                      </div>
                    ) : (
                      <div>
                        <div className="text-6xl mb-6">📊</div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-4">
                          Ready for AI Analysis
                        </h3>
                        <p className="text-gray-600 mb-6">
                          Review the information and start the AI triage analysis
                        </p>
                        <button
                          onClick={performTriageAnalysis}
                          className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                        >
                          Start AI Analysis
                        </button>
                      </div>
                    )}
                  </motion.div>
                )}

                {/* Step 4: Results */}
                {currentStep === 4 && assessment && (
                  <motion.div
                    key="results"
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    className="space-y-6"
                  >
                    <div className="text-center">
                      <div className="text-6xl mb-4">🏥</div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2">
                        Triage Assessment Complete
                      </h3>
                    </div>

                    <div className={`p-6 rounded-lg border-2 ${urgencyLevels[assessment.urgencyLevel].color}`}>
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h4 className="text-lg font-bold capitalize">
                            {assessment.urgencyLevel.replace('_', ' ')} Priority
                          </h4>
                          <p className="text-sm">
                            {urgencyLevels[assessment.urgencyLevel].description}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold">
                            Priority {urgencyLevels[assessment.urgencyLevel].priority}
                          </div>
                          <div className="text-sm">
                            Wait Time: {urgencyLevels[assessment.urgencyLevel].waitTime}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="bg-gray-50 rounded-lg p-4">
                        <h5 className="font-semibold text-gray-900 mb-3">Recommendations</h5>
                        <div className="space-y-2">
                          {assessment.recommendations.map((rec, idx) => (
                            <div key={idx} className="flex items-start space-x-2">
                              <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
                              <div>
                                <div className="font-medium text-gray-900">{rec.description}</div>
                                <div className="text-sm text-gray-600">{rec.timeframe}</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="bg-gray-50 rounded-lg p-4">
                        <h5 className="font-semibold text-gray-900 mb-3">Assessment Details</h5>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-gray-600">AI Confidence:</span>
                            <span className="font-medium">{Math.round(assessment.aiConfidence * 100)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Disposition:</span>
                            <span className="font-medium">{assessment.disposition}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-600">Assessment Time:</span>
                            <span className="font-medium">{assessment.createdAt.toLocaleTimeString()}</span>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="flex space-x-4">
                      <button
                        onClick={resetTriage}
                        className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        New Triage Assessment
                      </button>
                      <button className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                        Print Report
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Navigation Buttons */}
              {currentStep < 3 && (
                <div className="flex justify-between mt-8 pt-6 border-t border-gray-200">
                  <button
                    onClick={prevStep}
                    disabled={currentStep === 0}
                    className={`px-4 py-2 rounded-lg ${currentStep === 0
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                  >
                    Previous
                  </button>

                  <button
                    onClick={nextStep}
                    disabled={
                      (currentStep === 0 && (!patientData.name || !patientData.age)) ||
                      (currentStep === 1 && !patientData.chiefComplaint) ||
                      (currentStep === 2 && symptoms.length === 0)
                    }
                    className={`px-4 py-2 rounded-lg ${(currentStep === 0 && (!patientData.name || !patientData.age)) ||
                        (currentStep === 1 && !patientData.chiefComplaint) ||
                        (currentStep === 2 && symptoms.length === 0)
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                      }`}
                  >
                    Next
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar - Triage History */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm">
            <div className="px-4 py-3 border-b border-gray-200">
              <h3 className="font-semibold text-gray-900">Recent Assessments</h3>
            </div>

            <div className="p-4">
              <div className="space-y-4">
                {triageHistory.map((entry) => (
                  <div key={entry.id} className="border-l-4 border-blue-200 pl-4">
                    <div className="font-medium text-gray-900">{entry.patientName}</div>
                    <div className="text-sm text-gray-600">{entry.chiefComplaint}</div>
                    <div className="flex items-center justify-between mt-2">
                      <span className={`px-2 py-1 text-xs rounded-full ${urgencyLevels[entry.urgency].color}`}>
                        {entry.urgency}
                      </span>
                      <span className="text-xs text-gray-500">
                        {entry.timestamp.toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Quick Stats */}
          <div className="mt-6 bg-white rounded-lg shadow-sm p-4">
            <h4 className="font-semibold text-gray-900 mb-3">Today's Stats</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Assessments:</span>
                <span className="font-medium">12</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Emergency:</span>
                <span className="font-medium text-red-600">2</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Urgent:</span>
                <span className="font-medium text-orange-600">3</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Standard:</span>
                <span className="font-medium text-blue-600">7</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AITriage;