"""Sanity tests to verify the testing environment."""
import unittest
import os
import sys
from app import create_app
from tests.conftest import TestConfig

class TestSanity(unittest.TestCase):
    """Test cases for basic sanity checks."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
    
    def tearDown(self):
        """Tear down test fixtures after each test method."""
        self.app_context.pop()
    
    def test_sanity(self):
        """A simple test that should always pass."""
        self.assertEqual(1 + 1, 2)
    
    def test_import_app(self):
        """Test that the app can be imported and created."""
        self.assertTrue(callable(create_app), "create_app should be callable")
        app = create_app(TestConfig)
        self.assertIsNotNone(app, "App should be created successfully")
    
    def test_flask_config(self):
        """Test that Flask configuration works."""
        self.assertTrue(self.app.config['TESTING'], "Test config should be loaded")
        self.assertEqual(
            self.app.config['SQLALCHEMY_DATABASE_URI'], 
            'sqlite:///:memory:',
            "Should use in-memory SQLite for testing"
        )

if __name__ == '__main__':
    unittest.main()
