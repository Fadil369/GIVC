import React, { useState } from 'react';
import { AIAgentType, AnalysisResult } from '@/types';
import {
  CpuChipIcon,
  PhotoIcon,
  DocumentTextIcon,
  HeartIcon,
  ShieldCheckIcon,
  PlayIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  ChartBarIcon,
  ClockIcon,
} from '@heroicons/react/24/outline';

interface AgentData {
  type: AIAgentType;
  name: string;
  description: string;
  icon: React.ComponentType<any>;
  capabilities: string[];
  confidence: number;
  isActive: boolean;
  lastRun?: Date;
  totalAnalyses: number;
  averageTime: number;
  color: string;
}

const MedicalAgents: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<AIAgentType | null>(null);
  const [isRunning, setIsRunning] = useState<Record<AIAgentType, boolean>>({
    dicom_analysis: false,
    lab_parser: false,
    clinical_decision: false,
    compliance_monitor: false,
  });
  const [results, setResults] = useState<AnalysisResult[]>([]);

  const agents: AgentData[] = [
    {
      type: 'dicom_analysis',
      name: 'DICOM Analysis Agent',
      description: 'AI-powered medical imaging analysis with ResNet-50 neural network',
      icon: PhotoIcon,
      capabilities: [
        'DICOM Image Processing',
        'Anatomical Structure Detection',
        'Abnormality Identification',
        'Measurement Extraction',
        'Radiology Report Generation',
        'Multi-modal Support (CT, MRI, X-Ray)'
      ],
      confidence: 0.92,
      isActive: true,
      lastRun: new Date('2024-01-15T10:30:00'),
      totalAnalyses: 1247,
      averageTime: 2.3,
      color: 'bg-blue-500',
    },
    {
      type: 'lab_parser',
      name: 'Lab Results Parser',
      description: 'OCR and intelligent parsing of laboratory results and reports',
      icon: DocumentTextIcon,
      capabilities: [
        'OCR Text Extraction',
        'Lab Value Recognition',
        'Reference Range Validation',
        'Critical Value Detection',
        'Trend Analysis',
        'Multi-format Support (PDF, Images, HL7)'
      ],
      confidence: 0.95,
      isActive: true,
      lastRun: new Date('2024-01-15T09:15:00'),
      totalAnalyses: 890,
      averageTime: 1.8,
      color: 'bg-green-500',
    },
    {
      type: 'clinical_decision',
      name: 'Clinical Decision Support',
      description: 'Evidence-based clinical decision support and diagnosis assistance',
      icon: HeartIcon,
      capabilities: [
        'Differential Diagnosis Generation',
        'Treatment Recommendation',
        'Drug Interaction Checking',
        'Clinical Guideline Integration',
        'Risk Stratification',
        'Follow-up Planning'
      ],
      confidence: 0.88,
      isActive: true,
      lastRun: new Date('2024-01-15T08:45:00'),
      totalAnalyses: 567,
      averageTime: 3.2,
      color: 'bg-purple-500',
    },
    {
      type: 'compliance_monitor',
      name: 'Compliance Monitor',
      description: 'Real-time HIPAA compliance monitoring and audit trail management',
      icon: ShieldCheckIcon,
      capabilities: [
        'HIPAA Compliance Monitoring',
        'Access Control Validation',
        'Audit Log Analysis',
        'Privacy Violation Detection',
        'Security Assessment',
        'Compliance Reporting'
      ],
      confidence: 0.98,
      isActive: true,
      lastRun: new Date('2024-01-15T11:00:00'),
      totalAnalyses: 2156,
      averageTime: 0.5,
      color: 'bg-red-500',
    },
  ];

  const runAgent = async (agentType: AIAgentType) => {
    setIsRunning(prev => ({ ...prev, [agentType]: true }));
    
    // Simulate agent processing
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Generate mock result
    const agent = agents.find(a => a.type === agentType)!;
    const mockResult: AnalysisResult = {
      id: Date.now().toString(),
      fileId: 'mock-file-id',
      agentType,
      confidence: agent.confidence + Math.random() * 0.05 - 0.025, // Slight variation
      findings: [
        {
          type: 'abnormality',
          description: `Mock finding from ${agent.name}`,
          severity: 'medium',
          confidence: agent.confidence,
        }
      ],
      recommendations: [
        {
          type: 'follow_up',
          description: `Recommendation from ${agent.name}`,
          priority: 'routine',
        }
      ],
      processedAt: new Date(),
      processingTime: agent.averageTime + Math.random() * 2 - 1,
      version: '1.0.0',
    };
    
    setResults(prev => [mockResult, ...prev]);
    setIsRunning(prev => ({ ...prev, [agentType]: false }));
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return 'text-green-600';
    if (confidence >= 0.8) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatTime = (seconds: number) => {
    return `${seconds.toFixed(1)}s`;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Medical AI Agents</h1>
        <p className="text-gray-600 mt-2">
          Advanced AI-powered medical analysis and decision support systems
        </p>
        <div className="flex items-center justify-center space-x-4 mt-4">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
            🤖 4 Active Agents
          </span>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            📊 Real-time Processing
          </span>
        </div>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {agents.map((agent) => (
          <div 
            key={agent.type}
            className={`
              card cursor-pointer transition-all duration-200 hover:shadow-lg
              ${selectedAgent === agent.type ? 'ring-2 ring-primary-500 bg-primary-50' : ''}
            `}
            onClick={() => setSelectedAgent(agent.type)}
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`p-2 rounded-lg ${agent.color} bg-opacity-10`}>
                <agent.icon className={`h-6 w-6 ${agent.color.replace('bg-', 'text-')}`} />
              </div>
              <div className={`
                w-3 h-3 rounded-full
                ${agent.isActive ? 'bg-green-500 animate-pulse-slow' : 'bg-gray-300'}
              `}></div>
            </div>
            
            <h3 className="font-semibold text-gray-900 mb-2">{agent.name}</h3>
            <p className="text-sm text-gray-600 mb-4 line-clamp-2">{agent.description}</p>
            
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">Confidence</span>
                <span className={`font-medium ${getConfidenceColor(agent.confidence)}`}>
                  {(agent.confidence * 100).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Analyses</span>
                <span className="font-medium text-gray-900">{agent.totalAnalyses.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">Avg Time</span>
                <span className="font-medium text-gray-900">{formatTime(agent.averageTime)}</span>
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-200">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  runAgent(agent.type);
                }}
                disabled={isRunning[agent.type]}
                className={`
                  w-full flex items-center justify-center space-x-2 py-2 px-3 rounded-md text-sm font-medium transition-colors
                  ${isRunning[agent.type]
                    ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                    : `${agent.color} text-white hover:opacity-90`
                  }
                `}
              >
                {isRunning[agent.type] ? (
                  <>
                    <div className="loading-spinner w-4 h-4"></div>
                    <span>Running...</span>
                  </>
                ) : (
                  <>
                    <PlayIcon className="h-4 w-4" />
                    <span>Run Agent</span>
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Agent Details */}
      {selectedAgent && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          {(() => {
            const agent = agents.find(a => a.type === selectedAgent)!;
            return (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`p-3 rounded-lg ${agent.color} bg-opacity-10`}>
                      <agent.icon className={`h-8 w-8 ${agent.color.replace('bg-', 'text-')}`} />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">{agent.name}</h2>
                      <p className="text-gray-600">{agent.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getConfidenceColor(agent.confidence)} bg-gray-100`}>
                      <div className="w-2 h-2 bg-current rounded-full mr-2"></div>
                      {(agent.confidence * 100).toFixed(1)}% Confidence
                    </div>
                  </div>
                </div>

                {/* Capabilities */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">Capabilities</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                    {agent.capabilities.map((capability, index) => (
                      <div key={index} className="flex items-center space-x-2 p-3 bg-gray-50 rounded-lg">
                        <div className="w-2 h-2 bg-primary-500 rounded-full"></div>
                        <span className="text-sm font-medium text-gray-700">{capability}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Performance Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <ChartBarIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900">{agent.totalAnalyses.toLocaleString()}</div>
                    <div className="text-sm text-gray-600">Total Analyses</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <ClockIcon className="h-8 w-8 text-green-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900">{formatTime(agent.averageTime)}</div>
                    <div className="text-sm text-gray-600">Average Time</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <CpuChipIcon className="h-8 w-8 text-purple-600 mx-auto mb-2" />
                    <div className="text-2xl font-bold text-gray-900">{(agent.confidence * 100).toFixed(1)}%</div>
                    <div className="text-sm text-gray-600">Confidence Score</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <div className={`w-8 h-8 rounded-full mx-auto mb-2 flex items-center justify-center ${agent.isActive ? 'bg-green-500' : 'bg-gray-400'}`}>
                      <div className="w-3 h-3 bg-white rounded-full"></div>
                    </div>
                    <div className="text-2xl font-bold text-gray-900">{agent.isActive ? 'Active' : 'Inactive'}</div>
                    <div className="text-sm text-gray-600">Status</div>
                  </div>
                </div>

                {/* Last Run Info */}
                {agent.lastRun && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-center space-x-2">
                      <ClockIcon className="h-5 w-5 text-blue-600" />
                      <span className="font-medium text-blue-900">Last Run</span>
                    </div>
                    <div className="text-sm text-blue-700 mt-1">
                      {agent.lastRun.toLocaleString()}
                    </div>
                  </div>
                )}
              </div>
            );
          })()}
        </div>
      )}

      {/* Recent Results */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Recent Analysis Results</h2>
            <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View All Results
            </button>
          </div>
          
          <div className="space-y-4">
            {results.slice(0, 5).map((result) => {
              const agent = agents.find(a => a.type === result.agentType)!;
              return (
                <div key={result.id} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-3">
                      <div className={`p-2 rounded-lg ${agent.color} bg-opacity-10`}>
                        <agent.icon className={`h-5 w-5 ${agent.color.replace('bg-', 'text-')}`} />
                      </div>
                      <div>
                        <h3 className="font-medium text-gray-900">{agent.name}</h3>
                        <div className="text-sm text-gray-500">
                          {result.processedAt.toLocaleString()} • {formatTime(result.processingTime)}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <span className={`text-sm font-medium ${getConfidenceColor(result.confidence)}`}>
                        {(result.confidence * 100).toFixed(1)}%
                      </span>
                      <div className="flex items-center space-x-1">
                        <button className="p-1 text-gray-400 hover:text-primary-600">
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        <button className="p-1 text-gray-400 hover:text-blue-600">
                          <ArrowDownTrayIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Findings</h4>
                      <div className="space-y-1">
                        {result.findings.map((finding, index) => (
                          <div key={index} className="text-sm text-gray-600">
                            • {finding.description}
                          </div>
                        ))}
                      </div>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Recommendations</h4>
                      <div className="space-y-1">
                        {result.recommendations.map((rec, index) => (
                          <div key={index} className="text-sm text-gray-600">
                            • {rec.description}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card text-center">
          <div className="text-2xl font-bold text-primary-600">
            {agents.filter(a => a.isActive).length}
          </div>
          <div className="text-sm text-gray-600">Active Agents</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-green-600">
            {agents.reduce((sum, a) => sum + a.totalAnalyses, 0).toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Total Analyses</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-blue-600">
            {(agents.reduce((sum, a) => sum + a.confidence, 0) / agents.length * 100).toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600">Average Confidence</div>
        </div>
      </div>
    </div>
  );
};

export default MedicalAgents;