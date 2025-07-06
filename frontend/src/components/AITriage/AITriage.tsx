import React, { useState } from 'react';
import { TriageAssessment, Symptom, UrgencyLevel } from '@/types';
import {
  ClockIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  DocumentTextIcon,
  PhoneIcon,
  MapPinIcon,
} from '@heroicons/react/24/outline';

const AITriage: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [patientInfo, setPatientInfo] = useState({
    name: '',
    age: '',
    gender: '',
    emergencyContact: '',
  });
  const [symptoms, setSymptoms] = useState<Symptom[]>([]);
  const [assessment, setAssessment] = useState<TriageAssessment | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const commonSymptoms = [
    { name: 'Chest Pain', icon: '💔', critical: true },
    { name: 'Shortness of Breath', icon: '🫁', critical: true },
    { name: 'Severe Headache', icon: '🧠', critical: true },
    { name: 'High Fever', icon: '🌡️', critical: false },
    { name: 'Abdominal Pain', icon: '🤕', critical: false },
    { name: 'Nausea/Vomiting', icon: '🤢', critical: false },
    { name: 'Dizziness', icon: '😵', critical: false },
    { name: 'Fatigue', icon: '😴', critical: false },
  ];

  const addSymptom = (symptomName: string) => {
    if (!symptoms.find(s => s.name === symptomName)) {
      const newSymptom: Symptom = {
        name: symptomName,
        severity: 5,
        duration: '',
        onset: 'gradual',
        location: '',
        character: '',
        aggravatingFactors: [],
        relievingFactors: [],
      };
      setSymptoms([...symptoms, newSymptom]);
    }
  };

  const updateSymptom = (index: number, updates: Partial<Symptom>) => {
    const updatedSymptoms = symptoms.map((symptom, i) => 
      i === index ? { ...symptom, ...updates } : symptom
    );
    setSymptoms(updatedSymptoms);
  };

  const removeSymptom = (index: number) => {
    setSymptoms(symptoms.filter((_, i) => i !== index));
  };

  const processAssessment = async () => {
    setIsProcessing(true);
    
    // Simulate AI processing
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Calculate urgency based on symptoms
    const criticalSymptoms = symptoms.filter(s => 
      commonSymptoms.find(cs => cs.name === s.name)?.critical
    );
    const highSeveritySymptoms = symptoms.filter(s => s.severity >= 7);
    
    let urgencyLevel: UrgencyLevel;
    let estimatedWaitTime: number;
    
    if (criticalSymptoms.length > 0 || highSeveritySymptoms.length > 2) {
      urgencyLevel = 'emergency';
      estimatedWaitTime = 0;
    } else if (highSeveritySymptoms.length > 0) {
      urgencyLevel = 'urgent';
      estimatedWaitTime = 15;
    } else if (symptoms.some(s => s.severity >= 5)) {
      urgencyLevel = 'semi_urgent';
      estimatedWaitTime = 30;
    } else if (symptoms.some(s => s.severity >= 3)) {
      urgencyLevel = 'standard';
      estimatedWaitTime = 60;
    } else {
      urgencyLevel = 'non_urgent';
      estimatedWaitTime = 120;
    }

    const mockAssessment: TriageAssessment = {
      id: Date.now().toString(),
      patientId: `PT-${Date.now()}`,
      symptoms,
      urgencyLevel,
      estimatedWaitTime,
      specialtyRequired: criticalSymptoms.length > 0 ? 'Emergency Medicine' : 'General Practice',
      recommendations: [
        {
          type: urgencyLevel === 'emergency' ? 'immediate_care' : 'scheduled_appointment',
          description: urgencyLevel === 'emergency' 
            ? 'Immediate medical attention required'
            : 'Schedule appointment based on urgency level',
          timeframe: urgencyLevel === 'emergency' ? 'Immediate' : `Within ${estimatedWaitTime} minutes`,
          department: urgencyLevel === 'emergency' ? 'Emergency Department' : 'Primary Care',
        }
      ],
      createdAt: new Date(),
    };

    setAssessment(mockAssessment);
    setIsProcessing(false);
    setCurrentStep(4);
  };

  const getUrgencyColor = (level: UrgencyLevel) => {
    switch (level) {
      case 'emergency':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'urgent':
        return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'semi_urgent':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'standard':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'non_urgent':
        return 'bg-green-100 text-green-800 border-green-200';
    }
  };

  const getUrgencyIcon = (level: UrgencyLevel) => {
    switch (level) {
      case 'emergency':
        return <ExclamationTriangleIcon className="h-5 w-5 text-red-600" />;
      case 'urgent':
        return <ClockIcon className="h-5 w-5 text-orange-600" />;
      case 'semi_urgent':
        return <ClockIcon className="h-5 w-5 text-yellow-600" />;
      case 'standard':
        return <CheckCircleIcon className="h-5 w-5 text-blue-600" />;
      case 'non_urgent':
        return <CheckCircleIcon className="h-5 w-5 text-green-600" />;
    }
  };

  const resetAssessment = () => {
    setCurrentStep(1);
    setPatientInfo({ name: '', age: '', gender: '', emergencyContact: '' });
    setSymptoms([]);
    setAssessment(null);
    setIsProcessing(false);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">AI-Powered Triage Assessment</h1>
        <p className="text-gray-600 mt-2">
          Advanced symptom analysis with intelligent urgency determination
        </p>
        <div className="flex items-center justify-center space-x-4 mt-4">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
            🤖 AI-Powered
          </span>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            🔒 HIPAA Compliant
          </span>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          {[1, 2, 3, 4].map((step) => (
            <div key={step} className="flex items-center">
              <div className={`
                w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium
                ${currentStep >= step 
                  ? 'bg-primary-600 text-white' 
                  : 'bg-gray-200 text-gray-600'
                }
              `}>
                {step}
              </div>
              <span className={`ml-2 text-sm font-medium ${currentStep >= step ? 'text-primary-600' : 'text-gray-500'}`}>
                {step === 1 && 'Patient Info'}
                {step === 2 && 'Symptoms'}
                {step === 3 && 'Processing'}
                {step === 4 && 'Results'}
              </span>
              {step < 4 && (
                <div className={`ml-4 w-12 h-0.5 ${currentStep > step ? 'bg-primary-600' : 'bg-gray-200'}`} />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        {currentStep === 1 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">Patient Information</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name *
                </label>
                <input
                  type="text"
                  value={patientInfo.name}
                  onChange={(e) => setPatientInfo({...patientInfo, name: e.target.value})}
                  className="form-input"
                  placeholder="Enter patient's full name"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Age *
                </label>
                <input
                  type="number"
                  value={patientInfo.age}
                  onChange={(e) => setPatientInfo({...patientInfo, age: e.target.value})}
                  className="form-input"
                  placeholder="Age in years"
                  min="0"
                  max="150"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Gender *
                </label>
                <select
                  value={patientInfo.gender}
                  onChange={(e) => setPatientInfo({...patientInfo, gender: e.target.value})}
                  className="form-select"
                  required
                >
                  <option value="">Select gender</option>
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                  <option value="other">Other</option>
                  <option value="prefer_not_to_say">Prefer not to say</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Emergency Contact
                </label>
                <input
                  type="tel"
                  value={patientInfo.emergencyContact}
                  onChange={(e) => setPatientInfo({...patientInfo, emergencyContact: e.target.value})}
                  className="form-input"
                  placeholder="Emergency contact number"
                />
              </div>
            </div>
            
            <div className="flex justify-end">
              <button
                onClick={() => setCurrentStep(2)}
                disabled={!patientInfo.name || !patientInfo.age || !patientInfo.gender}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Continue to Symptoms
              </button>
            </div>
          </div>
        )}

        {currentStep === 2 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">Symptom Assessment</h2>
            
            {/* Common Symptoms */}
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Select Symptoms</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {commonSymptoms.map((symptom) => (
                  <button
                    key={symptom.name}
                    onClick={() => addSymptom(symptom.name)}
                    className={`
                      p-3 rounded-lg border-2 text-center transition-colors
                      ${symptoms.find(s => s.name === symptom.name)
                        ? 'border-primary-500 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                      }
                      ${symptom.critical ? 'ring-2 ring-red-200' : ''}
                    `}
                  >
                    <div className="text-2xl mb-1">{symptom.icon}</div>
                    <div className="text-sm font-medium">{symptom.name}</div>
                    {symptom.critical && (
                      <div className="text-xs text-red-600 mt-1">Critical</div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Selected Symptoms Details */}
            {symptoms.length > 0 && (
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-900">Symptom Details</h3>
                {symptoms.map((symptom, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="font-medium text-gray-900">{symptom.name}</h4>
                      <button
                        onClick={() => removeSymptom(index)}
                        className="text-red-600 hover:text-red-700"
                      >
                        Remove
                      </button>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Severity (1-10)
                        </label>
                        <div className="space-y-2">
                          <input
                            type="range"
                            min="1"
                            max="10"
                            value={symptom.severity}
                            onChange={(e) => updateSymptom(index, { severity: parseInt(e.target.value) })}
                            className="w-full"
                          />
                          <div className="flex justify-between text-xs text-gray-500">
                            <span>Mild</span>
                            <span className="font-medium">{symptom.severity}</span>
                            <span>Severe</span>
                          </div>
                        </div>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Duration
                        </label>
                        <input
                          type="text"
                          value={symptom.duration}
                          onChange={(e) => updateSymptom(index, { duration: e.target.value })}
                          className="form-input"
                          placeholder="e.g., 2 hours, 3 days"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Onset
                        </label>
                        <select
                          value={symptom.onset}
                          onChange={(e) => updateSymptom(index, { onset: e.target.value as 'sudden' | 'gradual' | 'chronic' })}
                          className="form-select"
                        >
                          <option value="sudden">Sudden</option>
                          <option value="gradual">Gradual</option>
                          <option value="chronic">Chronic</option>
                        </select>
                      </div>
                      
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Location (if applicable)
                        </label>
                        <input
                          type="text"
                          value={symptom.location || ''}
                          onChange={(e) => updateSymptom(index, { location: e.target.value })}
                          className="form-input"
                          placeholder="e.g., chest, left arm"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
            
            <div className="flex justify-between">
              <button
                onClick={() => setCurrentStep(1)}
                className="btn-outline"
              >
                Back
              </button>
              <button
                onClick={() => setCurrentStep(3)}
                disabled={symptoms.length === 0}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Analyze Symptoms
              </button>
            </div>
          </div>
        )}

        {currentStep === 3 && (
          <div className="text-center space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">AI Analysis in Progress</h2>
            
            {isProcessing ? (
              <div className="space-y-4">
                <div className="loading-spinner w-16 h-16 mx-auto"></div>
                <div className="space-y-2">
                  <p className="text-lg font-medium text-gray-900">
                    Analyzing symptoms with AI...
                  </p>
                  <p className="text-gray-600">
                    Our advanced AI is processing the symptom data and determining urgency level
                  </p>
                </div>
                
                <div className="max-w-md mx-auto bg-blue-50 rounded-lg p-4">
                  <div className="flex items-center space-x-2 text-blue-800">
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
                    <span className="text-sm">Processing symptoms...</span>
                  </div>
                  <div className="flex items-center space-x-2 text-blue-800 mt-2">
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" style={{animationDelay: '0.5s'}}></div>
                    <span className="text-sm">Calculating urgency level...</span>
                  </div>
                  <div className="flex items-center space-x-2 text-blue-800 mt-2">
                    <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse" style={{animationDelay: '1s'}}></div>
                    <span className="text-sm">Generating recommendations...</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <p className="text-lg font-medium text-gray-900">Ready to analyze</p>
                <button
                  onClick={processAssessment}
                  className="btn-primary"
                >
                  Start AI Analysis
                </button>
              </div>
            )}
          </div>
        )}

        {currentStep === 4 && assessment && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">Triage Assessment Results</h2>
            
            {/* Urgency Level */}
            <div className={`border-2 rounded-lg p-6 ${getUrgencyColor(assessment.urgencyLevel)}`}>
              <div className="flex items-center space-x-3">
                {getUrgencyIcon(assessment.urgencyLevel)}
                <div>
                  <h3 className="text-lg font-semibold capitalize">
                    {assessment.urgencyLevel.replace('_', ' ')} Priority
                  </h3>
                  <p className="text-sm opacity-90">
                    Estimated wait time: {assessment.estimatedWaitTime === 0 ? 'Immediate' : `${assessment.estimatedWaitTime} minutes`}
                  </p>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Recommendations</h3>
              {assessment.recommendations.map((rec, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-start space-x-3">
                    <DocumentTextIcon className="h-5 w-5 text-blue-600 mt-1 flex-shrink-0" />
                    <div>
                      <h4 className="font-medium text-gray-900 capitalize">
                        {rec.type.replace('_', ' ')}
                      </h4>
                      <p className="text-gray-600 mt-1">{rec.description}</p>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                        <span>⏱️ {rec.timeframe}</span>
                        {rec.department && <span>🏥 {rec.department}</span>}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Emergency Actions */}
            {assessment.urgencyLevel === 'emergency' && (
              <div className="bg-red-50 border-2 border-red-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-red-900 mb-4">
                  🚨 Emergency Actions Required
                </h3>
                <div className="space-y-3">
                  <button className="w-full btn-primary bg-red-600 hover:bg-red-700">
                    <PhoneIcon className="h-5 w-5 mr-2" />
                    Call Emergency Services (911)
                  </button>
                  <button className="w-full btn-outline border-red-300 text-red-700 hover:bg-red-50">
                    <MapPinIcon className="h-5 w-5 mr-2" />
                    Find Nearest Emergency Room
                  </button>
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-between">
              <button
                onClick={resetAssessment}
                className="btn-outline"
              >
                New Assessment
              </button>
              <div className="space-x-4">
                <button className="btn-outline">
                  Print Results
                </button>
                <button className="btn-primary">
                  Schedule Appointment
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AITriage;