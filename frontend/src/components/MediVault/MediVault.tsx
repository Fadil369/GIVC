import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { MedicalFile, FileCategory, ProcessingStatus } from '@/types';
import {
  CloudArrowUpIcon,
  FolderIcon,
  EyeIcon,
  ArrowDownTrayIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  Bars3Icon,
  Squares2X2Icon,
} from '@heroicons/react/24/outline';

const MediVault: React.FC = () => {
  const [files, setFiles] = useState<MedicalFile[]>([
    {
      id: '1',
      name: 'chest_xray_001.dcm',
      type: 'dicom',
      size: 2048576,
      uploadedAt: new Date('2024-01-15'),
      uploadedBy: 'Dr. Smith',
      category: 'radiology',
      status: 'completed',
      complianceStatus: 'compliant',
      metadata: {
        patientId: 'PT-001',
        studyDate: new Date('2024-01-15'),
        modality: 'CR',
        bodyPart: 'Chest',
        physician: 'Dr. Smith',
      },
    },
    {
      id: '2',
      name: 'lab_results_CBC.pdf',
      type: 'lab_result',
      size: 1024768,
      uploadedAt: new Date('2024-01-14'),
      uploadedBy: 'Lab Tech',
      category: 'laboratory',
      status: 'processing',
      complianceStatus: 'compliant',
      metadata: {
        patientId: 'PT-002',
        studyDate: new Date('2024-01-14'),
      },
    },
    {
      id: '3',
      name: 'clinical_notes_consultation.pdf',
      type: 'clinical_note',
      size: 512384,
      uploadedAt: new Date('2024-01-13'),
      uploadedBy: 'Dr. Johnson',
      category: 'clinical',
      status: 'completed',
      complianceStatus: 'compliant',
    },
  ]);
  
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedCategory, setSelectedCategory] = useState<FileCategory | 'all'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [uploading, setUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setUploading(true);
    
    // Simulate file upload
    acceptedFiles.forEach((file) => {
      const newFile: MedicalFile = {
        id: Date.now().toString(),
        name: file.name,
        type: file.name.includes('.dcm') ? 'dicom' : 
              file.name.includes('lab') ? 'lab_result' : 'clinical_note',
        size: file.size,
        uploadedAt: new Date(),
        uploadedBy: 'Current User',
        category: file.name.includes('.dcm') ? 'radiology' : 
                  file.name.includes('lab') ? 'laboratory' : 'clinical',
        status: 'uploading',
        complianceStatus: 'compliant',
      };
      
      setFiles(prev => [...prev, newFile]);
      
      // Simulate processing
      setTimeout(() => {
        setFiles(prev => prev.map(f => 
          f.id === newFile.id ? { ...f, status: 'processing' as ProcessingStatus } : f
        ));
      }, 1000);
      
      setTimeout(() => {
        setFiles(prev => prev.map(f => 
          f.id === newFile.id ? { ...f, status: 'completed' as ProcessingStatus } : f
        ));
      }, 3000);
    });
    
    setTimeout(() => setUploading(false), 1000);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/dicom': ['.dcm'],
      'application/pdf': ['.pdf'],
      'image/*': ['.jpg', '.jpeg', '.png', '.tiff'],
      'text/*': ['.txt', '.hl7'],
    },
    maxSize: 100 * 1024 * 1024, // 100MB
  });

  const filteredFiles = files.filter(file => {
    const matchesCategory = selectedCategory === 'all' || file.category === selectedCategory;
    const matchesSearch = file.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         file.metadata?.patientId?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const getFileIcon = (file: MedicalFile) => {
    switch (file.type) {
      case 'dicom':
        return '📷'; // Medical imaging
      case 'lab_result':
        return '🧪'; // Lab test
      case 'clinical_note':
        return '📋'; // Clinical notes
      default:
        return '📄'; // Generic document
    }
  };

  const getStatusColor = (status: ProcessingStatus) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'processing':
        return 'text-blue-600 bg-blue-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'uploading':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const formatFileSize = (bytes: number) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">MediVault</h1>
          <p className="text-gray-600">Secure medical file management and analysis</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
            🔒 HIPAA Compliant
          </span>
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
            🔐 AES-256 Encrypted
          </span>
        </div>
      </div>

      {/* Upload Zone */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer
          ${isDragActive 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${uploading ? 'opacity-50 pointer-events-none' : ''}
        `}
      >
        <input {...getInputProps()} />
        <CloudArrowUpIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        
        {uploading ? (
          <div>
            <div className="loading-spinner w-8 h-8 mx-auto mb-4"></div>
            <p className="text-lg font-medium text-gray-900">Uploading files...</p>
            <p className="text-gray-600">Encrypting and processing your medical data</p>
          </div>
        ) : isDragActive ? (
          <div>
            <p className="text-lg font-medium text-primary-700">Drop files here</p>
            <p className="text-primary-600">Release to upload to MediVault</p>
          </div>
        ) : (
          <div>
            <p className="text-lg font-medium text-gray-900">
              Drag & drop medical files here, or click to select
            </p>
            <p className="text-gray-600 mt-2">
              Supports: DICOM (.dcm), PDF, Images, HL7, and more
            </p>
            <p className="text-sm text-gray-500 mt-2">
              Maximum file size: 100MB per file
            </p>
          </div>
        )}
      </div>

      {/* Filters and Search */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
        <div className="flex flex-1 items-center space-x-4">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search files, patients, or metadata..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          {/* Category Filter */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value as FileCategory | 'all')}
            className="form-select"
          >
            <option value="all">All Categories</option>
            <option value="radiology">Radiology</option>
            <option value="laboratory">Laboratory</option>
            <option value="clinical">Clinical</option>
            <option value="administrative">Administrative</option>
            <option value="billing">Billing</option>
          </select>
        </div>

        {/* View Toggle */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setViewMode('grid')}
            className={`p-2 rounded-md ${viewMode === 'grid' ? 'bg-primary-100 text-primary-700' : 'text-gray-400 hover:text-gray-600'}`}
          >
            <Squares2X2Icon className="h-5 w-5" />
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`p-2 rounded-md ${viewMode === 'list' ? 'bg-primary-100 text-primary-700' : 'text-gray-400 hover:text-gray-600'}`}
          >
            <Bars3Icon className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Files Display */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        {filteredFiles.length === 0 ? (
          <div className="text-center py-12">
            <FolderIcon className="mx-auto h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No files found</h3>
            <p className="text-gray-600">
              {searchTerm || selectedCategory !== 'all' 
                ? 'Try adjusting your search or filters'
                : 'Upload your first medical file to get started'
              }
            </p>
          </div>
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 p-6">
            {filteredFiles.map((file) => (
              <div key={file.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-3">
                  <div className="text-2xl">{getFileIcon(file)}</div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(file.status)}`}>
                    {file.status}
                  </span>
                </div>
                
                <h4 className="font-medium text-gray-900 truncate mb-2" title={file.name}>
                  {file.name}
                </h4>
                
                <div className="text-sm text-gray-500 space-y-1">
                  <div>Size: {formatFileSize(file.size)}</div>
                  <div>Category: {file.category}</div>
                  {file.metadata?.patientId && (
                    <div>Patient: {file.metadata.patientId}</div>
                  )}
                  <div>Uploaded: {file.uploadedAt.toLocaleDateString()}</div>
                </div>
                
                <div className="flex items-center justify-between mt-4 pt-3 border-t border-gray-200">
                  <div className="flex items-center space-x-2">
                    <button className="p-1 text-gray-400 hover:text-primary-600">
                      <EyeIcon className="h-4 w-4" />
                    </button>
                    <button className="p-1 text-gray-400 hover:text-blue-600">
                      <ArrowDownTrayIcon className="h-4 w-4" />
                    </button>
                    <button className="p-1 text-gray-400 hover:text-red-600">
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                  <div className={`w-2 h-2 rounded-full ${file.complianceStatus === 'compliant' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    File
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Category
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Size
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Uploaded
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredFiles.map((file) => (
                  <tr key={file.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="text-lg mr-3">{getFileIcon(file)}</div>
                        <div>
                          <div className="text-sm font-medium text-gray-900">
                            {file.name}
                          </div>
                          {file.metadata?.patientId && (
                            <div className="text-sm text-gray-500">
                              Patient: {file.metadata.patientId}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                        {file.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(file.status)} capitalize`}>
                        {file.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatFileSize(file.size)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {file.uploadedAt.toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex items-center space-x-2">
                        <button className="text-primary-600 hover:text-primary-900">
                          <EyeIcon className="h-4 w-4" />
                        </button>
                        <button className="text-blue-600 hover:text-blue-900">
                          <ArrowDownTrayIcon className="h-4 w-4" />
                        </button>
                        <button className="text-red-600 hover:text-red-900">
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card text-center">
          <div className="text-2xl font-bold text-primary-600">{files.length}</div>
          <div className="text-sm text-gray-600">Total Files</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-secondary-600">
            {formatFileSize(files.reduce((sum, f) => sum + f.size, 0))}
          </div>
          <div className="text-sm text-gray-600">Total Storage</div>
        </div>
        <div className="card text-center">
          <div className="text-2xl font-bold text-green-600">
            {files.filter(f => f.complianceStatus === 'compliant').length}
          </div>
          <div className="text-sm text-gray-600">Compliant Files</div>
        </div>
      </div>
    </div>
  );
};

export default MediVault;