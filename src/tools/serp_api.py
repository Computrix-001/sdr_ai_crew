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
                "engine": "google"
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
                          emails: bool = True) -> str:
        """Build a search query based on filters"""
        query_parts = []
        
        if keyword:
            query_parts.append(f'"{keyword}"')
            
        if website:
            query_parts.append(f'site:{website}')
            
        if position:
            query_parts.append(f'"{position}"')
            
        # Add email domains if requested
        if emails:
            email_domains = '"@gmail.com" OR "@yahoo.com" OR "@hotmail.com" OR "@outlook.com" OR "@aol.com"'
            query_parts.append(f'({email_domains})')
        
        # Combine all parts
        query = " ".join(query_parts)
        
        # Add location as a separate parameter if provided
        location_param = {}
        if location:
            location_param = {"location": location}
            
        return query, location_param