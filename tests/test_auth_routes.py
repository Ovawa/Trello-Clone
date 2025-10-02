import pytest
from flask import session, url_for
from models import User, db

def test_register_route(client, app):
    """Test user registration through the API."""
    # Test GET request to register page
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Register' in response.data
    
    # Test successful registration
    response = client.post(
        '/auth/register',
        data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'confirm': 'testpass123'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Registration successful' in response.data
    
    # Verify user was created in the database
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'

def test_login_route(client, test_user):
    """Test user login through the API."""
    # Test GET request to login page
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    
    # Test successful login
    response = client.post(
        '/auth/login',
        data={
            'username': 'testuser',
            'password': 'testpass'
        },
        follow_redirects=True
    )
    assert response.status_code == 200
    assert b'Login successful' in response.data
    
    # Test session is set
    with client.session_transaction() as sess:
        assert 'user_id' in sess

def test_logout_route(client, test_user, auth):
    """Test user logout through the API."""
    # Login first
    auth.login('testuser', 'testpass')
    
    # Test logout
    response = client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data
    
    # Test session is cleared
    with client.session_transaction() as sess:
        assert 'user_id' not in sess

@pytest.mark.parametrize(('username', 'password', 'message'), [
    ('', '', b'Username is required'),
    ('test', '', b'Password is required'),
    ('wrong', 'wrong', b'Invalid username or password'),
])
def test_login_validate_input(client, test_user, username, password, message):
    """Test login form validation."""
    response = client.post(
        '/auth/login',
        data={'username': username, 'password': password},
        follow_redirects=True
    )
    assert message in response.data

@pytest.fixture
def test_user(app):
    """Create a test user for authentication tests."""
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
        return user
