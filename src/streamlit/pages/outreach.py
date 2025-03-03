import streamlit as st
import sys
import os
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'))

# Add parent directory to path to import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

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

def main():
    st.markdown('<div class="main-header">Email Outreach 📧</div>', unsafe_allow_html=True)
    
    # Configuration status
    email_config_ok = check_email_config()
    openai_config_ok = check_azure_openai_config()
    
    if not email_config_ok or not openai_config_ok:
        st.warning("⚠️ Configuration Issues Detected")
        
        if not email_config_ok:
            st.markdown("""
            <div class="config-error">
                ❌ Azure Communication Services not configured properly
            </div>
            """, unsafe_allow_html=True)
            st.info("Please check your .env file for AZURE_COMMUNICATION_CONNECTION_STRING and AZURE_COMMUNICATION_SENDER_EMAIL")
        
        if not openai_config_ok:
            st.markdown("""
            <div class="config-error">
                ❌ Azure OpenAI not configured properly
            </div>
            """, unsafe_allow_html=True)
            st.info("Please check your .env file for Azure OpenAI credentials")
    else:
        st.markdown("""
        <div class="config-ok">
            ✅ All services configured properly
        </div>
        """, unsafe_allow_html=True)
    
    # Tabs for different outreach methods
    tab1, tab2 = st.tabs(["Single Outreach", "Bulk Outreach"])
    
    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        
        with st.form("outreach_form"):
            st.markdown("### Lead Information")
            
            col1, col2 = st.columns(2)
            
            with col1:
                company_name = st.text_input("Company Name")
                contact_name = st.text_input("Contact Name")
            
            with col2:
                contact_email = st.text_input("Contact Email")
                contact_role = st.text_input("Contact Role")
            
            col3, col4 = st.columns(2)
            
            with col3:
                industry = st.text_input("Industry")
                website = st.text_input("Website")
            
            with col4:
                st.markdown("### Email Customization")
                tone = st.select_slider(
                    "Email Tone",
                    options=["Formal", "Professional", "Casual", "Friendly"]
                )
                
                email_length = st.select_slider(
                    "Email Length",
                    options=["Very Short", "Short", "Medium", "Detailed"]
                )
            
            value_prop = st.text_area("Value Proposition (optional)")
            
            submitted = st.form_submit_button("Generate Email", use_container_width=True)
            
            if submitted:
                if not contact_email:
                    st.error("Contact email is required")
                elif not company_name:
                    st.error("Company name is required")
                else:
                    with st.spinner("Generating personalized email..."):
                        try:
                            outreach_agent = OutreachAgent()
                            email_content = outreach_agent.generate_email({
                                'company_name': company_name,
                                'contact_name': contact_name,
                                'contact_email': contact_email,
                                'contact_role': contact_role,
                                'industry': industry,
                                'website': website,
                                'research_data': f"Tone: {tone}\nLength: {email_length}\nValue Proposition: {value_prop}"
                            })
                            
                            st.success("Email Generated!")
                            
                            # Email preview
                            st.markdown("""
                            <div class="email-preview">
                                <div class="email-subject">{}</div>
                                <hr style="margin: 0.5rem 0;">
                                <div class="email-content">{}</div>
                            </div>
                            """.format(email_content['subject'], email_content['content']), unsafe_allow_html=True)
                            
                            # Send button
                            if st.button("📧 Send Email", type="primary"):
                                success = outreach_agent.send_email(
                                    recipient=contact_email,
                                    subject=email_content['subject'],
                                    content=email_content['content']
                                )
                                if success:
                                    st.success(f"✅ Email sent successfully to {contact_email}!")
                                else:
                                    st.error("❌ Failed to send email. Please check your configuration.")
                                    
                        except Exception as e:
                            st.error(f"Error generating email: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        
        st.markdown("### Upload Leads for Bulk Outreach")
        
        uploaded_file = st.file_uploader("Upload CSV with leads", type=['csv'])
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                required_columns = ['company_name', 'contact_email']
                
                if not all(col in df.columns for col in required_columns):
                    st.warning(f"CSV must contain at least these columns: {', '.join(required_columns)}")
                else:
                    st.success(f"Successfully loaded {len(df)} leads")
                    st.dataframe(df, use_container_width=True)
                    
                    if st.button("📧 Generate & Send Bulk Emails", type="primary"):
                        if not email_config_ok or not openai_config_ok:
                            st.error("Cannot proceed due to configuration issues")
                        else:
                            with st.spinner("Processing bulk outreach..."):
                                try:
                                    outreach_agent = OutreachAgent()
                                    
                                    # Create a progress bar
                                    progress_bar = st.progress(0)
                                    
                                    # Process each lead
                                    results = []
                                    for idx, lead in df.iterrows():
                                        lead_dict = lead.to_dict()
                                        
                                        # Generate email
                                        email_content = outreach_agent.generate_email(lead_dict)
                                        
                                        # Send email
                                        success = outreach_agent.send_email(
                                            recipient=lead_dict['contact_email'],
                                            subject=email_content['subject'],
                                            content=email_content['content']
                                        )
                                        
                                        results.append({
                                            **lead_dict,
                                            'email_sent': success,
                                            'email_subject': email_content['subject']
                                        })
                                        
                                        # Update progress
                                        progress_bar.progress((idx + 1) / len(df))
                                    
                                    # Display results
                                    results_df = pd.DataFrame(results)
                                    successful = sum(results_df['email_sent'])
                                    
                                    st.success(f"Bulk outreach completed! {successful} of {len(results)} emails sent successfully.")
                                    st.dataframe(results_df[['company_name', 'contact_email', 'email_sent', 'email_subject']])
                                    
                                except Exception as e:
                                    st.error(f"Error during bulk outreach: {str(e)}")
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()