import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

import logger from '@/services/logger';

const CustomerSupportHub = () => {
  const [activeTab, setActiveTab] = useState('chat');
  const [chatMessages, setChatMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [supportTickets, setSupportTickets] = useState([]);
  const [knowledgeBase, setKnowledgeBase] = useState([]);
  const [liveAgents, setLiveAgents] = useState([]);
  const [customerInfo, setCustomerInfo] = useState({});
  const [chatMode, setChatMode] = useState('ai'); // 'ai' or 'human'
  const messagesEndRef = useRef(null);

  const supportCategories = [
    {
      id: 'claims',
      name: 'Claims Support',
      icon: '📋',
      description: 'Claim status, approvals, and processing help',
      commonQuestions: [
        'Check my claim status',
        'Why was my claim denied?',
        'How to submit a new claim',
        'Required documents for claims'
      ]
    },
    {
      id: 'coverage',
      name: 'Coverage Questions',
      icon: '🛡️',
      description: 'Policy coverage, benefits, and plan details',
      commonQuestions: [
        'What does my plan cover?',
        'Find in-network providers',
        'Prescription drug coverage',
        'Preventive care benefits'
      ]
    },
    {
      id: 'billing',
      name: 'Billing & Payments',
      icon: '💳',
      description: 'Premium payments, billing issues, and statements',
      commonQuestions: [
        'View my billing statement',
        'Update payment method',
        'Explain premium charges',
        'Set up auto-pay'
      ]
    },
    {
      id: 'enrollment',
      name: 'Enrollment & Changes',
      icon: '📝',
      description: 'Plan changes, enrollment, and member updates',
      commonQuestions: [
        'Change my plan',
        'Add family members',
        'Update personal information',
        'Special enrollment periods'
      ]
    },
    {
      id: 'technical',
      name: 'Technical Support',
      icon: '⚙️',
      description: 'Website, app, and digital platform assistance',
      commonQuestions: [
        'Reset my password',
        'Download mobile app',
        'Website navigation help',
        'Digital ID card access'
      ]
    }
  ];

  useEffect(() => {
    // Initialize with welcome message
    setChatMessages([
      {
        id: 1,
        type: 'ai',
        content: 'Hello! I\'m your AI healthcare assistant. I can help you with claims, coverage questions, billing, and more. How can I assist you today?',
        timestamp: new Date(),
        suggestions: [
          'Check claim status',
          'Find a doctor',
          'Coverage questions',
          'Billing help'
        ]
      }
    ]);

    // Load mock data
    loadMockData();
    scrollToBottom();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [chatMessages]);

  const loadMockData = () => {
    // Mock support tickets
    setSupportTickets([
      {
        id: 'T-2025-001',
        subject: 'Claim denial inquiry',
        status: 'open',
        priority: 'high',
        category: 'claims',
        created: new Date('2025-01-28'),
        lastUpdate: new Date('2025-01-29'),
        description: 'Need help understanding why claim was denied'
      },
      {
        id: 'T-2025-002',
        subject: 'Coverage verification needed',
        status: 'in-progress',
        priority: 'medium',
        category: 'coverage',
        created: new Date('2025-01-25'),
        lastUpdate: new Date('2025-01-29'),
        description: 'Verify coverage for upcoming procedure'
      }
    ]);

    // Mock knowledge base
    setKnowledgeBase([
      {
        id: 1,
        title: 'How to Submit a Claim',
        category: 'claims',
        views: 1250,
        rating: 4.8,
        summary: 'Step-by-step guide for claim submission'
      },
      {
        id: 2,
        title: 'Understanding Your Benefits',
        category: 'coverage',
        views: 980,
        rating: 4.6,
        summary: 'Comprehensive guide to your health plan benefits'
      },
      {
        id: 3,
        title: 'Finding In-Network Providers',
        category: 'coverage',
        views: 756,
        rating: 4.7,
        summary: 'How to find providers in your network'
      }
    ]);

    // Mock live agents
    setLiveAgents([
      {
        id: 1,
        name: 'Sarah Johnson',
        avatar: '👩‍💼',
        specialty: 'Claims Specialist',
        status: 'available',
        rating: 4.9,
        languages: ['English', 'Arabic']
      },
      {
        id: 2,
        name: 'Ahmed Al-Rashid',
        avatar: '👨‍💼',
        specialty: 'Coverage Expert',
        status: 'busy',
        rating: 4.8,
        languages: ['Arabic', 'English']
      },
      {
        id: 3,
        name: 'Lisa Chen',
        avatar: '👩‍⚕️',
        specialty: 'Medical Coordinator',
        status: 'available',
        rating: 4.9,
        languages: ['English', 'Mandarin']
      }
    ]);

    // Mock customer info
    setCustomerInfo({
      id: 'M-123456789',
      name: 'John Smith',
      planType: 'Premium Plus',
      memberSince: '2023-03-15',
      status: 'Active',
      upcomingRenewal: '2025-03-15'
    });
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return;

    const newMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setChatMessages(prev => [...prev, newMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = generateAIResponse(inputMessage);
      setChatMessages(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 1500);
  };

  const generateAIResponse = (userMessage) => {
    const lowerMessage = userMessage.toLowerCase();
    let response = '';
    let suggestions = [];
    let actions = [];

    if (lowerMessage.includes('claim') || lowerMessage.includes('claims')) {
      response = 'I can help you with your claims! I can check claim status, explain denial reasons, or guide you through the submission process. What specific claim information do you need?';
      suggestions = ['Check claim status', 'Explain denial', 'Submit new claim', 'Required documents'];
      actions = [
        { type: 'view_claims', label: 'View My Claims', icon: '📋' },
        { type: 'submit_claim', label: 'Submit New Claim', icon: '➕' }
      ];
    } else if (lowerMessage.includes('coverage') || lowerMessage.includes('benefits')) {
      response = 'I\'d be happy to help explain your coverage! Your Premium Plus plan includes comprehensive medical, dental, and vision benefits. What specific coverage question do you have?';
      suggestions = ['In-network providers', 'Prescription coverage', 'Preventive care', 'Deductible info'];
      actions = [
        { type: 'view_benefits', label: 'View Benefits Summary', icon: '📄' },
        { type: 'find_provider', label: 'Find Provider', icon: '🔍' }
      ];
    } else if (lowerMessage.includes('bill') || lowerMessage.includes('payment')) {
      response = 'I can assist with billing and payment questions. Your next premium payment of $285 is due February 15th. Would you like to view your statement or update payment information?';
      suggestions = ['View statement', 'Update payment method', 'Set up autopay', 'Payment history'];
      actions = [
        { type: 'view_billing', label: 'View Billing', icon: '💳' },
        { type: 'make_payment', label: 'Make Payment', icon: '💰' }
      ];
    } else if (lowerMessage.includes('doctor') || lowerMessage.includes('provider')) {
      response = 'I can help you find healthcare providers in your network. What type of provider are you looking for, and in which area?';
      suggestions = ['Primary care physician', 'Specialist', 'Hospital', 'Urgent care'];
      actions = [
        { type: 'provider_search', label: 'Provider Directory', icon: '🏥' },
        { type: 'appointment', label: 'Schedule Appointment', icon: '📅' }
      ];
    } else {
      response = 'I\'m here to help with any questions about your health insurance. I can assist with claims, coverage, billing, finding providers, and more. What would you like to know?';
      suggestions = ['Claims help', 'Coverage questions', 'Find a doctor', 'Billing support'];
    }

    return {
      id: Date.now(),
      type: 'ai',
      content: response,
      timestamp: new Date(),
      suggestions,
      actions
    };
  };

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
    handleSendMessage();
  };

  const handleActionClick = (action) => {
    // Handle different action types
    switch (action.type) {
      case 'view_claims':
        setActiveTab('tickets');
        break;
      case 'view_benefits':
        // Navigate to benefits page
        break;
      case 'find_provider':
        // Navigate to provider directory
        break;
      default:
        logger.info('Action clicked:', action);
    }
  };

  const escalateToHuman = () => {
    setChatMode('human');
    const escalationMessage = {
      id: Date.now(),
      type: 'system',
      content: 'Connecting you with a live agent. Please wait while we find an available specialist...',
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, escalationMessage]);

    setTimeout(() => {
      const agentMessage = {
        id: Date.now() + 1,
        type: 'agent',
        content: 'Hi! This is Sarah, a claims specialist. I\'ve reviewed your chat history and I\'m ready to help. What can I assist you with today?',
        timestamp: new Date(),
        agentInfo: {
          name: 'Sarah Johnson',
          title: 'Senior Claims Specialist',
          avatar: '👩‍💼'
        }
      };
      setChatMessages(prev => [...prev, agentMessage]);
    }, 3000);
  };

  const StatusBadge = ({ status }) => {
    const colors = {
      open: 'bg-red-100 text-red-800',
      'in-progress': 'bg-yellow-100 text-yellow-800',
      resolved: 'bg-green-100 text-green-800',
      closed: 'bg-gray-100 text-gray-800'
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[status]}`}>
        {status.replace('-', ' ')}
      </span>
    );
  };

  const PriorityBadge = ({ priority }) => {
    const colors = {
      low: 'bg-gray-100 text-gray-800',
      medium: 'bg-blue-100 text-blue-800',
      high: 'bg-orange-100 text-orange-800',
      urgent: 'bg-red-100 text-red-800'
    };
    return (
      <span className={`px-2 py-1 text-xs font-medium rounded-full ${colors[priority]}`}>
        {priority}
      </span>
    );
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Customer Support Hub</h1>
        <p className="text-gray-600">
          24/7 AI-powered assistance with human agent escalation
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {[
              { id: 'chat', name: 'AI Chat Assistant', icon: '🤖' },
              { id: 'tickets', name: 'Support Tickets', icon: '🎫' },
              { id: 'knowledge', name: 'Knowledge Base', icon: '📚' },
              { id: 'agents', name: 'Live Agents', icon: '👥' }
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

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-8">
        {/* Main Content */}
        <div className="xl:col-span-3">
          <AnimatePresence mode="wait">
            {/* AI Chat Assistant */}
            {activeTab === 'chat' && (
              <motion.div
                key="chat"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-white rounded-lg shadow-sm border border-gray-200"
              >
                {/* Chat Header */}
                <div className="px-6 py-4 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                        <span className="text-white text-lg">🤖</span>
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">
                          {chatMode === 'ai' ? 'AI Healthcare Assistant' : 'Live Agent - Sarah Johnson'}
                        </h3>
                        <p className="text-sm text-gray-500">
                          {chatMode === 'ai' ? 'Instant responses • Available 24/7' : 'Claims Specialist • Online'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {chatMode === 'ai' && (
                        <button
                          onClick={escalateToHuman}
                          className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
                        >
                          Talk to Human Agent
                        </button>
                      )}
                      <div className="flex items-center space-x-1">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-xs text-gray-500">Online</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Chat Messages */}
                <div className="h-96 overflow-y-auto p-6 space-y-4">
                  {chatMessages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`max-w-xs lg:max-w-md ${
                        message.type === 'user' 
                          ? 'bg-blue-600 text-white rounded-l-lg rounded-tr-lg'
                          : message.type === 'system'
                          ? 'bg-gray-100 text-gray-600 rounded-lg'
                          : 'bg-gray-50 text-gray-900 rounded-r-lg rounded-tl-lg'
                      } px-4 py-2`}>
                        {message.type === 'agent' && message.agentInfo && (
                          <div className="flex items-center space-x-2 mb-2 text-xs text-gray-500">
                            <span>{message.agentInfo.avatar}</span>
                            <span>{message.agentInfo.name}</span>
                            <span>•</span>
                            <span>{message.agentInfo.title}</span>
                          </div>
                        )}
                        <p className="text-sm">{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          message.type === 'user' ? 'text-blue-100' : 'text-gray-400'
                        }`}>
                          {message.timestamp.toLocaleTimeString()}
                        </p>
                        
                        {/* Suggestions */}
                        {message.suggestions && message.suggestions.length > 0 && (
                          <div className="mt-3 space-y-1">
                            {message.suggestions.map((suggestion, idx) => (
                              <button
                                key={idx}
                                onClick={() => handleSuggestionClick(suggestion)}
                                className="block w-full text-left text-xs bg-white text-gray-700 px-2 py-1 rounded border hover:bg-gray-50 transition-colors"
                              >
                                {suggestion}
                              </button>
                            ))}
                          </div>
                        )}

                        {/* Actions */}
                        {message.actions && message.actions.length > 0 && (
                          <div className="mt-3 space-y-1">
                            {message.actions.map((action, idx) => (
                              <button
                                key={idx}
                                onClick={() => handleActionClick(action)}
                                className="flex items-center space-x-2 w-full text-left text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded hover:bg-blue-100 transition-colors"
                              >
                                <span>{action.icon}</span>
                                <span>{action.label}</span>
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                  
                  {isTyping && (
                    <div className="flex justify-start">
                      <div className="bg-gray-50 rounded-r-lg rounded-tl-lg px-4 py-2">
                        <div className="flex space-x-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>

                {/* Chat Input */}
                <div className="px-6 py-4 border-t border-gray-200">
                  <div className="flex space-x-4">
                    <input
                      type="text"
                      value={inputMessage}
                      onChange={(e) => setInputMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      placeholder="Type your message..."
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <button
                      onClick={handleSendMessage}
                      disabled={!inputMessage.trim()}
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Send
                    </button>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Support Tickets */}
            {activeTab === 'tickets' && (
              <motion.div
                key="tickets"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <div className="flex items-center justify-between">
                      <h3 className="text-lg font-semibold text-gray-900">Your Support Tickets</h3>
                      <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                        Create New Ticket
                      </button>
                    </div>
                  </div>
                  
                  <div className="divide-y divide-gray-200">
                    {supportTickets.map((ticket) => (
                      <div key={ticket.id} className="p-6 hover:bg-gray-50 transition-colors">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center space-x-3">
                            <h4 className="text-sm font-semibold text-gray-900">{ticket.subject}</h4>
                            <StatusBadge status={ticket.status} />
                            <PriorityBadge priority={ticket.priority} />
                          </div>
                          <span className="text-xs text-gray-500">#{ticket.id}</span>
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{ticket.description}</p>
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>Created: {ticket.created.toLocaleDateString()}</span>
                          <span>Last Updated: {ticket.lastUpdate.toLocaleDateString()}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Knowledge Base */}
            {activeTab === 'knowledge' && (
              <motion.div
                key="knowledge"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6"
              >
                {/* Support Categories */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {supportCategories.map((category) => (
                    <div key={category.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow cursor-pointer">
                      <div className="flex items-center space-x-3 mb-3">
                        <span className="text-3xl">{category.icon}</span>
                        <h3 className="text-lg font-semibold text-gray-900">{category.name}</h3>
                      </div>
                      <p className="text-sm text-gray-600 mb-4">{category.description}</p>
                      <div className="space-y-2">
                        {category.commonQuestions.slice(0, 3).map((question, idx) => (
                          <div key={idx} className="text-xs text-blue-600 hover:text-blue-800 cursor-pointer">
                            • {question}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Popular Articles */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                  <div className="px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-semibold text-gray-900">Popular Help Articles</h3>
                  </div>
                  
                  <div className="divide-y divide-gray-200">
                    {knowledgeBase.map((article) => (
                      <div key={article.id} className="p-6 hover:bg-gray-50 transition-colors cursor-pointer">
                        <div className="flex items-center justify-between mb-2">
                          <h4 className="text-sm font-semibold text-gray-900">{article.title}</h4>
                          <div className="flex items-center space-x-2">
                            <span className="text-xs text-gray-500">{article.views} views</span>
                            <div className="flex items-center">
                              <span className="text-yellow-400">★</span>
                              <span className="text-xs text-gray-500 ml-1">{article.rating}</span>
                            </div>
                          </div>
                        </div>
                        <p className="text-sm text-gray-600">{article.summary}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Live Agents */}
            {activeTab === 'agents' && (
              <motion.div
                key="agents"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="bg-white rounded-lg shadow-sm border border-gray-200"
              >
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">Available Live Agents</h3>
                  <p className="text-sm text-gray-600">Connect with specialized human agents for complex issues</p>
                </div>
                
                <div className="divide-y divide-gray-200">
                  {liveAgents.map((agent) => (
                    <div key={agent.id} className="p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-2xl">
                            {agent.avatar}
                          </div>
                          <div>
                            <h4 className="text-sm font-semibold text-gray-900">{agent.name}</h4>
                            <p className="text-sm text-gray-600">{agent.specialty}</p>
                            <div className="flex items-center space-x-2 mt-1">
                              <div className={`w-2 h-2 rounded-full ${
                                agent.status === 'available' ? 'bg-green-500' : 'bg-yellow-500'
                              }`}></div>
                              <span className="text-xs text-gray-500 capitalize">{agent.status}</span>
                              <span className="text-xs text-gray-400">•</span>
                              <span className="text-xs text-gray-500">Rating: {agent.rating}/5</span>
                            </div>
                            <div className="flex items-center space-x-1 mt-1">
                              {agent.languages.map((lang, idx) => (
                                <span key={idx} className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full">
                                  {lang}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        <button
                          disabled={agent.status !== 'available'}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                            agent.status === 'available'
                              ? 'bg-blue-600 text-white hover:bg-blue-700'
                              : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          }`}
                        >
                          {agent.status === 'available' ? 'Connect Now' : 'Busy'}
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Sidebar */}
        <div className="xl:col-span-1 space-y-6">
          {/* Customer Info */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Account</h3>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Member ID</label>
                <p className="text-sm font-medium text-gray-900">{customerInfo.id}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Plan Type</label>
                <p className="text-sm font-medium text-gray-900">{customerInfo.planType}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Status</label>
                <p className="text-sm font-medium text-green-600">{customerInfo.status}</p>
              </div>
              <div>
                <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Next Renewal</label>
                <p className="text-sm font-medium text-gray-900">{customerInfo.upcomingRenewal}</p>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
            <div className="space-y-2">
              {[
                { name: 'View Claims', icon: '📋', href: '/claims' },
                { name: 'Find Provider', icon: '🏥', href: '/providers' },
                { name: 'Download ID Card', icon: '🆔', href: '/id-card' },
                { name: 'Update Profile', icon: '👤', href: '/profile' },
                { name: 'Payment History', icon: '💳', href: '/billing' }
              ].map((action) => (
                <button
                  key={action.name}
                  className="w-full flex items-center space-x-3 p-2 text-left hover:bg-gray-50 rounded-lg transition-colors"
                >
                  <span className="text-lg">{action.icon}</span>
                  <span className="text-sm font-medium text-gray-900">{action.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Support Hours */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-blue-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Support Hours</h3>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">AI Assistant:</span>
                <span className="font-medium text-gray-900">24/7</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Live Agents:</span>
                <span className="font-medium text-gray-900">8 AM - 10 PM</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Emergency:</span>
                <span className="font-medium text-gray-900">24/7</span>
              </div>
            </div>
            <div className="mt-4 p-3 bg-white rounded-lg border border-blue-200">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span className="text-sm font-medium text-gray-900">All systems operational</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerSupportHub;
