from agents.lead_generation_agent import LeadGenerationAgent
from agents.lead_research_agent import LeadResearchAgent
from agents.outreach_agent import OutreachAgent
from agents.conversation_agent import ConversationAgent
from tools.serp_api import SerpApiClient
from openai import AzureOpenAI
import os
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_azure_deployment() -> bool:
    """Verify Azure OpenAI deployment configuration"""
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    if not deployment_name:
        print("❌ Azure OpenAI deployment name not configured")
        return False
        
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_API_KEY"),
            api_version=os.getenv("AZURE_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_API_BASE")
        )
        
        # Test deployment
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[{"role": "system", "content": "Test"}],
            max_tokens=5
        )
        print(f"✅ Azure OpenAI deployment '{deployment_name}' verified")
        return True
    except Exception as e:
        print(f"❌ Azure OpenAI deployment verification failed: {str(e)}")
        return False

def process_generated_leads() -> List[Dict]:
    """Process leads generated through SERP API"""
    print("Starting SDR AI Crew System - Lead Generation...")
    
    try:
        # Initialize agents
        serp_client = SerpApiClient()
        lead_gen_agent = LeadGenerationAgent(serp_client)
        research_agent = LeadResearchAgent()
        outreach_agent = OutreachAgent()
        
        # Generate leads with filters
        keyword = "B2B SaaS"
        website = "linkedin.com"
        location = "USA"
        position = "CEO"
        
        print(f"Generating leads with filters: Keyword={keyword}, Website={website}, Location={location}, Position={position}")
        
        generated_leads = lead_gen_agent.generate_leads_with_filters(
            keyword=keyword,
            website=website,
            location=location,
            position=position,
            num_results=5
        )
        
        if generated_leads:
            # Research generated leads
            print("\nResearching generated leads...")
            analyzed_leads = research_agent.analyze_leads(generated_leads)
            
            # Process outreach
            print("\nProcessing outreach for generated leads...")
            results = outreach_agent.process_leads(analyzed_leads)
            return results
    except Exception as e:
        print(f"Error in lead generation process: {e}")
    return []

def process_csv_leads() -> List[Dict]:
    """Process leads from external CSV file"""
    print("\nStarting SDR AI Crew System - CSV Processing...")
    
    try:
        # Initialize agents
        research_agent = LeadResearchAgent()
        outreach_agent = OutreachAgent()
        
        # Process leads from CSV
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "leads.csv")
        
        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return []
        
        # Research CSV leads
        print("Analyzing leads from CSV...")
        analyzed_leads = research_agent.process_csv_leads(csv_path)
        
        if analyzed_leads:
            # Process outreach
            print("\nProcessing outreach for CSV leads...")
            results = outreach_agent.process_leads(analyzed_leads)
            return results
    except Exception as e:
        print(f"Error in CSV processing: {e}")
    return []

def check_environment() -> bool:
    """Check all required environment variables and configurations"""
    print("Checking environment variables...")
    
    # Check Azure OpenAI configuration
    azure_openai_configured = False
    
    # Check CrewAI format
    if all([os.getenv("AZURE_API_KEY"), os.getenv("AZURE_API_BASE"), os.getenv("AZURE_API_VERSION")]):
        print("✅ Azure OpenAI credentials configured (CrewAI format)")
        azure_openai_configured = True
    # Check legacy format
    elif all([os.getenv("AZURE_OPENAI_API_KEY"), os.getenv("AZURE_OPENAI_ENDPOINT"), os.getenv("AZURE_OPENAI_API_VERSION")]):
        print("✅ Azure OpenAI credentials configured (Legacy format)")
        azure_openai_configured = True
    else:
        print("❌ Azure OpenAI credentials not configured properly")
        return False
    
    # Verify Azure OpenAI deployment
    if not verify_azure_deployment():
        return False
    
    # Check Azure Communication Services
    if os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING") and os.getenv("AZURE_COMMUNICATION_SENDER_EMAIL"):
        print("✅ Azure Communication Services configured")
    else:
        print("❌ Azure Communication Services not configured properly")
        return False
    
    # Check SERP API
    if os.getenv("SERPAPI_API_KEY"):
        print("✅ SERP API configured")
    else:
        print("❌ SERP API not configured properly")
        return False
    
    return True

def main():
    # Check environment and configurations
    if not check_environment():
        print("\n⚠️ Cannot proceed: Missing or invalid configuration")
        print("Please check your .env file and Azure OpenAI deployment settings")
        return
    
    # Process both lead sources
    generated_results = process_generated_leads()
    csv_results = process_csv_leads()
    
    # Combined results
    all_results = generated_results + csv_results
    
    print("\nFinal Summary:")
    print(f"Total Leads Processed: {len(all_results)}")
    print(f"Successfully Contacted: {sum(1 for r in all_results if r.get('email_sent', False))}")
    print("-" * 50)
    
    # Suggest next steps
    print("\nNext Steps:")
    print("1. Run the Streamlit app to interact with the system")
    print("2. Check the conversation agent for any responses")
    print("3. Update the leads CSV with new prospects")
    print("\nTo run the Streamlit app, use: streamlit run src/streamlit/app.py")

if __name__ == "__main__":
    main()