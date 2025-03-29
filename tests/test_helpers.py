from typing import Dict, Any
import os

def get_test_config() -> Dict[str, Any]:
    """Get test configuration"""
    return {
        "api_key": os.getenv("AZURE_API_KEY"),
        "api_base": os.getenv("AZURE_API_BASE"),
        "api_version": os.getenv("AZURE_API_VERSION"),
        "deployment_name": "gama"
    }

def get_test_lead() -> Dict[str, Any]:
    """Get test lead data"""
    return {
        "company_name": "Test Company",
        "contact_email": "test@example.com",
        "industry": "Technology",
        "website": "https://example.com"
    }