import os
import tempfile
import pytest
from app import create_app, db
from config import Config

class TestConfig(Config):
    """Test configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test module."""
    # Create the app with test configuration
    app = create_app(TestConfig)
    
    # Create the database and load test data
    with app.app_context():
        db.create_all()
        
        # Create a test user
        from models import User
        user = User(username='testuser', email='test@example.com')
        user.set_password('testpass')
        db.session.add(user)
        db.session.commit()
    
    yield app
    
    # Clean up the database after the test
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

class AuthActions:
    """Class to handle authentication in tests."""
    def __init__(self, client):
        self._client = client
    
    def login(self, username='testuser', password='testpass'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password},
            follow_redirects=True
        )
    
    def logout(self):
        return self._client.get('/auth/logout', follow_redirects=True)

@pytest.fixture
def auth(client):
    """Fixture for handling authentication in tests."""
    return AuthActions(client)
