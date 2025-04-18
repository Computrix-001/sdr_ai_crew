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
    # Assuming a ConversationAgent exists - replace if name is different
    from agents.conversation_agent import ConversationAgent
except ImportError:
    st.warning("ConversationAgent not found. Displaying static example data.")
    ConversationAgent = None

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(parent_dir), '.env'))

# --- Helper Functions ---
# Placeholder for fetching conversation data
# Replace with actual calls to your backend/database/agent
def get_conversation_data():
    # EXAMPLE STATIC DATA - Replace with dynamic fetching
    return {
        "Active": [
            {"id": "conv1", "company": "Alpha Corp", "contact": "John Doe", "email": "john.doe@alpha.com", "status": "FollowingUp", "last_contact": "2 days ago", "messages": [
                {"text": "Hi John, following up on our proposal.", "sender": "ai", "time": "2 days ago"},
                {"text": "Thanks, reviewing it this week.", "sender": "lead", "time": "1 day ago"}
            ]},
            {"id": "conv2", "company": "Beta Solutions", "contact": "Jane Smith", "email": "jane.s@beta.com", "status": "Negotiating", "last_contact": "1 day ago", "messages": [
                 {"text": "Can we adjust the payment terms?", "sender": "lead", "time": "1 day ago"},
                 {"text": "Let me check with finance and get back to you.", "sender": "ai", "time": "1 day ago"},
            ]}
        ],
        "Completed": [
             {"id": "conv3", "company": "Gamma Tech", "contact": "Peter Jones", "email": "peter.j@gamma.com", "status": "ClosedWon", "last_contact": "1 week ago", "messages": []},
             {"id": "conv4", "company": "Delta Inc", "contact": "Mary Brown", "email": "m.brown@delta.com", "status": "ClosedLost", "last_contact": "2 weeks ago", "messages": []}
        ]
    }

def get_status_badge(status):
    """Generate HTML for status badge based on CSS classes."""
    safe_status = "".join(filter(str.isalnum, status)) # Make status safe for class name
    return f'<span class="status-badge status-{safe_status}">{status}</span>'

# --- UI Component Functions ---
def display_conversation_list(conversations, status_filter):
    if not conversations:
        st.info(f"No {status_filter.lower()} conversations found.")
        return

    for idx, conv in enumerate(conversations):
        conv_id = conv.get('id', f'conv_{status_filter}_{idx}') # Unique key
        company = conv.get('company', 'N/A')
        contact = conv.get('contact', 'N/A')
        last_contact = conv.get('last_contact', 'N/A')
        status = conv.get('status', 'Unknown')
        num_messages = len(conv.get('messages', []))

        # Use st.button to make the card clickable and store selection in session state
        # We simulate a card look using markdown inside the button area or use st.container
        container = st.container(border=True)
        with container:
             # Card content using markdown and CSS classes
             card_html = f"""
                 <div class="conversation-card-content">
                     <div class="company-name">{company} {get_status_badge(status)}</div>
                     <div class="conversation-details">Contact: {contact}</div>
                     <div class="conversation-summary">
                         <span>Last: {last_contact}</span>
                         <span>{num_messages} messages</span>
                     </div>
                 </div>
             """
             st.markdown(card_html, unsafe_allow_html=True)

             # Invisible overlay or explicit button for selection
             if st.button("View Details", key=conv_id, type="secondary", use_container_width=True):
                 st.session_state.selected_conversation_id = conv_id
                 st.session_state.selected_conversation_data = conv # Store full data
                 st.rerun() # Rerun to update the details view

def display_conversation_details(conversation):
    if not conversation:
        st.info("Select a conversation from the list to view details.")
        return

    st.markdown(f"### Conversation with {conversation.get('company', 'N/A')}")

    # Display basic info
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Contact:** {conversation.get('contact', 'N/A')}")
        st.markdown(f"**Email:** {conversation.get('email', 'N/A')}")
    with col2:
         st.markdown(f"**Status:** {conversation.get('status', 'N/A')}")
         st.markdown(f"**Last Contact:** {conversation.get('last_contact', 'N/A')}")

    st.markdown("---")
    st.markdown("##### Message History")

    # Message display area
    st.markdown('<div class="message-container">', unsafe_allow_html=True)
    messages = conversation.get('messages', [])
    if not messages:
        st.caption("No messages in this conversation yet.")
    else:
        for msg in messages:
            sender_type = msg.get('sender', 'unknown') # 'ai' or 'lead'
            msg_class = "message-outgoing" if sender_type == 'ai' else "message-incoming"
            text = msg.get('text', '')
            time_str = msg.get('time', '')

            st.markdown(f"""
            <div class="message {msg_class}">
                <div class="message-text">{text}</div>
                <div class="message-time">{time_str}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Reply Form (only for active conversations)
    if conversation.get('status') in ["FollowingUp", "Negotiating"]:
        st.markdown("---")
        st.markdown("##### Send Reply")
        with st.form("reply_form", clear_on_submit=True):
            reply_text = st.text_area("Your Reply", height=100, key="ct_reply_text")
            send_clicked = st.form_submit_button("Send Reply", type="primary")

            if send_clicked and reply_text:
                # --- Placeholder for sending reply via agent ---
                st.info("Sending reply...")
                print(f"Simulating sending reply to {conversation.get('email')}: {reply_text}")
                time.sleep(1) # Simulate network delay
                st.success("Reply sent successfully (Simulated)!")
                # --- End Placeholder ---

                # --- Placeholder for updating conversation data ---
                # In a real app, you'd fetch updated data or update local state
                # This adds the message locally for immediate feedback (will be lost on full refresh)
                new_message = {"text": reply_text, "sender": "ai", "time": "Just now"}
                st.session_state.selected_conversation_data['messages'].append(new_message)
                st.rerun() # Rerun to show the new message
                # --- End Placeholder ---


# --- Main Page Execution ---
def run_conversation_tracking():
    st.set_page_config(page_title="Conversation Tracking", page_icon="💬", layout="wide")
    load_css()

    st.markdown('<div class="main-header">Conversation Tracking</div>', unsafe_allow_html=True)

    # Fetch conversation data (using placeholder)
    all_conversations = get_conversation_data()
    active_convos = all_conversations.get("Active", [])
    completed_convos = all_conversations.get("Completed", [])

    # Initialize session state for selection
    if 'selected_conversation_id' not in st.session_state:
        st.session_state.selected_conversation_id = None
        st.session_state.selected_conversation_data = None

    # Layout: List on the left, Details on the right
    col_list, col_details = st.columns([1, 2]) # Adjust ratio as needed

    with col_list:
        st.markdown('<div class="sub-header">Conversations</div>', unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Active", "Completed"])

        with tab1:
            display_conversation_list(active_convos, "Active")
        with tab2:
            display_conversation_list(completed_convos, "Completed")

    with col_details:
        st.markdown('<div class="sub-header">Details & Actions</div>', unsafe_allow_html=True)
        # Display details based on session state selection
        display_conversation_details(st.session_state.get('selected_conversation_data'))


if __name__ == "__main__":
    run_conversation_tracking()