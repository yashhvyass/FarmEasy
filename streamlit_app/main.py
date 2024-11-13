import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from helper.langchain_helper import create_vector_db, get_qa_chain
from datetime import datetime, timedelta
import time


# Page Configuration
st.set_page_config(
    page_title="FarmEasy Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session states
if 'messages' not in st.session_state:
    st.session_state.messages = []

def load_mock_data():
    """Load mock data for demonstration"""
    return {
        'weather': pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=30),
            'temperature': np.random.uniform(15, 30, 30),
            'rainfall': np.random.uniform(0, 50, 30),
            'humidity': np.random.uniform(40, 80, 30)
        })
    }

def create_maps_section():
    """Create maps section with metrics for distance, time, and weather"""
    st.subheader("📍 Route Information")
    source = st.session_state.source_state
    destination = st.session_state.destination_state
    distance_km = np.random.uniform(200, 1500)
    travel_time_hr = distance_km / 80

    # First row of metrics
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    with row1_col1:
        st.metric(label="Source", value=source)
    with row1_col2:
        st.metric(label="Destination", value=destination)
    with row1_col3:
        st.metric(label="Distance (km)", value=f"{distance_km:.2f} km")

    # Second row of metrics
    row2_col1, row2_col2, row2_col3 = st.columns(3)
    with row2_col1:
        st.metric(label="Estimated Time (hours)", value=f"{travel_time_hr:.2f} hr")
    with row2_col2:
        st.metric(label="Weather at Source", value=f"{np.random.uniform(15, 30):.1f}°C")
    with row2_col3:
        st.metric(label="Weather at Destination", value=f"{np.random.uniform(15, 30):.1f}°C")

    # Map with route information
    states_df = pd.DataFrame({
        'state': [source, destination],
        'latitude': [39.8283, 37.7749],
        'longitude': [-98.5795, -95.7129]
    })
    fig = px.line_mapbox(states_df, lat='latitude', lon='longitude', title="Route Map",
                         hover_name='state', zoom=3, mapbox_style='carto-positron')
    st.plotly_chart(fig, use_container_width=True)

def create_chat_section():
    """Create AI Farm Assistant chat section with fixed size container and scrollable chat history"""
    st.subheader("💬 AI Farm Assistant")
    
    # Create a fixed-size container for the entire chat section
    with st.container():
        # Custom CSS for fixed-size chat container with scrolling
        st.markdown("""
            <style>
                .chat-container {
                    height: 400px;
                    overflow-y: auto;
                    border: 1px solid #4a4a4a;
                    border-radius: 10px;
                    padding: 15px;
                    margin-bottom: 15px;
                    background-color: #2b2b2b;
                }
                .message {
                    margin: 8px 0;
                    padding: 8px 12px;
                    border-radius: 8px;
                    word-wrap: break-word;
                }
                .user-message {
                    background-color: #3a3a3a;
                    margin-left: 20px;
                }
                .assistant-message {
                    background-color: #4a4a4a;
                    margin-right: 20px;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Chat history container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.messages:
            message_class = "user-message" if message["role"] == "user" else "assistant-message"
            st.markdown(
                f'<div class="message {message_class}">{message["content"]}</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Form to capture user input
        with st.form(key='chat_form', clear_on_submit=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                user_input = st.text_input("Ask anything...", key="user_input")
            with col2:
                submit_button = st.form_submit_button("Send")

            if submit_button and user_input:
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": user_input})

                # Create a placeholder for loading animation
                with st.spinner("Thinking..."):
                    try:
                        # Generate assistant response
                        chain = get_qa_chain()
                        response = chain(user_input)
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": response["result"]
                        })
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                
                st.rerun()

        # Add JavaScript to auto-scroll to bottom when new messages are added
        if st.session_state.messages:
            st.markdown("""
                <script>
                    var chatContainer = document.querySelector('.chat-container');
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                </script>
                """, unsafe_allow_html=True)

def main():
    # Title
    st.title("🌾 FarmEasy Dashboard")
    
    # Sidebar with state selection
    with st.sidebar:
        st.title("Dashboard Controls")
        
        states = ["Select", "California", "Texas", "Iowa", "Illinois", "Nebraska"]
        st.session_state.source_state = st.selectbox("Source State", states, index=0)
        st.session_state.destination_state = st.selectbox("Destination State", states, index=1)

        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()

    data = load_mock_data()

    col1, col2 = st.columns([2, 1])
    with col1:
        create_maps_section()
    with col2:
        create_chat_section()

if __name__ == "__main__":
    main()