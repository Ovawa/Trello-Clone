import pytest
from flask import json
from models import List, Card, db, User, Board

# Test list routes
def test_create_list_authenticated(client, auth, test_user, test_board):
    """Test creating a list as an authenticated user."""
    # Login first
    auth.login('testuser', 'testpass')
    
    # Test creating a new list via API
    response = client.post(
        f'/api/boards/{test_board.id}/lists',
        data=json.dumps({
            'title': 'Test List',
            'position': 1
        }),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Test List'
    assert data['position'] == 1
    
    # Verify list was created in the database
    with client.application.app_context():
        list_item = List.query.filter_by(board_id=test_board.id).first()
        assert list_item is not None
        assert list_item.title == 'Test List'

def test_update_list_authenticated(client, auth, test_user, test_board, test_list):
    """Test updating a list as an authenticated user."""
    # Login first
    auth.login('testuser', 'testpass')
    
    # Update the list
    response = client.put(
        f'/api/lists/{test_list.id}',
        data=json.dumps({
            'title': 'Updated List Title',
            'position': 2
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Updated List Title'
    assert data['position'] == 2

# Test card routes
def test_create_card_authenticated(client, auth, test_user, test_board, test_list):
    """Test creating a card as an authenticated user."""
    # Login first
    auth.login('testuser', 'testpass')
    
    # Test creating a new card via API
    response = client.post(
        f'/api/lists/{test_list.id}/cards',
        data=json.dumps({
            'title': 'Test Card',
            'description': 'A test card',
            'position': 1
        }),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Test Card'
    assert data['position'] == 1
    
    # Verify card was created in the database
    with client.application.app_context():
        card = Card.query.filter_by(list_id=test_list.id).first()
        assert card is not None
        assert card.title == 'Test Card'

def test_assign_card_authenticated(client, auth, test_user, test_card):
    """Test assigning a card to a user."""
    # Login first
    auth.login('testuser', 'testpass')
    
    # Assign the card to the test user
    response = client.post(
        f'/api/cards/{test_card.id}/assign',
        data=json.dumps({
            'user_id': test_user.id
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'Card assigned successfully'
    
    # Verify assignment in the database
    with client.application.app_context():
        assignment = db.session.query(CardAssignment).filter_by(
            card_id=test_card.id,
            user_id=test_user.id
        ).first()
        assert assignment is not None

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

@pytest.fixture
def test_list(app, test_board):
    """Create a test list."""
    with app.app_context():
        list_item = List(
            title='Test List',
            board_id=test_board.id,
            position=1
        )
        db.session.add(list_item)
        db.session.commit()
        return list_item

@pytest.fixture
def test_card(app, test_list, test_user):
    """Create a test card."""
    with app.app_context():
        card = Card(
            title='Test Card',
            description='A test card',
            list_id=test_list.id,
            position=1
        )
        db.session.add(card)
        db.session.commit()
        return card
