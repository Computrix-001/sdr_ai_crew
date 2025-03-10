import streamlit as st
import sys
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'))

# Add parent directory to path to import from src
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from agents.lead_research_agent import LeadResearchAgent

st.set_page_config(page_title="Lead Research", page_icon="🔍", layout="wide")

# Custom CSS (keeping the existing CSS)
st.markdown("""
<style>
    .main-header { font-size: 2rem; font-weight: 700; color: #1E3A8A; margin-bottom: 1rem; }
    .upload-section { background-color: #F3F4F6; padding: 1.5rem; border-radius: 10px; margin-bottom: 1.5rem; }
    .research-card { background-color: white; border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem; 
                    border: 1px solid #E5E7EB; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .company-name { font-size: 1.2rem; font-weight: 600; color: #1E40AF; }
    .section-title { font-size: 1rem; font-weight: 600; color: #4B5563; margin-top: 0.75rem; margin-bottom: 0.25rem; }
    .score-badge { display: inline-block; padding: 0.25rem 0.5rem; border-radius: 9999px; 
                  font-size: 0.875rem; font-weight: 500; margin-right: 0.5rem; }
    .score-high { background-color: #D1FAE5; color: #065F46; }
    .score-medium { background-color: #FEF3C7; color: #92400E; }
    .score-low { background-color: #FEE2E2; color: #B91C1C; }
    .progress-bar-container { margin-top: 1rem; margin-bottom: 1rem; }
    .error-message { color: #DC2626; padding: 1rem; background-color: #FEE2E2; border-radius: 0.5rem; }
    .success-message { color: #065F46; padding: 1rem; background-color: #D1FAE5; border-radius: 0.5rem; }
</style>
""", unsafe_allow_html=True)

def validate_environment():
    """Validate all required environment variables"""
    required_vars = {
        'AZURE_OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY'),
        'AZURE_OPENAI_ENDPOINT': os.getenv('AZURE_OPENAI_ENDPOINT'),
        'AZURE_OPENAI_API_VERSION': os.getenv('AZURE_OPENAI_API_VERSION'),
        'AZURE_OPENAI_DEPLOYMENT': os.getenv('AZURE_OPENAI_DEPLOYMENT')
    }
    
    missing_vars = [key for key, value in required_vars.items() if not value]
    
    if missing_vars:
        st.error("❌ Missing required environment variables:")
        for var in missing_vars:
            st.error(f"- {var}")
        return False
    return True

def process_uploaded_file(uploaded_file):
    """Process and validate uploaded CSV file"""
    try:
        if uploaded_file is None:
            return None
            
        # Try to read CSV with explicit encoding
        try:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded_file, encoding='latin-1')
        
        # Debug print
        st.write("DataFrame Shape:", df.shape)
        st.write("DataFrame Columns:", df.columns.tolist())
        
        # Check if file is empty
        if df.empty:
            st.error("The uploaded CSV file is empty")
            return None
            
        # Check for required columns
        required_columns = ['company_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing required columns: {', '.join(missing_columns)}")
            return None
            
        return df
    except pd.errors.EmptyDataError:
        st.error("The uploaded CSV file is empty")
        return None
    except Exception as e:
        st.error(f"Error reading CSV: {str(e)}")
        st.write("Error details:", str(e))
        return None

def display_research_results(research_results):
    """Display research results in a nicely formatted card"""
    if not research_results:
        st.error("No research results to display")
        return
        
    company_name = research_results.get('company_name', 'Unknown Company')
    website = research_results.get('website', 'N/A')
    industry = research_results.get('industry', 'N/A')
    research_data = research_results.get('research_data', '')
    scoring_analysis = research_results.get('scoring_analysis', '')
    
    if 'Error during research' in research_data:
        st.error(f"Research Error for {company_name}: {research_data}")
        return
        
    st.markdown(f"""
    <div class="research-card">
        <div class="company-name">{company_name}</div>
        <div style="margin-top: 0.5rem; font-size: 0.9rem;">
            <span>Website: <a href="{website}" target="_blank">{website}</a></span>
            <span style="margin-left: 1rem;">Industry: {industry}</span>
        </div>
        
        <div class="section-title">Research Insights</div>
        <div style="white-space: pre-line;">{research_data}</div>
        
        <div class="section-title">Lead Scoring</div>
        <div style="white-space: pre-line;">{scoring_analysis}</div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Export Research", key=f"export_{company_name}"):
            research_df = pd.DataFrame([research_results])
            csv = research_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Research",
                data=csv,
                file_name=f"{company_name}_research.csv",
                mime="text/csv"
            )
    with col2:
        if st.button("📧 Start Outreach", key=f"outreach_{company_name}"):
            st.session_state.outreach_data = research_results
            st.switch_page("pages/outreach.py")

def main():
    st.markdown('<div class="main-header">Lead Research 🔍</div>', unsafe_allow_html=True)
    
    # Validate environment variables
    if not validate_environment():
        st.stop()
    
    # File upload section
    st.markdown("### Upload Leads")
    
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            uploaded_file = st.file_uploader("Upload your leads CSV", type=['csv'])
            
            if uploaded_file:
                df = process_uploaded_file(uploaded_file)
                if df is not None:
                    st.success(f"Successfully loaded {len(df)} leads")
                    st.dataframe(df, use_container_width=True)
        
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
        df = process_uploaded_file(uploaded_file)
        if df is not None:
            try:
                leads = df.to_dict('records')
                research_agent = LeadResearchAgent()
                
                progress_bar = st.progress(0)
                researched_leads = []
                
                for idx, lead in enumerate(leads):
                    with st.spinner(f"Researching {lead['company_name']} ({idx+1}/{len(leads)})"):
                        researched_lead = research_agent.research_company(lead)
                        researched_leads.append(researched_lead)
                        progress_bar.progress((idx + 1) / len(leads))
                        display_research_results(researched_lead)
                
                if researched_leads:
                    results_df = pd.DataFrame(researched_leads)
                    csv = results_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Export All Research Results",
                        data=csv,
                        file_name="lead_research_results.csv",
                        mime="text/csv"
                    )
                    
            except Exception as e:
                st.error(f"Error during batch research: {str(e)}")
    
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
                display_research_results(researched_lead)
                
        except Exception as e:
            st.error(f"Error researching {manual_company}: {str(e)}")

if __name__ == "__main__":
    main()