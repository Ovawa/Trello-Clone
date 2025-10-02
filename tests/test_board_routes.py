import pytest
from flask import session, url_for
from models import Board, db, User, BoardMember

# Test board creation
def test_create_board_authenticated(client, auth):
    """Test creating a board as an authenticated user."""
    # Login first
    auth.login('testuser', 'testpass')
    
    # Test GET request to create board page
    response = client.get('/boards/create')
    assert response.status_code == 200
    assert b'Create New Board' in response.data
    
    # Test creating a new board
    response = client.post(
        '/boards/create',
        data={
            'title': 'Test Board',
            'description': 'A test board',
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Board created successfully' in response.data
    assert b'Test Board' in response.data

def test_view_board_authenticated(client, auth, test_user, test_board):
    """Test viewing a board as an authenticated user."""
    # Login first
    auth.login('testuser', 'testpass')
    
    # Test viewing the board
    response = client.get(f'/board/{test_board.id}')
    assert response.status_code == 200
    assert test_board.title.encode() in response.data
    assert b'Add List' in response.data  # Should see add list button

def test_edit_board_authenticated(client, auth, test_user, test_board):
    """Test editing a board as the owner."""
    # Login as the owner
    auth.login('testuser', 'testpass')
    
    # Test updating the board
    response = client.post(
        f'/board/{test_board.id}/edit',
        data={
            'title': 'Updated Board Title',
            'description': 'Updated description',
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Board updated successfully' in response.data
    assert b'Updated Board Title' in response.data

def test_delete_board_authenticated(client, auth, test_user, test_board):
    """Test deleting a board as the owner."""
    # Login as the owner
    auth.login('testuser', 'testpass')
    
    # Test deleting the board
    response = client.post(
        f'/board/{test_board.id}/delete',
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Board deleted successfully' in response.data
    
    # Verify board was deleted
    with client.application.app_context():
        board = Board.query.get(test_board.id)
        assert board is None

# Test board member management
def test_add_board_member(client, auth, test_user, test_board):
    """Test adding a member to a board."""
    # Login as the owner
    auth.login('testuser', 'testpass')
    
    # Create a test member
    with client.application.app_context():
        member = User(username='member', email='member@example.com')
        member.set_password('testpass')
        db.session.add(member)
        db.session.commit()
        member_id = member.id
    
    # Add member to the board
    response = client.post(
        f'/board/{test_board.id}/members/add',
        data={'user_id': member_id, 'role': 'member'},
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Member added successfully' in response.data
    
    # Verify member was added
    with client.application.app_context():
        membership = BoardMember.query.filter_by(
            board_id=test_board.id,
            user_id=member_id
        ).first()
        assert membership is not None
        assert membership.role == 'member'

# Fixtures
@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_board(app, test_user):
    """Create a test board."""
    with app.app_context():
        board = Board(
            title='Test Board',
            description='A test board',
            owner_id=test_user.id
        )
        db.session.add(board)
        db.session.commit()
        return board
