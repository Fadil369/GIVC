import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const MediVaultProfessional = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [files, setFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const fileInputRef = useRef();

  // Professional medical document data
  useEffect(() => {
    setFiles([
      {
        id: 1,
        name: 'Chest X-Ray Analysis Report',
        type: 'pdf',
        size: '2.4 MB',
        date: '2025-01-15',
        category: 'radiology',
        patient: 'Dr. Sarah Johnson',
        status: 'processed',
        thumbnail: '🩻',
        encrypted: true,
        aiAnalyzed: true,
        tags: ['chest', 'x-ray', 'diagnostic'],
        priority: 'normal'
      },
      {
        id: 2,
        name: 'Comprehensive Blood Panel Results',
        type: 'pdf',
        size: '1.8 MB',
        date: '2025-01-14',
        category: 'laboratory',
        patient: 'Dr. Michael Chen',
        status: 'pending',
        thumbnail: '🩸',
        encrypted: true,
        aiAnalyzed: false,
        tags: ['blood', 'chemistry', 'metabolic'],
        priority: 'high'
      },
      {
        id: 3,
        name: 'MRI Brain Imaging Study',
        type: 'dicom',
        size: '45.7 MB',
        date: '2024-12-28',
        category: 'radiology',
        patient: 'Dr. Emily Rodriguez',
        status: 'processed',
        thumbnail: '🧠',
        encrypted: true,
        aiAnalyzed: true,
        tags: ['mri', 'brain', 'neurology'],
        priority: 'urgent'
      },
      {
        id: 4,
        name: 'Cardiac ECG Analysis',
        type: 'pdf',
        size: '956 KB',
        date: '2025-01-13',
        category: 'cardiology',
        patient: 'Dr. David Park',
        status: 'processed',
        thumbnail: '💓',
        encrypted: true,
        aiAnalyzed: true,
        tags: ['ecg', 'cardiac', 'rhythm'],
        priority: 'normal'
      },
      {
        id: 5,
        name: 'Insurance Claims Documentation',
        type: 'pdf',
        size: '1.2 MB',
        date: '2025-01-10',
        category: 'insurance',
        patient: 'Claims Department',
        status: 'approved',
        thumbnail: '📋',
        encrypted: true,
        aiAnalyzed: true,
        tags: ['claim', 'approved', 'reimbursement'],
        priority: 'normal'
      }
    ]);
  }, []);

  const fileTypeConfig = {
    pdf: { color: 'from-red-500 to-red-600', textColor: 'text-red-700', bgColor: 'bg-red-50' },
    dicom: { color: 'from-blue-500 to-blue-600', textColor: 'text-blue-700', bgColor: 'bg-blue-50' },
    txt: { color: 'from-gray-500 to-gray-600', textColor: 'text-gray-700', bgColor: 'bg-gray-50' },
    jpg: { color: 'from-green-500 to-green-600', textColor: 'text-green-700', bgColor: 'bg-green-50' },
    png: { color: 'from-green-500 to-green-600', textColor: 'text-green-700', bgColor: 'bg-green-50' }
  };

  const categories = [
    { id: 'all', name: 'All Documents', icon: '📁', count: files.length },
    { id: 'radiology', name: 'Radiology', icon: '🩻', count: files.filter(f => f.category === 'radiology').length },
    { id: 'laboratory', name: 'Laboratory', icon: '🧪', count: files.filter(f => f.category === 'laboratory').length },
    { id: 'cardiology', name: 'Cardiology', icon: '💓', count: files.filter(f => f.category === 'cardiology').length },
    { id: 'insurance', name: 'Insurance', icon: '📋', count: files.filter(f => f.category === 'insurance').length }
  ];

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFiles = (fileList) => {
    Array.from(fileList).forEach((file, index) => {
      const fileId = Date.now() + index;
      
      // Simulate upload with progress
      setUploadProgress(prev => ({ ...prev, [fileId]: 0 }));
      
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          const currentProgress = prev[fileId] || 0;
          if (currentProgress >= 100) {
            clearInterval(interval);
            
            // Add to files list after upload completes
            setTimeout(() => {
              const newFile = {
                id: fileId,
                name: file.name,
                type: file.name.split('.').pop().toLowerCase(),
                size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
                date: new Date().toISOString().split('T')[0],
                category: 'uncategorized',
                patient: 'Pending Classification',
                status: 'processing',
                thumbnail: '📄',
                encrypted: true,
                aiAnalyzed: false,
                tags: ['new', 'unprocessed'],
                priority: 'normal'
              };
              
              setFiles(prev => [newFile, ...prev]);
              setUploadProgress(prev => {
                const { [fileId]: removed, ...rest } = prev;
                return rest;
              });
            }, 500);
            return prev;
          }
          return { ...prev, [fileId]: currentProgress + Math.random() * 15 + 5 };
        });
      }, 150);
    });
  };

  const filteredFiles = files.filter(file => {
    const matchesSearch = file.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         file.patient.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         file.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesFilter = filterType === 'all' || file.category === filterType;
    return matchesSearch && matchesFilter;
  });

  const getPriorityColor = (priority) => {
    const colors = {
      urgent: 'bg-red-100 text-red-700 border-red-200',
      high: 'bg-orange-100 text-orange-700 border-orange-200',
      normal: 'bg-green-100 text-green-700 border-green-200'
    };
    return colors[priority] || colors.normal;
  };

  const getStatusColor = (status) => {
    const colors = {
      processed: 'bg-green-100 text-green-800',
      processing: 'bg-yellow-100 text-yellow-800',
      pending: 'bg-blue-100 text-blue-800',
      approved: 'bg-emerald-100 text-emerald-800',
      error: 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const stats = {
    totalFiles: files.length,
    totalSize: files.reduce((acc, file) => acc + parseFloat(file.size.replace(' MB', '').replace(' KB', '') / 1000), 0).toFixed(1),
    encrypted: files.filter(f => f.encrypted).length,
    aiAnalyzed: files.filter(f => f.aiAnalyzed).length,
    processed: files.filter(f => f.status === 'processed').length,
    pending: files.filter(f => f.status === 'pending' || f.status === 'processing').length
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30">
      <div className="p-8 lg:p-12 max-w-7xl mx-auto">
        {/* Header Section - Professional */}
        <div className="mb-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center lg:text-left"
          >
            <div className="flex items-center space-x-4 mb-6">
              <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-3xl flex items-center justify-center shadow-xl">
                <span className="text-3xl text-white">🗂️</span>
              </div>
              <div>
                <h1 className="text-4xl lg:text-5xl font-bold text-gray-900">
                  MediVault Professional
                </h1>
                <p className="text-xl text-gray-600 mt-2">
                  Secure, intelligent medical document management
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Statistics Overview - Professional Design */}
        <div className="grid grid-cols-2 lg:grid-cols-6 gap-6 mb-12">
          {[
            { label: 'Total Documents', value: stats.totalFiles, icon: '📁', gradient: 'from-blue-500 to-blue-600' },
            { label: 'Storage Used', value: `${stats.totalSize} MB`, icon: '💾', gradient: 'from-purple-500 to-purple-600' },
            { label: 'Encrypted Files', value: stats.encrypted, icon: '🔒', gradient: 'from-green-500 to-green-600' },
            { label: 'AI Analyzed', value: stats.aiAnalyzed, icon: '🤖', gradient: 'from-yellow-500 to-yellow-600' },
            { label: 'Processed', value: stats.processed, icon: '✅', gradient: 'from-emerald-500 to-emerald-600' },
            { label: 'Pending Review', value: stats.pending, icon: '⏳', gradient: 'from-orange-500 to-orange-600' }
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white/80 backdrop-blur-sm rounded-3xl p-6 shadow-xl border border-white/50 hover:shadow-2xl transition-all duration-300"
            >
              <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${stat.gradient} flex items-center justify-center mb-4 shadow-lg`}>
                <span className="text-xl text-white">{stat.icon}</span>
              </div>
              <p className="text-2xl lg:text-3xl font-bold text-gray-900 mb-2">{stat.value}</p>
              <p className="text-sm lg:text-base text-gray-600">{stat.label}</p>
            </motion.div>
          ))}
        </div>

        {/* Upload Section - Professional Design */}
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 lg:p-12 shadow-xl border border-white/50 mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Document Upload</h2>
          
          <div
            className={`relative border-2 border-dashed rounded-3xl p-12 text-center transition-all duration-300 ${
              dragActive
                ? 'border-blue-500 bg-blue-50/50'
                : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50/30'
            }`}
            onDragEnter={(e) => { e.preventDefault(); setDragActive(true); }}
            onDragLeave={(e) => { e.preventDefault(); setDragActive(false); }}
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              onChange={(e) => handleFiles(e.target.files)}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              accept=".pdf,.jpg,.jpeg,.png,.dcm,.txt,.doc,.docx"
            />
            
            <div className="text-6xl mb-6">📤</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Drop medical documents here or click to browse
            </h3>
            <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
              Supports PDF, DICOM, JPG, PNG, TXT files up to 100MB. All files are automatically encrypted and analyzed.
            </p>
            
            <button
              onClick={() => fileInputRef.current?.click()}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-semibold text-lg shadow-lg"
            >
              Select Files
            </button>
            
            <div className="mt-8 grid grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                { icon: '🔒', label: 'End-to-end Encrypted', color: 'text-green-600' },
                { icon: '🤖', label: 'AI Analysis', color: 'text-blue-600' },
                { icon: '⚡', label: 'Instant Processing', color: 'text-purple-600' },
                { icon: '🛡️', label: 'HIPAA Compliant', color: 'text-yellow-600' }
              ].map((feature, index) => (
                <div key={index} className="flex items-center justify-center space-x-3">
                  <span className="text-2xl">{feature.icon}</span>
                  <span className={`font-medium ${feature.color}`}>{feature.label}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Upload Progress */}
          {Object.keys(uploadProgress).length > 0 && (
            <div className="mt-8 space-y-4">
              <h4 className="text-xl font-bold text-gray-900">Uploading Files</h4>
              {Object.entries(uploadProgress).map(([fileId, progress]) => (
                <div key={fileId} className="bg-gray-50 rounded-2xl p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="font-medium text-gray-700">Processing...</span>
                    <span className="text-gray-600">{Math.round(progress)}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-300"
                      style={{ width: `${progress}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Search and Filter */}
        <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-xl border border-white/50 mb-12">
          <div className="flex flex-col lg:flex-row gap-6">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </div>
                <input
                  type="text"
                  placeholder="Search documents, patients, or tags..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-12 pr-6 py-4 text-lg border border-gray-300 rounded-2xl focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                />
              </div>
            </div>
            
            {/* Category Filters */}
            <div className="flex flex-wrap gap-3">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setFilterType(category.id)}
                  className={`flex items-center space-x-3 px-6 py-3 rounded-2xl font-semibold transition-all duration-300 ${
                    filterType === category.id
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <span className="text-lg">{category.icon}</span>
                  <span>{category.name}</span>
                  <span className={`px-2 py-1 rounded-full text-sm ${
                    filterType === category.id ? 'bg-white/20' : 'bg-gray-300'
                  }`}>
                    {category.count}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Documents Grid - Professional Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-8">
          {filteredFiles.map((file) => (
            <motion.div
              key={file.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="bg-white/80 backdrop-blur-sm rounded-3xl p-8 shadow-xl border border-white/50 hover:shadow-2xl hover:scale-105 transition-all duration-300 group cursor-pointer"
            >
              {/* File Header */}
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center space-x-4">
                  <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${fileTypeConfig[file.type]?.color || 'from-gray-500 to-gray-600'} flex items-center justify-center shadow-lg`}>
                    <span className="text-2xl text-white">{file.thumbnail}</span>
                  </div>
                  <div className="min-w-0 flex-1">
                    <h3 className="text-lg font-bold text-gray-900 mb-1 group-hover:text-blue-600 transition-colors">
                      {file.name}
                    </h3>
                    <p className="text-sm text-gray-600">{file.size}</p>
                  </div>
                </div>
                
                <div className="flex flex-col items-center space-y-2">
                  {file.encrypted && <span className="text-green-500 text-lg" title="Encrypted">🔒</span>}
                  {file.aiAnalyzed && <span className="text-blue-500 text-lg" title="AI Analyzed">🤖</span>}
                </div>
              </div>

              {/* File Details */}
              <div className="space-y-4 mb-6">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600">Provider:</span>
                  <span className="text-sm font-semibold text-gray-900">{file.patient}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600">Date:</span>
                  <span className="text-sm text-gray-900">{file.date}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600">Priority:</span>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold border ${getPriorityColor(file.priority)}`}>
                    {file.priority.toUpperCase()}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600">Status:</span>
                  <span className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusColor(file.status)}`}>
                    {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                  </span>
                </div>
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-2 mb-6">
                {file.tags.slice(0, 3).map((tag) => (
                  <span
                    key={tag}
                    className="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full"
                  >
                    {tag}
                  </span>
                ))}
                {file.tags.length > 3 && (
                  <span className="px-3 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">
                    +{file.tags.length - 3} more
                  </span>
                )}
              </div>

              {/* Actions */}
              <div className="flex space-x-3">
                <button className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-semibold">
                  View Document
                </button>
                <button className="px-4 py-3 bg-gray-100 text-gray-700 rounded-2xl hover:bg-gray-200 transition-colors">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                  </svg>
                </button>
              </div>
            </motion.div>
          ))}
        </div>

        {filteredFiles.length === 0 && (
          <div className="bg-white/80 backdrop-blur-sm rounded-3xl p-12 shadow-xl border border-white/50 text-center">
            <div className="text-6xl mb-6">📁</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-4">No documents found</h3>
            <p className="text-lg text-gray-600 mb-8">Try adjusting your search or filter criteria</p>
            <button
              onClick={() => {
                setSearchTerm('');
                setFilterType('all');
              }}
              className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-2xl hover:from-blue-700 hover:to-purple-700 transition-all duration-300 font-semibold text-lg"
            >
              Clear All Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MediVaultProfessional;
