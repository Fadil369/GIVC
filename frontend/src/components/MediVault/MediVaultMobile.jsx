import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const MediVaultMobile = () => {
  const [activeTab, setActiveTab] = useState('upload');
  const [files, setFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [uploadProgress, setUploadProgress] = useState({});
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const fileInputRef = useRef();

  // Mock file data with realistic medical documents
  useEffect(() => {
    setFiles([
      {
        id: 1,
        name: 'Chest X-Ray Report - Jan 2025.pdf',
        type: 'pdf',
        size: '2.4 MB',
        date: '2025-01-15',
        category: 'radiology',
        patient: 'John Smith',
        status: 'processed',
        thumbnail: '🩻',
        encrypted: true,
        aiAnalyzed: true,
        tags: ['chest', 'x-ray', 'routine']
      },
      {
        id: 2,
        name: 'Blood Test Results - Jan 2025.pdf',
        type: 'pdf',
        size: '1.2 MB',
        date: '2025-01-14',
        category: 'laboratory',
        patient: 'Sarah Johnson',
        status: 'pending',
        thumbnail: '🩸',
        encrypted: true,
        aiAnalyzed: false,
        tags: ['blood', 'chemistry', 'routine']
      },
      {
        id: 3,
        name: 'MRI Brain Scan - Dec 2024.dcm',
        type: 'dicom',
        size: '45.7 MB',
        date: '2024-12-28',
        category: 'radiology',
        patient: 'Michael Brown',
        status: 'processed',
        thumbnail: '🧠',
        encrypted: true,
        aiAnalyzed: true,
        tags: ['mri', 'brain', 'neurology']
      },
      {
        id: 4,
        name: 'ECG Reading - Jan 2025.txt',
        type: 'txt',
        size: '156 KB',
        date: '2025-01-13',
        category: 'cardiology',
        patient: 'Emma Davis',
        status: 'processed',
        thumbnail: '💓',
        encrypted: true,
        aiAnalyzed: true,
        tags: ['ecg', 'cardiac', 'rhythm']
      },
      {
        id: 5,
        name: 'Insurance Claim - CLM-2025-001.pdf',
        type: 'pdf',
        size: '890 KB',
        date: '2025-01-10',
        category: 'insurance',
        patient: 'Robert Wilson',
        status: 'approved',
        thumbnail: '📋',
        encrypted: true,
        aiAnalyzed: true,
        tags: ['claim', 'approved', 'surgery']
      }
    ]);
  }, []);

  const fileTypes = {
    pdf: { color: 'text-red-600 bg-red-50', icon: '📄' },
    dicom: { color: 'text-blue-600 bg-blue-50', icon: '🏥' },
    txt: { color: 'text-gray-600 bg-gray-50', icon: '📝' },
    jpg: { color: 'text-green-600 bg-green-50', icon: '🖼️' },
    png: { color: 'text-green-600 bg-green-50', icon: '🖼️' }
  };

  const categories = [
    { id: 'all', name: 'All Files', icon: '📁', count: files.length },
    { id: 'radiology', name: 'Radiology', icon: '🩻', count: files.filter(f => f.category === 'radiology').length },
    { id: 'laboratory', name: 'Laboratory', icon: '🧪', count: files.filter(f => f.category === 'laboratory').length },
    { id: 'cardiology', name: 'Cardiology', icon: '💓', count: files.filter(f => f.category === 'cardiology').length },
    { id: 'insurance', name: 'Insurance', icon: '📋', count: files.filter(f => f.category === 'insurance').length }
  ];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

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
      
      // Start upload simulation
      setUploadProgress(prev => ({ ...prev, [fileId]: 0 }));
      
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          const currentProgress = prev[fileId] || 0;
          if (currentProgress >= 100) {
            clearInterval(interval);
            
            // Add to files list
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
                tags: ['new', 'unprocessed']
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
      }, 200);
    });
  };

  const filteredFiles = files.filter(file => {
    const matchesSearch = file.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         file.patient.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         file.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesFilter = filterType === 'all' || file.category === filterType;
    return matchesSearch && matchesFilter;
  });

  const getStatusColor = (status) => {
    const colors = {
      processed: 'bg-green-100 text-green-800',
      processing: 'bg-yellow-100 text-yellow-800',
      pending: 'bg-blue-100 text-blue-800',
      approved: 'bg-green-100 text-green-800',
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50">
      <div className="px-4 py-6 lg:px-8 lg:py-8 max-w-7xl mx-auto">
        {/* Header - Mobile Optimized */}
        <div className="mb-6 lg:mb-8">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between">
            <div className="mb-4 lg:mb-0">
              <h1 className="text-2xl lg:text-3xl font-bold text-gray-900 flex items-center">
                <span className="text-3xl lg:text-4xl mr-3">🗂️</span>
                MediVault
              </h1>
              <p className="text-sm lg:text-base text-gray-600 mt-1">
                Secure medical document storage with AI-powered analysis
              </p>
            </div>
            <div className="flex items-center space-x-2 lg:space-x-4">
              <div className="flex items-center space-x-2 px-3 py-2 bg-green-50 border border-green-200 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs lg:text-sm font-medium text-green-700">Secure & Encrypted</span>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Overview - Mobile Grid */}
        <div className="grid grid-cols-2 lg:grid-cols-6 gap-3 lg:gap-4 mb-6 lg:mb-8">
          {[
            { label: 'Total Files', value: stats.totalFiles, icon: '📁', color: 'bg-blue-50 text-blue-600' },
            { label: 'Storage Used', value: `${stats.totalSize} MB`, icon: '💾', color: 'bg-purple-50 text-purple-600' },
            { label: 'Encrypted', value: stats.encrypted, icon: '🔒', color: 'bg-green-50 text-green-600' },
            { label: 'AI Analyzed', value: stats.aiAnalyzed, icon: '🤖', color: 'bg-yellow-50 text-yellow-600' },
            { label: 'Processed', value: stats.processed, icon: '✅', color: 'bg-green-50 text-green-600' },
            { label: 'Pending', value: stats.pending, icon: '⏳', color: 'bg-orange-50 text-orange-600' }
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white/80 backdrop-blur-sm rounded-xl p-3 lg:p-4 shadow-sm border border-gray-200/50"
            >
              <div className={`w-8 h-8 lg:w-10 lg:h-10 ${stat.color} rounded-lg flex items-center justify-center mb-2`}>
                <span className="text-sm lg:text-base">{stat.icon}</span>
              </div>
              <p className="text-lg lg:text-xl font-bold text-gray-900">{stat.value}</p>
              <p className="text-xs lg:text-sm text-gray-600">{stat.label}</p>
            </motion.div>
          ))}
        </div>

        {/* Tab Navigation */}
        <div className="mb-6">
          <div className="flex overflow-x-auto pb-2 scrollbar-hide">
            <div className="flex space-x-2 lg:space-x-4 min-w-max">
              {[
                { id: 'upload', name: 'Upload', icon: '⬆️' },
                { id: 'files', name: 'Files', icon: '📁' },
                { id: 'analytics', name: 'Analytics', icon: '📊' },
                { id: 'settings', name: 'Settings', icon: '⚙️' }
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 py-2 lg:px-6 lg:py-3 rounded-lg font-medium text-sm lg:text-base transition-all duration-200 whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'bg-white text-blue-700 shadow-md border border-blue-200'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-white/50'
                  }`}
                >
                  <span>{tab.icon}</span>
                  <span>{tab.name}</span>
                </button>
              ))}
            </div>
          </div>
        </div>

        <AnimatePresence mode="wait">
          {/* Upload Tab */}
          {activeTab === 'upload' && (
            <motion.div
              key="upload"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* File Upload Area */}
              <div className="bg-white/80 backdrop-blur-sm rounded-xl lg:rounded-2xl p-6 lg:p-8 shadow-sm border border-gray-200/50">
                <div
                  className={`relative border-2 border-dashed rounded-xl lg:rounded-2xl p-8 lg:p-12 text-center transition-all ${
                    dragActive
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
                  }`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
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
                  
                  <div className="text-4xl lg:text-6xl mb-4">📤</div>
                  <h3 className="text-lg lg:text-xl font-semibold text-gray-900 mb-2">
                    Drop medical files here or click to browse
                  </h3>
                  <p className="text-sm lg:text-base text-gray-600 mb-4">
                    Supports PDF, DICOM, JPG, PNG, TXT files up to 100MB
                  </p>
                  
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                  >
                    Select Files
                  </button>
                  
                  <div className="mt-6 grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600">
                    <div className="flex items-center justify-center space-x-2">
                      <span className="text-green-500">🔒</span>
                      <span>End-to-end Encrypted</span>
                    </div>
                    <div className="flex items-center justify-center space-x-2">
                      <span className="text-blue-500">🤖</span>
                      <span>AI Analysis</span>
                    </div>
                    <div className="flex items-center justify-center space-x-2">
                      <span className="text-purple-500">⚡</span>
                      <span>Instant Processing</span>
                    </div>
                    <div className="flex items-center justify-center space-x-2">
                      <span className="text-yellow-500">🛡️</span>
                      <span>HIPAA Compliant</span>
                    </div>
                  </div>
                </div>

                {/* Upload Progress */}
                {Object.keys(uploadProgress).length > 0 && (
                  <div className="mt-6 space-y-3">
                    <h4 className="font-medium text-gray-900">Uploading Files</h4>
                    {Object.entries(uploadProgress).map(([fileId, progress]) => (
                      <div key={fileId} className="bg-gray-50 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">Uploading...</span>
                          <span className="text-sm text-gray-600">{Math.round(progress)}%</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                            style={{ width: `${progress}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>
          )}

          {/* Files Tab */}
          {activeTab === 'files' && (
            <motion.div
              key="files"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="space-y-6"
            >
              {/* Search and Filter */}
              <div className="bg-white/80 backdrop-blur-sm rounded-xl p-4 lg:p-6 shadow-sm border border-gray-200/50">
                <div className="flex flex-col lg:flex-row gap-4">
                  <div className="flex-1">
                    <div className="relative">
                      <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">🔍</span>
                      <input
                        type="text"
                        placeholder="Search files, patients, or tags..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                  
                  <div className="flex overflow-x-auto pb-2 lg:pb-0 space-x-2 lg:space-x-0">
                    {categories.map((category) => (
                      <button
                        key={category.id}
                        onClick={() => setFilterType(category.id)}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition-all ${
                          filterType === category.id
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        <span>{category.icon}</span>
                        <span>{category.name}</span>
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          filterType === category.id ? 'bg-blue-500' : 'bg-gray-300'
                        }`}>
                          {category.count}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              </div>

              {/* Files Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4 lg:gap-6">
                {filteredFiles.map((file) => (
                  <motion.div
                    key={file.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-white/80 backdrop-blur-sm rounded-xl p-4 lg:p-6 shadow-sm border border-gray-200/50 hover:shadow-lg hover:border-gray-300/50 transition-all group cursor-pointer"
                  >
                    {/* File Header */}
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <div className={`w-10 h-10 lg:w-12 lg:h-12 ${fileTypes[file.type]?.color || 'bg-gray-50 text-gray-600'} rounded-lg flex items-center justify-center`}>
                          <span className="text-lg">{file.thumbnail}</span>
                        </div>
                        <div className="min-w-0 flex-1">
                          <h3 className="font-medium text-gray-900 text-sm lg:text-base truncate group-hover:text-blue-600 transition-colors">
                            {file.name}
                          </h3>
                          <p className="text-xs lg:text-sm text-gray-600">{file.size}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-1">
                        {file.encrypted && <span className="text-green-500" title="Encrypted">🔒</span>}
                        {file.aiAnalyzed && <span className="text-blue-500" title="AI Analyzed">🤖</span>}
                      </div>
                    </div>

                    {/* File Info */}
                    <div className="space-y-2 mb-4">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Patient:</span>
                        <span className="font-medium text-gray-900">{file.patient}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Date:</span>
                        <span className="text-gray-900">{file.date}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">Status:</span>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(file.status)}`}>
                          {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                        </span>
                      </div>
                    </div>

                    {/* Tags */}
                    <div className="flex flex-wrap gap-1 mb-4">
                      {file.tags.slice(0, 3).map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
                        >
                          {tag}
                        </span>
                      ))}
                      {file.tags.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          +{file.tags.length - 3}
                        </span>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex space-x-2">
                      <button className="flex-1 px-3 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors">
                        View
                      </button>
                      <button className="px-3 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 transition-colors">
                        Share
                      </button>
                      <button className="px-3 py-2 bg-gray-100 text-gray-700 text-sm rounded-lg hover:bg-gray-200 transition-colors">
                        ⋯
                      </button>
                    </div>
                  </motion.div>
                ))}
              </div>

              {filteredFiles.length === 0 && (
                <div className="bg-white/80 backdrop-blur-sm rounded-xl p-8 lg:p-12 shadow-sm border border-gray-200/50 text-center">
                  <div className="text-4xl lg:text-6xl mb-4">📁</div>
                  <h3 className="text-lg lg:text-xl font-semibold text-gray-900 mb-2">No files found</h3>
                  <p className="text-gray-600 mb-6">Try adjusting your search or filter criteria</p>
                  <button
                    onClick={() => {
                      setSearchTerm('');
                      setFilterType('all');
                    }}
                    className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Clear Filters
                  </button>
                </div>
              )}
            </motion.div>
          )}

          {/* Other tabs placeholder */}
          {(activeTab === 'analytics' || activeTab === 'settings') && (
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="bg-white/80 backdrop-blur-sm rounded-xl lg:rounded-2xl p-8 lg:p-12 shadow-sm border border-gray-200/50 text-center"
            >
              <div className="text-6xl lg:text-8xl mb-4">
                {activeTab === 'analytics' ? '📊' : '⚙️'}
              </div>
              <h2 className="text-xl lg:text-2xl font-bold text-gray-900 mb-2">
                {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)} Dashboard
              </h2>
              <p className="text-gray-600 mb-6">
                Advanced {activeTab} features coming soon
              </p>
              <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                Explore {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default MediVaultMobile;
