from serpapi import GoogleSearch
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

class SerpApiClient:
    """SERP API client for lead generation"""
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError("SERPAPI_API_KEY not found in environment variables")

    def search(self, query: str, num_results: int = 10, search_params: Dict = None) -> Optional[Dict]:
        """Execute search using SERP API"""
        try:
            params = {
                "q": query,
                "num": num_results,
                "api_key": self.api_key,
                "engine": "google",
                "gl": "us",  # Search in US
                "hl": "en"   # Language in English
            }
            
            # Add any additional search parameters
            if search_params:
                params.update(search_params)
            
            search = GoogleSearch(params)
            return search.get_dict()
        except Exception as e:
            print(f"Error in SERP API search: {e}")
            return None
            
    def build_search_query(self, keyword: str = None, website: str = None, 
                          location: str = None, position: str = None, 
                          emails: bool = True, phone: bool = True) -> tuple:
        """Build a search query based on filters"""
        query_parts = []
        
        if keyword:
            query_parts.append(f'"{keyword}"')
            
        if website:
            query_parts.append(f'site:{website}')
            
        if position:
            query_parts.append(f'"{position}"')
            
        # Add contact information patterns
        if emails:
            email_patterns = '"@gmail.com" OR "@yahoo.com" OR "@hotmail.com" OR "@outlook.com" OR "@company.com" OR "@business.com"'
            query_parts.append(f'({email_patterns})')
        
        if phone:
            phone_patterns = '"phone:" OR "contact:" OR "tel:" OR "mobile:"'
            query_parts.append(f'({phone_patterns})')
        
        # Combine all parts
        query = " ".join(query_parts)
        
        # Add location as a separate parameter if provided
        location_param = {}
        if location:
            location_param = {"location": location}
            
        return query, location_param

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract email and phone number from text"""
        import re
        
        # Email pattern
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, text)
        
        # Phone pattern (various formats)
        phone_pattern = r'(?:(?:\+?1\s*(?:[.-]\s*)?)?(?:\(\s*([0-9]{3})\s*\)|([0-9]{3}))\s*(?:[.-]\s*)?)?([0-9]{3})\s*(?:[.-]\s*)?([0-9]{4})'
        phone_match = re.search(phone_pattern, text)
        
        return {
            'email': email_match.group(0) if email_match else None,
            'phone': phone_match.group(0) if phone_match else None
        }