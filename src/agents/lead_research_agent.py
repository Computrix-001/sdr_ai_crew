from typing import List, Dict
from openai import AzureOpenAI
import os
import pandas as pd
import streamlit as st

class LeadResearchAgent:
    def __init__(self):
        """Initialize LeadResearchAgent with Azure OpenAI client"""
        try:
            # Try with new CrewAI format first
            if os.getenv("AZURE_API_KEY") and os.getenv("AZURE_API_BASE"):
                self.client = AzureOpenAI(
                    api_key=os.getenv("AZURE_API_KEY"),
                    api_version=os.getenv("AZURE_API_VERSION"),
                    azure_endpoint=os.getenv("AZURE_API_BASE")
                )
            # Fall back to legacy format
            elif os.getenv("AZURE_OPENAI_API_KEY") and os.getenv("AZURE_OPENAI_ENDPOINT"):
                self.client = AzureOpenAI(
                    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
                    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
                )
            else:
                raise ValueError("Azure OpenAI credentials not found in environment variables")
        except Exception as e:
            print(f"Azure OpenAI initialization failed: {str(e)}")
            raise

    def research_company(self, lead: Dict) -> Dict:
        """Research company using available information and enrich lead data"""
        try:
            research_prompt = f"""
            Analyze this company and provide detailed insights:
            Company Name: {lead.get('company_name')}
            Industry: {lead.get('industry')}
            Website: {lead.get('website')}
            Description: {lead.get('description')}

            Please provide:
            1. Company Overview
            2. Key Products/Services
            3. Target Market
            4. Likely Pain Points
            5. Recent News/Developments
            6. Competitive Advantages
            7. Potential Use Cases
            8. Recommended Approach
            """

            response = self.client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                messages=[
                    {"role": "system", "content": "You are an expert business analyst providing detailed company research."},
                    {"role": "user", "content": research_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )

            research_data = response.choices[0].message.content.strip()
            
            # Calculate lead score
            scoring_prompt = f"""
            Based on this research, rate from 1-10:
            1. Solution Fit
            2. Pain Point Match
            3. Market Timing
            4. Decision Making Authority
            
            Research: {research_data}
            """
            
            scoring_response = self.client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
                messages=[
                    {"role": "system", "content": "You are an expert at scoring sales leads."},
                    {"role": "user", "content": scoring_prompt}
                ],
                max_tokens=100
            )
            
            scores = scoring_response.choices[0].message.content.strip()

            return {
                **lead,
                'research_data': research_data,
                'scoring_analysis': scores,
                'research_timestamp': pd.Timestamp.now().isoformat()
            }

        except Exception as e:
            print(f"Error researching company {lead.get('company_name')}: {e}")
            return lead

    def analyze_leads(self, leads: List[Dict]) -> List[Dict]:
        """Analyze a list of leads using Azure OpenAI"""
        analyzed_leads = []
        for lead in leads:
            print(f"\nResearching: {lead.get('company_name', 'Unknown Company')}")
            analyzed_lead = self.research_company(lead)
            analyzed_leads.append(analyzed_lead)
            print(f"Research completed for: {lead.get('company_name')}")
        return analyzed_leads

    def process_csv_leads(self, csv_path: str) -> List[Dict]:
        """Process leads from CSV file"""
        try:
            df = pd.read_csv(csv_path)
            leads = df.to_dict('records')
            return self.analyze_leads(leads)
        except Exception as e:
            print(f"Error processing CSV: {e}")
            return []
            
    def research_lead(self, lead: Dict) -> Dict:
        """Research a single lead - simplified for UI"""
        try:
            # Convert pandas Series to dict if needed
            if hasattr(lead, 'to_dict'):
                lead = lead.to_dict()
                
            return self.research_company(lead)
        except Exception as e:
            print(f"Error researching lead: {e}")
            return lead