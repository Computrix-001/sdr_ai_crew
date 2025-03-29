import unittest
import os
import sys
from dotenv import load_dotenv

# Add project root to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.outreach_agent import OutreachAgent
from src.utils.helpers import validate_email

class TestOutreachAgent(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        # Load environment variables
        load_dotenv()
        try:
            cls.agent = OutreachAgent()
        except Exception as e:
            print(f"Failed to initialize OutreachAgent: {str(e)}")
            raise

    def test_initialization(self):
        """Test if the agent initializes correctly"""
        self.assertIsNotNone(self.agent.email_client)
        self.assertIsNotNone(self.agent.client)  # OpenAI client
        
    def test_email_validation(self):
        """Test email validation"""
        valid_email = "test@example.com"
        invalid_email = "invalid-email"
        
        # Test with valid email
        self.assertTrue(
            self.agent._validate_email(
                valid_email, 
                "Test Subject", 
                "Test content"
            )
        )
        
        # Test with invalid email
        self.assertFalse(
            self.agent._validate_email(
                invalid_email,
                "Test Subject",
                "Test content"
            )
        )

    def test_html_conversion(self):
        """Test HTML conversion"""
        test_content = "Hello\n\nThis is a test."
        html = self.agent._convert_to_html(test_content)
        self.assertIn("<p>Hello</p>", html)
        self.assertIn("<p>This is a test.</p>", html)
    
    def test_rate_limiting(self):
        """Test rate limiting"""
        self.assertTrue(self.agent.rate_limiter.can_send())
        
        # Test rate limit
        for _ in range(50):  # Fill up the rate limit
            self.agent.rate_limiter.can_send()
            
        # Should be rate limited now
        self.assertFalse(self.agent.rate_limiter.can_send())

if __name__ == '__main__':
    unittest.main()