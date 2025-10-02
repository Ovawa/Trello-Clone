// Profile page functionality

let currentMonth = new Date().getMonth();
let currentYear = new Date().getFullYear();
let calendarTasks = [];
let currentUser = null;

// Load current user
async function loadCurrentUser() {
    try {
        currentUser = await apiRequest('/auth/me');
        document.getElementById('profileUsername').textContent = currentUser.username;
    } catch (error) {
        console.error('Failed to load user:', error);
    }
}

// Load user tasks
async function loadTasks() {
    try {
        const tasks = await apiRequest('/api/users/me/tasks');
        console.log('Loaded tasks:', tasks);
        renderTasks(tasks);
    } catch (error) {
        console.error('Failed to load tasks:', error);
        const container = document.getElementById('tasksList');
        container.innerHTML = `<p style="color: var(--danger-color); padding: 1rem;">Error: ${error.message}</p>`;
        showNotification('Failed to load tasks', 'error');
    }
}

// Render tasks
function renderTasks(tasks) {
    const container = document.getElementById('tasksList');
    
    if (tasks.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); padding: 1rem;">No tasks assigned to you</p>';
        return;
    }
    
    container.innerHTML = tasks.map(task => {
        const dueDate = task.due_date ? new Date(task.due_date) : null;
        const isOverdue = dueDate && dueDate < new Date() && !task.completed;
        const boardTitle = task.board ? task.board.title : 'Board';
        const boardId = task.board ? task.board.id : '#';
        
        return `
            <div class="task-item" onclick="goToBoard(${boardId})">
                <div class="task-title">${escapeHtml(task.title)}</div>
                <div class="task-meta">
                    <span>${escapeHtml(boardTitle)}</span>
                    ${dueDate ? `<span class="${isOverdue ? 'overdue' : ''}">${task.completed ? 'Completed' : 'Due'}: ${dueDate.toLocaleDateString()}</span>` : ''}
                    ${task.completed ? '<span style="color: var(--success-color);">Completed</span>' : ''}
                </div>
            </div>
        `;
    }).join('');
}

function goToBoard(boardId) {
    window.location.href = `/board/${boardId}`;
}

// Load calendar
async function loadCalendar() {
    try {
        calendarTasks = await apiRequest(`/api/users/me/calendar?month=${currentMonth + 1}&year=${currentYear}`);
        console.log('Loaded calendar tasks:', calendarTasks);
        renderCalendar();
    } catch (error) {
        console.error('Failed to load calendar:', error);
        showNotification('Failed to load calendar', 'error');
    }
}

// Render calendar
function renderCalendar() {
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December'];
    
    document.getElementById('currentMonth').textContent = `${monthNames[currentMonth]} ${currentYear}`;
    
    const calendar = document.getElementById('calendar');
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const prevLastDay = new Date(currentYear, currentMonth, 0);
    
    const firstDayOfWeek = firstDay.getDay();
    const lastDate = lastDay.getDate();
    const prevLastDate = prevLastDay.getDate();
    
    let calendarHTML = '';
    
    // Day headers
    const dayHeaders = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    dayHeaders.forEach(day => {
        calendarHTML += `<div class="calendar-day-header">${day}</div>`;
    });
    
    // Previous month days
    for (let i = firstDayOfWeek - 1; i >= 0; i--) {
        calendarHTML += `<div class="calendar-day other-month">${prevLastDate - i}</div>`;
    }
    
    // Current month days
    const today = new Date();
    for (let day = 1; day <= lastDate; day++) {
        const date = new Date(currentYear, currentMonth, day);
        const isToday = date.toDateString() === today.toDateString();
        const tasksOnDay = calendarTasks.filter(task => {
            const taskDate = new Date(task.due_date);
            return taskDate.getDate() === day;
        });
        
        const hasTasks = tasksOnDay.length > 0;
        
        calendarHTML += `
            <div class="calendar-day ${isToday ? 'today' : ''} ${hasTasks ? 'has-tasks' : ''}" 
                 onclick="showDayTasks(${day})" data-day="${day}">
                ${day}
            </div>
        `;
    }
    
    // Next month days
    const remainingCells = 42 - (firstDayOfWeek + lastDate);
    for (let i = 1; i <= remainingCells; i++) {
        calendarHTML += `<div class="calendar-day other-month">${i}</div>`;
    }
    
    calendar.innerHTML = calendarHTML;
}

// Show tasks for selected day
function showDayTasks(day) {
    const tasksOnDay = calendarTasks.filter(task => {
        const taskDate = new Date(task.due_date);
        return taskDate.getDate() === day;
    });
    
    const container = document.getElementById('calendarTasks');
    
    if (tasksOnDay.length === 0) {
        container.innerHTML = `<p style="color: var(--text-secondary); padding: 1rem;">No tasks on ${currentMonth + 1}/${day}/${currentYear}</p>`;
        return;
    }
    
    container.innerHTML = `
        <h4 style="padding: 0.5rem 0; border-bottom: 1px solid var(--border-color); margin-bottom: 0.5rem;">
            Tasks on ${currentMonth + 1}/${day}/${currentYear}
        </h4>
        ${tasksOnDay.map(task => `
            <div class="calendar-task-item" onclick="goToBoard(${task.board_id})">
                <div style="font-weight: 500;">${escapeHtml(task.title)}</div>
                <div style="font-size: 0.75rem; color: var(--text-secondary);">
                    ${escapeHtml(task.board_title || 'Board')}
                    ${task.completed ? '<span style="color: var(--success-color);"> ✓ Completed</span>' : ''}
                </div>
            </div>
        `).join('')}
    `;
}

// Previous month
document.getElementById('prevMonth').addEventListener('click', () => {
    currentMonth--;
    if (currentMonth < 0) {
        currentMonth = 11;
        currentYear--;
    }
    loadCalendar();
});

// Next month
document.getElementById('nextMonth').addEventListener('click', () => {
    currentMonth++;
    if (currentMonth > 11) {
        currentMonth = 0;
        currentYear++;
    }
    loadCalendar();
});

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
loadCurrentUser();
loadTasks();
loadCalendar();
