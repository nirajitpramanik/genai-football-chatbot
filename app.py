import streamlit as st
import os
from dotenv import load_dotenv
from chatbot.data_fetcher import FootballDataFetcher
from chatbot.intent_processor import IntentProcessor
from chatbot.response_generator import ResponseGenerator
from chatbot.utils import setup_logging
import logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Football GenAI Chatbot",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_chatbot():
    """Initialize chatbot components"""
    try:
        data_fetcher = FootballDataFetcher()
        intent_processor = IntentProcessor()
        response_generator = ResponseGenerator()
        return data_fetcher, intent_processor, response_generator
    except Exception as e:
        logger.error(f"Error initializing chatbot: {e}")
        st.error("Failed to initialize chatbot components")
        return None, None, None

def main():
    # Title and description
    st.title("⚽ Football GenAI Chatbot")
    st.markdown("Ask me anything about football players, teams, transfers, and statistics!")
    
    # Initialize session state
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! I'm your football assistant. Ask me about players, teams, transfers, or statistics!"
        })
    
    if 'conversation_context' not in st.session_state:
        st.session_state.conversation_context = {}
    
    # Initialize chatbot components
    data_fetcher, intent_processor, response_generator = init_chatbot()
    
    if not all([data_fetcher, intent_processor, response_generator]):
        st.error("Chatbot initialization failed. Please check your configuration.")
        return
    
    # Sidebar
    with st.sidebar:
        st.header("Quick Actions")
        
        # Popular players search
        st.subheader("🌟 Popular Players")
        popular_players = ["Lionel Messi", "Cristiano Ronaldo", "Kylian Mbappé", "Erling Haaland"]
        for player in popular_players:
            if st.button(f"Tell me about {player}", key=f"popular_{player}"):
                user_input = f"Tell me about {player}"
                process_user_input(user_input, data_fetcher, intent_processor, response_generator)
        
        # Popular teams
        st.subheader("🏆 Popular Teams")  
        popular_teams = ["Real Madrid", "Barcelona", "Manchester City", "Bayern Munich"]
        for team in popular_teams:
            if st.button(f"Tell me about {team}", key=f"team_{team}"):
                user_input = f"Tell me about {team}"
                process_user_input(user_input, data_fetcher, intent_processor, response_generator)
        
        # Clear conversation
        if st.button("🗑️ Clear Conversation"):
            st.session_state.messages = [st.session_state.messages[0]]  # Keep welcome message
            st.session_state.conversation_context = {}
            st.rerun()
        
        # Settings
        st.subheader("⚙️ Settings")
        response_style = st.selectbox(
            "Response Style",
            ["Casual", "Professional", "Detailed"],
            key="response_style"
        )
        
        # Statistics
        st.subheader("📊 Session Stats")
        st.metric("Messages", len(st.session_state.messages) - 1)  # Exclude welcome message
    
    # Main chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask me about football..."):
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Process user input and generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = process_user_input(
                        prompt, data_fetcher, intent_processor, response_generator
                    )
                    st.markdown(response)
            
            # Add assistant response to chat
            st.session_state.messages.append({"role": "assistant", "content": response})

def process_user_input(user_input, data_fetcher, intent_processor, response_generator):
    """Process user input and return response"""
    try:
        # Step 1: Process intent and extract entities
        intent_result = intent_processor.process(user_input, st.session_state.conversation_context)
        
        # Step 2: Fetch relevant data
        data = None
        if intent_result['intent'] in ['player_info', 'player_stats']:
            if intent_result['entities'].get('player_name'):
                data = data_fetcher.get_player_info(intent_result['entities']['player_name'])
        elif intent_result['intent'] in ['team_info', 'team_stats']:
            if intent_result['entities'].get('team_name'):
                data = data_fetcher.get_team_info(intent_result['entities']['team_name'])
        elif intent_result['intent'] == 'transfers':
            if intent_result['entities'].get('player_name'):
                data = data_fetcher.get_player_transfers(intent_result['entities']['player_name'])
        elif intent_result['intent'] == 'league_table':
            if intent_result['entities'].get('league_name'):
                data = data_fetcher.get_league_table(intent_result['entities']['league_name'])
        
        # Step 3: Generate response
        response = response_generator.generate_response(
            intent_result, 
            data, 
            user_input,
            st.session_state.conversation_context,
            style=st.session_state.get('response_style', 'Casual')
        )
        
        # Step 4: Update conversation context
        st.session_state.conversation_context.update({
            'last_intent': intent_result['intent'],
            'last_entities': intent_result['entities'],
            'last_data': data
        })
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing user input: {e}")
        return "I'm sorry, I encountered an error processing your request. Please try rephrasing your question."

if __name__ == "__main__":
    main()