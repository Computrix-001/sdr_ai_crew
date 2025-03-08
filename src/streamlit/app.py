import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables before anything else
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env'))

# Add parent directory to path to import from src
parent_dir = os.path.dirname(os.path.dirname(__file__))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Check environment variables
env_vars = {
    "AZURE_API_KEY": os.getenv("AZURE_API_KEY"),
    "AZURE_API_BASE": os.getenv("AZURE_API_BASE"),
    "AZURE_API_VERSION": os.getenv("AZURE_API_VERSION"),
    "AZURE_COMMUNICATION_CONNECTION_STRING": os.getenv("AZURE_COMMUNICATION_CONNECTION_STRING"),
    "SERPAPI_API_KEY": os.getenv("SERPAPI_API_KEY")
}

st.set_page_config(
    page_title="Gama AI SDR System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2563EB;
        margin-top: 1rem;
    }
    .card {
        border-radius: 10px;
        padding: 1.5rem;
        background-color: #F3F4F6;
        margin-bottom: 1rem;
        border-left: 5px solid #3B82F6;
    }
    .metric-card {
        background-color: #EFF6FF;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        border: 1px solid #DBEAFE;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1E40AF;
    }
    .metric-label {
        font-size: 1rem;
        color: #6B7280;
    }
    .activity-item {
        padding: 0.75rem;
        border-bottom: 1px solid #E5E7EB;
    }
    .activity-time {
        font-size: 0.8rem;
        color: #6B7280;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    .action-button {
        background-color: #2563EB;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        text-align: center;
        margin-bottom: 0.5rem;
        cursor: pointer;
    }
    .env-status {
        padding: 0.5rem;
        border-radius: 5px;
        margin-bottom: 0.5rem;
    }
    .env-ok {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .env-error {
        background-color: #FEE2E2;
        color: #B91C1C;
    }
</style>
""", unsafe_allow_html=True)

def get_mock_metrics():
    return {
        "leads": {"value": 127, "delta": 15},
        "emails": {"value": 89, "delta": 12},
        "responses": {"value": 34, "delta": 5},
        "meetings": {"value": 8, "delta": 2}
    }

def display_metrics():
    metrics = get_mock_metrics()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Leads Generated</div>
            <div style="color: green; font-size: 0.9rem;">↑ {}</div>
        </div>
        """.format(metrics["leads"]["value"], metrics["leads"]["delta"]), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Emails Sent</div>
            <div style="color: green; font-size: 0.9rem;">↑ {}</div>
        </div>
        """.format(metrics["emails"]["value"], metrics["emails"]["delta"]), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Responses</div>
            <div style="color: green; font-size: 0.9rem;">↑ {}</div>
        </div>
        """.format(metrics["responses"]["value"], metrics["responses"]["delta"]), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">{}</div>
            <div class="metric-label">Meetings Scheduled</div>
            <div style="color: green; font-size: 0.9rem;">↑ {}</div>
        </div>
        """.format(metrics["meetings"]["value"], metrics["meetings"]["delta"]), unsafe_allow_html=True)

def display_recent_activity():
    st.markdown('<div class="sub-header">Recent Activity</div>', unsafe_allow_html=True)
    
    activities = [
        {"time": "10 mins ago", "action": "New lead generated: TechCorp", "icon": "🎯"},
        {"time": "1 hour ago", "action": "Email sent to DataSoft", "icon": "📧"},
        {"time": "2 hours ago", "action": "Response received from AITech", "icon": "💬"},
        {"time": "1 day ago", "action": "Meeting scheduled with CloudServ", "icon": "📅"}
    ]
    
    for activity in activities:
        st.markdown(f"""
        <div class="activity-item">
            <div>{activity['icon']} <b>{activity['action']}</b></div>
            <div class="activity-time">{activity['time']}</div>
        </div>
        """, unsafe_allow_html=True)

def check_environment():
    st.markdown('<div class="sub-header">Environment Status</div>', unsafe_allow_html=True)
    
    all_ok = True
    for key, value in env_vars.items():
        if value:
            st.markdown(f"""
            <div class="env-status env-ok">
                ✅ {key}: Configured
            </div>
            """, unsafe_allow_html=True)
        else:
            all_ok = False
            st.markdown(f"""
            <div class="env-status env-error">
                ❌ {key}: Missing
            </div>
            """, unsafe_allow_html=True)
    
    if not all_ok:
        st.warning("Some environment variables are missing. Please check your .env file.")
        st.info("Make sure your .env file includes all required variables for Azure OpenAI, Azure Communication Services, and SERP API.")

def main():
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-header">Gama AI SDR System</div>', unsafe_allow_html=True)
        
        st.image("https://img.icons8.com/fluency/96/000000/artificial-intelligence.png", width=80)
        
        st.markdown("### Navigation")
        st.markdown("🏠 Dashboard")  # Current page
        st.page_link("pages/lead_generation.py", label="Lead Generation", icon="🎯")
        st.page_link("pages/lead_research.py", label="Lead Research", icon="🔍")
        st.page_link("pages/outreach.py", label="Email Outreach", icon="📧")
        st.page_link("pages/conversation_tracking.py", label="Conversations", icon="💬")
        
        st.markdown("---")
        st.markdown("### Quick Actions")
        
        st.markdown("""
        <div class="action-button">✨ Generate New Leads</div>
        <div class="action-button">📊 Export Reports</div>
        <div class="action-button">📧 Send Bulk Emails</div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### System Info")
        st.markdown(f"Version: 1.0.0")
        st.markdown(f"Last Updated: {datetime.now().strftime('%Y-%m-%d')}")
    
    # Main content
    st.markdown('<div class="main-header">Welcome to Gama AI SDR System</div>', unsafe_allow_html=True)
    
    # Welcome message in a card
    st.markdown("""
    <div class="card">
        <h3>Your AI-Powered Sales Development Platform 🚀</h3>
        <p>Streamline your sales process with our intelligent SDR system:</p>
        <ul>
            <li><b>Smart Lead Generation:</b> Find qualified prospects automatically</li>
            <li><b>Deep Lead Research:</b> Get detailed company insights</li>
            <li><b>Automated Outreach:</b> Personalized email campaigns</li>
            <li><b>Intelligent Conversations:</b> AI-powered response handling</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Environment check
    check_environment()
    
    # Display metrics
    st.markdown('<div class="sub-header">Dashboard Overview</div>', unsafe_allow_html=True)
    display_metrics()
    
    # Two-column layout for activity and quick actions
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_recent_activity()
    
    with col2:
        st.markdown('<div class="sub-header">Quick Stats</div>', unsafe_allow_html=True)
        
        # Create a sample chart
        chart_data = pd.DataFrame({
            'Date': pd.date_range(start=datetime.now() - timedelta(days=6), periods=7, freq='D'),
            'Leads': [5, 7, 12, 8, 10, 15, 18],
            'Emails': [3, 5, 8, 6, 7, 10, 12]
        })
        chart_data = chart_data.set_index('Date')
        st.line_chart(chart_data)
        
        st.markdown("""
        <div class="card" style="border-left-color: #10B981;">
            <h4>Weekly Performance</h4>
            <p>Leads: <b>+28%</b> from last week</p>
            <p>Conversion: <b>12.4%</b></p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()