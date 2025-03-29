from dotenv import load_dotenv
import os
import unittest

class TestConfiguration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()
        
    def test_environment_variables(self):
        """Test if all required environment variables are set"""
        required_vars = [
            "AZURE_API_KEY",
            "AZURE_API_BASE",
            "AZURE_API_VERSION",
            "AZURE_COMMUNICATION_CONNECTION_STRING",
            "AZURE_COMMUNICATION_SENDER_EMAIL"
        ]
        
        for var in required_vars:
            self.assertIsNotNone(
                os.getenv(var), 
                f"Environment variable {var} is not set"
            )

if __name__ == '__main__':
    unittest.main()