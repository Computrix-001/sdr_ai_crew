import streamlit as st
import sys
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
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
    from agents.outreach_agent import OutreachAgent
except ImportError:
    st.error("Failed to import OutreachAgent. Check project structure and sys.path.")
    OutreachAgent = None

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(parent_dir), '.env'))

# --- Helper Functions ---
def check_email_config():
    """Check Azure Communication Services email configuration."""
    connection_string = os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING")
    sender_email = os.getenv("AZURE_COMMUNICATION_SENDER_EMAIL")
    return connection_string and sender_email

def check_azure_openai_config():
    """Check Azure OpenAI configuration needed for email generation."""
    return all(os.getenv(k) for k in ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT"])

# --- UI Component Functions ---
def display_config_status():
    st.markdown('<div class="sub-header">Configuration Status</div>', unsafe_allow_html=True)
    email_ok = check_email_config()
    openai_ok = check_azure_openai_config()

    if email_ok:
        st.markdown('<div class="config-status config-ok">✅ Azure Email Service: Configured</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="config-status config-error">❌ Azure Email Service: Not Configured (Check AZURE_COMMUNICATION_ vars in `.env`)</div>', unsafe_allow_html=True)

    if openai_ok:
        st.markdown('<div class="config-status config-ok">✅ Azure OpenAI Service: Configured</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="config-status config-error">❌ Azure OpenAI Service: Not Configured (Check AZURE_OPENAI_ vars in `.env`)</div>', unsafe_allow_html=True)

    return email_ok and openai_ok

def display_lead_selection():
    st.markdown('<div class="sub-header">Select Lead for Outreach</div>', unsafe_allow_html=True)
    # Check if a lead was passed from the research page via session state
    target_lead = st.session_state.get('outreach_target_lead', None)

    if target_lead:
        st.success(f"Selected Lead: **{target_lead.get('company_name', 'N/A')}**")
        st.caption(f"Email: {target_lead.get('contact_email', 'Not Available')}")
        # Display minimal info, full details used in generation
        if st.button("Clear Selection", key="or_clear_selection"):
            del st.session_state.outreach_target_lead
            st.rerun() # Rerun to update UI
        return target_lead
    else:
        st.info("No lead selected. Please research a lead on the 'Lead Research' page and click 'Start Outreach'.")
        # Optionally add manual input fields here if direct outreach is desired
        return None

def display_email_customization(lead):
    st.markdown('<div class="sub-header">Customize Email</div>', unsafe_allow_html=True)
    with st.expander("Email Customization Options", expanded=True):
        tone_options = ["Professional", "Friendly", "Direct", "Enthusiastic"]
        length_options = ["Short", "Medium", "Long"]

        col1, col2 = st.columns(2)
        with col1:
            tone = st.selectbox("Select Tone", tone_options, key="or_tone")
        with col2:
            email_length = st.selectbox("Select Length", length_options, index=1, key="or_length") # Default to Medium

        # Allow overriding contact name if needed
        default_contact = lead.get('contact_name') if lead.get('contact_name') else "there" # Fallback
        contact_name = st.text_input("Recipient Name (if known)", value=default_contact, key="or_contact_name")

        # Value proposition - crucial for good emails
        value_prop = st.text_area(
            "Key Value Proposition / Talking Point",
            placeholder="Briefly mention the core benefit or solution relevant to this lead...",
            height=100,
            key="or_value_prop"
        )
    return tone, email_length, contact_name, value_prop

def display_email_preview(subject, content):
    st.markdown('<div class="sub-header">Email Preview</div>', unsafe_allow_html=True)
    if subject and content:
        with st.container(border=True):
            st.markdown(f'<div class="email-subject">{subject}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="email-content">{content}</div>', unsafe_allow_html=True)
    else:
        st.info("Click 'Generate Email' to create a preview.")

# --- Main Page Execution ---
def run_outreach():
    st.set_page_config(page_title="Email Outreach", page_icon="📧", layout="wide")
    load_css()

    st.markdown('<div class="main-header">Email Outreach</div>', unsafe_allow_html=True)

    all_configs_ok = display_config_status()
    if not all_configs_ok:
        st.warning("Please configure all required services before proceeding with outreach.")
        st.stop()

    # Initialize agent
    agent = None
    if OutreachAgent:
        try:
            agent = OutreachAgent()
        except Exception as e:
            st.error(f"Failed to initialize Outreach Agent: {e}")
            st.stop()
    else:
        st.error("OutreachAgent could not be imported.")
        st.stop()

    # Initialize session state for email content
    if 'generated_email_subject' not in st.session_state:
        st.session_state.generated_email_subject = None
    if 'generated_email_content' not in st.session_state:
        st.session_state.generated_email_content = None

    selected_lead = display_lead_selection()

    if selected_lead:
        # Check if lead has an email address
        recipient_email = selected_lead.get('contact_email')
        if not recipient_email:
            st.error("Selected lead does not have an email address. Cannot proceed with outreach.")
            st.stop()

        tone, email_length, contact_name, value_prop = display_email_customization(selected_lead)

        col1, col2 = st.columns([1, 3]) # Buttons column smaller
        with col1:
             generate_clicked = st.button("📝 Generate Email", key="or_generate", type="primary")
        # Email preview section
        with col2:
             # Placeholder for status during generation/sending
             status_placeholder = st.empty()

        if generate_clicked:
            if not value_prop:
                 st.warning("Please provide a Key Value Proposition for better email personalization.")
            else:
                status_placeholder.info("Generating personalized email...")
                try:
                    # Prepare lead data for the agent's generate_email method
                    # Include customization options
                    lead_data_for_generation = {
                        **selected_lead,
                        'contact_name': contact_name, # Use potentially overridden name
                        'tone': tone,
                        'email_length': email_length,
                        'value_prop': value_prop
                    }
                    # Call agent method (adjust based on actual method signature)
                    email_output = agent.generate_email(lead_data_for_generation)

                    if email_output and 'subject' in email_output and 'content' in email_output:
                        st.session_state.generated_email_subject = email_output['subject']
                        st.session_state.generated_email_content = email_output['content']
                        status_placeholder.success("Email generated successfully!")
                        time.sleep(1) # Show success briefly
                        status_placeholder.empty() # Clear status
                    else:
                        st.session_state.generated_email_subject = None
                        st.session_state.generated_email_content = None
                        status_placeholder.error("Failed to generate email content.")

                except Exception as e:
                    status_placeholder.error(f"Error generating email: {e}")
                    st.session_state.generated_email_subject = None
                    st.session_state.generated_email_content = None

        display_email_preview(st.session_state.generated_email_subject, st.session_state.generated_email_content)

        # Send button - only show if email is generated
        if st.session_state.generated_email_subject and st.session_state.generated_email_content:
             send_clicked = st.button("🚀 Send Email", key="or_send", type="primary")

             if send_clicked:
                 status_placeholder.info(f"Sending email to {recipient_email}...")
                 try:
                     # Call agent's send_email method (adjust based on actual signature)
                     success = agent.send_email(
                         recipient=recipient_email,
                         subject=st.session_state.generated_email_subject,
                         content=st.session_state.generated_email_content
                     )

                     if success:
                         status_placeholder.success(f"Email sent successfully to {recipient_email}!")
                         # Clear generated content and potentially the selected lead after sending
                         st.session_state.generated_email_subject = None
                         st.session_state.generated_email_content = None
                         if 'outreach_target_lead' in st.session_state:
                              del st.session_state.outreach_target_lead
                         # Add short delay and rerun to reset UI
                         time.sleep(2)
                         st.rerun()
                     else:
                         status_placeholder.error("Failed to send email. Check logs or Azure Email Service status.")

                 except Exception as e:
                     status_placeholder.error(f"Error sending email: {e}")

if __name__ == "__main__":
    run_outreach()