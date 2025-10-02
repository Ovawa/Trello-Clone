"""Basic test file to verify test setup."""
import unittest
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestBasicSetup(unittest.TestCase):
    """Basic test cases to verify the test setup."""
    
    def test_import_app(self):
        """Test that the app can be imported."""
        try:
            from app import create_app
            self.assertTrue(callable(create_app), "create_app should be callable")
        except ImportError as e:
            self.fail(f"Failed to import app: {e}")
    
    def test_simple_assertion(self):
        """Test a simple assertion."""
        self.assertEqual(1 + 1, 2)

if __name__ == '__main__':
    unittest.main()
