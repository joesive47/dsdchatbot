// DSD Chatbot - Main JavaScript Functions

// Utility functions
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = 
otification ;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 4000);
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showNotification('Copied to clipboard!', 'success');
    }).catch(() => {
        showNotification('Failed to copy', 'error');
    });
}

// API functions
async function testAPI() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        
        if (response.ok) {
            showNotification('API test successful!', 'success');
            return data;
        } else {
            throw new Error(HTTP );
        }
    } catch (error) {
        showNotification(API test failed: , 'error');
        throw error;
    }
}

async function sendChatMessage(message, userId = 'web_user', sessionId = 'web_session') {
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: userId,
                session_id: sessionId
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            return data;
        } else {
            throw new Error(data.error || 'Unknown error');
        }
    } catch (error) {
        showNotification(Chat error: , 'error');
        throw error;
    }
}

// Form utilities
function validateForm(formElement) {
    const requiredFields = formElement.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.style.borderColor = '#dc3545';
            isValid = false;
        } else {
            field.style.borderColor = '#28a745';
        }
    });
    
    return isValid;
}

function resetForm(formElement) {
    formElement.reset();
    const fields = formElement.querySelectorAll('.form-control');
    fields.forEach(field => {
        field.style.borderColor = '#e1e5e9';
    });
}

// Loading states
function showLoading(element) {
    const originalContent = element.innerHTML;
    element.dataset.originalContent = originalContent;
    element.innerHTML = '<span class="loading-spinner"></span> Loading...';
    element.disabled = true;
}

function hideLoading(element) {
    const originalContent = element.dataset.originalContent;
    element.innerHTML = originalContent;
    element.disabled = false;
}

// Railway specific functions
function checkRailwayStatus() {
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            const statusElement = document.getElementById('railway-status');
            if (statusElement) {
                statusElement.textContent = data.railway_info?.no_cold_start ? 'No Cold Start ' : 'Standard';
            }
        })
        .catch(error => {
            console.error('Railway status check failed:', error);
        });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚂 DSD Chatbot JavaScript loaded');
    
    // Check Railway status
    checkRailwayStatus();
    
    // Add click handlers for copy buttons
    document.querySelectorAll('[data-copy]').forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.dataset.copy;
            copyToClipboard(textToCopy);
        });
    });
    
    // Add form validation
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                showNotification('Please fill in all required fields', 'error');
            }
        });
    });
});

// Export functions for global use
window.DSDChatbot = {
    showNotification,
    formatFileSize,
    copyToClipboard,
    testAPI,
    sendChatMessage,
    validateForm,
    resetForm,
    showLoading,
    hideLoading,
    checkRailwayStatus
};
