import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
# Removed AzureOpenAI import as it's not used directly here now
import sys

# --- Add parent directory to path ---
# Ensure this structure works for your execution context
try:
    parent_dir = os.path.dirname(os.path.dirname(__file__))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
except IndexError:
    print("Warning: Could not automatically add parent directory to sys.path.")
# --- End Add path ---

# Load environment variables from root directory
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

# --- Function to load CSS ---
def load_css(file_name="style.css"):
    css_path = os.path.join(os.path.dirname(__file__), file_name)
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    else:
        st.warning(f"CSS file not found at {css_path}")
# --- End Load CSS function ---

# --- Placeholder Data Fetching Functions ---
# Replace these with actual calls to your backend logic/database
def get_dashboard_metrics():
    # EXAMPLE: Replace with dynamic data
    return {
        "leads": {"value": 138, "delta": 13, "delta_type": "positive"},
        "emails": {"value": 910, "delta": 60, "delta_type": "positive"},
        "responses": {"value": 105, "delta": 7, "delta_type": "positive"},
        "meetings": {"value": 24, "delta": 2, "delta_type": "positive"}
    }

def get_recent_activities():
    # EXAMPLE: Replace with dynamic data
    return [
        {"time": "5 mins ago", "action": "New lead generated: Innovate Inc", "icon": "🎯"},
        {"time": "25 mins ago", "action": "Email sent to Alpha Corp", "icon": "📧"},
        {"time": "1 hour ago", "action": "Meeting scheduled with Beta Solutions", "icon": "📅"},
        {"time": "3 hours ago", "action": "Response received from Gamma Tech", "icon": "💬"},
        {"time": "Yesterday", "action": "Lead Research completed for Omega Systems", "icon": "🔍"}
    ]
# --- End Placeholders ---


# --- UI Component Functions ---
def display_sidebar():
    with st.sidebar:
        st.markdown('<div class="sidebar-header">Gama AI SDR</div>', unsafe_allow_html=True) # Shortened Name
        # Consider adding a small logo image here if available
        # st.image("path/to/your/logo.png", width=80)

        # Navigation uses Streamlit's multipage feature, styled via CSS
        st.page_link("app.py", label="Dashboard", icon="🏠")
        st.page_link("pages/lead_generation.py", label="Lead Generation", icon="🎯")
        st.page_link("pages/lead_research.py", label="Lead Research", icon="🔍")
        st.page_link("pages/outreach.py", label="Email Outreach", icon="📧")
        st.page_link("pages/conversation_tracking.py", label="Conversations", icon="💬")

        st.markdown("---")
        st.markdown("### Quick Actions")
        if st.button("✨ Generate New Leads", use_container_width=True, type="secondary"):
            st.switch_page("pages/lead_generation.py")
        if st.button("📊 Export Reports", use_container_width=True, type="secondary"):
            st.info("Export functionality coming soon!") # Placeholder
        if st.button("📧 Send Bulk Emails", use_container_width=True, type="secondary"):
            st.info("Bulk email functionality coming soon!") # Placeholder

        st.markdown("---")
        st.markdown("### System Info")
        # Consider loading version from a config file or __version__ variable
        st.caption(f"Version: 1.0.1") # Example version bump
        st.caption(f"Status: Operational") # Example status

def display_metrics():
    st.markdown('<div class="sub-header">Performance Overview</div>', unsafe_allow_html=True)
    metrics = get_dashboard_metrics()
    cols = st.columns(len(metrics)) # Dynamically create columns

    metric_labels = {
        "leads": "Leads Generated",
        "emails": "Emails Sent",
        "responses": "Responses Received",
        "meetings": "Meetings Scheduled"
    }

    for i, (key, data) in enumerate(metrics.items()):
        with cols[i]:
            delta_val = data.get('delta', 0)
            delta_type = data.get('delta_type', 'positive' if delta_val >= 0 else 'negative')
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{data.get('value', 0)}</div>
                <div class="metric-label">{metric_labels.get(key, key.capitalize())}</div>
                <div class="metric-delta {delta_type}">{delta_val}</div>
            </div>
            """, unsafe_allow_html=True)

def display_recent_activity():
    st.markdown('<div class="sub-header">Recent Activity</div>', unsafe_allow_html=True)
    activities = get_recent_activities()

    with st.container(border=True): # Use Streamlit's border feature for the container
        if not activities:
            st.info("No recent activity to display.")
        else:
            for activity in activities:
                st.markdown(f"""
                <div class="activity-item">
                    <div class="activity-details">
                         <span class="activity-icon">{activity.get('icon','')}</span>
                         <span class="activity-action">{activity.get('action','No action description')}</span>
                    </div>
                    <div class="activity-time">{activity.get('time','')}</div>
                </div>
                """, unsafe_allow_html=True)

def check_environment():
    st.markdown('<div class="sub-header">System Status</div>', unsafe_allow_html=True)
    # Simplified check, focusing on key services
    env_vars_status = {
        "Azure OpenAI": all(os.getenv(k) for k in ["AZURE_OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_DEPLOYMENT"]),
        "Azure Email": all(os.getenv(k) for k in ["AZURE_COMMUNICATION_CONNECTION_STRING", "AZURE_COMMUNICATION_SENDER_EMAIL"]),
        "SERP API": bool(os.getenv("SERPAPI_API_KEY")),
    }
    all_ok = True
    for service, configured in env_vars_status.items():
        css_class = "env-ok" if configured else "env-error"
        icon = "✅" if configured else "❌"
        status_text = "Configured" if configured else "Missing/Incomplete"
        st.markdown(f'<div class="env-status {css_class}">{icon} {service}: {status_text}</div>', unsafe_allow_html=True)
        if not configured:
            all_ok = False

    if not all_ok:
        st.warning("Some services may not function correctly due to missing configuration. Please check your `.env` file.")

# --- Main App Execution ---
def main():
    st.set_page_config(page_title="Gama AI SDR Dashboard", page_icon="📊", layout="wide")
    load_css() # Load the external CSS

    display_sidebar()

    # Main content area using CSS class for padding/margins if needed
    st.markdown('<div class="main-container">', unsafe_allow_html=True)

    st.markdown('<div class="main-header">SDR AI Dashboard</div>', unsafe_allow_html=True)

    # Welcome message using st.info or a custom card class
    st.info("""
        **Welcome to your AI-Powered Sales Development Hub!** 🚀
        Monitor performance, manage leads, and streamline outreach.
    """, icon="👋")

    check_environment()
    display_metrics()
    display_recent_activity()

    # Example placeholder for future charts/tables
    st.markdown('<div class="sub-header">Further Analysis (Placeholder)</div>', unsafe_allow_html=True)
    st.caption("More detailed reports and charts will be available here soon.")

    st.markdown('</div>', unsafe_allow_html=True) # Close main-container div


if __name__ == "__main__":
    main()