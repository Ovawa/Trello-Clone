import pytest
from datetime import datetime, timedelta
from models import db, User, Board, List, Card, BoardMember, CardAssignment, Activity, Notification, Attachment, ChecklistItem

def test_user_model(app):
    """Test User model creation and relationships."""
    with app.app_context():
        # Create a test user
        user = User(
            username='testuser',
            email='test@example.com'
        )
        user.set_password('testpass123')
        
        # Test password hashing
        assert user.password_hash is not None
        assert user.password_hash != 'testpass123'
        assert user.check_password('testpass123') is True
        assert user.check_password('wrongpass') is False
        
        # Test to_dict method
        user_dict = user.to_dict()
        assert user_dict['username'] == 'testuser'
        assert 'password_hash' not in user_dict

def test_board_model(app):
    """Test Board model creation and relationships."""
    with app.app_context():
        # Create a test user
        user = User(username='boardowner', email='owner@example.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        
        # Create a board
        board = Board(
            title='Test Board',
            description='A test board',
            owner_id=user.id
        )
        db.session.add(board)
        db.session.commit()
        
        # Test relationships
        assert board.owner == user
        assert board in user.owned_boards
        
        # Test to_dict method
        board_dict = board.to_dict()
        assert board_dict['title'] == 'Test Board'
        assert 'lists' in board_dict

def test_list_model(app):
    """Test List model creation and relationships."""
    with app.app_context():
        # Create a test board
        user = User(username='listuser', email='list@example.com')
        user.set_password('testpass')
        board = Board(title='List Test Board', owner=user)
        db.session.add_all([user, board])
        db.session.commit()
        
        # Create a list
        list_item = List(
            title='To Do',
            board_id=board.id,
            position=1
        )
        db.session.add(list_item)
        db.session.commit()
        
        # Test relationships
        assert list_item.board == board
        assert list_item in board.lists
        
        # Test to_dict method
        list_dict = list_item.to_dict()
        assert list_dict['title'] == 'To Do'
        assert 'cards' in list_dict

def test_card_model(app):
    """Test Card model creation and relationships."""
    with app.app_context():
        # Create test data
        user = User(username='carduser', email='card@example.com')
        user.set_password('testpass')
        board = Board(title='Card Test Board', owner=user)
        list_item = List(title='Card List', board=board, position=1)
        db.session.add_all([user, board, list_item])
        db.session.commit()
        
        # Create a card
        due_date = datetime.utcnow() + timedelta(days=7)
        card = Card(
            title='Test Card',
            description='A test card',
            list_id=list_item.id,
            due_date=due_date,
            position=1
        )
        db.session.add(card)
        db.session.commit()
        
        # Test relationships
        assert card.list == list_item
        assert card in list_item.cards
        
        # Test to_dict method
        card_dict = card.to_dict()
        assert card_dict['title'] == 'Test Card'
        assert 'assignments' in card_dict

def test_board_member_model(app):
    """Test BoardMember model creation and relationships."""
    with app.app_context():
        # Create test data
        owner = User(username='owner', email='owner@example.com')
        member = User(username='member', email='member@example.com')
        board = Board(title='Member Test Board', owner=owner)
        db.session.add_all([owner, member, board])
        db.session.commit()
        
        # Create a board member
        board_member = BoardMember(
            board_id=board.id,
            user_id=member.id,
            role='member'
        )
        db.session.add(board_member)
        db.session.commit()
        
        # Test relationships
        assert board_member.user == member
        assert board_member.board == board
        assert board_member in member.board_memberships
        assert board_member in board.members
        
        # Test to_dict method
        member_dict = board_member.to_dict()
        assert member_dict['role'] == 'member'
        assert 'user' in member_dict

def test_card_assignment_model(app):
    """Test CardAssignment model creation and relationships."""
    with app.app_context():
        # Create test data
        user = User(username='assignee', email='assignee@example.com')
        board = Board(title='Assignment Test Board', owner=user)
        list_item = List(title='Assignment List', board=board, position=1)
        card = Card(title='Assignment Card', list=list_item, position=1)
        db.session.add_all([user, board, list_item, card])
        db.session.commit()
        
        # Create a card assignment
        assignment = CardAssignment(
            card_id=card.id,
            user_id=user.id
        )
        db.session.add(assignment)
        db.session.commit()
        
        # Test relationships
        assert assignment.card == card
        assert assignment.user == user
        assert assignment in card.assignments
        assert assignment in user.card_assignments
        
        # Test to_dict method
        assignment_dict = assignment.to_dict()
        assert 'user' in assignment_dict
        assert 'assigned_at' in assignment_dict

def test_activity_model(app):
    """Test Activity model creation and relationships."""
    with app.app_context():
        # Create test data
        user = User(username='activityuser', email='activity@example.com')
        board = Board(title='Activity Test Board', owner=user)
        db.session.add_all([user, board])
        db.session.commit()
        
        # Create an activity
        activity = Activity(
            board_id=board.id,
            user_id=user.id,
            action='create',
            entity_type='board',
            entity_id=board.id,
            description=f'Created board {board.title}'
        )
        db.session.add(activity)
        db.session.commit()
        
        # Test relationships
        assert activity.user == user
        assert activity.board == board
        assert activity in user.activities
        assert activity in board.activities
        
        # Test to_dict method
        activity_dict = activity.to_dict()
        assert activity_dict['action'] == 'create'
        assert 'user' in activity_dict
        assert 'created_at' in activity_dict

def test_notification_model(app):
    """Test Notification model creation and relationships."""
    with app.app_context():
        # Create test data
        user = User(username='notified', email='notified@example.com')
        board = Board(title='Notification Test Board', owner=user)
        db.session.add_all([user, board])
        db.session.commit()
        
        # Create a notification
        notification = Notification(
            user_id=user.id,
            title='Test Notification',
            message='This is a test notification',
            type='info',
            related_board_id=board.id
        )
        db.session.add(notification)
        db.session.commit()
        
        # Test relationships
        assert notification.user == user
        assert notification.board == board
        assert notification in user.notifications
        
        # Test to_dict method
        notification_dict = notification.to_dict()
        assert notification_dict['title'] == 'Test Notification'
        assert 'is_read' in notification_dict
        assert 'created_at' in notification_dict

def test_attachment_model(app):
    """Test Attachment model creation and relationships."""
    with app.app_context():
        # Create test data
        user = User(username='attachuser', email='attach@example.com')
        board = Board(title='Attachment Test Board', owner=user)
        list_item = List(title='Attachment List', board=board, position=1)
        card = Card(title='Attachment Card', list=list_item, position=1)
        db.session.add_all([user, board, list_item, card])
        db.session.commit()
        
        # Create an attachment
        attachment = Attachment(
            card_id=card.id,
            filename='test.txt',
            filepath='/uploads/test.txt',
            file_size=1024
        )
        db.session.add(attachment)
        db.session.commit()
        
        # Test relationships
        assert attachment.card == card
        assert attachment in card.attachments
        
        # Test to_dict method
        attachment_dict = attachment.to_dict()
        assert attachment_dict['filename'] == 'test.txt'
        assert 'uploaded_at' in attachment_dict

def test_checklist_item_model(app):
    """Test ChecklistItem model creation and relationships."""
    with app.app_context():
        # Create test data
        user = User(username='checkuser', email='check@example.com')
        board = Board(title='Checklist Test Board', owner=user)
        list_item = List(title='Checklist List', board=board, position=1)
        card = Card(title='Checklist Card', list=list_item, position=1)
        db.session.add_all([user, board, list_item, card])
        db.session.commit()
        
        # Create a checklist item
        checklist_item = ChecklistItem(
            card_id=card.id,
            title='Test Item',
            completed=False,
            position=1
        )
        db.session.add(checklist_item)
        db.session.commit()
        
        # Test relationships
        assert checklist_item.card == card
        assert checklist_item in card.checklists
        
        # Test toggling completion
        assert checklist_item.completed is False
        checklist_item.completed = True
        assert checklist_item.completed is True
        
        # Test to_dict method
        item_dict = checklist_item.to_dict()
        assert item_dict['title'] == 'Test Item'
        assert 'position' in item_dict
        assert 'created_at' in item_dict
