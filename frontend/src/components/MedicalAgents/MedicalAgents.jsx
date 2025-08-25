import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const MedicalAgents = () => {
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [activeAnalysis, setActiveAnalysis] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [inputData, setInputData] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const medicalAgents = [
    {
      id: 'radiology',
      name: 'Radiology AI',
      icon: '🩻',
      specialty: 'Medical Imaging',
      description: 'Advanced AI for analyzing X-rays, CT scans, MRIs, and other medical imaging',
      capabilities: [
        'X-ray analysis for fractures and pathologies',
        'CT scan interpretation and anomaly detection',
        'MRI analysis for soft tissue evaluation',
        'DICOM image processing and measurement',
        'Automated reporting and findings summary'
      ],
      accuracy: '94.2%',
      processingTime: '2-5 minutes',
      supportedFormats: ['DICOM', 'JPEG', 'PNG', 'TIFF'],
      color: 'bg-blue-100 text-blue-800 border-blue-300'
    },
    {
      id: 'pathology',
      name: 'Pathology AI',
      icon: '🔬',
      specialty: 'Digital Pathology',
      description: 'AI-powered microscopic analysis of tissue samples and cellular structures',
      capabilities: [
        'Cancer detection and classification',
        'Tissue morphology analysis',
        'Cell counting and characterization',
        'Biomarker identification',
        'Grade and stage assessment'
      ],
      accuracy: '96.8%',
      processingTime: '3-8 minutes',
      supportedFormats: ['WSI', 'TIFF', 'SVS', 'NDPI'],
      color: 'bg-green-100 text-green-800 border-green-300'
    },
    {
      id: 'cardiology',
      name: 'Cardiology AI',
      icon: '❤️',
      specialty: 'Cardiovascular Analysis',
      description: 'Specialized AI for ECG analysis, echocardiography, and cardiac imaging',
      capabilities: [
        'ECG rhythm analysis and arrhythmia detection',
        'Echocardiogram assessment',
        'Cardiac catheterization analysis',
        'Heart rate variability analysis',
        'Risk stratification and prediction'
      ],
      accuracy: '92.5%',
      processingTime: '1-3 minutes',
      supportedFormats: ['XML', 'PDF', 'DICOM', 'HL7'],
      color: 'bg-red-100 text-red-800 border-red-300'
    },
    {
      id: 'dermatology',
      name: 'Dermatology AI',
      icon: '🧴',
      specialty: 'Skin Analysis',
      description: 'AI dermatoscopy for skin lesion analysis and dermatological conditions',
      capabilities: [
        'Melanoma and skin cancer detection',
        'Lesion classification and assessment',
        'Dermatitis and eczema analysis',
        'Mole mapping and tracking',
        'Skin condition severity scoring'
      ],
      accuracy: '89.7%',
      processingTime: '30 seconds - 2 minutes',
      supportedFormats: ['JPEG', 'PNG', 'TIFF', 'BMP'],
      color: 'bg-orange-100 text-orange-800 border-orange-300'
    },
    {
      id: 'laboratory',
      name: 'Laboratory AI',
      icon: '🧪',
      specialty: 'Lab Data Analysis',
      description: 'Comprehensive analysis of laboratory test results and biomarkers',
      capabilities: [
        'Blood work interpretation',
        'Biochemistry panel analysis',
        'Hematology report evaluation',
        'Trend analysis and monitoring',
        'Reference range validation'
      ],
      accuracy: '97.3%',
      processingTime: '1-2 minutes',
      supportedFormats: ['HL7', 'XML', 'CSV', 'PDF'],
      color: 'bg-purple-100 text-purple-800 border-purple-300'
    },
    {
      id: 'ophthalmology',
      name: 'Ophthalmology AI',
      icon: '👁️',
      specialty: 'Eye Care Analysis',
      description: 'Advanced retinal imaging analysis and eye condition assessment',
      capabilities: [
        'Diabetic retinopathy screening',
        'Glaucoma detection and monitoring',
        'Macular degeneration analysis',
        'Retinal vessel analysis',
        'Visual field interpretation'
      ],
      accuracy: '93.1%',
      processingTime: '2-4 minutes',
      supportedFormats: ['DICOM', 'JPEG', 'TIFF', 'PNG'],
      color: 'bg-indigo-100 text-indigo-800 border-indigo-300'
    }
  ];

  useEffect(() => {
    // Load analysis history
    const mockHistory = [
      {
        id: 1,
        agentId: 'radiology',
        patientId: 'P-12345',
        timestamp: new Date('2024-01-15T14:30:00'),
        type: 'Chest X-ray',
        findings: 'No acute abnormalities detected',
        confidence: 94.2,
        status: 'completed'
      },
      {
        id: 2,
        agentId: 'cardiology',
        patientId: 'P-12346',
        timestamp: new Date('2024-01-15T13:15:00'),
        type: 'ECG Analysis',
        findings: 'Normal sinus rhythm, no arrhythmias detected',
        confidence: 96.8,
        status: 'completed'
      },
      {
        id: 3,
        agentId: 'laboratory',
        patientId: 'P-12347',
        timestamp: new Date('2024-01-15T12:00:00'),
        type: 'Complete Blood Count',
        findings: 'All parameters within normal limits',
        confidence: 98.1,
        status: 'completed'
      }
    ];
    setAnalysisHistory(mockHistory);
  }, []);

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    setUploadedFiles([...uploadedFiles, ...files]);
  };

  const removeFile = (index) => {
    setUploadedFiles(uploadedFiles.filter((_, i) => i !== index));
  };

  const startAnalysis = async () => {
    if (!selectedAgent) return;
    
    setIsProcessing(true);
    
    // Simulate AI processing
    setTimeout(() => {
      const mockAnalysis = {
        id: Date.now(),
        agentId: selectedAgent.id,
        agentName: selectedAgent.name,
        patientId: `P-${Date.now()}`,
        timestamp: new Date(),
        type: getAnalysisType(selectedAgent.id),
        inputData: inputData || 'File upload analysis',
        findings: generateMockFindings(selectedAgent.id),
        recommendations: generateMockRecommendations(selectedAgent.id),
        confidence: 90 + Math.random() * 10,
        technicalDetails: generateTechnicalDetails(selectedAgent.id),
        status: 'completed'
      };
      
      setActiveAnalysis(mockAnalysis);
      setAnalysisHistory([mockAnalysis, ...analysisHistory]);
      setIsProcessing(false);
    }, 4000);
  };

  const getAnalysisType = (agentId) => {
    const types = {
      radiology: 'Medical Imaging Analysis',
      pathology: 'Tissue Sample Analysis',
      cardiology: 'Cardiovascular Assessment',
      dermatology: 'Skin Lesion Analysis',
      laboratory: 'Lab Results Analysis',
      ophthalmology: 'Retinal Imaging Analysis'
    };
    return types[agentId] || 'Medical Analysis';
  };

  const generateMockFindings = (agentId) => {
    const findings = {
      radiology: [
        'No acute pathological findings identified',
        'Lung fields clear bilaterally',
        'Cardiac silhouette within normal limits',
        'No evidence of pneumothorax or pleural effusion'
      ],
      pathology: [
        'Cellular morphology appears normal',
        'No malignant cells identified',
        'Inflammatory markers within expected range',
        'Tissue architecture preserved'
      ],
      cardiology: [
        'Regular heart rhythm detected',
        'PR interval: 160ms (normal)',
        'QRS duration: 95ms (normal)',
        'No ST segment abnormalities'
      ],
      dermatology: [
        'Benign appearing lesion characteristics',
        'Symmetrical borders observed',
        'Uniform pigmentation pattern',
        'No concerning features identified'
      ],
      laboratory: [
        'Hemoglobin: 14.2 g/dL (normal)',
        'White blood cell count: 7,200/μL (normal)',
        'Platelet count: 280,000/μL (normal)',
        'All parameters within reference ranges'
      ],
      ophthalmology: [
        'Optic disc appears normal',
        'Macula without exudates or hemorrhages',
        'Retinal vessels show normal caliber',
        'No signs of diabetic retinopathy'
      ]
    };
    return findings[agentId] || ['Analysis completed successfully'];
  };

  const generateMockRecommendations = (agentId) => {
    const recommendations = {
      radiology: [
        'Continue routine monitoring',
        'Follow-up if symptoms persist',
        'Consider additional views if clinically indicated'
      ],
      pathology: [
        'Regular screening recommended',
        'Maintain current treatment protocol',
        'Repeat analysis in 6 months if indicated'
      ],
      cardiology: [
        'Continue current cardiac medications',
        'Regular exercise as tolerated',
        'Follow-up ECG in 3-6 months'
      ],
      dermatology: [
        'Routine dermatological surveillance',
        'Sun protection measures advised',
        'Monitor for changes in size or color'
      ],
      laboratory: [
        'Maintain current therapy',
        'Repeat labs in 3 months',
        'Continue preventive care measures'
      ],
      ophthalmology: [
        'Annual eye examinations recommended',
        'Continue diabetes management if applicable',
        'Report any vision changes immediately'
      ]
    };
    return recommendations[agentId] || ['Follow standard clinical protocols'];
  };

  const generateTechnicalDetails = (agentId) => {
    return {
      processingTime: '3.2 seconds',
      algorithmsUsed: ['Deep Neural Network', 'Convolutional Neural Network', 'Machine Learning'],
      confidence: Math.round((90 + Math.random() * 10) * 10) / 10,
      dataPoints: Math.floor(1000 + Math.random() * 9000),
      imageResolution: agentId === 'radiology' ? '2048x2048' : 'N/A',
      modelVersion: '2.1.0'
    };
  };

  const resetAnalysis = () => {
    setSelectedAgent(null);
    setActiveAnalysis(null);
    setInputData('');
    setUploadedFiles([]);
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Medical AI Agents</h1>
        <p className="text-gray-600">
          Advanced AI-powered analysis across medical specialties
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Agents Selection */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow-sm">
            <div className="px-4 py-3 border-b border-gray-200">
              <h3 className="font-semibold text-gray-900">Select AI Agent</h3>
            </div>
            
            <div className="p-4">
              <div className="space-y-3">
                {medicalAgents.map((agent) => (
                  <button
                    key={agent.id}
                    onClick={() => setSelectedAgent(agent)}
                    className={`w-full p-3 text-left rounded-lg border-2 transition-all ${
                      selectedAgent?.id === agent.id
                        ? agent.color + ' border-current'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="text-2xl">{agent.icon}</div>
                      <div>
                        <div className="font-medium text-gray-900">{agent.name}</div>
                        <div className="text-xs text-gray-600">{agent.specialty}</div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Agent Statistics */}
          <div className="mt-6 bg-white rounded-lg shadow-sm p-4">
            <h4 className="font-semibold text-gray-900 mb-3">Today's Activity</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Total Analyses:</span>
                <span className="font-medium">47</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Active Agents:</span>
                <span className="font-medium">6</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Avg. Accuracy:</span>
                <span className="font-medium">94.8%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Processing Time:</span>
                <span className="font-medium">3.2 min</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Analysis Area */}
        <div className="lg:col-span-3">
          {!selectedAgent ? (
            <div className="bg-white rounded-lg shadow-sm p-12 text-center">
              <div className="text-6xl mb-4">🤖</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                Select an AI Agent
              </h3>
              <p className="text-gray-600">
                Choose a medical AI agent from the sidebar to begin analysis
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Agent Details */}
              <div className="bg-white rounded-lg shadow-sm">
                <div className="px-6 py-4 border-b border-gray-200">
                  <div className="flex items-center space-x-4">
                    <div className="text-3xl">{selectedAgent.icon}</div>
                    <div>
                      <h2 className="text-xl font-semibold text-gray-900">
                        {selectedAgent.name}
                      </h2>
                      <p className="text-gray-600">{selectedAgent.specialty}</p>
                    </div>
                    <div className="ml-auto">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${selectedAgent.color}`}>
                        Accuracy: {selectedAgent.accuracy}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-6">
                  <p className="text-gray-700 mb-6">{selectedAgent.description}</p>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Capabilities</h4>
                      <ul className="space-y-2">
                        {selectedAgent.capabilities.map((capability, idx) => (
                          <li key={idx} className="flex items-start space-x-2">
                            <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
                            <span className="text-sm text-gray-700">{capability}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Specifications</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Processing Time:</span>
                          <span className="font-medium">{selectedAgent.processingTime}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Supported Formats:</span>
                          <span className="font-medium">{selectedAgent.supportedFormats.join(', ')}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Input Section */}
              <div className="bg-white rounded-lg shadow-sm">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="font-semibold text-gray-900">Analysis Input</h3>
                </div>

                <div className="p-6 space-y-6">
                  {/* File Upload */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Upload Medical Files
                    </label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
                      <input
                        type="file"
                        multiple
                        onChange={handleFileUpload}
                        className="hidden"
                        id="file-upload"
                        accept={selectedAgent.supportedFormats.map(format => 
                          format.toLowerCase() === 'dicom' ? '.dcm' : 
                          format.toLowerCase() === 'jpeg' ? '.jpg,.jpeg' :
                          `.${format.toLowerCase()}`
                        ).join(',')}
                      />
                      <label htmlFor="file-upload" className="cursor-pointer">
                        <div className="text-4xl mb-2">📁</div>
                        <p className="text-gray-600">
                          Click to upload or drag and drop
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          Supported: {selectedAgent.supportedFormats.join(', ')}
                        </p>
                      </label>
                    </div>

                    {uploadedFiles.length > 0 && (
                      <div className="mt-4 space-y-2">
                        <h4 className="text-sm font-medium text-gray-700">Uploaded Files:</h4>
                        {uploadedFiles.map((file, idx) => (
                          <div key={idx} className="flex items-center justify-between bg-gray-50 rounded p-2">
                            <span className="text-sm text-gray-700">{file.name}</span>
                            <button
                              onClick={() => removeFile(idx)}
                              className="text-red-600 hover:text-red-800"
                            >
                              ✕
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Text Input */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Clinical Data or Notes (Optional)
                    </label>
                    <textarea
                      value={inputData}
                      onChange={(e) => setInputData(e.target.value)}
                      rows={4}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter patient data, symptoms, or additional clinical information..."
                    />
                  </div>

                  {/* Action Buttons */}
                  <div className="flex space-x-4">
                    <button
                      onClick={startAnalysis}
                      disabled={isProcessing || (uploadedFiles.length === 0 && !inputData)}
                      className={`flex-1 px-6 py-3 rounded-lg font-medium transition-colors ${
                        isProcessing || (uploadedFiles.length === 0 && !inputData)
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-blue-600 text-white hover:bg-blue-700'
                      }`}
                    >
                      {isProcessing ? 'Processing...' : 'Start Analysis'}
                    </button>
                    <button
                      onClick={resetAnalysis}
                      className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Reset
                    </button>
                  </div>
                </div>
              </div>

              {/* Processing Status */}
              {isProcessing && (
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <div className="text-center">
                    <div className="text-4xl mb-4">⚡</div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      AI Analysis in Progress
                    </h3>
                    <p className="text-gray-600 mb-4">
                      {selectedAgent.name} is analyzing your data...
                    </p>
                    <div className="w-64 mx-auto bg-gray-200 rounded-full h-2">
                      <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{width: '60%'}} />
                    </div>
                  </div>
                </div>
              )}

              {/* Analysis Results */}
              {activeAnalysis && !isProcessing && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white rounded-lg shadow-sm"
                >
                  <div className="px-6 py-4 border-b border-gray-200">
                    <div className="flex items-center justify-between">
                      <h3 className="font-semibold text-gray-900">Analysis Results</h3>
                      <span className="text-sm text-gray-500">
                        {activeAnalysis.timestamp.toLocaleString()}
                      </span>
                    </div>
                  </div>

                  <div className="p-6 space-y-6">
                    {/* Confidence Score */}
                    <div className="bg-green-50 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-semibold text-green-900">Confidence Score</h4>
                        <span className="text-2xl font-bold text-green-600">
                          {Math.round(activeAnalysis.confidence)}%
                        </span>
                      </div>
                      <div className="w-full bg-green-200 rounded-full h-2">
                        <div
                          className="bg-green-600 h-2 rounded-full"
                          style={{ width: `${activeAnalysis.confidence}%` }}
                        />
                      </div>
                    </div>

                    {/* Findings */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Key Findings</h4>
                      <div className="space-y-2">
                        {activeAnalysis.findings.map((finding, idx) => (
                          <div key={idx} className="flex items-start space-x-2">
                            <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
                            <span className="text-gray-700">{finding}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Recommendations */}
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Recommendations</h4>
                      <div className="space-y-2">
                        {activeAnalysis.recommendations.map((rec, idx) => (
                          <div key={idx} className="flex items-start space-x-2">
                            <div className="w-2 h-2 bg-orange-600 rounded-full mt-2 flex-shrink-0" />
                            <span className="text-gray-700">{rec}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Technical Details */}
                    <div className="bg-gray-50 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-900 mb-3">Technical Details</h4>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">Processing Time:</span>
                          <span className="font-medium">{activeAnalysis.technicalDetails.processingTime}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Data Points:</span>
                          <span className="font-medium">{activeAnalysis.technicalDetails.dataPoints.toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Model Version:</span>
                          <span className="font-medium">{activeAnalysis.technicalDetails.modelVersion}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Resolution:</span>
                          <span className="font-medium">{activeAnalysis.technicalDetails.imageResolution}</span>
                        </div>
                      </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="flex space-x-4">
                      <button className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                        Generate Report
                      </button>
                      <button className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                        Share Results
                      </button>
                      <button className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors">
                        Save to Records
                      </button>
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Recent Analysis History */}
              {analysisHistory.length > 0 && (
                <div className="bg-white rounded-lg shadow-sm">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="font-semibold text-gray-900">Recent Analyses</h3>
                  </div>
                  
                  <div className="p-6">
                    <div className="space-y-4">
                      {analysisHistory.slice(0, 3).map((analysis) => (
                        <div key={analysis.id} className="border-l-4 border-blue-200 pl-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="font-medium text-gray-900">{analysis.type}</div>
                              <div className="text-sm text-gray-600">{analysis.findings}</div>
                              <div className="text-xs text-gray-500 mt-1">
                                Patient: {analysis.patientId} • {analysis.timestamp.toLocaleString()}
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="text-sm font-medium text-green-600">
                                {Math.round(analysis.confidence)}% confidence
                              </div>
                              <div className="text-xs text-gray-500">{analysis.status}</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MedicalAgents;