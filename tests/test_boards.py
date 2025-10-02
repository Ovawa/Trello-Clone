import pytest
from models import Board, List, Card, db

# Test board creation
def test_create_board(client, auth):
    # Login first
    auth.register('testuser', 'testpass')
    auth.login('testuser', 'testpass')
    
    # Test board creation page
    response = client.get('/boards/create')
    assert response.status_code == 200
    
    # Test creating a board
    response = client.post(
        '/boards/create',
        data={'title': 'Test Board', 'description': 'Test Description'},
        follow_redirects=True
    )
    assert b'Test Board' in response.data
    
    # Check if board was added to the database
    with client.application.app_context():
        board = Board.query.first()
        assert board is not None
        assert board.title == 'Test Board'
        assert board.user_id == 1  # First user

# Test board view
def test_view_board(client, auth):
    # Login and create a test board
    auth.register('testuser', 'testpass')
    auth.login('testuser', 'testpass')
    
    # Create a test board
    with client.application.app_context():
        board = Board(title='Test Board', user_id=1)
        db.session.add(board)
        db.session.commit()
        board_id = board.id
    
    # Test viewing the board
    response = client.get(f'/boards/{board_id}')
    assert response.status_code == 200
    assert b'Test Board' in response.data

# Test board deletion
def test_delete_board(client, auth):
    # Login and create a test board
    auth.register('testuser', 'testpass')
    auth.login('testuser', 'testpass')
    
    # Create a test board
    with client.application.app_context():
        board = Board(title='Test Board', user_id=1)
        db.session.add(board)
        db.session.commit()
        board_id = board.id
    
    # Test deleting the board
    response = client.post(f'/boards/{board_id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert b'Board deleted successfully' in response.data
    
    # Check if board was deleted from the database
    with client.application.app_context():
        board = Board.query.get(board_id)
        assert board is None
