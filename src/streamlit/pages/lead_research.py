import streamlit as st
import sys
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'))

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.lead_research_agent import LeadResearchAgent

st.set_page_config(page_title="Lead Research", page_icon="🔍", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .upload-section {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .research-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .company-name {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1E40AF;
    }
    .section-title {
        font-size: 1rem;
        font-weight: 600;
        color: #4B5563;
        margin-top: 0.75rem;
        margin-bottom: 0.25rem;
    }
    .score-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    .score-high {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .score-medium {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .score-low {
        background-color: #FEE2E2;
        color: #B91C1C;
    }
    .progress-bar-container {
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def check_azure_openai_config():
    """Check if Azure OpenAI is properly configured"""
    # Check for CrewAI format
    crew_format = all([
        os.getenv("AZURE_API_KEY"),
        os.getenv("AZURE_API_BASE"),
        os.getenv("AZURE_API_VERSION")
    ])
    
    # Check for legacy format
    legacy_format = all([
        os.getenv("AZURE_OPENAI_API_KEY"),
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_API_VERSION")
    ])
    
    return crew_format or legacy_format

def display_research_results(research_results):
    """Display research results in a nicely formatted card"""
    company_name = research_results.get('company_name', 'Unknown Company')
    research_data = research_results.get('research_data', 'No research data available')
    scoring_analysis = research_results.get('scoring_analysis', 'No scoring available')
    
    st.markdown(f"""
    <div class="research-card">
        <div class="company-name">{company_name}</div>
        <div style="margin-top: 0.5rem; font-size: 0.9rem;">
            <span>Website: <a href="{research_results.get('website', '#')}" target="_blank">{research_results.get('website', 'N/A')}</a></span>
            <span style="margin-left: 1rem;">Industry: {research_results.get('industry', 'N/A')}</span>
        </div>
        
        <div class="section-title">Research Insights</div>
        <div style="white-space: pre-line;">{research_data}</div>
        
        <div class="section-title">Lead Scoring</div>
        <div style="white-space: pre-line;">{scoring_analysis}</div>
        
        <div style="margin-top: 1rem;">
            <button style="background-color: #2563EB; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.25rem; cursor: pointer;">
                Export Research
            </button>
            <button style="background-color: #10B981; color: white; border: none; padding: 0.5rem 1rem; border-radius: 0.25rem; margin-left: 0.5rem; cursor: pointer;">
                Start Outreach
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    st.markdown('<div class="main-header">Lead Research 🔍</div>', unsafe_allow_html=True)
    
    # Check Azure OpenAI configuration
    if not check_azure_openai_config():
        st.error("❌ Azure OpenAI not configured correctly!")
        st.info("""
        Please check your .env file for Azure OpenAI credentials.
        
        You need either:
        - AZURE_API_KEY, AZURE_API_BASE, and AZURE_API_VERSION (CrewAI format)
        - AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_API_VERSION (Legacy format)
        """)
        return
    
    # File upload section
    st.markdown("### Upload Leads")
    
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            uploaded_file = st.file_uploader("Upload your leads CSV", type=['csv'])
            
            if uploaded_file:
                try:
                    df = pd.read_csv(uploaded_file)
                    required_columns = ['company_name']
                    
                    if not all(col in df.columns for col in required_columns):
                        st.warning(f"CSV must contain at least these columns: {', '.join(required_columns)}")
                    else:
                        st.success(f"Successfully loaded {len(df)} leads")
                        st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Error reading CSV: {str(e)}")
        
        with col2:
            st.write("Or research a single company")
            manual_company = st.text_input("Company Name")
            manual_website = st.text_input("Website (optional)")
            manual_industry = st.text_input("Industry (optional)")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Research buttons
    col_research_file, col_research_single, col_spacer = st.columns([1, 1, 2])
    
    with col_research_file:
        research_file_clicked = st.button("🔍 Research Uploaded Leads", 
                                         type="primary", 
                                         disabled=uploaded_file is None,
                                         use_container_width=True)
    
    with col_research_single:
        research_single_clicked = st.button("🔍 Research Single Company", 
                                           type="primary", 
                                           disabled=not manual_company,
                                           use_container_width=True)
    
    # Research section
    if research_file_clicked and uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            leads = df.to_dict('records')
            
            research_agent = LeadResearchAgent()
            
            # Create a progress bar
            st.markdown('<div class="progress-bar-container">', unsafe_allow_html=True)
            progress_bar = st.progress(0)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Research each lead
            researched_leads = []
            for idx, lead in enumerate(leads):
                with st.spinner(f"Researching {lead['company_name']} ({idx+1}/{len(leads)})"):
                    researched_lead = research_agent.research_company(lead)
                    researched_leads.append(researched_lead)
                    
                    # Update progress
                    progress_bar.progress((idx + 1) / len(leads))
                    
                    # Display research results
                    display_research_results(researched_lead)
            
            # Save results
            results_df = pd.DataFrame(researched_leads)
            csv = results_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Export All Research Results",
                data=csv,
                file_name="lead_research_results.csv",
                mime="text/csv"
            )
                
        except Exception as e:
            st.error(f"Error during research: {str(e)}")
    
    elif research_single_clicked and manual_company:
        try:
            lead = {
                'company_name': manual_company,
                'website': manual_website,
                'industry': manual_industry,
                'description': ''
            }
            
            with st.spinner(f"Researching {manual_company}..."):
                research_agent = LeadResearchAgent()
                researched_lead = research_agent.research_company(lead)
                
                # Display research results
                display_research_results(researched_lead)
                
        except Exception as e:
            st.error(f"Error during research: {str(e)}")

if __name__ == "__main__":
    main()