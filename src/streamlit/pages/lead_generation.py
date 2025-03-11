import streamlit as st
import sys
import os
import pandas as pd
from dotenv import load_dotenv
import requests
from io import StringIO
import json

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'))

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from agents.lead_generation_agent import LeadGenerationAgent
from tools.serp_api import SerpApiClient

st.set_page_config(page_title="Lead Generation", page_icon="🎯", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .filter-section {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .results-card {
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
    .company-url {
        color: #2563EB;
        font-size: 0.9rem;
    }
    .company-description {
        margin-top: 0.5rem;
        font-size: 0.95rem;
    }
    .search-button {
        background-color: #2563EB;
        color: white;
    }
    .export-button {
        background-color: #10B981;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def send_leads_to_netlify(leads_df: pd.DataFrame) -> bool:
    """Send leads data to Netlify app with progress tracking"""
    try:
        total_leads = len(leads_df)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Prepare data
        status_text.text("Preparing leads data...")
        progress_bar.progress(0.2)
        
        csv_buffer = StringIO()
        leads_df.to_csv(csv_buffer, index=False)
        csv_string = csv_buffer.getvalue()
        
        # Prepare request
        status_text.text("Sending to Netlify...")
        progress_bar.progress(0.5)
        
        response = requests.post(
            'https://dreamy-marzipan-6317cf.netlify.app/api/upload',
            headers={
                'x-api-key': 'gama_sk_f3d2r9q7h5k8m4n6p9s2v5x8z1c4b7',
                'Content-Type': 'text/csv',
                'Accept': 'application/json'
            },
            data=csv_string
        )
        
        progress_bar.progress(0.8)
        status_text.text("Processing response...")
        
        if response.status_code == 200:
            progress_bar.progress(1.0)
            status_text.text(f"Successfully processed {total_leads} leads!")
            return True
        else:
            status_text.text("Error processing leads")
            return False
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return False

def validate_leads_data(leads_df: pd.DataFrame) -> bool:
    """Validate leads data before sending"""
    required_columns = ['company_name', 'contact_email', 'website']
    missing_columns = [col for col in required_columns if col not in leads_df.columns]
    
    if missing_columns:
        st.error(f"Missing required columns: {', '.join(missing_columns)}")
        return False
        
    if leads_df.empty:
        st.error("No leads data to send")
        return False
        
    return True

def main():
    st.markdown('<div class="main-header">Lead Generation 🎯</div>', unsafe_allow_html=True)
    
    # Check if SERP API key is configured
    if not os.getenv("SERPAPI_API_KEY"):
        st.error("❌ SERP API key not configured!")
        st.info("Please add SERPAPI_API_KEY to your .env file")
        return
    
    # Search filters section
    st.markdown("### Search Filters")
    
    with st.container():
        st.markdown('<div class="filter-section">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            keyword = st.text_input("Keyword/Industry", placeholder="e.g., SaaS, Healthcare, Marketing")
            website = st.text_input("Website Domain", placeholder="e.g., linkedin.com, instagram.com")
        
        with col2:
            location = st.text_input("Location", placeholder="e.g., New York, California, USA")
            position = st.text_input("Position/Title", placeholder="e.g., CEO, Marketing Manager")
        
        col3, col4 = st.columns(2)
        
        with col3:
            num_results = st.slider("Number of results", 5, 50, 10)
            include_contact = st.checkbox("Include contact information (email/phone)", value=True)
        
        with col4:
            st.write("Advanced Options")
            search_type = st.radio("Search Type", ["Standard", "Deep Search"], horizontal=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    col_search, col_export = st.columns([1, 5])
    with col_search:
        search_clicked = st.button("🔍 Generate Leads", type="primary", use_container_width=True)
    
    # Results section
    if search_clicked:
        if not keyword and not website and not position:
            st.warning("Please enter at least one search parameter (keyword, website, or position)")
        else:
            with st.spinner("Generating leads..."):
                try:
                    # Initialize agents
                    serp_client = SerpApiClient()
                    lead_gen_agent = LeadGenerationAgent(serp_client)
                    
                    # Generate leads with filters
                    leads = lead_gen_agent.generate_leads_with_filters(
                        keyword=keyword,
                        website=website,
                        location=location,
                        position=position,
                        num_results=num_results
                    )
                    
                    # Display results
                    if leads:
                        st.success(f"Found {len(leads)} potential leads!")
                        
                        # Convert leads to DataFrame for tabular display
                        leads_df = lead_gen_agent.format_leads_table(leads)
                        
                        # Create two columns for the export buttons
                        col_export, col_send, col_space = st.columns([1, 1, 2])
                        
                        with col_export:
                            csv = leads_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Export CSV",
                                data=csv,
                                file_name="generated_leads.csv",
                                mime="text/csv",
                                use_container_width=True
                            )
                        
                        with col_send:
                            if st.button("🚀 Send to Netlify", use_container_width=True):
                                with st.spinner("Processing leads..."):
                                    if validate_leads_data(leads_df):
                                        if send_leads_to_netlify(leads_df):
                                            st.success("✅ Leads successfully sent!")
                                        else:
                                            st.error("Failed to send leads")
                        
                        # Display leads in table format
                        st.markdown("### Generated Leads")
                        st.dataframe(
                            leads_df,
                            use_container_width=True,
                            column_config={
                                "company_name": "Company",
                                "contact_email": "Email",
                                "contact_phone": "Phone",
                                "website": st.column_config.LinkColumn("Website"),
                                "description": st.column_config.TextColumn("Description", width="large"),
                                "industry": "Industry",
                                "location": "Location",
                                "source": "Source"
                            }
                        )
                        
                        # Display individual lead cards for detailed view
                        st.markdown("### Detailed Lead Information")
                        for lead in leads:
                            with st.container():
                                st.markdown(f"""
                                <div class="results-card">
                                    <div class="company-name">{lead['company_name']}</div>
                                    <div class="company-url">🔗 <a href="{lead['website']}" target="_blank">{lead['website']}</a></div>
                                    <div class="company-description">{lead['description']}</div>
                                    <div style="margin-top: 0.5rem;">
                                        <span style="color: #6B7280; font-size: 0.9rem;">
                                            Email: {lead['contact_email'] if lead['contact_email'] else 'Not found'} | 
                                            Phone: {lead['contact_phone'] if lead['contact_phone'] else 'Not found'}
                                        </span>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.warning("No leads found. Try adjusting your search parameters.")
                        
                except Exception as e:
                    st.error(f"Error generating leads: {str(e)}")
                    st.info("Please check your search parameters and try again.")

if __name__ == "__main__":
    main()