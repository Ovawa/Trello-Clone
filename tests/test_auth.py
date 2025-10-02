import pytest
from flask import session
from models import User

def test_register(client, app):
    """Test user registration."""
    # Test that registration page renders
    response = client.get('/auth/register')
    assert response.status_code == 200
    
    # Test successful registration
    response = client.post(
        '/auth/register',
        data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass',
            'confirm': 'testpass'
        },
        follow_redirects=True
    )
    assert b'Registration successful' in response.data
    
    # Check if user was added to the database
    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'

def test_login(client, auth):
    """Test user login."""
    # Test that login page renders
    response = client.get('/auth/login')
    assert response.status_code == 200
    
    # Test successful login
    response = auth.login('testuser', 'testpass')
    assert b'Login successful' in response.data
    
    # Test that user is logged in
    with client:
        client.get('/')
        assert 'user_id' in session

def test_logout(client, auth):
    """Test user logout."""
    # Login first
    auth.login('testuser', 'testpass')
    
    # Test logout
    with client:
        response = auth.logout()
        assert 'user_id' not in session
        assert b'You have been logged out' in response.data

def test_login_required(client):
    """Test that login is required for protected views."""
    response = client.get('/')
    assert response.status_code == 302  # Should redirect to login
    assert '/auth/login' in response.location
