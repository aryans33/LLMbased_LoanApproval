"""
AI-Powered Loan Approval Chatbot - Streamlit Application

A professional loan eligibility assessment tool powered by Google's Gemini API.
Provides intelligent conversation flow for gathering financial information and
making preliminary loan approval decisions.

Author: [Your Name]
Version: 2.0.0
License: MIT
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

import streamlit as st
from dotenv import load_dotenv

from services.gemini_service import GeminiChatbot
from utils.metrics_tracker import MetricsTracker


# ==================== Configuration ====================

class AppConfig:
    """Application configuration constants."""
    
    PAGE_TITLE = "Loan Approval Assistant"
    PAGE_ICON = "💼"
    LAYOUT = "wide"
    SIDEBAR_STATE = "expanded"
    
    # Data field labels and formats
    DATA_LABELS = {
        'gross_monthly_income': ('💵 Monthly Income', 'currency'),
        'total_monthly_debt': ('💳 Monthly Debt', 'currency'),
        'loan_amount': ('🏦 Loan Amount', 'currency'),
        'employment_status': ('💼 Employment', 'text'),
        'credit_score_range': ('📊 Credit Score', 'text')
    }


# ==================== Initialization ====================

def initialize_app() -> None:
    """Configure the Streamlit application page settings."""
    load_dotenv()
    
    st.set_page_config(
        page_title=AppConfig.PAGE_TITLE,
        page_icon=AppConfig.PAGE_ICON,
        layout=AppConfig.LAYOUT,
        initial_sidebar_state=AppConfig.SIDEBAR_STATE
    )


def initialize_session_state() -> None:
    """
    Initialize all Streamlit session state variables.
    
    Raises:
        SystemExit: If GEMINI_API_KEY is not found in environment variables.
    """
    # Chatbot initialization
    if 'chatbot' not in st.session_state:
        # Try to get API key from Streamlit secrets first, then from environment
        api_key = None
        try:
            api_key = st.secrets.get("GEMINI_API_KEY")
        except (FileNotFoundError, KeyError):
            api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:
            st.error("❌ GEMINI_API_KEY not found!")
            st.info("Please add your Gemini API key to Streamlit secrets or .env file")
            st.stop()
        st.session_state.chatbot = GeminiChatbot(api_key)
    
    # Chat session initialization
    if 'chat_session' not in st.session_state:
        st.session_state.chat_session = st.session_state.chatbot.create_new_chat()
    
    # Message history initialization
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        _add_initial_message()
    
    # Metrics tracker initialization
    if 'metrics_tracker' not in st.session_state:
        st.session_state.metrics_tracker = MetricsTracker()
    
    # Initialization flag
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True


def _add_initial_message() -> None:
    """Add the initial welcome message from the chatbot."""
    initial_content = st.session_state.chat_session['history'][0]['parts'][0]
    st.session_state.messages.append({
        'role': 'assistant',
        'content': initial_content,
        'timestamp': datetime.now()
    })


# ==================== Styling ====================

class StyleManager:
    """Manage application styling with clean white theme."""
    
    @staticmethod
    def get_css() -> str:
        """
        Get clean white theme CSS styles.
        
        Returns:
            CSS stylesheet as a string
        """
        return """
        <style>
            /* Main App Styling */
            [data-testid="stAppViewContainer"] {
                background: #ffffff;
            }
            
            [data-testid="stSidebar"] {
                background: #fafafa;
                border-right: 1px solid #e5e5e5;
            }
            
            [data-testid="stHeader"] {
                background: transparent;
            }
            
            /* Typography */
            h1, h2, h3, h4, h5, h6 {
                color: #1a1a1a;
                font-weight: 600;
            }
            
            p, span, div {
                color: #333333;
            }
            
            /* Privacy Notice */
            .privacy-notice {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 20px;
                border-radius: 12px;
                border-left: 4px solid #0066cc;
                margin: 20px 0;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
            }
            
            .privacy-notice strong {
                color: #0066cc;
                font-weight: 600;
            }
            
            .privacy-notice p {
                color: #495057;
                margin: 0;
                line-height: 1.6;
            }
            
            /* Data Display Cards */
            .data-item {
                background: #ffffff;
                padding: 18px;
                border-radius: 12px;
                border: 1px solid #e5e5e5;
                margin: 12px 0;
                transition: all 0.3s ease;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            }
            
            .data-item:hover {
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                transform: translateY(-2px);
            }
            
            .data-label {
                font-size: 11px;
                color: #6c757d;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 0.8px;
                margin-bottom: 8px;
            }
            
            .data-value {
                font-size: 22px;
                font-weight: 700;
                color: #1a1a1a;
                margin-top: 4px;
            }
            
            /* Decision Boxes */
            .decision-approved {
                background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                border-left: 5px solid #28a745;
                padding: 20px;
                border-radius: 12px;
                margin: 15px 0;
                color: #155724;
                box-shadow: 0 2px 8px rgba(40, 167, 69, 0.15);
            }
            
            .decision-approved strong {
                color: #0d4b1e;
            }
            
            .decision-conditional {
                background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
                border-left: 5px solid #ffc107;
                padding: 20px;
                border-radius: 12px;
                margin: 15px 0;
                color: #856404;
                box-shadow: 0 2px 8px rgba(255, 193, 7, 0.15);
            }
            
            .decision-conditional strong {
                color: #533f03;
            }
            
            .decision-rejected {
                background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
                border-left: 5px solid #dc3545;
                padding: 20px;
                border-radius: 12px;
                margin: 15px 0;
                color: #721c24;
                box-shadow: 0 2px 8px rgba(220, 53, 69, 0.15);
            }
            
            .decision-rejected strong {
                color: #491217;
            }
            
            /* Buttons */
            .stButton > button {
                background: #0066cc;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: 500;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(0, 102, 204, 0.2);
            }
            
            .stButton > button:hover {
                background: #0052a3;
                box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
                transform: translateY(-1px);
            }
            
            .stButton > button:active {
                transform: translateY(0);
            }
            
            /* Chat Messages */
            [data-testid="stChatMessageContent"] {
                background: #ffffff;
                border-radius: 12px;
                padding: 15px;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
            }
            
            /* Chat Input */
            [data-testid="stChatInput"] {
                background: #ffffff;
                border: 2px solid #e5e5e5;
                border-radius: 12px;
                transition: border-color 0.3s ease;
            }
            
            [data-testid="stChatInput"]:focus-within {
                border-color: #0066cc;
            }
            
            /* Metrics */
            [data-testid="stMetric"] {
                background: #ffffff;
                padding: 15px;
                border-radius: 10px;
                border: 1px solid #e5e5e5;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            }
            
            [data-testid="stMetricLabel"] {
                color: #6c757d;
                font-weight: 500;
            }
            
            [data-testid="stMetricValue"] {
                color: #1a1a1a;
                font-weight: 700;
            }
            
            /* Divider */
            hr {
                border: none;
                border-top: 1px solid #e5e5e5;
                margin: 20px 0;
            }
            
            /* Info Box */
            .stInfo {
                background: #e7f3ff;
                border-left: 4px solid #0066cc;
                color: #004085;
            }
            
            /* Success/Error Messages */
            .stSuccess {
                background: #d4edda;
                border-left: 4px solid #28a745;
                color: #155724;
            }
            
            .stError {
                background: #f8d7da;
                border-left: 4px solid #dc3545;
                color: #721c24;
            }
            
            /* Sidebar Styling */
            [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
                color: #495057;
            }
            
            /* Caption Text */
            .stCaption {
                color: #6c757d;
                font-size: 14px;
            }
            
            /* Scrollbar */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: #f1f1f1;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #c1c1c1;
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #a1a1a1;
            }
            
            /* Spinner */
            [data-testid="stSpinner"] > div {
                border-color: #0066cc !important;
            }
        </style>
        """


# ==================== UI Components ====================

class UIComponents:
    """Reusable UI components for the application."""
    
    @staticmethod
    def render_header() -> None:
        """Render the application header."""
        st.title("💼 Loan Approval Assistant")
        st.caption("AI-Powered Loan Eligibility Assessment using Google Gemini")
    
    @staticmethod
    def render_privacy_notice() -> None:
        """Render the privacy notice banner."""
        st.markdown("""
        <div class="privacy-notice">
            <strong>🔒 Privacy Notice:</strong> This is a preliminary assessment tool. 
            We don't collect sensitive information like SSN or account numbers. 
            Final approval requires document verification. Your conversation is private and secure.
        </div>
        """, unsafe_allow_html=True)


class DataDisplay:
    """Handle display of extracted financial data."""
    
    @staticmethod
    def format_currency(amount: float) -> str:
        """
        Format a number as Indian Rupees currency.
        
        Args:
            amount: Numeric amount to format
            
        Returns:
            Formatted currency string
        """
        return f"₹{amount:,.2f}"
    
    @staticmethod
    def format_value(value: Any, format_type: str) -> str:
        """
        Format a value based on its type.
        
        Args:
            value: Value to format
            format_type: Type of formatting ('currency' or 'text')
            
        Returns:
            Formatted string
        """
        if format_type == 'currency':
            return DataDisplay.format_currency(value)
        return str(value).replace('_', ' ').title()
    
    @staticmethod
    def render_extracted_data() -> None:
        """Display extracted financial data in the sidebar."""
        extracted = st.session_state.chat_session.get('extracted_data', {})
        
        if not extracted:
            st.info("💡 No data extracted yet. Start the conversation!")
            return
        
        for key, (label, format_type) in AppConfig.DATA_LABELS.items():
            if key in extracted and extracted[key]:
                formatted_value = DataDisplay.format_value(extracted[key], format_type)
                
                st.markdown(f"""
                <div class="data-item">
                    <div class="data-label">{label}</div>
                    <div class="data-value">{formatted_value}</div>
                </div>
                """, unsafe_allow_html=True)


class MetricsDisplay:
    """Handle display of conversation metrics."""
    
    @staticmethod
    def render_metrics() -> None:
        """Display comprehensive conversation metrics."""
        metrics = st.session_state.chatbot.get_conversation_metrics(
            st.session_state.chat_session
        )
        
        # Primary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Conversation Turns", metrics.get('turn_count', 0))
            st.metric("Duration", f"{metrics.get('conversation_duration_seconds', 0):.0f}s")
        
        with col2:
            intent_status = "✅" if metrics.get('intent_recognized', False) else "❌"
            st.metric("Intent Recognized", intent_status)
            st.metric("Entities Extracted", metrics.get('entity_extraction_count', 0))
        
        with col3:
            st.metric("Data Completeness", f"{metrics.get('data_completeness', 0):.0f}%")
            st.metric("Errors", metrics.get('error_count', 0))
        
        # Entity details
        if metrics.get('entities_extracted'):
            st.write("**Extracted Entities:**", ", ".join(metrics['entities_extracted']))


class MessageFormatter:
    """Format chat messages with appropriate styling."""
    
    @staticmethod
    def format_content(content: str) -> str:
        """
        Format message content with decision-specific styling.
        
        Args:
            content: Raw message content
            
        Returns:
            HTML-formatted content
        """
        if 'LOAN APPLICATION DECISION' not in content:
            return content
        
        css_class = MessageFormatter._get_decision_class(content)
        return f'<div class="{css_class}">{content}</div>'
    
    @staticmethod
    def _get_decision_class(content: str) -> str:
        """Determine CSS class based on decision type."""
        if 'Approved' in content and 'Conditional' not in content:
            return 'decision-approved'
        elif 'Conditional' in content:
            return 'decision-conditional'
        return 'decision-rejected'


# ==================== Chat Operations ====================

class ChatManager:
    """Manage chat operations and state."""
    
    @staticmethod
    def reset_conversation() -> None:
        """Reset the chat conversation to initial state."""
        st.session_state.chat_session = st.session_state.chatbot.create_new_chat()
        st.session_state.messages = []
        _add_initial_message()
        st.rerun()
    
    @staticmethod
    def display_message_history() -> None:
        """Display all chat messages in the conversation."""
        for message in st.session_state.messages:
            with st.chat_message(message['role']):
                formatted_content = MessageFormatter.format_content(message['content'])
                st.markdown(formatted_content, unsafe_allow_html=True)
    
    @staticmethod
    def handle_user_input(prompt: str) -> None:
        """
        Process user input and generate bot response.
        
        Args:
            prompt: User's input message
        """
        # Add user message
        ChatManager._add_user_message(prompt)
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get and display bot response
        ChatManager._get_bot_response(prompt)
        
        # Log metrics
        ChatManager._log_metrics()
        
        # Refresh UI
        st.rerun()
    
    @staticmethod
    def _add_user_message(content: str) -> None:
        """Add user message to conversation history."""
        st.session_state.messages.append({
            'role': 'user',
            'content': content,
            'timestamp': datetime.now()
        })
    
    @staticmethod
    def _get_bot_response(prompt: str) -> None:
        """Generate and display bot response."""
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response, updated_session = st.session_state.chatbot.send_message(
                    st.session_state.chat_session,
                    prompt
                )
                
                # Update session
                st.session_state.chat_session = updated_session
                
                # Display response
                formatted_response = MessageFormatter.format_content(response)
                st.markdown(formatted_response, unsafe_allow_html=True)
                
                # Save response
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now()
                })
    
    @staticmethod
    def _log_metrics() -> None:
        """Log conversation metrics for analytics."""
        if st.session_state.chat_session.get('turn_count', 0) > 0:
            metrics = st.session_state.chatbot.get_conversation_metrics(
                st.session_state.chat_session
            )
            session_id = st.session_state.chat_session.get('session_id', 'streamlit-session')
            st.session_state.metrics_tracker.log_conversation_metrics(session_id, metrics)


# ==================== Sidebar ====================

class Sidebar:
    """Manage sidebar content and interactions."""
    
    @staticmethod
    def render() -> None:
        """Render the complete sidebar."""
        with st.sidebar:
            st.header("📋 Extracted Information")
            DataDisplay.render_extracted_data()
            
            st.divider()
            
            # Action buttons
            show_metrics = Sidebar._render_action_buttons()
            
            # Conditional metrics display
            if show_metrics:
                st.divider()
                st.subheader("📊 Conversation Metrics")
                MetricsDisplay.render_metrics()
            
            # Session stats
            Sidebar._render_session_stats()
    
    @staticmethod
    def _render_action_buttons() -> bool:
        """
        Render action buttons and return metrics visibility state.
        
        Returns:
            True if metrics should be displayed
        """
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset Chat", use_container_width=True):
                ChatManager.reset_conversation()
        
        with col2:
            show_metrics = st.button("📊 Metrics", use_container_width=True)
        
        return show_metrics
    
    @staticmethod
    def _render_session_stats() -> None:
        """Render session statistics."""
        st.divider()
        session_start = st.session_state.chat_session.get('conversation_start', 0)
        turn_count = st.session_state.chat_session.get('turn_count', 0)
        
        st.caption(f"**Session Started:** {session_start:.0f}")
        st.caption(f"**Total Turns:** {turn_count}")


# ==================== Main Application ====================

def main() -> None:
    """Main application entry point."""
    # Initialize application
    initialize_app()
    initialize_session_state()
    
    # Apply clean white styling
    st.markdown(StyleManager.get_css(), unsafe_allow_html=True)
    
    # Render UI components
    UIComponents.render_header()
    UIComponents.render_privacy_notice()
    
    # Render sidebar
    Sidebar.render()
    
    # Main chat area
    st.divider()
    ChatManager.display_message_history()
    
    # Handle user input
    if prompt := st.chat_input("Type your message here... (e.g., 'I want to apply for a loan')"):
        ChatManager.handle_user_input(prompt)


if __name__ == "__main__":
    main()