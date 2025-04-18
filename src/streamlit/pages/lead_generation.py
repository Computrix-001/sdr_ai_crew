import streamlit as st
import sys
import os
import pandas as pd
from dotenv import load_dotenv
import time # For simulating progress
import requests # Keep for potential future API calls like Netlify example
from io import StringIO # Keep for potential future API calls

# --- Add parent directory to path ---
try:
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    streamlit_dir = os.path.dirname(os.path.dirname(__file__)) # src/streamlit
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    # Function to load CSS needs to be defined or imported in each page file
    def load_css(file_name="style.css"):
        css_path = os.path.join(streamlit_dir, file_name)
        if os.path.exists(css_path):
            with open(css_path) as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        else:
            st.warning(f"CSS file not found at {css_path}")
except IndexError:
    print("Warning: Could not automatically add parent directory to sys.path.")
# --- End Add path ---

# Import agent after path is set
try:
    from agents.lead_generation_agent import LeadGenerationAgent
except ImportError:
    st.error("Failed to import LeadGenerationAgent. Check project structure and sys.path.")
    # Optionally stop execution if agent is critical
    # st.stop()
    LeadGenerationAgent = None # Assign None to avoid further errors

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(parent_dir), '.env'))

# --- UI Component Functions ---

def display_filters():
    st.markdown('<div class="sub-header">Search Filters</div>', unsafe_allow_html=True)
    with st.container(border=True): # Use Streamlit border feature
        col1, col2 = st.columns(2)
        with col1:
            keyword = st.text_input("Keyword/Industry", placeholder="e.g., SaaS, Healthcare", key="lg_keyword")
            website = st.text_input("Website Domain (Optional)", placeholder="e.g., linkedin.com", key="lg_website")
        with col2:
            location = st.text_input("Location (Optional)", placeholder="e.g., New York, USA", key="lg_location")
            position = st.text_input("Position/Title (Optional)", placeholder="e.g., CEO, Marketing Manager", key="lg_position")

        num_results = st.slider("Max Leads to Generate", 5, 50, 10, key="lg_num_results")
        # Removed advanced options for simplicity, can be added back if needed

    return keyword, website, location, position, num_results

def display_results(leads_df):
    st.markdown('<div class="sub-header">Generated Leads</div>', unsafe_allow_html=True)
    if leads_df is None or leads_df.empty:
        st.info("No leads generated yet or the search returned no results.")
        return

    st.dataframe(leads_df, use_container_width=True)

    # --- Export Button ---
    csv = leads_df.to_csv(index=False).encode('utf-8')
    st.download_button(
         label="📥 Download Leads as CSV",
         data=csv,
         file_name='generated_leads.csv',
         mime='text/csv',
         key='lg_download_csv'
     )
    # --- End Export Button ---

    # --- Optional: Display as Cards (can be slow for many leads) ---
    # display_leads_as_cards(leads_df)
    # --- End Optional Display ---

# Optional: Function to display leads as individual cards
# def display_leads_as_cards(leads_df):
#     if len(leads_df) > 20: # Limit card display for performance
#         st.caption("Displaying first 20 leads as cards.")
#         leads_df = leads_df.head(20)
#
#     for index, lead in leads_df.iterrows():
#         with st.container(border=True):
#             st.markdown(f'<div class="company-name">{lead.get("company_name", "N/A")}</div>', unsafe_allow_html=True)
#             if pd.notna(lead.get("website")):
#                 st.markdown(f'<a href="{lead["website"]}" target="_blank" class="company-url">{lead["website"]}</a>', unsafe_allow_html=True)
#             # Add other details like email, phone, profiles if available and desired
#             if pd.notna(lead.get("contact_email")):
#                 st.write(f"📧 {lead['contact_email']}")
#             if pd.notna(lead.get("contact_phone")):
#                 st.write(f"📞 {lead['contact_phone']}")
#             if pd.notna(lead.get("linkedin_url")):
#                 st.markdown(f'🔗 <a href="{lead["linkedin_url"]}" target="_blank">LinkedIn</a>', unsafe_allow_html=True)
#             if pd.notna(lead.get("github_url")):
#                  st.markdown(f'🔗 <a href="{lead["github_url"]}" target="_blank">GitHub</a>', unsafe_allow_html=True)
#             if pd.notna(lead.get("description")):
#                 st.markdown(f'<div class="company-description">{lead["description"][:150]}...</div>', unsafe_allow_html=True) # Show snippet


# --- Main Page Execution ---
def run_lead_generation():
    st.set_page_config(page_title="Lead Generation", page_icon="🎯", layout="wide")
    load_css()

    st.markdown('<div class="main-header">Lead Generation</div>', unsafe_allow_html=True)

    # Check for SERP API key
    if not os.getenv("SERPAPI_API_KEY"):
        st.error("❌ SERP API key (SERPAPI_API_KEY) is not configured in your `.env` file. Lead generation requires this key.")
        st.stop() # Stop execution if key is missing

    # Initialize agent (handle potential import error)
    agent = None
    if LeadGenerationAgent:
        try:
            agent = LeadGenerationAgent()
        except Exception as e:
            st.error(f"Failed to initialize Lead Generation Agent: {e}")
            st.stop()
    else:
        st.error("LeadGenerationAgent could not be imported.")
        st.stop()


    keyword, website, location, position, num_results = display_filters()

    # Initialize session state for results
    if 'generated_leads_df' not in st.session_state:
        st.session_state.generated_leads_df = None

    search_clicked = st.button("🔍 Generate Leads", type="primary", key="lg_generate")

    if search_clicked:
        if not keyword and not website and not position:
            st.warning("Please provide at least one search parameter (Keyword, Website, or Position).")
        else:
            # Show progress
            progress_bar = st.progress(0, text="Initializing lead generation...")
            try:
                # Call the agent method
                progress_bar.progress(30, text=f"Searching for leads based on criteria...")
                leads_data = agent.generate_leads_with_filters(
                    keyword=keyword if keyword else None,
                    website=website if website else None,
                    location=location if location else None,
                    position=position if position else None,
                    num_results=num_results
                )
                progress_bar.progress(80, text=f"Processing results...")

                # Format results into DataFrame
                if leads_data:
                    st.session_state.generated_leads_df = agent.format_leads_table(leads_data)
                    progress_bar.progress(100, text=f"Found {len(st.session_state.generated_leads_df)} leads!")
                    st.success(f"Successfully generated {len(st.session_state.generated_leads_df)} leads!")
                else:
                    st.session_state.generated_leads_df = pd.DataFrame() # Empty DataFrame if no leads
                    progress_bar.progress(100, text="No leads found matching the criteria.")
                    st.info("No leads found matching the specified criteria.")

                time.sleep(0.5) # Keep message visible briefly
                progress_bar.empty() # Remove progress bar

            except Exception as e:
                progress_bar.empty()
                st.error(f"An error occurred during lead generation: {e}")
                st.session_state.generated_leads_df = None # Clear results on error

    # Display results from session state
    display_results(st.session_state.generated_leads_df)

if __name__ == "__main__":
    run_lead_generation()
