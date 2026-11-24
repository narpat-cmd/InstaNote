/**
 * InstaNote Admin Panel - Main JavaScript
 * Handles common functionality across all pages
 */

// Global variables
let socket = null;
let isConnected = false;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    initializeTooltips();
    setupGlobalEventListeners();
});

/**
 * Initialize Socket.IO connection
 */
function initializeSocket() {
    if (typeof io === 'undefined') {
        console.warn('Socket.IO not loaded, real-time features disabled');
        return;
    }

    socket = io({
        transports: ['websocket', 'polling'],
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000
    });

    socket.on('connect', function() {
        isConnected = true;
        console.log('Socket.IO connected');
        updateConnectionStatus(true);
    });

    socket.on('disconnect', function() {
        isConnected = false;
        console.log('Socket.IO disconnected');
        updateConnectionStatus(false);
    });

    socket.on('connect_error', function(error) {
        console.error('Socket.IO connection error:', error);
        updateConnectionStatus(false);
    });

    socket.on('stats_update', function(data) {
        handleStatsUpdate(data);
    });

    socket.on('job_update', function(data) {
        handleJobUpdate(data);
    });
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
    const indicator = document.getElementById('connectionStatus');
    if (indicator) {
        indicator.className = 'badge ' + (connected ? 'bg-success' : 'bg-danger');
        indicator.textContent = connected ? 'Connected' : 'Disconnected';
    }
}

/**
 * Handle stats update from server
 */
function handleStatsUpdate(data) {
    if (data.topics) {
        updateStatCard('totalPosts', data.topics.total_posts);
        updateStatCard('postsToday', data.topics.today);
        updateStatCard('postsThisWeek', data.topics.this_week);
    }

    if (data.scheduler) {
        updateStatCard('pendingJobs', data.scheduler.pending_jobs);
        updateStatCard('successfulPosts', data.scheduler.successful_posts);
        updateStatCard('failedPosts', data.scheduler.failed_posts);

        const statusBadge = document.getElementById('schedulerStatus');
        if (statusBadge) {
            statusBadge.className = 'badge ' + (data.scheduler.is_running ? 'bg-success' : 'bg-danger');
            statusBadge.textContent = data.scheduler.is_running ? 'Running' : 'Stopped';
        }
    }
}

/**
 * Handle job update from server
 */
function handleJobUpdate(data) {
    const jobRow = document.getElementById('job-' + data.job_id);
    if (jobRow) {
        const statusCell = jobRow.querySelector('.job-status');
        if (statusCell) {
            statusCell.className = 'badge ' + getStatusBadgeClass(data.status);
            statusCell.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
        }
    }
}

/**
 * Get badge class for job status
 */
function getStatusBadgeClass(status) {
    switch (status) {
        case 'pending': return 'bg-warning';
        case 'running': return 'bg-info';
        case 'completed': return 'bg-success';
        case 'failed': return 'bg-danger';
        case 'cancelled': return 'bg-secondary';
        default: return 'bg-secondary';
    }
}

/**
 * Update a stat card value
 */
function updateStatCard(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

/**
 * Setup global event listeners
 */
function setupGlobalEventListeners() {
    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // Confirm before dangerous actions
    document.addEventListener('click', function(e) {
        if (e.target.matches('[data-confirm]')) {
            const message = e.target.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
                e.stopPropagation();
            }
        }
    });
}

/**
 * Show toast notification
 */
function showToast(message, type = 'info') {
    const container = getOrCreateToastContainer();

    const toast = document.createElement('div');
    toast.className = 'toast align-items-center text-white bg-' + type + ' border-0';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = '<div class="d-flex"><div class="toast-body">' + escapeHtml(message) + '</div><button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button></div>';

    container.appendChild(toast);

    const bsToast = new bootstrap.Toast(toast, {
        autohide: true,
        delay: 5000
    });

    bsToast.show();

    // Remove from DOM after hiding
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Get or create toast container
 */
function getOrCreateToastContainer() {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '1080';
        document.body.appendChild(container);
    }
    return container;
}

/**
 * Format date for display
 */
function formatDate(date, options = {}) {
    const defaultOptions = {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(date).toLocaleDateString(undefined, {...defaultOptions, ...options});
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
function formatRelativeTime(date) {
    const now = new Date();
    const then = new Date(date);
    const diff = now - then;

    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    const weeks = Math.floor(days / 7);

    if (seconds < 60) return 'just now';
    if (minutes < 60) return minutes + 'm ago';
    if (hours < 24) return hours + 'h ago';
    if (days < 7) return days + 'd ago';
    if (weeks < 4) return weeks + 'w ago';
    return formatDate(date, {hour: undefined, minute: undefined});
}

/**
 * Debounce function
 */
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

/**
 * Throttle function
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Make API request with error handling
 */
async function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json'
        }
    };

    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...(options.headers || {})
        }
    };

    try {
        const response = await fetch(url, mergedOptions);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }

        return data;
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

/**
 * Export functions to global scope for use in templates
 */
window.InstaNote = {
    showToast,
    formatDate,
    formatRelativeTime,
    apiRequest,
    debounce,
    throttle,
    socket: () => socket,
    escapeHtml
};