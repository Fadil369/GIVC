// ClaimLinc AI Workspace - Application Logic

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

// Application State
const appState = {
    currentView: 'dashboard',
    userData: {
        name: 'Dr. Fadil',
        role: 'Admin',
        branch: 'Main Office'
    },
    claimsData: [],
    notifications: [],
    tasks: []
};

// Initialize Application
function initializeApp() {
    setupNavigation();
    setupModalHandlers();
    setupNotifications();
    setupAIAssistant();
    setupCharts();
    setupSheetControls();
    setupExportHandlers();
    loadDashboardData();
    setupTaskManager();
    setupCollaboration();
    
    console.log('ClaimLinc AI Workspace initialized successfully');
}

// Navigation System
function setupNavigation() {
    const navItems = document.querySelectorAll('.nav-item');
    
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const viewName = item.getAttribute('data-view');
            switchView(viewName);
            
            // Update active nav item
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

function switchView(viewName) {
    // Hide all views
    document.querySelectorAll('.view').forEach(view => {
        view.classList.remove('active');
    });
    
    // Show selected view
    const targetView = document.getElementById(`${viewName}-view`);
    if (targetView) {
        targetView.classList.add('active');
        appState.currentView = viewName;
        
        // Load view-specific data
        loadViewData(viewName);
    }
}

function loadViewData(viewName) {
    switch(viewName) {
        case 'dashboard':
            loadDashboardData();
            break;
        case 'ai-analysis':
            runAIAnalysis();
            break;
        case 'reports':
            loadReports();
            break;
        case 'tasks':
            loadTasks();
            break;
    }
}

// Dashboard Data
function loadDashboardData() {
    // Simulate loading data from Google Sheets
    const mockData = {
        totalClaims: 1247,
        totalRejections: 89,
        approvedClaims: 1048,
        totalAmount: 3254780
    };
    
    // Update KPI cards
    document.getElementById('totalClaims').textContent = mockData.totalClaims.toLocaleString();
    document.getElementById('totalRejections').textContent = mockData.totalRejections.toLocaleString();
    document.getElementById('approvedClaims').textContent = mockData.approvedClaims.toLocaleString();
    document.getElementById('totalAmount').textContent = `SAR ${mockData.totalAmount.toLocaleString()}`;
    
    // Update charts
    updateCharts();
    
    // Load recent activity
    loadRecentActivity();
}

function loadRecentActivity() {
    const activities = [
        { icon: 'fa-file-medical', color: '#667eea', text: 'New claim submission from Riyadh branch', time: '5 min ago' },
        { icon: 'fa-exclamation-circle', color: '#f5576c', text: 'Rejection alert: 15 claims from Bupa require attention', time: '15 min ago' },
        { icon: 'fa-check-circle', color: '#43e97b', text: 'Resubmission successful: 23 claims approved', time: '1 hour ago' },
        { icon: 'fa-user-plus', color: '#4facfe', text: 'New team member added: Sarah Ahmed (Unaizah)', time: '2 hours ago' },
        { icon: 'fa-chart-line', color: '#f093fb', text: 'Monthly report generated and sent to stakeholders', time: '3 hours ago' }
    ];
    
    const activityList = document.getElementById('activityList');
    activityList.innerHTML = activities.map(activity => `
        <div class="activity-item">
            <div class="activity-icon" style="background: ${activity.color};">
                <i class="fas ${activity.icon}"></i>
            </div>
            <div>
                <p>${activity.text}</p>
                <span class="text-muted" style="font-size: 0.85rem;">${activity.time}</span>
            </div>
        </div>
    `).join('');
}

// Charts Setup
function setupCharts() {
    // This will be called when dashboard loads
}

function updateCharts() {
    // Payer Distribution Chart
    const payerCtx = document.getElementById('payerChart');
    if (payerCtx) {
        new Chart(payerCtx, {
            type: 'doughnut',
            data: {
                labels: ['Bupa Arabia', 'Tawuniya', 'GlobeMed', 'Others'],
                datasets: [{
                    data: [385, 428, 267, 167],
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(245, 87, 108, 0.8)',
                        'rgba(67, 233, 123, 0.8)',
                        'rgba(79, 172, 254, 0.8)'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // Monthly Trend Chart
    const trendCtx = document.getElementById('trendChart');
    if (trendCtx) {
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov'],
                datasets: [{
                    label: 'Approved Claims',
                    data: [850, 920, 880, 950, 1020, 980, 1050, 1100, 1080, 1150, 1048],
                    borderColor: 'rgba(67, 233, 123, 1)',
                    backgroundColor: 'rgba(67, 233, 123, 0.1)',
                    tension: 0.4,
                    fill: true
                }, {
                    label: 'Rejected Claims',
                    data: [120, 105, 95, 85, 90, 78, 82, 88, 75, 92, 89],
                    borderColor: 'rgba(245, 87, 108, 1)',
                    backgroundColor: 'rgba(245, 87, 108, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

// Sheet Controls
function setupSheetControls() {
    // Sheet tab switching
    const sheetTabs = document.querySelectorAll('.sheet-tab');
    sheetTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const sheetType = tab.getAttribute('data-sheet');
            
            // Update active tab
            sheetTabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            // Update active sheet
            document.querySelectorAll('.sheet-embed').forEach(sheet => {
                sheet.classList.remove('active');
            });
            document.getElementById(`sheet-${sheetType}`).classList.add('active');
        });
    });
    
    // Extract data button
    document.getElementById('extractDataBtn')?.addEventListener('click', extractSheetData);
    
    // Search and filters
    document.getElementById('sheetSearch')?.addEventListener('input', handleSheetSearch);
    document.getElementById('branchFilter')?.addEventListener('change', handleBranchFilter);
    document.getElementById('payerFilter')?.addEventListener('change', handlePayerFilter);
}

function extractSheetData() {
    // In a real implementation, this would use the Google Sheets API
    showNotification('Data extraction started. Processing...', 'info');
    
    setTimeout(() => {
        showNotification('Data extracted successfully! 1,247 records processed.', 'success');
    }, 2000);
}

function handleSheetSearch(e) {
    const searchTerm = e.target.value.toLowerCase();
    console.log('Searching for:', searchTerm);
    // Implement search logic here
}

function handleBranchFilter(e) {
    const branch = e.target.value;
    console.log('Filtering by branch:', branch);
    // Implement filter logic here
}

function handlePayerFilter(e) {
    const payer = e.target.value;
    console.log('Filtering by payer:', payer);
    // Implement filter logic here
}

// AI Assistant
function setupAIAssistant() {
    const aiAssistantBtn = document.getElementById('aiAssistantBtn');
    const modalChatInput = document.getElementById('modalChatInput');
    const modalSendBtn = document.getElementById('modalSendBtn');
    const chatInput = document.getElementById('chatInput');
    const sendChatBtn = document.getElementById('sendChatBtn');
    
    aiAssistantBtn?.addEventListener('click', () => {
        document.getElementById('aiAssistantModal').classList.add('active');
    });
    
    modalSendBtn?.addEventListener('click', () => sendAIMessage(modalChatInput));
    modalChatInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendAIMessage(modalChatInput);
    });
    
    sendChatBtn?.addEventListener('click', () => sendAIMessage(chatInput));
    chatInput?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendAIMessage(chatInput);
    });
    
    // Run analysis button
    document.getElementById('runAnalysisBtn')?.addEventListener('click', runAIAnalysis);
}

function sendAIMessage(inputElement) {
    const message = inputElement.value.trim();
    if (!message) return;
    
    // Add user message
    const chatContainer = inputElement.id.includes('modal') 
        ? document.getElementById('modalChatMessages')
        : document.getElementById('chatMessages');
    
    addChatMessage(chatContainer, message, 'user');
    inputElement.value = '';
    
    // Simulate AI response
    setTimeout(() => {
        const response = generateAIResponse(message);
        addChatMessage(chatContainer, response, 'bot');
    }, 1000);
}

function addChatMessage(container, message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${type}`;
    
    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="fas ${type === 'bot' ? 'fa-robot' : 'fa-user'}"></i>
        </div>
        <div class="message-content">
            <p>${message}</p>
        </div>
    `;
    
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function generateAIResponse(userMessage) {
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes('rejection') || lowerMessage.includes('reject')) {
        return `Based on the analysis of your claims data, the top rejection reasons are:
        
        1. **Missing Documentation** (32%) - Common in Bupa submissions
        2. **Invalid Diagnosis Codes** (24%) - Primarily from GlobeMed
        3. **Authorization Issues** (18%) - Tawuniya/Waseel related
        4. **Duplicate Claims** (15%) - Cross-branch submissions
        5. **Eligibility Verification Failed** (11%)
        
        Would you like me to generate a detailed report with recommendations?`;
    }
    
    if (lowerMessage.includes('bupa')) {
        return `Analyzing Bupa Arabia claims performance:
        
        - **Total Claims Submitted**: 385 (30.8% of total)
        - **Approval Rate**: 84.2%
        - **Average Processing Time**: 3.2 days
        - **Top Rejection Reason**: Missing prior authorization (42%)
        
        **Recommendation**: Implement pre-submission authorization check to reduce rejections by ~15%.`;
    }
    
    if (lowerMessage.includes('trend') || lowerMessage.includes('riyadh')) {
        return `Riyadh Branch Performance Trends:
        
        - **Monthly Claims**: 450-480 (38% of total)
        - **Approval Rate Trend**: ↗️ +8% over last quarter
        - **Revenue Impact**: SAR 1,234,560 (monthly average)
        - **Processing Efficiency**: 92% within 5 days
        
        The branch shows strong performance with improving trends.`;
    }
    
    return `I've analyzed your query. Here are the key insights:
    
    - Your overall claims approval rate is **84%**, which is above industry average
    - Monthly processing volume has increased by **12%** this quarter
    - **Riyadh branch** leads in performance metrics
    - Consider focusing on **documentation completeness** to improve approval rates
    
    How else can I help you analyze your claims data?`;
}

function runAIAnalysis() {
    const insightsContainer = document.getElementById('aiInsights');
    
    insightsContainer.innerHTML = '<p class="text-muted">Running AI analysis...</p>';
    
    setTimeout(() => {
        insightsContainer.innerHTML = `
            <div class="insight-card">
                <div class="insight-header">
                    <i class="fas fa-exclamation-circle"></i>
                    <span>Top Rejection Reasons</span>
                </div>
                <div class="insight-content">
                    <ol style="margin-left: 1.5rem; margin-top: 0.5rem;">
                        <li><strong>Missing Documentation</strong> - 32% of rejections</li>
                        <li><strong>Invalid Diagnosis Codes</strong> - 24% of rejections</li>
                        <li><strong>Authorization Issues</strong> - 18% of rejections</li>
                    </ol>
                </div>
            </div>
            
            <div class="insight-card">
                <div class="insight-header">
                    <i class="fas fa-chart-line"></i>
                    <span>Performance Trends</span>
                </div>
                <div class="insight-content">
                    <p>• Approval rate improved by <strong>8%</strong> this month</p>
                    <p>• Average processing time reduced to <strong>3.5 days</strong></p>
                    <p>• Riyadh branch leads with <strong>92% approval rate</strong></p>
                </div>
            </div>
            
            <div class="insight-card">
                <div class="insight-header">
                    <i class="fas fa-lightbulb"></i>
                    <span>AI Recommendations</span>
                </div>
                <div class="insight-content">
                    <p>• Implement pre-submission validation for documentation</p>
                    <p>• Provide ICD-10 coding training for Abha branch</p>
                    <p>• Automate authorization checks for Tawuniya claims</p>
                </div>
            </div>
        `;
    }, 1500);
}

// Modal Handlers
function setupModalHandlers() {
    const closeAiModal = document.getElementById('closeAiModal');
    const aiAssistantModal = document.getElementById('aiAssistantModal');
    
    closeAiModal?.addEventListener('click', () => {
        aiAssistantModal.classList.remove('active');
    });
    
    // Close modal on outside click
    aiAssistantModal?.addEventListener('click', (e) => {
        if (e.target === aiAssistantModal) {
            aiAssistantModal.classList.remove('active');
        }
    });
}

// Notifications
function setupNotifications() {
    const notificationBtn = document.getElementById('notificationBtn');
    const notificationPanel = document.getElementById('notificationPanel');
    const markAllRead = document.getElementById('markAllRead');
    
    notificationBtn?.addEventListener('click', () => {
        notificationPanel.classList.toggle('active');
    });
    
    markAllRead?.addEventListener('click', () => {
        document.querySelectorAll('.notification-item').forEach(item => {
            item.classList.remove('unread');
        });
        document.getElementById('notificationBadge').textContent = '0';
    });
    
    // Close notification panel when clicking outside
    document.addEventListener('click', (e) => {
        if (!notificationPanel.contains(e.target) && !notificationBtn.contains(e.target)) {
            notificationPanel.classList.remove('active');
        }
    });
}

function showNotification(message, type = 'info') {
    // Create a toast notification
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        position: fixed;
        top: 90px;
        right: 20px;
        background: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 3000;
        animation: slideInRight 0.3s ease-out;
    `;
    
    const icon = type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle';
    const color = type === 'success' ? '#43e97b' : type === 'error' ? '#ff4757' : '#4facfe';
    
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <i class="fas fa-${icon}" style="color: ${color}; font-size: 1.5rem;"></i>
            <p style="margin: 0;">${message}</p>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Task Manager
function setupTaskManager() {
    const addTaskBtn = document.getElementById('addTaskBtn');
    
    addTaskBtn?.addEventListener('click', () => {
        const taskTitle = prompt('Enter task title:');
        if (taskTitle) {
            addTask(taskTitle, 'todoTasks');
        }
    });
    
    // Load sample tasks
    loadSampleTasks();
}

function loadSampleTasks() {
    const tasks = [
        { title: 'Review Bupa rejections from last week', list: 'todoTasks', branch: 'Riyadh' },
        { title: 'Update authorization codes for Tawuniya', list: 'inProgressTasks', branch: 'Abha' },
        { title: 'Generate monthly performance report', list: 'doneTasks', branch: 'All' }
    ];
    
    tasks.forEach(task => addTask(task.title, task.list, task.branch));
}

function addTask(title, listId, branch = 'All') {
    const taskList = document.getElementById(listId);
    if (!taskList) return;
    
    const taskItem = document.createElement('div');
    taskItem.className = 'task-item';
    taskItem.innerHTML = `
        <h4 style="font-size: 0.95rem; margin-bottom: 0.5rem;">${title}</h4>
        <p style="font-size: 0.85rem; color: var(--text-secondary);">Branch: ${branch}</p>
        <div style="margin-top: 0.5rem; display: flex; gap: 0.5rem;">
            <button class="btn-text" style="font-size: 0.85rem;">Edit</button>
            <button class="btn-text" style="font-size: 0.85rem; color: var(--danger-color);">Delete</button>
        </div>
    `;
    
    taskList.appendChild(taskItem);
}

// Collaboration
function setupCollaboration() {
    const addCommentBtn = document.getElementById('addCommentBtn');
    
    addCommentBtn?.addEventListener('click', () => {
        const comment = prompt('Enter your comment:');
        if (comment) {
            addComment(comment);
        }
    });
    
    loadSampleComments();
}

function loadSampleComments() {
    const comments = [
        { user: 'Dr. Fadil', text: 'Reviewed the Bupa rejections. Most are due to missing documentation.', time: '10 min ago' },
        { user: 'Sarah Ahmed', text: 'Riyadh branch has completed all resubmissions for this week.', time: '1 hour ago' }
    ];
    
    const commentsList = document.getElementById('commentsList');
    commentsList.innerHTML = comments.map(comment => `
        <div class="activity-item">
            <div class="activity-icon" style="background: linear-gradient(135deg, #667eea, #764ba2);">
                <i class="fas fa-user"></i>
            </div>
            <div>
                <h4 style="font-size: 0.95rem; margin-bottom: 0.25rem;">${comment.user}</h4>
                <p style="margin-bottom: 0.5rem;">${comment.text}</p>
                <span class="text-muted" style="font-size: 0.85rem;">${comment.time}</span>
            </div>
        </div>
    `).join('');
}

function addComment(text) {
    showNotification('Comment added successfully!', 'success');
    loadSampleComments(); // Reload to show new comment
}

// Export Handlers
function setupExportHandlers() {
    document.querySelectorAll('.export-card').forEach(card => {
        card.addEventListener('click', () => {
            const format = card.getAttribute('data-format');
            exportData(format);
        });
    });
}

function exportData(format) {
    showNotification(`Exporting data as ${format.toUpperCase()}...`, 'info');
    
    setTimeout(() => {
        showNotification(`Data exported successfully as ${format.toUpperCase()}!`, 'success');
        // In real implementation, trigger actual download
    }, 1500);
}

// Reports
function loadReports() {
    const generateReportBtn = document.getElementById('generateReportBtn');
    
    generateReportBtn?.addEventListener('click', () => {
        generateReport();
    });
}

function generateReport() {
    const reportType = document.getElementById('reportType').value;
    const startDate = document.getElementById('reportStartDate').value;
    const endDate = document.getElementById('reportEndDate').value;
    const format = document.getElementById('reportFormat').value;
    
    if (!startDate || !endDate) {
        showNotification('Please select date range', 'error');
        return;
    }
    
    const preview = document.querySelector('.preview-content');
    preview.innerHTML = '<p class="text-muted">Generating report...</p>';
    
    setTimeout(() => {
        preview.innerHTML = `
            <div style="padding: 2rem; background: white; border-radius: 8px;">
                <h3>${reportType}</h3>
                <p><strong>Period:</strong> ${startDate} to ${endDate}</p>
                <p><strong>Format:</strong> ${format}</p>
                <hr style="margin: 1rem 0;">
                <p>Report preview will appear here...</p>
                <button class="btn btn-primary" style="margin-top: 1rem;">
                    <i class="fas fa-download"></i> Download ${format}
                </button>
            </div>
        `;
        showNotification('Report generated successfully!', 'success');
    }, 2000);
}

// Refresh Dashboard
document.getElementById('refreshDashboard')?.addEventListener('click', () => {
    showNotification('Refreshing dashboard data...', 'info');
    loadDashboardData();
});

// Add CSS animation for toast
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOutRight {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
