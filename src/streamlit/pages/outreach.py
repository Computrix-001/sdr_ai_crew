import streamlit as st
import sys
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'))

# Add parent directory to path to import from src
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from agents.outreach_agent import OutreachAgent

st.set_page_config(page_title="Email Outreach", page_icon="📧", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .form-section {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .email-preview {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .email-subject {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1E40AF;
        margin-bottom: 0.5rem;
    }
    .email-content {
        font-family: 'Arial', sans-serif;
        line-height: 1.6;
        white-space: pre-line;
    }
    .config-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }
    .config-ok {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .config-error {
        background-color: #FEE2E2;
        color: #B91C1C;
    }
    .tab-content {
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_email_config():
    """Check if email configuration is properly set up"""
    connection_string = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
    sender_email = os.getenv("AZURE_COMMUNICATION_SENDER_EMAIL")
    return connection_string and sender_email

def check_azure_openai_config():
    """Check if Azure OpenAI is properly configured"""
    crew_format = all([
        os.getenv("AZURE_OPENAI_API_KEY"),
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_API_VERSION")
    ])
    
    legacy_format = all([
        os.getenv("AZURE_OPENAI_API_KEY"),
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_API_VERSION")
    ])
    
    return crew_format or legacy_format

def main():
    st.markdown('<div class="main-header">Email Outreach 📧</div>', unsafe_allow_html=True)
    
    # Configuration status
    email_config_ok = check_email_config()
    openai_config_ok = check_azure_openai_config()
    
    if not email_config_ok or not openai_config_ok:
        st.warning("⚠️ Configuration Issues Detected")
        
        if not email_config_ok:
            st.error("❌ Azure Communication Services not configured properly")
            st.info("Please check your .env file for AZURE_COMMUNICATION_CONNECTION_STRING and AZURE_COMMUNICATION_SENDER_EMAIL")
        
        if not openai_config_ok:
            st.error("❌ Azure OpenAI not configured properly")
            st.info("Please check your .env file for Azure OpenAI credentials")
        return
    
    # Tabs for different outreach methods
    tab1, tab2 = st.tabs(["Single Outreach", "Bulk Outreach"])
    
    with tab1:
        st.markdown("### Lead Information")
        
        # Create two columns for the form
        col1, col2 = st.columns(2)
        
        # First column
        with col1:
            company_name = st.text_input("Company Name*", key="company_name")
            contact_email = st.text_input("Contact Email*", key="contact_email")
            industry = st.text_input("Industry", key="industry")
            
        # Second column
        with col2:
            contact_name = st.text_input("Contact Name", key="contact_name")
            contact_role = st.text_input("Contact Role", key="contact_role")
            website = st.text_input("Website", key="website")
        
        # Email customization
        st.markdown("### Email Customization")
        col3, col4 = st.columns(2)
        
        with col3:
            tone = st.select_slider(
                "Email Tone",
                options=["Formal", "Professional", "Casual", "Friendly"],
                value="Professional"
            )
        
        with col4:
            email_length = st.select_slider(
                "Email Length",
                options=["Very Short", "Short", "Medium", "Detailed"],
                value="Medium"
            )
        
        value_prop = st.text_area("Value Proposition (optional)")
        
        # Generate email button
        if st.button("Generate Email", type="primary", key="generate_single"):
            if not company_name:
                st.error("Company name is required")
            elif not contact_email:
                st.error("Contact email is required")
            else:
                try:
                    with st.spinner("Generating personalized email..."):
                        outreach_agent = OutreachAgent()
                        email_content = outreach_agent.generate_email({
                            'company_name': company_name,
                            'contact_name': contact_name,
                            'contact_email': contact_email,
                            'contact_role': contact_role,
                            'industry': industry,
                            'website': website,
                            'tone': tone,
                            'email_length': email_length,
                            'value_prop': value_prop
                        })
                        
                        if email_content:
                            st.success("Email Generated!")
                            
                            # Display email preview
                            st.markdown("""
                            <div class="email-preview">
                                <div class="email-subject">{}</div>
                                <hr style="margin: 0.5rem 0;">
                                <div class="email-content">{}</div>
                            </div>
                            """.format(
                                email_content['subject'],
                                email_content['content'].replace('\n', '<br>')
                            ), unsafe_allow_html=True)
                            
                            # Send email button
                            if st.button("Send Email", type="primary", key="send_single"):
                                with st.spinner("Sending email..."):
                                    success = outreach_agent.send_email(
                                        recipient=contact_email,
                                        subject=email_content['subject'],
                                        content=email_content['content']
                                    )
                                    if success:
                                        st.success(f"✅ Email sent successfully to {contact_email}!")
                                    else:
                                        st.error("Failed to send email. Please check your configuration.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    with tab2:
        st.markdown("### Upload Leads for Bulk Outreach")
        
        uploaded_file = st.file_uploader("Upload CSV with leads", type=['csv'])
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                required_columns = ['company_name', 'contact_email']
                
                if not all(col in df.columns for col in required_columns):
                    st.warning(f"CSV must contain these columns: {', '.join(required_columns)}")
                else:
                    st.success(f"Successfully loaded {len(df)} leads")
                    st.dataframe(df, use_container_width=True)
                    
                    if st.button("Process Bulk Outreach", type="primary", key="process_bulk"):
                        if not email_config_ok or not openai_config_ok:
                            st.error("Cannot proceed due to configuration issues")
                        else:
                            try:
                                outreach_agent = OutreachAgent()
                                
                                # Create progress tracking
                                progress_text = "Processing leads..."
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                # Process leads
                                results = []
                                for idx, lead in df.iterrows():
                                    progress = (idx + 1) / len(df)
                                    progress_bar.progress(progress)
                                    status_text.text(f"Processing {lead['company_name']} ({idx + 1}/{len(df)})")
                                    
                                    try:
                                        # Generate and send email
                                        email_content = outreach_agent.generate_email(lead.to_dict())
                                        success = outreach_agent.send_email(
                                            recipient=lead['contact_email'],
                                            subject=email_content['subject'],
                                            content=email_content['content']
                                        )
                                        
                                        results.append({
                                            **lead.to_dict(),
                                            'email_sent': success,
                                            'email_subject': email_content['subject'],
                                            'timestamp': datetime.now().isoformat()
                                        })
                                    except Exception as e:
                                        results.append({
                                            **lead.to_dict(),
                                            'email_sent': False,
                                            'error': str(e),
                                            'timestamp': datetime.now().isoformat()
                                        })
                                
                                # Display results
                                results_df = pd.DataFrame(results)
                                successful = sum(results_df['email_sent'])
                                
                                st.success(f"Bulk outreach completed! {successful} of {len(results)} emails sent successfully.")
                                
                                # Display results table
                                st.dataframe(
                                    results_df[[
                                        'company_name',
                                        'contact_email',
                                        'email_sent',
                                        'email_subject',
                                        'timestamp'
                                    ]],
                                    use_container_width=True
                                )
                                
                                # Export results
                                csv = results_df.to_csv(index=False)
                                st.download_button(
                                    "Download Results",
                                    csv,
                                    "outreach_results.csv",
                                    "text/csv",
                                    key="download_results"
                                )
                                
                            except Exception as e:
                                st.error(f"Error during bulk outreach: {str(e)}")
                                
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")

if __name__ == "__main__":
    main()