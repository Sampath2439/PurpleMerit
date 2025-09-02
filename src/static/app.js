// Multi-Agent Marketing System - Frontend JavaScript
// Handles UI interactions, API calls, and real-time updates

// Global variables
let currentUser = null;
let authToken = null;

// API base URL
const API_BASE = '/api';

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    loadRecentActivity();
    updateSystemStatus();
});

function initializeApp() {
    // Event listeners for modals
    document.getElementById('loginBtn').addEventListener('click', () => showModal('loginModal'));
    document.getElementById('registerBtn').addEventListener('click', () => showModal('registerModal'));
    
    // Form submissions
    document.getElementById('loginForm').addEventListener('submit', handleLogin);
    document.getElementById('registerForm').addEventListener('submit', handleRegister);
    
    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('fixed')) {
            e.target.classList.add('hidden');
        }
    });
    
    // Check if user is already logged in
    checkAuthStatus();
}

// Modal functions
function showModal(modalId) {
    document.getElementById(modalId).classList.remove('hidden');
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

// Authentication functions
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            authToken = data.token;
            
            // Store token in localStorage
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('user', JSON.stringify(currentUser));
            
            // Update UI
            updateUIForUser();
            closeModal('loginModal');
            
            // Show success message
            showNotification('Login successful!', 'success');
            
        } else {
            showNotification(data.error || 'Login failed', 'error');
        }
        
    } catch (error) {
        console.error('Login error:', error);
        showNotification('Login failed. Please try again.', 'error');
    }
}

async function handleRegister(e) {
    e.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        const response = await fetch(`${API_BASE}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = data.user;
            authToken = data.token;
            
            // Store token in localStorage
            localStorage.setItem('authToken', authToken);
            localStorage.setItem('user', JSON.stringify(currentUser));
            
            // Update UI
            updateUIForUser();
            closeModal('registerModal');
            
            // Show success message
            showNotification('Registration successful!', 'success');
            
        } else {
            showNotification(data.error || 'Registration failed', 'error');
        }
        
    } catch (error) {
        console.error('Registration error:', error);
        showNotification('Registration failed. Please try again.', 'error');
    }
}

function checkAuthStatus() {
    const token = localStorage.getItem('authToken');
    const user = localStorage.getItem('user');
    
    if (token && user) {
        try {
            currentUser = JSON.parse(user);
            authToken = token;
            updateUIForUser();
        } catch (error) {
            console.error('Error parsing user data:', error);
            logout();
        }
    }
}

function updateUIForUser() {
    if (currentUser) {
        // Update navigation
        document.getElementById('loginBtn').style.display = 'none';
        document.getElementById('registerBtn').style.display = 'none';
        
        // Add user menu
        const userMenu = document.createElement('div');
        userMenu.className = 'flex items-center space-x-4';
        userMenu.innerHTML = `
            <span class="text-white">Welcome, ${currentUser.username}</span>
            <button onclick="logout()" class="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors">
                <i class="fas fa-sign-out-alt mr-2"></i>Logout
            </button>
        `;
        
        const nav = document.querySelector('nav .flex.justify-between');
        nav.appendChild(userMenu);
        
        // Enable agent testing
        enableAgentTesting();
        
    } else {
        // Reset to default state
        document.getElementById('loginBtn').style.display = 'block';
        document.getElementById('registerBtn').style.display = 'block';
        
        // Remove user menu if exists
        const userMenu = document.querySelector('nav .flex.justify-between div:last-child');
        if (userMenu && userMenu.querySelector('span')) {
            userMenu.remove();
        }
        
        // Disable agent testing
        disableAgentTesting();
    }
}

function logout() {
    currentUser = null;
    authToken = null;
    
    // Clear localStorage
    localStorage.removeItem('authToken');
    localStorage.removeItem('user');
    
    // Update UI
    updateUIForUser();
    
    // Show notification
    showNotification('Logged out successfully', 'info');
}

// Agent testing functions
function enableAgentTesting() {
    const testButtons = document.querySelectorAll('[onclick^="testAgent"]');
    testButtons.forEach(button => {
        button.disabled = false;
        button.classList.remove('opacity-50', 'cursor-not-allowed');
    });
}

function disableAgentTesting() {
    const testButtons = document.querySelectorAll('[onclick^="testAgent"]');
    testButtons.forEach(button => {
        button.disabled = true;
        button.classList.add('opacity-50', 'cursor-not-allowed');
    });
}

async function testAgent(agentType) {
    if (!authToken) {
        showNotification('Please login to test agents', 'error');
        return;
    }
    
    try {
        let endpoint, requestData;
        
        switch (agentType) {
            case 'triage':
                endpoint = '/agents/triage';
                requestData = {
                    lead_data: {
                        lead_id: 'TEST_001',
                        company_name: 'Test Company',
                        industry: 'SaaS',
                        company_size: '201-1000',
                        persona: 'CMO',
                        region: 'US',
                        source: 'Website'
                    }
                };
                break;
                
            case 'engagement':
                endpoint = '/agents/engage';
                requestData = {
                    lead_data: {
                        lead_id: 'TEST_001',
                        company_name: 'Test Company',
                        industry: 'SaaS',
                        company_size: '201-1000',
                        persona: 'CMO',
                        region: 'US',
                        source: 'Website'
                    },
                    engagement_type: 'welcome'
                };
                break;
                
            case 'optimization':
                endpoint = '/agents/optimize';
                requestData = {
                    campaign_data: {
                        campaign_id: 'TEST_CAMP_001',
                        campaign_name: 'Test Campaign',
                        ctr: 0.025,
                        cpl_usd: 75.0,
                        roas: 1.8,
                        conversions: 15,
                        cost_usd: 1125.0
                    },
                    optimization_type: 'performance_check'
                };
                break;
                
            default:
                showNotification('Unknown agent type', 'error');
                return;
        }
        
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showTestResults(agentType, data);
            addActivityLog(agentType, 'success', data);
        } else {
            showNotification(data.error || 'Test failed', 'error');
            addActivityLog(agentType, 'error', { error: data.error });
        }
        
    } catch (error) {
        console.error('Agent test error:', error);
        showNotification('Test failed. Please try again.', 'error');
        addActivityLog(agentType, 'error', { error: 'Network error' });
    }
}

function showTestResults(agentType, results) {
    const modal = document.getElementById('testResultsModal');
    const resultsDiv = document.getElementById('testResults');
    
    let resultsHTML = `
        <div class="mb-4">
            <h4 class="font-semibold text-lg text-gray-800 mb-2">${agentType.charAt(0).toUpperCase() + agentType.slice(1)} Agent Test Results</h4>
            <div class="bg-gray-50 p-4 rounded-lg">
    `;
    
    if (results.status === 'success') {
        resultsHTML += `<p class="text-green-600 font-semibold mb-2">✓ Test completed successfully</p>`;
        
        // Display specific results based on agent type
        switch (agentType) {
            case 'triage':
                resultsHTML += `
                    <div class="space-y-2">
                        <div><strong>Triage Category:</strong> ${results.triage_category}</div>
                        <div><strong>Lead Score:</strong> ${results.lead_score}</div>
                        <div><strong>Routing Decision:</strong> ${results.routing_decision?.reason || 'N/A'}</div>
                    </div>
                `;
                break;
                
            case 'engagement':
                resultsHTML += `
                    <div class="space-y-2">
                        <div><strong>Channel:</strong> ${results.channel}</div>
                        <div><strong>Content:</strong> ${results.content}</div>
                        <div><strong>Status:</strong> ${results.engagement_result?.status || 'N/A'}</div>
                    </div>
                `;
                break;
                
            case 'optimization':
                resultsHTML += `
                    <div class="space-y-2">
                        <div><strong>Performance Score:</strong> ${results.optimization_result?.performance_score || 'N/A'}</div>
                        <div><strong>Recommendations:</strong> ${results.optimization_result?.recommendations?.length || 0} items</div>
                    </div>
                `;
                break;
        }
        
    } else {
        resultsHTML += `<p class="text-red-600 font-semibold mb-2">✗ Test failed</p>`;
        resultsHTML += `<div class="text-red-600">${results.message || 'Unknown error'}</div>`;
    }
    
    resultsHTML += `
            </div>
        </div>
        <div class="text-sm text-gray-600">
            <strong>Timestamp:</strong> ${new Date().toLocaleString()}
        </div>
    `;
    
    resultsDiv.innerHTML = resultsHTML;
    showModal('testResultsModal');
}

// Quick action functions
async function quickAction(actionType) {
    if (!authToken) {
        showNotification('Please login to use quick actions', 'error');
        return;
    }
    
    try {
        let endpoint, requestData;
        
        switch (actionType) {
            case 'triage':
                endpoint = '/agents/triage';
                requestData = {
                    lead_data: {
                        lead_id: `QUICK_${Date.now()}`,
                        company_name: 'Quick Test Company',
                        industry: 'FinTech',
                        company_size: '1001-5000',
                        persona: 'Founder',
                        region: 'EU',
                        source: 'Referral'
                    }
                };
                break;
                
            case 'engagement':
                endpoint = '/agents/engage';
                requestData = {
                    lead_data: {
                        lead_id: `QUICK_${Date.now()}`,
                        company_name: 'Quick Test Company',
                        industry: 'FinTech',
                        company_size: '1001-5000',
                        persona: 'Founder',
                        region: 'EU',
                        source: 'Referral'
                    },
                    engagement_type: 'follow_up'
                };
                break;
                
            case 'optimization':
                endpoint = '/agents/optimize';
                requestData = {
                    campaign_data: {
                        campaign_id: `QUICK_CAMP_${Date.now()}`,
                        campaign_name: 'Quick Test Campaign',
                        ctr: 0.018,
                        cpl_usd: 95.0,
                        roas: 1.2,
                        conversions: 8,
                        cost_usd: 760.0
                    },
                    optimization_type: 'performance_check'
                };
                break;
                
            case 'memory':
                endpoint = '/agents/memory/retrieve';
                requestData = { memory_type: 'episodic' };
                break;
                
            default:
                showNotification('Unknown action type', 'error');
                return;
        }
        
        const response = await fetch(`${API_BASE}${endpoint}`, {
            method: actionType === 'memory' ? 'GET' : 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: actionType === 'memory' ? undefined : JSON.stringify(requestData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification(`${actionType.charAt(0).toUpperCase() + actionType.slice(1)} action completed successfully`, 'success');
            addActivityLog(actionType, 'success', data);
        } else {
            showNotification(data.error || 'Action failed', 'error');
            addActivityLog(actionType, 'error', { error: data.error });
        }
        
    } catch (error) {
        console.error('Quick action error:', error);
        showNotification('Action failed. Please try again.', 'error');
        addActivityLog(actionType, 'error', { error: 'Network error' });
    }
}

// Activity log functions
function addActivityLog(actionType, status, data) {
    const activityLog = document.getElementById('activityLog');
    const timestamp = new Date().toLocaleString();
    
    const statusIcon = status === 'success' ? '✓' : '✗';
    const statusColor = status === 'success' ? 'text-green-600' : 'text-red-600';
    
    const activityItem = document.createElement('div');
    activityItem.className = 'flex items-center justify-between p-3 bg-gray-50 rounded-lg';
    activityItem.innerHTML = `
        <div class="flex items-center space-x-3">
            <span class="${statusColor} font-semibold">${statusIcon}</span>
            <span class="text-gray-800">${actionType.charAt(0).toUpperCase() + actionType.slice(1)} action</span>
        </div>
        <span class="text-sm text-gray-500">${timestamp}</span>
    `;
    
    // Add to beginning of log
    activityLog.insertBefore(activityItem, activityLog.firstChild);
    
    // Keep only last 10 items
    const items = activityLog.children;
    if (items.length > 10) {
        activityLog.removeChild(items[items.length - 1]);
    }
}

function loadRecentActivity() {
    // Load initial activity log
    const activities = [
        { type: 'system', status: 'startup', message: 'System initialized successfully' },
        { type: 'agent', status: 'startup', message: 'All agents activated' },
        { type: 'memory', status: 'startup', message: 'Memory system loaded' }
    ];
    
    activities.forEach(activity => {
        addActivityLog(activity.type, activity.status, { message: activity.message });
    });
}

// System status functions
async function updateSystemStatus() {
    try {
        const response = await fetch(`${API_BASE}/agents/system/status`);
        const data = await response.json();
        
        if (response.ok && data.status === 'operational') {
            // Update status indicators
            updateStatusIndicators(data);
        }
        
    } catch (error) {
        console.error('Error updating system status:', error);
    }
    
    // Update every 30 seconds
    setTimeout(updateSystemStatus, 30000);
}

function updateStatusIndicators(statusData) {
    // Update system status based on API response
    // This would update the dashboard with real-time data
}

// Utility functions
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' :
        type === 'error' ? 'bg-red-500 text-white' :
        type === 'warning' ? 'bg-yellow-500 text-white' :
        'bg-blue-500 text-white'
    }`;
    
    notification.innerHTML = `
        <div class="flex items-center space-x-2">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-2 hover:opacity-75">×</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    showNotification('An error occurred. Please check the console.', 'error');
});

// Export functions for global access
window.testAgent = testAgent;
window.quickAction = quickAction;
window.closeModal = closeModal;
window.logout = logout;

