// Dashboard functionality

let boards = [];

// Load boards
async function loadBoards() {
    try {
        boards = await apiRequest('/api/boards');
        console.log('Loaded boards:', boards);
        renderBoards();
    } catch (error) {
        console.error('Failed to load boards:', error);
        const boardsGrid = document.getElementById('boardsGrid');
        boardsGrid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--danger-color);">
                <h3>Error loading boards</h3>
                <p>${error.message}</p>
                <button class="btn btn-primary" onclick="loadBoards()">Retry</button>
            </div>
        `;
        showNotification('Failed to load boards: ' + error.message, 'error');
    }
}

// Render boards
function renderBoards() {
    const boardsGrid = document.getElementById('boardsGrid');
    
    console.log('Rendering boards, count:', boards.length);
    
    if (!boards || boards.length === 0) {
        boardsGrid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-secondary);">
                <h3>No boards yet</h3>
                <p>Create your first board to get started!</p>
            </div>
        `;
        return;
    }
    
    boardsGrid.innerHTML = boards.map(board => `
        <a href="/board/${board.id}" class="board-card">
            <h3>${escapeHtml(board.title)}</h3>
            <p>${escapeHtml(board.description || 'No description')}</p>
            <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">
                ${board.owner_id ? 'Owner' : 'Member'}
            </div>
        </a>
    `).join('');
}

// Create board
document.getElementById('createBoardBtn').addEventListener('click', () => {
    openModal('createBoardModal');
    document.getElementById('boardTitle').focus();
});

document.getElementById('createBoardForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const title = document.getElementById('boardTitle').value;
    const description = document.getElementById('boardDescription').value;
    
    try {
        const newBoard = await apiRequest('/api/boards', {
            method: 'POST',
            body: JSON.stringify({ title, description })
        });
        
        boards.push(newBoard);
        renderBoards();
        closeModal('createBoardModal');
        
        // Reset form
        document.getElementById('createBoardForm').reset();
        
        showNotification('Board created successfully', 'success');
        
        // Redirect to new board
        setTimeout(() => {
            window.location.href = `/board/${newBoard.id}`;
        }, 500);
    } catch (error) {
        showNotification(error.message, 'error');
    }
});

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize
loadBoards();
