from typing import List, Dict, Optional
from tools.serp_api import SerpApiClient
import pandas as pd
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
import json
import time # Import time for potential delays

# Load environment variables at the module level
load_dotenv()

class LeadGenerationAgent:
    """Agent responsible for generating leads using SERP API and AI filtering"""
    def __init__(self, serp_api_client: Optional[SerpApiClient] = None):
        self.serp_api_client = serp_api_client or SerpApiClient()
        self.openai_client = None
        self.deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT')

        # Initialize Azure OpenAI client robustly
        if all([os.getenv('AZURE_OPENAI_API_KEY'), os.getenv('AZURE_OPENAI_ENDPOINT'), self.deployment_name]):
            try:
                self.openai_client = AzureOpenAI(
                    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                    api_version=os.getenv('AZURE_OPENAI_API_VERSION', "2024-02-01"), # Default API version
                    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
                )
                # Perform a quick test call to verify deployment
                self.openai_client.models.retrieve(self.deployment_name)
                print(f"✅ Azure OpenAI client initialized for Lead Generation Agent. Deployment: {self.deployment_name}")
            except Exception as e:
                print(f"❌ Failed to initialize or verify Azure OpenAI client for Lead Generation: {e}")
                self.openai_client = None
        else:
             print("⚠️ Azure OpenAI environment variables missing (API Key, Endpoint, or Deployment Name). AI filtering disabled.")


    def _filter_leads_with_ai(self, leads: List[Dict], criteria: Dict) -> List[Dict]:
        """Filter leads using Azure OpenAI based on provided criteria"""
        if not self.openai_client or not leads:
            print("Skipping AI filtering (client not available or no leads).")
            return leads

        print(f"\n🤖 Filtering {len(leads)} potential leads using AI based on criteria: {criteria}...")
        filtered_leads = []
        max_retries = 2
        retry_delay = 3 # seconds

        # Customize this prompt carefully!
        prompt_template = """
        Analyze the potential B2B sales lead described in the snippet below based on the search criteria.
        Is this lead relevant for a company selling [**Your Product/Service - BE SPECIFIC HERE, e.g., 'AI-powered customer support software' or 'custom manufacturing components'**]?

        Search Criteria Used:
        - Keyword/Industry: {keyword}
        - Target Position/Role: {position}
        - Location Focus: {location}
        - Website Focus: {website}

        Lead Information from Search Result:
        - Title: {title}
        - Website (if available): {link}
        - Description/Snippet: {snippet}

        Evaluation Task:
        Based *only* on the title and snippet, determine relevance. Is this likely a company or individual that fits the target profile and could benefit from [**Your Product/Service again**]?
        Answer ONLY in JSON format with keys "is_relevant" (boolean) and "reasoning" (string, max 30 words explanation).

        Example Relevant Output:
        {{
          "is_relevant": true,
          "reasoning": "Snippet mentions challenges in customer retention for e-commerce, aligning with our AI support software's value proposition."
        }}
        Example Irrelevant Output:
        {{
          "is_relevant": false,
          "reasoning": "This is a news article discussing market trends, not a potential client company."
        }}

        Evaluate this lead:
        """

        for i, lead in enumerate(leads):
            print(f"  - Evaluating lead {i+1}/{len(leads)}: '{lead.get('company_name', 'N/A')}'")
            attempt = 0
            while attempt < max_retries:
                try:
                    prompt = prompt_template.format(
                        keyword=criteria.get('keyword', 'N/A'),
                        position=criteria.get('position', 'N/A'),
                        location=criteria.get('location', 'N/A'),
                        website=criteria.get('website', 'N/A'),
                        title=lead.get('company_name', 'N/A'),
                        link=lead.get('website', 'N/A'),
                        snippet=lead.get('description', '')[:1500] # Limit snippet length
                    )

                    response = self.openai_client.chat.completions.create(
                        model=self.deployment_name,
                        messages=[
                            {"role": "system", "content": "You are an AI assistant evaluating B2B sales lead relevance from web search snippets. Be concise."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=100,
                        temperature=0.1, # Very low temp for consistency
                        response_format={"type": "json_object"}
                    )
                    ai_response_content = response.choices[0].message.content

                    evaluation = json.loads(ai_response_content)
                    is_relevant = evaluation.get("is_relevant", False)
                    reasoning = evaluation.get("reasoning", "N/A")

                    print(f"    AI Decision: Relevant={is_relevant}. Reasoning: {reasoning}")
                    if is_relevant:
                        lead['ai_filter_reasoning'] = reasoning # Store reasoning
                        filtered_leads.append(lead)
                    break # Success, move to next lead

                except json.JSONDecodeError as e:
                    print(f"    Error: Failed to parse AI JSON response on attempt {attempt+1}: {ai_response_content}. Error: {e}")
                    # Don't retry JSON errors usually
                    break
                except Exception as e:
                    print(f"    Error evaluating lead with AI on attempt {attempt+1}: {e}")
                    attempt += 1
                    if attempt < max_retries:
                        print(f"    Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print(f"    Max retries reached for this lead. Skipping.")
                        break # Failed after retries

        print(f"🤖 AI Filtering Complete. Kept {len(filtered_leads)} out of {len(leads)} leads.")
        return filtered_leads

    def generate_leads(self, query: str, num_results: int = 5, search_params: Dict = None, filter_criteria: Dict = None) -> List[Dict]:
        """Generate leads using SERP API search and optional AI filtering"""
        print(f"\n--- Starting Lead Generation ---")
        print(f"Requested results: {num_results}")

        # Fetch more results if AI filtering is enabled
        fetch_multiplier = 3 if (filter_criteria and self.openai_client) else 1
        results_to_fetch = max(10, num_results * fetch_multiplier) # Fetch at least 10, or more for filtering
        print(f"Fetching {results_to_fetch} results from SerpApi for query: {query}")

        search_results = self.serp_api_client.search(query, results_to_fetch, search_params)
        if not search_results or "organic_results" not in search_results:
            print("❌ No organic search results found from SerpApi.")
            return []

        initial_leads = self.process_results(search_results)
        print(f"Processed {len(initial_leads)} potential leads from search results.")

        # Apply AI filtering
        if filter_criteria and self.openai_client:
            final_leads = self._filter_leads_with_ai(initial_leads, filter_criteria)
        else:
            final_leads = initial_leads # Skip AI filtering

        # Limit to the number of results requested by the user *after* filtering
        final_leads = final_leads[:num_results]

        print(f"✅ Returning {len(final_leads)} final leads.")
        print(f"--- Lead Generation Complete ---")
        return final_leads

    def generate_leads_with_filters(self, keyword: str = None, website: str = None,
                                   location: str = None, position: str = None,
                                   num_results: int = 5) -> List[Dict]:
        """Generate leads using filters and apply AI filtering"""
        query, location_param = self.serp_api_client.build_search_query(
            keyword=keyword, website=website, location=location, position=position,
            emails=True, phone=True # Keep trying to find contact info hints
        )
        print(f"Generated search query: {query}")
        if not query.strip():
             print("⚠️ Warning: Search query is empty. Please provide filters.")
             return []

        filter_criteria = {
            "keyword": keyword, "website": website, "location": location, "position": position
        }
        return self.generate_leads(query, num_results, location_param, filter_criteria)

    def process_results(self, search_results: Dict) -> List[Dict]:
        """Process search results into lead format, extracting contacts and profile links."""
        leads = []
        if "organic_results" not in search_results:
             return []

        for result in search_results.get("organic_results", []):
            snippet = result.get("snippet", "")
            primary_link = result.get("link")
            title = result.get("title")

            if not title or not snippet: # Skip results with no title or snippet
                 continue

            contact_info = self.serp_api_client.extract_contact_info(snippet + " " + title) # Check title too
            profile_links = self.serp_api_client.extract_profile_links(snippet, primary_link)

            lead = {
                "company_name": title,
                "website": primary_link,
                "description": snippet,
                "contact_email": contact_info.get('email'),
                "contact_phone": contact_info.get('phone'),
                "linkedin_url": profile_links.get('linkedin_url'),
                "github_url": profile_links.get('github_url'),
                "contact_name": None, # Could potentially be extracted later by research agent
                "industry": None,     # Could potentially be extracted later by research agent
                "location": result.get("displayed_link") # Sometimes location is in displayed link
                           or result.get("rich_snippet", {}).get("top", {}).get("detected_extensions", {}).get("location"),
                 # ai_filter_reasoning might be added later by _filter_leads_with_ai
            }
            # Basic deduplication based on website link if present
            is_duplicate = False
            if lead.get("website"):
                 for existing_lead in leads:
                      if existing_lead.get("website") == lead.get("website"):
                           is_duplicate = True
                           break
            if not is_duplicate:
                 leads.append(lead)

        return leads

    def format_leads_table(self, leads: List[Dict]) -> pd.DataFrame:
        """Format leads into a pandas DataFrame for tabular display."""
        if not leads:
             return pd.DataFrame() # Return empty DataFrame if no leads

        df = pd.DataFrame(leads)

        # Define desired column order
        columns = [
            "company_name", "contact_email", "contact_phone", "website",
            "linkedin_url", "github_url", "location", "description",
            "industry", "ai_filter_reasoning" # Include AI reasoning if available
        ]
        # Only include columns that actually exist in the DataFrame
        existing_columns = [col for col in columns if col in df.columns]

        return df[existing_columns]
