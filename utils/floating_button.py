"""
Floating Chatbot Button Component
Provides a reusable floating button that appears on all pages and navigates to Chatbot page.
"""
import streamlit as st

def add_floating_chatbot_button():
    """
    Add a floating chatbot button to the bottom-right corner of the page.
    Click it to navigate to the Chatbot page.
    """
    st.markdown("""
    <style>
        /* Floating Chatbot Button */
        .floating-chatbot-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            z-index: 999;
            transition: all 0.3s ease;
            text-decoration: none;
        }
        
        .floating-chatbot-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 16px rgba(102, 126, 234, 0.6);
            bottom: 35px;
        }
        
        .floating-chatbot-btn:active {
            transform: scale(0.95);
        }
        
        /* Pulse animation */
        @keyframes pulse {
            0% {
                box-shadow: 0 0 0 0 rgba(102, 126, 234, 0.7);
            }
            70% {
                box-shadow: 0 0 0 10px rgba(102, 126, 234, 0);
            }
            100% {
                box-shadow: 0 0 0 0 rgba(102, 126, 234, 0);
            }
        }
        
        .floating-chatbot-btn.pulse {
            animation: pulse 2s infinite;
        }
        
        /* Tooltip */
        .floating-chatbot-tooltip {
            position: fixed;
            bottom: 100px;
            right: 30px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            white-space: nowrap;
            opacity: 0;
            transition: opacity 0.3s ease;
            pointer-events: none;
            z-index: 1000;
        }
        
        .floating-chatbot-btn:hover + .floating-chatbot-tooltip,
        .floating-chatbot-tooltip:hover {
            opacity: 1;
        }
    </style>
    
    <a href="?page=4_Chatbot" class="floating-chatbot-btn pulse" title="Ask Chatbot" onclick="
        // Navigate to Chatbot page using Streamlit's navigation
        window.location.href = '?page=Chatbot' || window.location.href.split('?')[0].replace(/\\/[^\\/]*$/, '') + '/Chatbot';
    ">
        💬
    </a>
    <div class="floating-chatbot-tooltip">Ask Chatbot</div>
    """, unsafe_allow_html=True)
    
    # Alternative: Using st.query_params for navigation (Streamlit 1.28+)
    if st.sidebar.button("💬 Ask Chatbot", key="floating_chatbot_sidebar", help="Go to Chatbot"):
        st.switch_page("pages/.hidden/Chatbot.py")
