import streamlit as st
import sys
import os
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env'))

# Add parent directory to path to import from src
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.agents.conversation_agent import ConversationAgent

st.set_page_config(page_title="Conversations", page_icon="💬", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .conversation-card {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        cursor: pointer;
    }
    .conversation-card:hover {
        border-color: #3B82F6;
    }
    .company-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1E40AF;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-left: 0.5rem;
    }
    .status-negotiating {
        background-color: #DBEAFE;
        color: #1E40AF;
    }
    .status-following-up {
        background-color: #FEF3C7;
        color: #92400E;
    }
    .status-closed-won {
        background-color: #D1FAE5;
        color: #065F46;
    }
    .status-closed-lost {
        background-color: #FEE2E2;
        color: #B91C1C;
    }
    .message-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 1rem;
        background-color: #F9FAFB;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .message {
        padding: 0.75rem 1rem;
        border-radius: 10px;
        margin-bottom: 0.75rem;
        max-width: 80%;
    }
    .message-incoming {
        background-color: #E5E7EB;
        color: #1F2937;
        align-self: flex-start;
    }
    .message-outgoing {
        background-color: #DBEAFE;
        color: #1E40AF;
        align-self: flex-end;
        margin-left: auto;
    }
    .message-time {
        font-size: 0.7rem;
        color: #6B7280;
        margin-top: 0.25rem;
    }
    .tab-content {
        padding: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def get_mock_conversations():
    """Get mock conversation data for demonstration"""
    return {
        "Active": [
            {
                "company": "TechCorp", 
                "status": "Negotiating", 
                "last_contact": "2 days ago",
                "contact": "John Smith",
                "email": "john@techcorp.com",
                "messages": [
                    {"text": "Hi, I'm interested in learning more about your services.", "sender": "lead", "time": "5 days ago"},
                    {"text": "Hello John! Thank you for your interest. I'd be happy to tell you more about our AI-powered solutions.", "sender": "ai", "time": "5 days ago"},
                    {"text": "Can you provide pricing information?", "sender": "lead", "time": "3 days ago"},
                    {"text": "Certainly! Our pricing starts at $499/month for the basic package. Would you like me to send over a detailed pricing sheet?", "sender": "ai", "time": "2 days ago"}
                ]
            },
            {
                "company": "DataSoft", 
                "status": "Following Up", 
                "last_contact": "1 day ago",
                "contact": "Sarah Johnson",
                "email": "sarah@datasoft.io",
                "messages": [
                    {"text": "I saw your presentation at the tech conference last week.", "sender": "lead", "time": "4 days ago"},
                    {"text": "Hi Sarah! I'm glad you caught our presentation. What aspects of our solution interested you the most?", "sender": "ai", "time": "4 days ago"},
                    {"text": "I'm particularly interested in the data analytics features.", "sender": "lead", "time": "3 days ago"},
                    {"text": "Great choice! Our analytics suite is one of our strongest offerings. Would you be available for a demo this week?", "sender": "ai", "time": "1 day ago"}
                ]
            }
        ],
        "Completed": [
            {
                "company": "AITech", 
                "status": "Closed Won", 
                "last_contact": "1 week ago",
                "contact": "Michael Brown",
                "email": "michael@aitech.com",
                "messages": [
                    {"text": "We're looking for a new AI solution for our customer service.", "sender": "lead", "time": "3 weeks ago"},
                    {"text": "Hello Michael! Our AI solution would be perfect for enhancing your customer service operations.", "sender": "ai", "time": "3 weeks ago"},
                    {"text": "Let's schedule a demo for next week.", "sender": "lead", "time": "2 weeks ago"},
                    {"text": "Excellent! I've sent a calendar invite for Tuesday at 2pm.", "sender": "ai", "time": "2 weeks ago"},
                    {"text": "The demo was great. We'd like to move forward with the enterprise plan.", "sender": "lead", "time": "1 week ago"},
                    {"text": "Fantastic news! I'll prepare the contract right away. Welcome aboard!", "sender": "ai", "time": "1 week ago"}
                ]
            },
            {
                "company": "CloudServ", 
                "status": "Closed Lost", 
                "last_contact": "3 days ago",
                "contact": "Jessica Lee",
                "email": "jessica@cloudserv.net",
                "messages": [
                    {"text": "We're evaluating several vendors for our new project.", "sender": "lead", "time": "2 weeks ago"},
                    {"text": "Hi Jessica! I'd be happy to show you how our solution stands out from the competition.", "sender": "ai", "time": "2 weeks ago"},
                    {"text": "Can you match the pricing offered by your competitor?", "sender": "lead", "time": "1 week ago"},
                    {"text": "While our pricing is competitive for the value we provide, I can discuss some customized options.", "sender": "ai", "time": "1 week ago"},
                    {"text": "We've decided to go with another vendor. Thanks for your time.", "sender": "lead", "time": "3 days ago"},
                    {"text": "I understand. Thank you for considering us. Please keep us in mind for future projects!", "sender": "ai", "time": "3 days ago"}
                ]
            }
        ]
    }

def get_status_badge(status):
    """Get HTML for status badge"""
    status_class = status.lower().replace(" ", "-")
    return f'<span class="status-badge status-{status_class}">{status}</span>'

def main():
    st.markdown('<div class="main-header">Conversation Management 💬</div>', unsafe_allow_html=True)
    
    # Get conversation data
    conversations = get_mock_conversations()
    
    # Create tabs for active and completed conversations
    tab1, tab2 = st.tabs(["Active Conversations", "Completed Conversations"])
    
    # Selected conversation state
    if "selected_conversation" not in st.session_state:
        st.session_state.selected_conversation = None
    
    # Function to display conversation list
    def display_conversation_list(conv_list):
        for idx, conv in enumerate(conv_list):
            company = conv["company"]
            status = conv["status"]
            last_contact = conv["last_contact"]
            contact = conv["contact"]
            
            # Create a clickable card for each conversation
            card_html = f"""
            <div class="conversation-card" onclick="alert('Clicked {company}')">
                <div class="company-name">{company}{get_status_badge(status)}</div>
                <div style="margin-top: 0.25rem; font-size: 0.9rem;">
                    Contact: {contact}
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.8rem; color: #6B7280;">
                    <span>Last Contact: {last_contact}</span>
                    <span>{len(conv['messages'])} messages</span>
                </div>
            </div>
            """
            
            # Use a container and button to make the card clickable
            with st.container():
                st.markdown(card_html, unsafe_allow_html=True)
                
                # Hidden button that updates the session state
                if st.button(f"Select {company}", key=f"btn_{idx}_{status}", label_visibility="collapsed"):
                    st.session_state.selected_conversation = conv
                    st.rerun()
    
    # Display active conversations tab
    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Active Conversations")
            display_conversation_list(conversations["Active"])
        
        with col2:
            if st.session_state.selected_conversation and st.session_state.selected_conversation["status"] in ["Negotiating", "Following Up"]:
                conv = st.session_state.selected_conversation
                st.markdown(f"### Conversation with {conv['company']}")
                
                # Company info
                st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <div><strong>Contact:</strong> {conv['contact']}</div>
                    <div><strong>Email:</strong> {conv['email']}</div>
                    <div><strong>Status:</strong> {conv['status']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Message history
                st.markdown('<div class="message-container">', unsafe_allow_html=True)
                for msg in conv['messages']:
                    msg_class = "message-incoming" if msg['sender'] == 'lead' else "message-outgoing"
                    st.markdown(f"""
                    <div class="message {msg_class}">
                        <div>{msg['text']}</div>
                        <div class="message-time">{msg['time']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Reply form
                with st.form("reply_form"):
                    reply = st.text_area("Reply", height=100)
                    col_send, col_space = st.columns([1, 3])
                    with col_send:
                        send_clicked = st.form_submit_button("Send Reply", use_container_width=True)
                    
                    if send_clicked and reply:
                        # In a real app, this would send the reply
                        st.success("Reply sent!")
                        
                        # Add reply to conversation
                        new_message = {
                            "text": reply,
                            "sender": "ai",
                            "time": "Just now"
                        }
                        st.session_state.selected_conversation["messages"].append(new_message)
                        st.rerun()
            else:
                st.info("Select a conversation to view details")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display completed conversations tab
    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Completed Conversations")
            display_conversation_list(conversations["Completed"])
        
        with col2:
            if st.session_state.selected_conversation and st.session_state.selected_conversation["status"] in ["Closed Won", "Closed Lost"]:
                conv = st.session_state.selected_conversation
                st.markdown(f"### Conversation with {conv['company']}")
                
                # Company info with status badge
                status_color = "green" if conv['status'] == "Closed Won" else "red"
                st.markdown(f"""
                <div style="margin-bottom: 1rem;">
                    <div><strong>Contact:</strong> {conv['contact']}</div>
                    <div><strong>Email:</strong> {conv['email']}</div>
                    <div><strong>Status:</strong> <span style="color: {status_color};">{conv['status']}</span></div>
                </div>
                """, unsafe_allow_html=True)
                
                # Message history
                st.markdown('<div class="message-container">', unsafe_allow_html=True)
                for msg in conv['messages']:
                    msg_class = "message-incoming" if msg['sender'] == 'lead' else "message-outgoing"
                    st.markdown(f"""
                    <div class="message {msg_class}">
                        <div>{msg['text']}</div>
                        <div class="message-time">{msg['time']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Analytics for closed deals
                if conv['status'] == "Closed Won":
                    st.markdown("### Deal Analytics")
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Deal Value", "$12,500")
                    with col_b:
                        st.metric("Time to Close", "21 days")
                    with col_c:
                        st.metric("Emails Exchanged", len(conv['messages']))
            else:
                st.info("Select a conversation to view details")
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()