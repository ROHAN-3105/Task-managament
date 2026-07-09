/**
 * TaskFlow Frontend Interactions Script
 * Handles loader, dark mode, dashboard charts, search/filters, modals, and toasts.
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Hide Loader Spinner
    const loader = document.getElementById('loader-wrapper');
    if (loader) {
        setTimeout(() => {
            loader.style.opacity = '0';
            setTimeout(() => {
                loader.style.display = 'none';
            }, 500);
        }, 300);
    }

    // 2. Initialize Theme Toggle
    initThemeToggle();

    // 3. Auto-hide Toast Notifications
    initToasts();

    // 4. Animate Dashboard Counters
    animateCounters();

    // 5. Initialize Charts (Dashboard Only)
    initDashboardCharts();
});

// --- THEME MANAGEMENT ---
function initThemeToggle() {
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (!themeBtn) return;

    const themeIcon = document.getElementById('theme-icon');
    const currentTheme = localStorage.getItem('theme') || 'light';

    // Apply saved theme
    if (currentTheme === 'dark') {
        document.body.classList.add('dark-theme');
        updateThemeIcon(true);
    } else {
        document.body.classList.remove('dark-theme');
        updateThemeIcon(false);
    }

    themeBtn.addEventListener('click', () => {
        const isDark = document.body.classList.toggle('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        updateThemeIcon(isDark);
        
        // Re-render charts to adjust text colors for dark mode if on dashboard
        if (document.getElementById('taskStatusChart')) {
            setTimeout(recreateCharts, 100);
        }
    });
}

function updateThemeIcon(isDark) {
    const themeIcon = document.getElementById('theme-icon');
    if (!themeIcon) return;
    
    if (isDark) {
        // Sun Icon path
        themeIcon.innerHTML = `
            <circle cx="12" cy="12" r="5"></circle>
            <line x1="12" y1="1" x2="12" y2="3"></line>
            <line x1="12" y1="21" x2="12" y2="23"></line>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
            <line x1="1" y1="12" x2="3" y2="12"></line>
            <line x1="21" y1="12" x2="23" y2="12"></line>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
        `;
        themeIcon.style.stroke = 'var(--text-muted)';
        themeIcon.style.fill = 'none';
        themeIcon.style.strokeWidth = '2';
    } else {
        // Moon Icon path
        themeIcon.innerHTML = `<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>`;
        themeIcon.style.stroke = 'none';
        themeIcon.style.fill = 'var(--text-muted)';
    }
}

// --- TOAST NOTIFICATIONS ---
function initToasts() {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        // Auto fade out after 4 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 500);
        }, 4000);

        // Click to close
        toast.addEventListener('click', () => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        });
    });
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<div class="toast-body">${message}</div>`;
    container.appendChild(toast);

    // Trigger animation frame
    setTimeout(() => {
        toast.classList.add('show');
    }, 50);

    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 500);
    }, 4000);
}

// --- COUNTER ANIMATIONS ---
function animateCounters() {
    const counters = document.querySelectorAll('.counter-anim');
    counters.forEach(counter => {
        const target = parseInt(counter.getAttribute('data-target')) || 0;
        if (target === 0) {
            counter.innerText = '0';
            return;
        }

        const duration = 1000; // 1 second animation
        const stepTime = Math.max(Math.floor(duration / target), 15);
        let current = 0;

        const timer = setInterval(() => {
            current += Math.ceil(target / (duration / stepTime));
            if (current >= target) {
                counter.innerText = target;
                clearInterval(timer);
            } else {
                counter.innerText = current;
            }
        }, stepTime);
    });
}

// --- CHART MANAGEMENT (CHART.JS) ---
let statusChart = null;
let empChart = null;
let gaugeChart = null;

function recreateCharts() {
    if (statusChart) statusChart.destroy();
    if (empChart) empChart.destroy();
    if (gaugeChart) gaugeChart.destroy();
    initDashboardCharts();
}

function initDashboardCharts() {
    const statusCanvas = document.getElementById('taskStatusChart');
    if (!statusCanvas) return;

    const chartDataEl = document.getElementById('chart-data');
    const userRoleEl = document.getElementById('user-role');
    if (!chartDataEl) return;

    const chartData = JSON.parse(chartDataEl.textContent);
    const userRole = userRoleEl ? JSON.parse(userRoleEl.textContent) : 'Employee';
    
    // Resolve CSS variables dynamically for text color matching
    const isDark = document.body.classList.contains('dark-theme');
    const textColor = isDark ? '#cbd5e1' : '#1e1b4b';
    const gridColor = isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)';

    // 1. Task Status Chart (Pie/Doughnut)
    statusChart = new Chart(statusCanvas, {
        type: 'doughnut',
        data: {
            labels: ['Pending', 'In Progress', 'Completed'],
            datasets: [{
                data: [
                    chartData.status_counts['Pending'] || 0,
                    chartData.status_counts['In Progress'] || 0,
                    chartData.status_counts['Completed'] || 0
                ],
                backgroundColor: ['#f59e0b', '#3b82f6', '#10b981'],
                borderWidth: isDark ? 2 : 1,
                borderColor: isDark ? '#111827' : '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: 500 } }
                }
            },
            cutout: '65%'
        }
    });

    // 2. Tasks by Employee (Admin/Manager) OR Tasks by Priority (Employee)
    const empCanvas = document.getElementById('employeeTasksChart');
    if (userRole !== 'Employee') {
        // Admin & Manager: Stacked Bar Chart for Employee Tasks
        const employees = chartData.employee_tasks.map(item => item.name);
        const pendings = chartData.employee_tasks.map(item => item.pending);
        const progresses = chartData.employee_tasks.map(item => item.in_progress);
        const completeds = chartData.employee_tasks.map(item => item.completed);

        empChart = new Chart(empCanvas, {
            type: 'bar',
            data: {
                labels: employees,
                datasets: [
                    { label: 'Pending', data: pendings, backgroundColor: '#f59e0b' },
                    { label: 'In Progress', data: progresses, backgroundColor: '#3b82f6' },
                    { label: 'Completed', data: completeds, backgroundColor: '#10b981' }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true,
                        grid: { display: false },
                        ticks: { color: textColor, font: { family: 'Plus Jakarta Sans' } }
                    },
                    y: {
                        stacked: true,
                        grid: { color: gridColor },
                        ticks: { color: textColor, precision: 0, font: { family: 'Plus Jakarta Sans' } }
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: 500 } }
                    }
                }
            }
        });
    } else {
        // Employee: Bar Chart showing tasks by Priority
        // Let's compute priority counts client-side or parse them
        // In app.py, chart_data contains tasks count by status, but for employee priority count:
        // We can pass it or scan the table/cards. Let's make it a general priority count.
        // We will default to dummy values or compute priority counts from cards if cards page, 
        // but since we are on dashboard, let's assume we fetch them. 
        // Wait, for simplicity, since we set status_counts in app.py, let's map statuses:
        const statusVals = [
            chartData.status_counts['Pending'] || 0,
            chartData.status_counts['In Progress'] || 0,
            chartData.status_counts['Completed'] || 0
        ];
        
        empChart = new Chart(empCanvas, {
            type: 'bar',
            data: {
                labels: ['Pending', 'In Progress', 'Completed'],
                datasets: [{
                    label: 'My Tasks',
                    data: statusVals,
                    backgroundColor: ['#f59e0b', '#3b82f6', '#10b981'],
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { display: false },
                        ticks: { color: textColor, font: { family: 'Plus Jakarta Sans' } }
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: { color: textColor, precision: 0, font: { family: 'Plus Jakarta Sans' } }
                    }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });
    }

    // 3. Completion Rate Semi-doughnut (Gauge style)
    const rateCanvas = document.getElementById('completionRateChart');
    const total = (chartData.status_counts['Pending'] || 0) + 
                  (chartData.status_counts['In Progress'] || 0) + 
                  (chartData.status_counts['Completed'] || 0);
    const completed = chartData.status_counts['Completed'] || 0;
    const rate = total > 0 ? Math.round((completed / total) * 100) : 0;
    
    gaugeChart = new Chart(rateCanvas, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [rate, 100 - rate],
                backgroundColor: ['#8b5cf6', isDark ? '#1f2937' : '#e2e8f0'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false }, tooltip: { enabled: false } },
            rotation: -90,
            circumference: 180,
            cutout: '80%'
        }
    });
}

// --- EMPLOYEE SECTION FUNCTIONS ---
function filterEmployees() {
    const query = document.getElementById('employee-search').value.toLowerCase();
    const rows = document.querySelectorAll('.employee-row');
    let visibleCount = 0;

    rows.forEach(row => {
        const text = row.innerText.toLowerCase();
        if (text.includes(query)) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });

    const noRecords = document.getElementById('no-employees-found');
    if (noRecords) {
        noRecords.style.display = visibleCount === 0 ? '' : 'none';
    }
    
    const countEl = document.getElementById('employee-count');
    if (countEl) countEl.innerText = visibleCount;
}

function openAddModal() {
    const modal = document.getElementById('add-employee-modal');
    if (modal) modal.classList.add('active');
}

function closeAddModal() {
    const modal = document.getElementById('add-employee-modal');
    if (modal) modal.classList.remove('active');
}

function openEditModal(btn) {
    const modal = document.getElementById('edit-employee-modal');
    if (!modal) return;

    // Read attributes from button
    const id = btn.getAttribute('data-id');
    const name = btn.getAttribute('data-name');
    const email = btn.getAttribute('data-email');
    const phone = btn.getAttribute('data-phone');
    const department = btn.getAttribute('data-department');
    const designation = btn.getAttribute('data-designation');
    const username = btn.getAttribute('data-username');
    const role = btn.getAttribute('data-role');

    // Populate inputs
    document.getElementById('edit-name').value = name;
    document.getElementById('edit-email').value = email;
    document.getElementById('edit-phone').value = phone;
    document.getElementById('edit-department').value = department;
    document.getElementById('edit-designation').value = designation;
    document.getElementById('edit-username').value = username;
    document.getElementById('edit-password').value = ''; // clear password input field
    document.getElementById('edit-role').value = role;

    // Set Form Action Route URL
    const form = document.getElementById('edit-employee-form');
    form.action = `/employee/edit/${id}`;

    modal.classList.add('active');
}

function closeEditModal() {
    const modal = document.getElementById('edit-employee-modal');
    if (modal) modal.classList.remove('active');
}

function confirmDelete(name) {
    return confirm(`Are you sure you want to delete ${name}? This will remove all their details and login records permanently.`);
}

// --- TASK SECTION FUNCTIONS ---
function filterTasks() {
    const query = document.getElementById('task-search').value.toLowerCase();
    const statusFilter = document.getElementById('status-filter').value;
    const priorityFilter = document.getElementById('priority-filter').value;

    const cards = document.querySelectorAll('.task-card');
    let visibleCount = 0;

    cards.forEach(card => {
        const title = card.getAttribute('data-title').toLowerCase();
        const desc = card.getAttribute('data-desc').toLowerCase();
        const assignee = card.getAttribute('data-assignee').toLowerCase();
        const status = card.getAttribute('data-status');
        const priority = card.getAttribute('data-priority');

        const matchesSearch = title.includes(query) || desc.includes(query) || assignee.includes(query);
        const matchesStatus = statusFilter === 'All' || status === statusFilter;
        const matchesPriority = priorityFilter === 'All' || priority === priorityFilter;

        if (matchesSearch && matchesStatus && matchesPriority) {
            card.style.display = '';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    const noTasks = document.getElementById('no-tasks-found');
    if (noTasks) {
        noTasks.style.display = visibleCount === 0 ? 'grid' : 'none';
    }

    const countEl = document.getElementById('task-count');
    if (countEl) countEl.innerText = visibleCount;
}

function confirmDeleteTask(title) {
    return confirm(`Are you sure you want to delete the task "${title}"?`);
}

// --- TASK DETAIL MODAL ---
function openTaskDetailModal(title, desc, priority, status, due, assigneeName, assigneeEmail) {
    const modal = document.getElementById('task-detail-modal');
    if (!modal) return;

    document.getElementById('detail-title').innerText = title;
    document.getElementById('detail-desc').innerText = desc || 'No description provided.';
    
    // Priority badge
    const pBadge = document.getElementById('detail-priority');
    pBadge.className = `badge badge-${priority.toLowerCase()}`;
    pBadge.innerText = priority;
    
    // Status badge
    const sBadge = document.getElementById('detail-status');
    sBadge.className = `badge badge-${status.toLowerCase().replace(' ', '_')}`;
    sBadge.innerText = status;
    
    // Avatar
    document.getElementById('detail-avatar').innerText = assigneeName ? assigneeName[0].toUpperCase() : 'U';
    document.getElementById('detail-assignee-name').innerText = assigneeName || 'Unassigned';
    document.getElementById('detail-assignee-email').innerText = assigneeEmail || '';
    
    // Due Date
    document.getElementById('detail-due-span').innerText = due;

    modal.classList.add('active');
}

function closeTaskDetailModal() {
    const modal = document.getElementById('task-detail-modal');
    if (modal) modal.classList.remove('active');
}

// Mobile sidebar responsiveness toggle
const menuToggle = document.getElementById('sidebar-toggle');
if (menuToggle) {
    menuToggle.addEventListener('click', () => {
        const sidebar = document.getElementById('app-sidebar');
        if (sidebar) sidebar.classList.toggle('active');
    });
}
// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('app-sidebar');
    const menuToggle = document.getElementById('sidebar-toggle');
    if (sidebar && sidebar.classList.contains('active') && !sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
        sidebar.classList.remove('active');
    }
});
