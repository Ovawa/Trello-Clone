// Board page functionality

const boardId = window.location.pathname.split('/').pop();
let boardData = null;
let currentCard = null;
let draggedCard = null;

// Load board data
async function loadBoard() {
    try {
        boardData = await apiRequest(`/api/boards/${boardId}`);
        console.log('Board data loaded:', boardData);
        document.getElementById('boardTitle').textContent = boardData.title;
        
        // Always render lists (even if empty array)
        renderLists();
        loadActivities();
    } catch (error) {
        console.error('Load board error:', error);
        showNotification('Failed to load board', 'error');
        setTimeout(() => window.location.href = '/', 2000);
    }
}

// Render lists
function renderLists() {
    const container = document.getElementById('listsContainer');
    
    if (!boardData.lists || boardData.lists.length === 0) {
        container.innerHTML = '';
        return;
    }
    
    container.innerHTML = boardData.lists.map(list => `
        <div class="list" data-list-id="${list.id}">
            <div class="list-header">
                <h3 class="list-title">${escapeHtml(list.title)}</h3>
                <div class="list-actions">
                    <button class="btn-icon delete-list" data-list-id="${list.id}" title="Delete list">×</button>
                </div>
            </div>
            <div class="cards-container" data-list-id="${list.id}">
                ${renderCards(list.cards || [])}
            </div>
            <button class="add-card-btn" data-list-id="${list.id}">+ Add a card</button>
            <div class="add-card-form" data-list-id="${list.id}" style="display: none;">
                <textarea placeholder="Enter card title..."></textarea>
                <div class="add-card-actions">
                    <button class="btn btn-primary save-card">Add Card</button>
                    <button class="btn btn-secondary cancel-card">Cancel</button>
                </div>
            </div>
        </div>
    `).join('');
    
    setupListEventListeners();
    setupDragAndDrop();
}

// Render cards
function renderCards(cards) {
    return cards.map(card => {
        const badges = [];
        
        if (card.due_date) {
            const dueDate = new Date(card.due_date);
            const now = new Date();
            const isOverdue = dueDate < now && !card.completed;
            const isDueSoon = (dueDate - now) < 86400000 && !card.completed; // 24 hours
            
            badges.push(`
                <span class="badge ${card.completed ? 'completed' : isOverdue ? 'overdue' : isDueSoon ? 'due-soon' : ''}">
                    Due: ${dueDate.toLocaleDateString()}
                </span>
            `);
        }
        
        if (card.assignments && card.assignments.length > 0) {
            badges.push(`<span class="badge">Assigned: ${card.assignments.length}</span>`);
        }
        
        if (card.attachments && card.attachments.length > 0) {
            badges.push(`<span class="badge">Attachments: ${card.attachments.length}</span>`);
        }
        
        if (card.checklists && card.checklists.length > 0) {
            const completed = card.checklists.filter(c => c.completed).length;
            badges.push(`<span class="badge">Checklist: ${completed}/${card.checklists.length}</span>`);
        }
        
        return `
            <div class="card" draggable="true" data-card-id="${card.id}">
                <div class="card-title">${escapeHtml(card.title)}</div>
                ${badges.length > 0 ? `<div class="card-badges">${badges.join('')}</div>` : ''}
            </div>
        `;
    }).join('');
}

// Setup list event listeners
function setupListEventListeners() {
    // Add card buttons
    document.querySelectorAll('.add-card-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const listId = e.target.dataset.listId;
            e.target.style.display = 'none';
            document.querySelector(`.add-card-form[data-list-id="${listId}"]`).style.display = 'block';
            document.querySelector(`.add-card-form[data-list-id="${listId}"] textarea`).focus();
        });
    });
    
    // Save card
    document.querySelectorAll('.save-card').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const form = e.target.closest('.add-card-form');
            const listId = form.dataset.listId;
            const textarea = form.querySelector('textarea');
            const title = textarea.value.trim();
            
            if (!title) return;
            
            try {
                await apiRequest('/api/cards', {
                    method: 'POST',
                    body: JSON.stringify({ title, list_id: parseInt(listId) })
                });
                
                textarea.value = '';
                form.style.display = 'none';
                document.querySelector(`.add-card-btn[data-list-id="${listId}"]`).style.display = 'block';
                
                await loadBoard();
                showNotification('Card added', 'success');
            } catch (error) {
                showNotification(error.message, 'error');
            }
        });
    });
    
    // Cancel card
    document.querySelectorAll('.cancel-card').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const form = e.target.closest('.add-card-form');
            const listId = form.dataset.listId;
            form.querySelector('textarea').value = '';
            form.style.display = 'none';
            document.querySelector(`.add-card-btn[data-list-id="${listId}"]`).style.display = 'block';
        });
    });
    
    // Delete list
    document.querySelectorAll('.delete-list').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const listId = e.target.dataset.listId;
            if (!confirm('Delete this list and all its cards?')) return;
            
            try {
                await apiRequest(`/api/lists/${listId}`, { method: 'DELETE' });
                await loadBoard();
                showNotification('List deleted', 'success');
            } catch (error) {
                showNotification(error.message, 'error');
            }
        });
    });
    
    // Open card modal
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('click', () => {
            openCardModal(card.dataset.cardId);
        });
    });
}

// Setup drag and drop
function setupDragAndDrop() {
    const cards = document.querySelectorAll('.card');
    const containers = document.querySelectorAll('.cards-container');
    
    cards.forEach(card => {
        card.addEventListener('dragstart', (e) => {
            draggedCard = card;
            card.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        });
        
        card.addEventListener('dragend', () => {
            card.classList.remove('dragging');
            draggedCard = null;
        });
    });
    
    containers.forEach(container => {
        container.addEventListener('dragover', (e) => {
            e.preventDefault();
            const afterElement = getDragAfterElement(container, e.clientY);
            if (draggedCard) {
                if (afterElement == null) {
                    container.appendChild(draggedCard);
                } else {
                    container.insertBefore(draggedCard, afterElement);
                }
            }
        });
        
        container.addEventListener('drop', async (e) => {
            e.preventDefault();
            if (!draggedCard) return;
            
            const newListId = container.dataset.listId;
            const cardId = draggedCard.dataset.cardId;
            
            try {
                await apiRequest(`/api/cards/${cardId}`, {
                    method: 'PUT',
                    body: JSON.stringify({ list_id: parseInt(newListId) })
                });
                
                await loadBoard();
            } catch (error) {
                showNotification(error.message, 'error');
                await loadBoard(); // Reload to reset
            }
        });
    });
}

function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.card:not(.dragging)')];
    
    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

// Open card modal
async function openCardModal(cardId) {
    try {
        currentCard = await apiRequest(`/api/cards/${cardId}`);
        
        document.getElementById('cardTitle').value = currentCard.title;
        document.getElementById('cardDescription').value = currentCard.description || '';
        
        if (currentCard.due_date) {
            const date = new Date(currentCard.due_date);
            document.getElementById('cardDueDate').value = date.toISOString().slice(0, 16);
        } else {
            document.getElementById('cardDueDate').value = '';
        }
        
        renderChecklistItems();
        renderAttachments();
        renderAssignedUsers();
        
        openModal('cardModal');
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Render checklist items
function renderChecklistItems() {
    const container = document.getElementById('checklistItems');
    
    if (!currentCard.checklists || currentCard.checklists.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); font-size: 0.875rem;">No items yet</p>';
        return;
    }
    
    container.innerHTML = currentCard.checklists.map(item => `
        <div class="checklist-item ${item.completed ? 'completed' : ''}">
            <input type="checkbox" id="check-${item.id}" ${item.completed ? 'checked' : ''} 
                   onchange="toggleChecklistItem(${item.id}, this.checked)">
            <label for="check-${item.id}">${escapeHtml(item.title)}</label>
            <span class="delete-btn" onclick="deleteChecklistItem(${item.id})">✕</span>
        </div>
    `).join('');
}

// Toggle checklist item
async function toggleChecklistItem(itemId, completed) {
    try {
        await apiRequest(`/api/cards/${currentCard.id}/checklist/${itemId}`, {
            method: 'PUT',
            body: JSON.stringify({ completed })
        });
        
        currentCard = await apiRequest(`/api/cards/${currentCard.id}`);
        renderChecklistItems();
        await loadBoard(); // Refresh board to update badges
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Delete checklist item
async function deleteChecklistItem(itemId) {
    try {
        await apiRequest(`/api/cards/${currentCard.id}/checklist/${itemId}`, {
            method: 'DELETE'
        });
        
        currentCard = await apiRequest(`/api/cards/${currentCard.id}`);
        renderChecklistItems();
        await loadBoard();
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Add checklist item
document.getElementById('addChecklistBtn').addEventListener('click', async () => {
    const input = document.getElementById('newChecklistItem');
    const title = input.value.trim();
    
    if (!title) return;
    
    try {
        await apiRequest(`/api/cards/${currentCard.id}/checklist`, {
            method: 'POST',
            body: JSON.stringify({ title })
        });
        
        input.value = '';
        currentCard = await apiRequest(`/api/cards/${currentCard.id}`);
        renderChecklistItems();
        await loadBoard();
    } catch (error) {
        showNotification(error.message, 'error');
    }
});

// Render attachments
function renderAttachments() {
    const container = document.getElementById('attachmentsList');
    
    if (!currentCard.attachments || currentCard.attachments.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); font-size: 0.875rem;">No attachments</p>';
        return;
    }
    
    container.innerHTML = currentCard.attachments.map(att => `
        <div class="attachment-item">
            <span class="attachment-name">${escapeHtml(att.filename)}</span>
            <button class="btn btn-sm btn-danger" onclick="deleteAttachment(${att.id})">Delete</button>
        </div>
    `).join('');
}

// Upload file
document.getElementById('uploadFileBtn').addEventListener('click', () => {
    document.getElementById('fileInput').click();
});

document.getElementById('fileInput').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(`/api/cards/${currentCard.id}/attachments`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }
        
        currentCard = await apiRequest(`/api/cards/${currentCard.id}`);
        renderAttachments();
        await loadBoard();
        showNotification('File uploaded', 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    }
    
    e.target.value = '';
});

// Delete attachment
async function deleteAttachment(attachmentId) {
    try {
        await apiRequest(`/api/cards/${currentCard.id}/attachments/${attachmentId}`, {
            method: 'DELETE'
        });
        
        currentCard = await apiRequest(`/api/cards/${currentCard.id}`);
        renderAttachments();
        await loadBoard();
        showNotification('Attachment deleted', 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Render assigned users
function renderAssignedUsers() {
    const container = document.getElementById('assignedUsers');
    
    if (!currentCard.assignments || currentCard.assignments.length === 0) {
        container.innerHTML = '<p style="color: var(--text-secondary); font-size: 0.875rem;">No one assigned</p>';
        return;
    }
    
    container.innerHTML = currentCard.assignments.map(assignment => `
        <div class="assigned-user">
            <span>${escapeHtml(assignment.user.username)}</span>
            <button class="btn btn-sm btn-danger" onclick="unassignUser(${assignment.id})">Remove</button>
        </div>
    `).join('');
}

// Search users
let searchTimeout;
document.getElementById('searchUsers').addEventListener('input', async (e) => {
    clearTimeout(searchTimeout);
    const query = e.target.value.trim();
    
    if (!query) {
        document.getElementById('userSearchResults').innerHTML = '';
        return;
    }
    
    searchTimeout = setTimeout(async () => {
        try {
            const users = await apiRequest(`/api/users/search?q=${encodeURIComponent(query)}`);
            const resultsContainer = document.getElementById('userSearchResults');
            
            resultsContainer.innerHTML = users.map(user => `
                <div class="user-search-result" onclick="assignUser(${user.id}, '${escapeHtml(user.username)}')">
                    ${escapeHtml(user.username)}
                </div>
            `).join('');
        } catch (error) {
            console.error(error);
        }
    }, 300);
});

// Assign user
async function assignUser(userId, username) {
    try {
        await apiRequest(`/api/cards/${currentCard.id}/assignments`, {
            method: 'POST',
            body: JSON.stringify({ user_id: userId })
        });
        
        currentCard = await apiRequest(`/api/cards/${currentCard.id}`);
        renderAssignedUsers();
        await loadBoard();
        document.getElementById('searchUsers').value = '';
        document.getElementById('userSearchResults').innerHTML = '';
        showNotification(`Assigned ${username}`, 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Unassign user
async function unassignUser(assignmentId) {
    try {
        await apiRequest(`/api/cards/${currentCard.id}/assignments/${assignmentId}`, {
            method: 'DELETE'
        });
        
        currentCard = await apiRequest(`/api/cards/${currentCard.id}`);
        renderAssignedUsers();
        await loadBoard();
        showNotification('User unassigned', 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    }
}

// Save card changes
document.getElementById('saveCardBtn').addEventListener('click', async () => {
    const title = document.getElementById('cardTitle').value.trim();
    const description = document.getElementById('cardDescription').value;
    const dueDateValue = document.getElementById('cardDueDate').value;
    
    if (!title) {
        showNotification('Title is required', 'error');
        return;
    }
    
    const updates = {
        title,
        description,
        due_date: dueDateValue || null
    };
    
    try {
        await apiRequest(`/api/cards/${currentCard.id}`, {
            method: 'PUT',
            body: JSON.stringify(updates)
        });
        
        closeModal('cardModal');
        await loadBoard();
        showNotification('Card updated', 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    }
});

// Delete card
document.getElementById('deleteCardBtn').addEventListener('click', async () => {
    if (!confirm('Delete this card?')) return;
    
    try {
        await apiRequest(`/api/cards/${currentCard.id}`, {
            method: 'DELETE'
        });
        
        closeModal('cardModal');
        await loadBoard();
        showNotification('Card deleted', 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    }
});

// Add list
document.getElementById('addListBtn').addEventListener('click', () => {
    document.getElementById('addListBtn').style.display = 'none';
    document.getElementById('addListForm').style.display = 'block';
    document.getElementById('newListTitle').focus();
});

document.getElementById('saveListBtn').addEventListener('click', async () => {
    const title = document.getElementById('newListTitle').value.trim();
    
    if (!title) return;
    
    try {
        await apiRequest('/api/lists', {
            method: 'POST',
            body: JSON.stringify({ title, board_id: parseInt(boardId) })
        });
        
        document.getElementById('newListTitle').value = '';
        document.getElementById('addListForm').style.display = 'none';
        document.getElementById('addListBtn').style.display = 'block';
        
        await loadBoard();
        showNotification('List added', 'success');
    } catch (error) {
        showNotification(error.message, 'error');
    }
});

document.getElementById('cancelListBtn').addEventListener('click', () => {
    document.getElementById('newListTitle').value = '';
    document.getElementById('addListForm').style.display = 'none';
    document.getElementById('addListBtn').style.display = 'block';
});

// Invite member
document.getElementById('inviteMemberBtn').addEventListener('click', () => {
    openModal('inviteMemberModal');
});

document.getElementById('inviteMemberForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('inviteUsername').value.trim();
    
    try {
        await apiRequest(`/api/boards/${boardId}/members`, {
            method: 'POST',
            body: JSON.stringify({ username })
        });
        
        closeModal('inviteMemberModal');
        document.getElementById('inviteMemberForm').reset();
        showNotification('Member invited', 'success');
        await loadActivities();
    } catch (error) {
        showNotification(error.message, 'error');
    }
});

// Show members
document.getElementById('showMembersBtn').addEventListener('click', async () => {
    try {
        const members = await apiRequest(`/api/boards/${boardId}/members`);
        const container = document.getElementById('membersList');
        
        container.innerHTML = members.map(member => {
            const user = member.user;
            const initial = user.username.charAt(0).toUpperCase();
            
            return `
                <div class="member-item">
                    <div class="member-info">
                        <div class="member-avatar">${initial}</div>
                        <div>
                            <div>${escapeHtml(user.username)}</div>
                            <div class="member-role">${member.role}</div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        openModal('membersModal');
    } catch (error) {
        showNotification(error.message, 'error');
    }
});

// Load activities
async function loadActivities() {
    try {
        const activities = await apiRequest(`/api/boards/${boardId}/activities`);
        const container = document.getElementById('activityList');
        
        if (activities.length === 0) {
            container.innerHTML = '<p style="color: var(--text-secondary); padding: 1rem;">No activity yet</p>';
            return;
        }
        
        container.innerHTML = activities.map(activity => `
            <div class="activity-item">
                <span class="activity-user">${escapeHtml(activity.user.username)}</span>
                ${escapeHtml(activity.description)}
                <div class="activity-time">${formatRelativeTime(activity.created_at)}</div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Failed to load activities:', error);
    }
}

// Toggle activity log
document.getElementById('toggleActivityBtn').addEventListener('click', () => {
    const activityLog = document.querySelector('.activity-log');
    activityLog.classList.toggle('collapsed');
    document.getElementById('toggleActivityBtn').textContent = 
        activityLog.classList.contains('collapsed') ? '▲' : '▼';
});

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
loadBoard();
// Delete board
document.getElementById('deleteBoardBtn').addEventListener('click', async () => {
    if (!confirm('Are you sure you want to delete this board? This action cannot be undone.')) return;
    
    try {
        await apiRequest(`/api/boards/${boardId}`, {
            method: 'DELETE'
        });
        
        showNotification('Board deleted', 'success');
        setTimeout(() => {
            window.location.href = '/';
        }, 1000);
    } catch (error) {
        showNotification(error.message, 'error');
    }
});