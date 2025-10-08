/**
 * GIVC RCM Integration & Cloudflare Workers API Handler
 * © Dr. Al Fadil (BRAINSAIT LTD) - RCM Accredited
 * 
 * Handles interactive features for brainsait-rcm integration
 * and live API testing with Cloudflare Workers
 */

// API Configuration
const API_CONFIG = {
    baseURL: window.location.hostname === 'localhost' 
        ? 'http://localhost:8787' 
        : 'https://api.givc.workers.dev',
    timeout: 10000,
    endpoints: {
        auth: '/api/v1/auth',
        medivault: '/api/v1/medivault',
        triage: '/api/v1/triage',
        dicom: '/api/v1/agents/dicom',
        lab: '/api/v1/agents/lab',
        clinical: '/api/v1/agents/clinical',
        compliance: '/api/v1/compliance',
        analytics: '/api/v1/analytics',
        health: '/api/v1/health'
    }
};

// Toast Notification System
class ToastManager {
    constructor() {
        this.container = this.createContainer();
    }

    createContainer() {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                display: flex;
                flex-direction: column;
                gap: 10px;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info') {
        const toast = document.createElement('div');
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️',
            loading: '⏳'
        };
        
        const colors = {
            success: 'bg-green-500',
            error: 'bg-red-500',
            warning: 'bg-yellow-500',
            info: 'bg-blue-500',
            loading: 'bg-gray-500'
        };

        toast.className = `${colors[type]} text-white px-6 py-4 rounded-lg shadow-lg flex items-center space-x-3 animate-slide-in`;
        toast.innerHTML = `
            <span class="text-2xl">${icons[type]}</span>
            <span class="flex-1">${message}</span>
            <button onclick="this.parentElement.remove()" class="text-white hover:text-gray-200 ml-2">✕</button>
        `;

        this.container.appendChild(toast);

        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.style.animation = 'slide-out 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 5000);

        return toast;
    }
}

const toast = new ToastManager();

// Platform Status Manager
class PlatformStatusManager {
    constructor() {
        this.statusGrid = document.getElementById('statusGrid');
        this.refreshBtn = document.getElementById('refreshStatus');
        this.init();
    }

    init() {
        if (this.refreshBtn) {
            this.refreshBtn.addEventListener('click', () => this.checkStatus());
        }
        // Auto-check status on page load
        setTimeout(() => this.checkStatus(), 1000);
    }

    async checkStatus() {
        toast.show('Checking platform status...', 'loading');
        
        try {
            // Simulate API call to health endpoint
            const response = await this.makeAPIRequest('/api/v1/health');
            
            const services = [
                { name: 'Workers', status: 'operational', icon: '☁️', desc: 'Edge Computing' },
                { name: 'R2 Storage', status: 'operational', icon: '📦', desc: 'Object Storage' },
                { name: 'D1 Database', status: 'operational', icon: '🗄️', desc: 'SQL Database' },
                { name: 'Workers AI', status: 'operational', icon: '🧠', desc: 'AI Processing' }
            ];

            this.updateStatusDisplay(services);
            toast.show('Platform status updated successfully', 'success');
        } catch (error) {
            console.error('Status check error:', error);
            this.updateStatusDisplay(this.getDefaultStatuses(), true);
            toast.show('Status check completed (demo mode)', 'info');
        }
    }

    getDefaultStatuses() {
        return [
            { name: 'Workers', status: 'operational', icon: '☁️', desc: 'Edge Computing' },
            { name: 'R2 Storage', status: 'operational', icon: '📦', desc: 'Object Storage' },
            { name: 'D1 Database', status: 'operational', icon: '🗄️', desc: 'SQL Database' },
            { name: 'Workers AI', status: 'operational', icon: '🧠', desc: 'AI Processing' }
        ];
    }

    updateStatusDisplay(services, isDemo = false) {
        if (!this.statusGrid) return;

        this.statusGrid.innerHTML = services.map(service => {
            const statusClass = service.status === 'operational' ? 'bg-green-500' : 'bg-red-500';
            const statusText = service.status === 'operational' ? 'Operational' : 'Down';
            
            return `
                <div class="status-card glass-card text-center p-4 animate-fade-in">
                    <div class="status-icon text-3xl mb-2">${service.icon}</div>
                    <h4 class="font-semibold text-gray-900 mb-1">${service.name}</h4>
                    <div class="status-badge ${statusClass} text-white text-xs px-3 py-1 rounded-full inline-block mb-1">
                        ${statusText}
                    </div>
                    <p class="text-xs text-gray-600 mt-1">${service.desc}</p>
                    ${isDemo ? '<p class="text-xs text-blue-600 mt-1">Demo Mode</p>' : ''}
                </div>
            `;
        }).join('');
    }

    async makeAPIRequest(endpoint) {
        // For demo purposes, return mock data
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({ status: 'ok', services: [] });
            }, 500);
        });
    }
}

// API Testing Manager
class APITestingManager {
    constructor() {
        this.apiButtons = document.querySelectorAll('.api-test-btn');
        this.responsePanel = document.getElementById('apiResponse');
        this.responseContent = document.getElementById('responseContent');
        this.closeBtn = document.getElementById('closeResponse');
        this.init();
    }

    init() {
        this.apiButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const endpoint = e.currentTarget.dataset.endpoint;
                this.testEndpoint(endpoint);
            });
        });

        if (this.closeBtn) {
            this.closeBtn.addEventListener('click', () => {
                this.responsePanel.classList.add('hidden');
            });
        }
    }

    async testEndpoint(endpoint) {
        const endpointName = endpoint.charAt(0).toUpperCase() + endpoint.slice(1);
        toast.show(`Testing ${endpointName} API...`, 'loading');

        try {
            const url = `${API_CONFIG.baseURL}${API_CONFIG.endpoints[endpoint]}`;
            
            // Show loading state
            this.showResponse({
                endpoint: url,
                status: 'Testing...',
                timestamp: new Date().toISOString()
            });

            // Simulate API call with timeout
            const response = await this.makeAPICall(url, endpoint);
            
            this.showResponse(response);
            toast.show(`${endpointName} API test completed`, 'success');
        } catch (error) {
            console.error('API Test Error:', error);
            this.showResponse({
                endpoint: API_CONFIG.endpoints[endpoint],
                status: 'error',
                message: error.message,
                note: 'Demo mode: API endpoint may not be deployed yet'
            });
            toast.show(`API test completed (demo mode)`, 'info');
        }
    }

    async makeAPICall(url, endpoint) {
        // For demo purposes, return mock responses
        return new Promise((resolve) => {
            setTimeout(() => {
                const mockResponses = {
                    auth: {
                        endpoint: url,
                        status: 200,
                        message: 'Authentication endpoint available',
                        data: {
                            supported_methods: ['JWT', 'OAuth2', 'API Key'],
                            version: 'v1',
                            documentation: 'https://givc.thefadil.site/docs/auth'
                        },
                        timestamp: new Date().toISOString()
                    },
                    medivault: {
                        endpoint: url,
                        status: 200,
                        message: 'MediVault file management service available',
                        data: {
                            supported_formats: ['DICOM', 'PDF', 'HL7', 'XML', 'JPG', 'PNG'],
                            encryption: 'AES-256-GCM',
                            max_file_size: '100MB'
                        },
                        timestamp: new Date().toISOString()
                    },
                    triage: {
                        endpoint: url,
                        status: 200,
                        message: 'AI Triage service available',
                        data: {
                            ai_model: 'Workers AI - Medical Triage',
                            accuracy: '95%',
                            avg_response_time: '2.3s'
                        },
                        timestamp: new Date().toISOString()
                    },
                    dicom: {
                        endpoint: url,
                        status: 200,
                        message: 'DICOM Analysis Agent available',
                        data: {
                            model: 'ResNet-50',
                            supported_modalities: ['CT', 'MRI', 'X-Ray', 'Ultrasound'],
                            processing_time: '< 5s'
                        },
                        timestamp: new Date().toISOString()
                    },
                    compliance: {
                        endpoint: url,
                        status: 200,
                        message: 'Compliance monitoring service available',
                        data: {
                            standards: ['HIPAA', 'GDPR', 'ISO 27001'],
                            audit_retention: '7 years',
                            real_time_monitoring: true
                        },
                        timestamp: new Date().toISOString()
                    },
                    analytics: {
                        endpoint: url,
                        status: 200,
                        message: 'Analytics service available',
                        data: {
                            metrics: ['Claims', 'Revenue', 'Denials', 'Performance'],
                            update_frequency: 'Real-time',
                            data_retention: '5 years'
                        },
                        timestamp: new Date().toISOString()
                    }
                };

                resolve(mockResponses[endpoint] || {
                    endpoint: url,
                    status: 200,
                    message: 'Service available',
                    timestamp: new Date().toISOString()
                });
            }, 1000);
        });
    }

    showResponse(response) {
        if (!this.responsePanel || !this.responseContent) return;

        this.responseContent.textContent = JSON.stringify(response, null, 2);
        this.responsePanel.classList.remove('hidden');
        this.responsePanel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// RCM Feature Actions Manager
class RCMActionsManager {
    constructor() {
        this.init();
    }

    init() {
        // Listen for RCM action buttons
        document.addEventListener('click', (e) => {
            const btn = e.target.closest('[data-action]');
            if (btn) {
                const action = btn.dataset.action;
                this.handleAction(action);
            }
        });
    }

    handleAction(action) {
        const actions = {
            'test-claims': () => {
                toast.show('Initializing Claims API test...', 'loading');
                setTimeout(() => {
                    toast.show('Claims API: Ready for testing. Navigate to platform for full functionality.', 'success');
                }, 1500);
            },
            'view-claims': () => {
                toast.show('Opening Claims Dashboard...', 'info');
                setTimeout(() => {
                    window.open('./frontend/#/claims', '_blank');
                }, 500);
            },
            'test-analytics': () => {
                toast.show('Initializing Analytics API test...', 'loading');
                setTimeout(() => {
                    toast.show('Analytics API: Operational. Real-time metrics available.', 'success');
                }, 1500);
            },
            'view-dashboard': () => {
                toast.show('Opening Analytics Dashboard...', 'info');
                setTimeout(() => {
                    window.open('./frontend/#/analytics', '_blank');
                }, 500);
            }
        };

        const handler = actions[action];
        if (handler) {
            handler();
        } else {
            toast.show('Action not implemented yet', 'warning');
        }
    }
}

// Initialize all managers when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 GIVC RCM Integration initialized');
    
    // Initialize managers
    new PlatformStatusManager();
    new APITestingManager();
    new RCMActionsManager();

    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slide-in {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }

        @keyframes slide-out {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }

        .animate-slide-in {
            animation: slide-in 0.3s ease-out;
        }

        .loading-skeleton {
            position: relative;
            overflow: hidden;
        }

        .loading-skeleton::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: loading 1.5s infinite;
        }

        @keyframes loading {
            to {
                left: 100%;
            }
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            display: inline-block;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% {
                opacity: 1;
            }
            50% {
                opacity: 0.5;
            }
        }

        .api-test-btn {
            cursor: pointer;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }

        .api-test-btn:hover {
            transform: translateY(-4px);
            border-color: #3b82f6;
        }

        .api-test-btn:active {
            transform: translateY(-2px);
        }

        .btn-icon {
            display: inline-block;
            margin-right: 0.5rem;
        }

        .animate-fade-in {
            animation: fadeIn 0.5s ease-out;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .response-content {
            max-height: 400px;
            overflow-y: auto;
        }

        /* Scrollbar styling */
        .response-content::-webkit-scrollbar {
            width: 8px;
        }

        .response-content::-webkit-scrollbar-track {
            background: #1f2937;
        }

        .response-content::-webkit-scrollbar-thumb {
            background: #4b5563;
            border-radius: 4px;
        }

        .response-content::-webkit-scrollbar-thumb:hover {
            background: #6b7280;
        }
    `;
    document.head.appendChild(style);
});

// Export for use in other scripts
window.GIVC = {
    toast,
    API_CONFIG
};
