from typing import List, Dict, Optional
from tools.serp_api import SerpApiClient
import pandas as pd

class LeadGenerationAgent:
    """Agent responsible for generating leads using SERP API"""
    def __init__(self, serp_api_client: Optional[SerpApiClient] = None):
        self.serp_api_client = serp_api_client or SerpApiClient()

    def generate_leads(self, query: str, num_results: int = 5, search_params: Dict = None) -> List[Dict]:
        """Generate leads using SERP API search"""
        print(f"Searching for leads with query: {query}")
        
        search_results = self.serp_api_client.search(query, num_results, search_params)
        if not search_results:
            print("No search results found")
            return []
            
        leads = self.process_results(search_results)
        print(f"Found {len(leads)} potential leads")
        return leads
        
    def generate_leads_with_filters(self, keyword: str = None, website: str = None, 
                                   location: str = None, position: str = None,
                                   num_results: int = 5) -> List[Dict]:
        """Generate leads using filters"""
        query, location_param = self.serp_api_client.build_search_query(
            keyword=keyword, 
            website=website, 
            location=location, 
            position=position,
            emails=True,
            phone=True
        )
        
        print(f"Generated search query: {query}")
        return self.generate_leads(query, num_results, location_param)

    def process_results(self, search_results: Dict) -> List[Dict]:
        """Process search results into lead format"""
        leads = []
        for result in search_results.get("organic_results", []):
            # Extract contact information
            snippet = result.get("snippet", "")
            contact_info = self.serp_api_client.extract_contact_info(snippet)
            
            lead = {
                "company_name": result.get("title"),
                "website": result.get("link"),
                "description": snippet,
                "source": "SERP API",
                "contact_email": contact_info['email'],
                "contact_phone": contact_info['phone'],
                "contact_name": None,
                "industry": None,
                "location": result.get("location")
            }
            leads.append(lead)
        return leads

    def format_leads_table(self, leads: List[Dict]) -> pd.DataFrame:
        """Format leads into a pandas DataFrame for tabular display"""
        df = pd.DataFrame(leads)
        
        # Reorder columns for better display
        columns = [
            "company_name",
            "contact_email",
            "contact_phone",
            "website",
            "description",
            "industry",
            "location",
            "source"
        ]
        
        # Only include columns that exist in the DataFrame
        existing_columns = [col for col in columns if col in df.columns]
        
        return df[existing_columns]