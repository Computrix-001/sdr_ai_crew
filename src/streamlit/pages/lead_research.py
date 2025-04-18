import streamlit as st
import sys
import os
import pandas as pd
from dotenv import load_dotenv
import time

# --- Add parent directory to path ---
try:
    parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    streamlit_dir = os.path.dirname(os.path.dirname(__file__)) # src/streamlit
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    # Function to load CSS
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
    from agents.lead_research_agent import LeadResearchAgent
except ImportError:
    st.error("Failed to import LeadResearchAgent. Check project structure and sys.path.")
    LeadResearchAgent = None

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(parent_dir), '.env'))

# --- Helper Functions ---
def validate_environment():
    """Validate necessary environment variables for this page."""
    required_vars = {
        'AZURE_OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY'),
        'AZURE_OPENAI_ENDPOINT': os.getenv('AZURE_OPENAI_ENDPOINT'),
        'AZURE_OPENAI_DEPLOYMENT': os.getenv('AZURE_OPENAI_DEPLOYMENT'),
    }
    missing_vars = [key for key, value in required_vars.items() if not value]
    if missing_vars:
        st.error(f"❌ Missing required Azure OpenAI environment variables: {', '.join(missing_vars)}. Please check your `.env` file.")
        return False
    return True

def process_uploaded_file(uploaded_file):
    """Process uploaded CSV file into a DataFrame."""
    try:
        df = pd.read_csv(uploaded_file)
        # Basic validation: Check for essential columns (adjust as needed)
        required_cols = ['company_name']
        if not all(col in df.columns for col in required_cols):
            st.error(f"Uploaded CSV must contain at least the following columns: {', '.join(required_cols)}")
            return None
        return df
    except Exception as e:
        st.error(f"Error processing uploaded file: {e}")
        return None

# --- UI Component Functions ---
def display_upload_section():
    st.markdown('<div class="sub-header">Upload or Enter Leads</div>', unsafe_allow_html=True)
    with st.container(border=True):
        tab1, tab2 = st.tabs(["Upload CSV", "Enter Manually"])

        with tab1:
            uploaded_file = st.file_uploader("Upload your leads CSV (must contain 'company_name')", type=['csv'], key="lr_upload")
            if uploaded_file:
                df = process_uploaded_file(uploaded_file)
                if df is not None:
                    st.success(f"Successfully loaded {len(df)} leads from CSV.")
                    # Store DataFrame in session state for processing
                    st.session_state.uploaded_leads_df = df
                    # Display a preview
                    st.dataframe(df.head(), use_container_width=True)
                else:
                    # Clear state if processing failed
                    if 'uploaded_leads_df' in st.session_state:
                        del st.session_state.uploaded_leads_df
            else:
                 # Clear state if no file is uploaded
                 if 'uploaded_leads_df' in st.session_state:
                     del st.session_state.uploaded_leads_df

        with tab2:
            st.markdown("##### Research a Single Company")
            manual_company = st.text_input("Company Name*", key="lr_manual_company")
            manual_website = st.text_input("Website (Optional)", key="lr_manual_website")
            manual_industry = st.text_input("Industry (Optional)", key="lr_manual_industry")
            # Store manual input in session state for processing
            if manual_company:
                st.session_state.manual_lead_input = {
                    'company_name': manual_company,
                    'website': manual_website if manual_website else None,
                    'industry': manual_industry if manual_industry else None
                }
            else:
                 if 'manual_lead_input' in st.session_state:
                     del st.session_state.manual_lead_input

def display_research_results(research_results_list):
    st.markdown('<div class="sub-header">Research Results</div>', unsafe_allow_html=True)

    if not research_results_list:
        st.info("No research results to display. Upload leads or enter manually and click 'Research'.")
        return

    for idx, result in enumerate(research_results_list):
        with st.container(border=True):
            st.markdown(f'<div class="company-name">{result.get("company_name", "N/A")}</div>', unsafe_allow_html=True)
            details_html = '<div class="company-details">'
            if result.get("website"):
                details_html += f'<span>Website: <a href="{result["website"]}" target="_blank">{result["website"]}</a></span>'
            if result.get("industry"):
                 details_html += f'<span>Industry: {result["industry"]}</span>'
            details_html += '</div>'
            st.markdown(details_html, unsafe_allow_html=True)

            # Display research data and scoring
            tab1, tab2 = st.tabs(["Research Insights", "Lead Scoring"])
            with tab1:
                research_data = result.get('research_data', 'No research data generated.')
                if 'Error during research' in research_data:
                     st.error(f"Research Error: {research_data}")
                else:
                     st.markdown(f'<div class="research-content">{research_data}</div>', unsafe_allow_html=True)
            with tab2:
                scoring_analysis = result.get('scoring_analysis', 'No scoring analysis generated.')
                st.markdown(f'<div class="research-content">{scoring_analysis}</div>', unsafe_allow_html=True)

            # Action buttons for each result
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                 # Simple export for single lead result
                 csv_single = pd.DataFrame([result]).to_csv(index=False).encode('utf-8')
                 st.download_button(label="📥 Export", data=csv_single,
                                    file_name=f"{result.get('company_name', 'lead')}_research.csv",
                                    mime='text/csv', key=f"lr_export_{idx}")
            with col2:
                 if st.button("📧 Start Outreach", key=f"lr_outreach_{idx}", type="secondary"):
                     # Store data needed for outreach page in session state
                     st.session_state.outreach_target_lead = result
                     st.success(f"Lead '{result.get('company_name')}' ready for outreach. Navigate to the Email Outreach page.")
                     # Consider automatically switching page: st.switch_page("pages/outreach.py")

# --- Main Page Execution ---
def run_lead_research():
    st.set_page_config(page_title="Lead Research", page_icon="🔍", layout="wide")
    load_css()

    st.markdown('<div class="main-header">Lead Research</div>', unsafe_allow_html=True)

    if not validate_environment():
        st.stop()

    # Initialize agent
    agent = None
    if LeadResearchAgent:
        try:
            agent = LeadResearchAgent()
        except Exception as e:
            st.error(f"Failed to initialize Lead Research Agent: {e}")
            st.stop()
    else:
        st.error("LeadResearchAgent could not be imported.")
        st.stop()

    # Initialize session state for results
    if 'research_results' not in st.session_state:
        st.session_state.research_results = []

    display_upload_section()

    # Research Buttons
    col_research_file, col_research_single, col_spacer = st.columns([1, 1, 2])
    research_file_clicked = False
    research_single_clicked = False

    with col_research_file:
        # Disable button if no file is uploaded/processed
        research_file_clicked = st.button("🔍 Research Uploaded Leads",
                                         type="primary",
                                         key="lr_research_file",
                                         disabled='uploaded_leads_df' not in st.session_state)
    with col_research_single:
        # Disable button if no manual company name
         research_single_clicked = st.button("🔍 Research Manual Entry",
                                            type="primary",
                                            key="lr_research_single",
                                            disabled='manual_lead_input' not in st.session_state)

    # --- Processing Logic ---
    leads_to_process = []
    if research_file_clicked and 'uploaded_leads_df' in st.session_state:
        # Convert DataFrame rows to list of dicts for the agent
        leads_to_process = st.session_state.uploaded_leads_df.to_dict('records')
        st.info(f"Starting research for {len(leads_to_process)} leads from CSV...")

    elif research_single_clicked and 'manual_lead_input' in st.session_state:
        leads_to_process = [st.session_state.manual_lead_input]
        st.info(f"Starting research for '{leads_to_process[0]['company_name']}'...")

    if leads_to_process:
        progress_bar = st.progress(0, text="Initializing research...")
        results = []
        total = len(leads_to_process)
        try:
            for i, lead_input in enumerate(leads_to_process):
                progress_text = f"Researching lead {i+1}/{total}: {lead_input.get('company_name', 'N/A')}..."
                progress_bar.progress((i + 1) / total, text=progress_text)
                # Call the agent's research method (assuming research_company exists)
                # Adjust this call based on the actual agent method name and signature
                research_output = agent.research_company(lead_input)
                results.append(research_output)

            st.session_state.research_results = results
            progress_bar.empty()
            st.success(f"Research completed for {total} lead(s).")
            # Clear input state after processing
            if research_file_clicked and 'uploaded_leads_df' in st.session_state:
                del st.session_state.uploaded_leads_df
            if research_single_clicked and 'manual_lead_input' in st.session_state:
                del st.session_state.manual_lead_input

        except Exception as e:
            progress_bar.empty()
            st.error(f"An error occurred during research: {e}")
            # Optionally clear partial results on error
            # st.session_state.research_results = []

    # Display results from session state
    display_research_results(st.session_state.research_results)

if __name__ == "__main__":
    run_lead_research()