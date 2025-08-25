import { useAuth } from '../hooks/useAuth.jsx';
import InsuranceAPIService from '../services/insuranceAPI.jsx';
import type { ChatMessage, ChatSession } from '../types/insurance.jsx';
import {
    ChatBubbleLeftEllipsisIcon,
    CheckCircleIcon,
    ClockIcon,
    DocumentArrowUpIcon,
    ExclamationTriangleIcon,
    PaperAirplaneIcon,
    PhoneIcon,
    UserCircleIcon,
} from '@heroicons/react/24/outline.jsx';
import { AnimatePresence, motion } from 'framer-motion';
import React, { useEffect, useRef, useState } from 'react';

interface CustomerSupportProps {
  className?: string;
}

const CustomerSupport= '' }) => {
  const { user } = useAuth();
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [sessionHistory, setSessionHistory] = useState([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const supportCategories = [
    { id: 'general', name: 'General Questions', icon: ChatBubbleLeftEllipsisIcon },
    { id: 'claims', name: 'Claims Support', icon: DocumentArrowUpIcon },
    { id: 'enrollment', name: 'Plan Enrollment', icon: UserCircleIcon },
    { id: 'billing', name: 'Billing & Payments', icon: CheckCircleIcon },
    { id: 'benefits', name: 'Benefits Information', icon: ClockIcon },
    { id: 'emergency', name: 'Emergency Support', icon: ExclamationTriangleIcon },
  ];

  const quickActions = [
    'Check my claim status',
    'Find a doctor in my network',
    'Understand my benefits',
    'Update my information',
    'Request a new ID card',
    'Appeal a denied claim',
  ];

  useEffect(() => {
    loadSessionHistory();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadSessionHistory = async () => {
    if (!user?.id) return;

    try {
      const response = await InsuranceAPIService.getChatSessions(user.id, {
        page: 1,
        limit: 10,
        sort: [{ field: 'startTime', order: 'desc' }],
      });

      if (response.success && response.data) {
        setSessionHistory(response.data.data);
      }
    } catch (error) {
      console.error('Failed to load session history:', error);
    }
  };

  const startNewSession = async (category=> {
    if (!user?.id) return;

    try {
      setIsLoading(true);
      const response = await InsuranceAPIService.createChatSession(user.id, category);

      if (response.success && response.data) {
        setCurrentSession(response.data);
        setMessages(response.data.messages || []);
        
        // Send welcome message
        setTimeout(() => {
          sendWelcomeMessage(category);
        }, 500);
      }
    } catch (error) {
      console.error('Failed to start new session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const sendWelcomeMessage = async (category=> {
    const welcomeMessages = {
      general: "Hi! I'm your GIVC AI assistant. How can I help you today?",
      claims: "I'm here to help with your claims. I can check status, help with appeals, or answer questions about the claims process.",
      enrollment: "I can help you find the perfect health plan! Let me know your needs and I'll provide personalized recommendations.",
      billing: "I can assist with billing questions, payment issues, or explain charges on your account.",
      benefits: "I'm here to help you understand your benefits and how to make the most of your coverage.",
      emergency: "For medical emergencies, please call 911. For urgent coverage questions, I'm here to help 24/7.",
    };

    const message = welcomeMessages[category as keyof typeof welcomeMessages] || welcomeMessages.general;
    
    const aiMessage= {
      id: `welcome_${Date.now()}`,
      sender: 'ai',
      content: message,
      timestamp: new Date().toISOString(),
      type: 'text',
      metadata: {
        intent: 'welcome',
        confidence: 1.0,
      },
    };

    setMessages(prev => [...prev, aiMessage]);
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !currentSession || isLoading) return;

    const userMessage= {
      id: `user_${Date.now()}`,
      sender: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString(),
      type: 'text',
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await InsuranceAPIService.sendChatMessage(
        currentSession.id,
        inputMessage.trim()
      );

      if (response.success && response.data) {
        setTimeout(() => {
          setMessages(prev => [...prev, response.data!]);
          setIsTyping(false);
        }, 1500); // Simulate AI thinking time
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      setIsTyping(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickAction = (action=> {
    setInputMessage(action);
    if (currentSession) {
      setTimeout(() => sendMessage(), 100);
    }
  };

  const escalateToHuman = async () => {
    if (!currentSession) return;

    try {
      const response = await InsuranceAPIService.escalateToHuman(
        currentSession.id,
        'Customer requested human assistance'
      );

      if (response.success && response.data) {
        setCurrentSession(response.data);
        const escalationMessage= {
          id: `escalation_${Date.now()}`,
          sender: 'ai',
          content: 'I\'m connecting you with a human agent. Please wait a moment...',
          timestamp: new Date().toISOString(),
          type: 'text',
        };
        setMessages(prev => [...prev, escalationMessage]);
      }
    } catch (error) {
      console.error('Failed to escalate to human:', error);
    }
  };

  const loadPreviousSession = async (session=> {
    try {
      setIsLoading(true);
      const response = await InsuranceAPIService.getChatSession(session.id);

      if (response.success && response.data) {
        setCurrentSession(response.data);
        setMessages(response.data.messages || []);
      }
    } catch (error) {
      console.error('Failed to load previous session:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!currentSession) {
    return (
      <div className={`max-w-6xl mx-auto p-6 ${className}`}>
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Customer Support</h1>
          <p className="text-gray-600">
            Get instant help with our AI-powered support system, available 24/7
          </p>
        </div>

        {/* Support Categories */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {supportCategories.map((category) => {
            const IconComponent = category.icon;
            return (
              <motion.div
                key={category.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="bg-white rounded-xl shadow-lg p-6 cursor-pointer border-2 border-transparent hover:border-blue-500 transition-all"
                onClick={() => startNewSession(category.id)}
              >
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                    <IconComponent className="w-6 h-6 text-blue-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">{category.name}</h3>
                </div>
                <p className="text-gray-600 text-sm">
                  Get instant help with {category.name.toLowerCase()}
                </p>
              </motion.div>
            );
          })}
        </div>

        {/* Recent Sessions */}
        {sessionHistory.length > 0 && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Conversations</h2>
            <div className="space-y-3">
              {sessionHistory.slice(0, 3).map((session) => (
                <div
                  key={session.id}
                  className="bg-white rounded-lg p-4 shadow-md hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => loadPreviousSession(session)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium text-gray-900 capitalize">
                        {session.category} Support
                      </h3>
                      <p className="text-sm text-gray-600">
                        {new Date(session.startTime).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="flex items-center">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium ${
                          session.status === 'resolved'
                            ? 'bg-green-100 text-green-800'
                            === 'active'
                            ? 'bg-blue-100 text-blue-800'
                            : 'bg-gray-100 text-gray-800'
                        }`}
                      >
                        {session.status}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Emergency Contact */}
        <div className="bg-red-50 border border-red-200 rounded-xl p-6">
          <div className="flex items-start">
            <PhoneIcon className="w-6 h-6 text-red-600 mr-3 mt-1" />
            <div>
              <h3 className="text-lg font-semibold text-red-900 mb-2">Emergency Support</h3>
              <p className="text-red-700 mb-4">
                For medical emergencies, call 911 immediately. For urgent insurance matters outside
                business hours, our 24/7 emergency line is available.
              </p>
              <button className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
                Call Emergency Line
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`max-w-4xl mx-auto p-6 ${className}`}>
      <div className="bg-white rounded-xl shadow-lg h-[600px] flex flex-col">
        {/* Chat Header */}
        <div className="border-b border-gray-200 p-4 flex items-center justify-between">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center mr-3">
              <ChatBubbleLeftEllipsisIcon className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">GIVC AI Assistant</h3>
              <p className="text-sm text-gray-600 capitalize">{currentSession.category} Support</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {currentSession.status !== 'escalated' && (
              <button
                onClick={escalateToHuman}
                className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                Talk to Human
              </button>
            )}
            <button
              onClick={() => setCurrentSession(null)}
              className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              New Chat
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.sender === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-900'
                  }`}
                >
                  <p className="text-sm">{message.content}</p>
                  <p className="text-xs mt-1 opacity-70">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-gray-100 px-4 py-2 rounded-lg">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Quick Actions */}
        {messages.length <= 1 && (
          <div className="px-4 py-2 border-t border-gray-100">
            <p className="text-sm text-gray-600 mb-2">Quick actions:</p>
            <div className="flex flex-wrap gap-2">
              {quickActions.slice(0, 3).map((action) => (
                <button
                  key={action}
                  onClick={() => handleQuickAction(action)}
                  className="px-3 py-1 text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 rounded-full transition-colors"
                >
                  {action}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex items-center space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Type your message..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !inputMessage.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white p-2 rounded-lg transition-colors"
              title="Send message"
              aria-label="Send message"
            >
              <PaperAirplaneIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerSupport;
