from serpapi import GoogleSearch
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import re
import phonenumbers # <-- ADDED

class SerpApiClient:
    """SERP API client for lead generation with contact and profile extraction."""
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
                "gl": "us",  # Consider making this configurable based on location search
                "hl": "en"
            }
            if search_params:
                params.update(search_params)

            print(f"Executing SerpApi search with params: {params}") # Added print for debug
            search = GoogleSearch(params)
            results = search.get_dict()
            # print(f"SerpApi raw results: {results}") # Uncomment for deep debugging
            return results
        except Exception as e:
            print(f"Error in SERP API search: {e}")
            return None

    def build_search_query(self, keyword: str = None, website: str = None,
                          location: str = None, position: str = None,
                          emails: bool = True, phone: bool = True) -> tuple:
        """Build a search query based on filters. Simplified query hints."""
        query_parts = []
        if keyword: query_parts.append(f'"{keyword}"')
        # Include website search only if it's specific (e.g., linkedin.com)
        # Avoid using generic website searches if keyword is broad
        if website and '.' in website: query_parts.append(f'site:{website}')
        if position: query_parts.append(f'"{position}"')

        # Simplified query hints, relying more on extraction functions
        if emails: query_parts.append(f'("email" OR "contact")')
        if phone: query_parts.append(f'("phone" OR "contact" OR "tel")')

        # Combine query parts
        query = " ".join(query_parts)

        # Location parameter for SerpApi
        location_param = {"location": location} if location else {}

        return query, location_param

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract email and phone number from text using improved methods."""
        extracted_email = None
        extracted_phone = None

        # 1. Improved Email Extraction
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_matches = re.finditer(email_pattern, text)
        for match in email_matches:
            email = match.group(0).lower() # Normalize to lowercase
            # Basic filter to avoid common false positives
            if not any(ext in email for ext in ['.png', '.jpg', '.gif', '.webp', '.svg', '.jpeg']) and \
               '@example.' not in email and \
               'sentry.io' not in email and \
               not email.startswith('http') and \
               len(email.split('@')[0]) > 1 and \
               len(email.split('@')[-1].split('.')) >= 2 and \
               len(email.split('@')[-1].split('.')[-1]) >= 2:
                    extracted_email = email
                    break # Take the first plausible match

        # 2. Phone Number Extraction using phonenumbers library
        try:
            # Use finditer with a default region (e.g., "US"). Consider making region dynamic.
            for match in phonenumbers.PhoneNumberMatcher(text, "US"):
                number = match.number
                if phonenumbers.is_valid_number(number):
                    # Format to E.164 standard for consistency
                    formatted_number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
                    # Basic check to avoid overly simple numbers sometimes matched
                    if len(re.sub(r'\D', '', formatted_number)) >= 10:
                         extracted_phone = formatted_number
                         break # Take the first valid, reasonably long number found
        except Exception as e:
            # Log phonenumbers parsing errors if they occur, but don't crash
            print(f"Warning: Error during phone number parsing: {e}")

        return {
            'email': extracted_email,
            'phone': extracted_phone
        }

    def extract_profile_links(self, text: str, primary_link: Optional[str] = None) -> Dict[str, Optional[str]]:
        """Extract social/professional profile links (LinkedIn, GitHub) from text."""
        profiles = {
            'linkedin_url': None,
            'github_url': None
        }

        # Regex patterns - refined slightly
        linkedin_pattern = r'(https?://(?:www\.)?linkedin\.com/(?:in|pub|company)/[a-zA-Z0-9_-]+(?:/[a-zA-Z0-9_-]+)*)/?'
        github_pattern = r'(https?://(?:www\.)?github\.com/[a-zA-Z0-9_-]+)/?'

        search_text = text
        if primary_link:
            search_text += " " + primary_link

        # Find LinkedIn links
        linkedin_matches = re.finditer(linkedin_pattern, search_text, re.IGNORECASE)
        best_linkedin = None
        for match in linkedin_matches:
            url = match.group(1).rstrip('/')
            if '/in/' in url and len(url.split('/in/')[1]) > 1: # Prioritize personal profiles with non-empty identifier
                best_linkedin = url
                break
            elif ('/pub/' in url or '/company/' in url) and not best_linkedin: # Fallback
                 best_linkedin = url
        profiles['linkedin_url'] = best_linkedin

        # Find GitHub links
        github_matches = re.finditer(github_pattern, search_text, re.IGNORECASE)
        for match in github_matches:
            url = match.group(1).rstrip('/')
            path_part = url.split('github.com/')[-1]
            # Avoid common non-profile paths and ensure it's not just github.com
            if '/' not in path_part and path_part and path_part.lower() not in [
                'topics', 'trending', 'sponsors', 'explore', 'marketplace', 'pricing', 'features',
                'about', 'contact', 'login', 'join', 'collections', 'new', 'codespaces', 'settings',
                'notifications', 'organizations', 'orgs', 'apps', 'integrations', 'blog', 'readme', 'security'
                ]:
                 profiles['github_url'] = url
                 break # Take the first likely user profile

        return profiles