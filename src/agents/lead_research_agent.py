from typing import List, Dict
from openai import AzureOpenAI
import os
import pandas as pd
import streamlit as st

class LeadResearchAgent:
    def __init__(self):
        """Initialize LeadResearchAgent with Azure OpenAI client"""
        try:
            # Initialize Azure OpenAI client with hardcoded API version
            self.client = AzureOpenAI(
                api_key=os.getenv('AZURE_API_KEY'),
                api_version="2024-07-18-preview",  # Hardcode correct version
                azure_endpoint=os.getenv('AZURE_API_BASE')
            )
            
            # Set deployment name
            self.deployment_name = "gama"  # Hardcode the deployment name
            
            # Test the deployment
            try:
                test_response = self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=[{"role": "system", "content": "Test connection"}],
                    max_tokens=5
                )
                print(f"✅ Successfully connected to Azure OpenAI deployment: {self.deployment_name}")
            except Exception as e:
                print(f"❌ Deployment test failed: {str(e)}")
                raise ValueError(f"Azure OpenAI deployment '{self.deployment_name}' not found or inaccessible")
                
        except Exception as e:
            print(f"Azure OpenAI initialization failed: {str(e)}")
            raise

    def validate_lead(self, lead: Dict) -> bool:
        """Validate required lead information"""
        required_fields = ['company_name']
        return all(lead.get(field) for field in required_fields)

    def validate_research_response(self, research_data: str) -> bool:
        """Validate that research response contains required sections"""
        required_sections = [
            "Company Overview",
            "Key Products/Services",
            "Target Market",
            "Pain Points"
        ]
        return all(section.lower() in research_data.lower() for section in required_sections)

    def research_company(self, lead: Dict) -> Dict:
        """Research company using available information and enrich lead data"""
        try:
            if not self.validate_lead(lead):
                raise ValueError("Invalid lead data: Missing required fields")

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

            # Use the deployment name directly
            response = self.client.chat.completions.create(
                model=self.deployment_name,  # Use deployment name here
                messages=[
                    {"role": "system", "content": "You are an expert business analyst providing detailed company research."},
                    {"role": "user", "content": research_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )

            research_data = response.choices[0].message.content.strip()
            
            # Validate research response
            if not self.validate_research_response(research_data):
                print(f"Warning: Incomplete research data for {lead.get('company_name')}")
            
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
        total_leads = len(leads)
        
        print(f"\nStarting analysis of {total_leads} leads...")
        
        for index, lead in enumerate(leads, 1):
            company_name = lead.get('company_name', 'Unknown Company')
            try:
                print(f"\n[{index}/{total_leads}] Researching: {company_name}")
                analyzed_lead = self.research_company(lead)
                analyzed_leads.append(analyzed_lead)
                print(f"✓ Research completed for: {company_name}")
            except Exception as e:
                print(f"✗ Error researching {company_name}: {str(e)}")
                # Add error information to lead data
                lead['research_error'] = str(e)
                analyzed_leads.append(lead)
                
        print(f"\nAnalysis completed. Processed {len(analyzed_leads)} leads.")
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