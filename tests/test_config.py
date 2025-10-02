import os
import sys
import unittest
from app import create_app, db
from config import Config

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestConfig(unittest.TestCase):
    """Test application configuration."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        self.app_context.pop()
    
    def test_default_config(self):
        """Test creating app with default config."""
        self.assertFalse(self.app.config['TESTING'])
        self.assertEqual(
            self.app.config['SQLALCHEMY_DATABASE_URI'], 
            'sqlite:///boardify.db',
            "Should use the default SQLite database"
        )
        self.assertTrue(self.app.config['WTF_CSRF_ENABLED'])
    
    def test_testing_config(self):
        """Test testing configuration."""
        class TestingConfig(Config):
            TESTING = True
            WTF_CSRF_ENABLED = False
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
        
        test_app = create_app(TestingConfig)
        self.assertTrue(test_app.config['TESTING'])
        self.assertEqual(
            test_app.config['SQLALCHEMY_DATABASE_URI'], 
            'sqlite:///:memory:',
            "Should use in-memory SQLite for testing"
        )
        self.assertFalse(test_app.config['WTF_CSRF_ENABLED'])

if __name__ == '__main__':
    unittest.main()
