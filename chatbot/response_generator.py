import os
import requests
import json
from typing import Dict, List, Optional, Any
import logging

import streamlit as st

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Generates natural language responses using Google Gemini API and templates"""
    
    def __init__(self):
        # Google Gemini API setup
        self.gemini_api_key = st.secrets["GEMINI_API_KEY"] #os.getenv("GEMINI_API_KEY")
        self.gemini_model = "gemini-2.0-flash"  # Free tier model
        self.gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent"
        
        self.ai_available = bool(self.gemini_api_key)
        
        # Response templates for different intents (keeping your existing templates)
        self.templates = {
            'player_info': self._get_player_info_template,
            'player_stats': self._get_player_stats_template,
            'team_info': self._get_team_info_template,
            'transfers': self._get_transfers_template,
            'market_value': self._get_market_value_template,
            'greeting': self._get_greeting_template,
            'help': self._get_help_template,
            'league_table': self._get_league_table_template,
            'comparison': self._get_comparison_template,
            'no_data': self._get_no_data_template
        }
    
    def generate_response(self, intent_result: Dict, data: Any, 
                         original_question: str, context: Dict = None, 
                         style: str = "Casual") -> str:
        """Main response generation function"""
        
        intent = intent_result['intent']
        entities = intent_result['entities']
        
        # If we have Gemini API available, use it for complex responses
        if self.ai_available and intent not in ['greeting', 'help']:
            try:
                return self._generate_gemini_response(
                    intent_result, data, original_question, context, style
                )
            except Exception as e:
                logger.warning(f"Gemini API failed, falling back to templates: {e}")
        
        # Fallback to template-based responses
        return self._generate_template_response(intent, entities, data, style)
    
    def _generate_gemini_response(self, intent_result: Dict, data: Any, 
                                original_question: str, context: Dict, style: str) -> str:
        """Generate response using Google Gemini API"""
        
        # Prepare system instructions based on style
        system_instructions = {
            "Casual": "You are a friendly football expert who talks casually and uses emojis. Keep responses conversational, engaging, and around 2-3 paragraphs. Use a warm, enthusiastic tone.",
            "Professional": "You are a professional football analyst. Provide detailed, accurate information in a formal tone. Structure your response clearly and professionally.",
            "Detailed": "You are a comprehensive football encyclopedia. Provide extensive details and background information. Include context and comprehensive analysis."
        }
        
        system_instruction = system_instructions.get(style, system_instructions["Casual"])
        
        # Prepare the prompt
        prompt = f"""System: {system_instruction}

User Question: {original_question}
Intent: {intent_result['intent']}
Entities: {intent_result['entities']}

Available Data: {json.dumps(data, indent=2) if data else "No specific data available"}

Please provide a helpful response about football/soccer based on the question and data provided. 
If the data is incomplete or missing, acknowledge it and provide what general information you can.
Keep the response concise but informative (2-3 paragraphs max unless detailed style is requested).
Focus on being helpful and accurate."""

        # Prepare the request payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 300,
                "stopSequences": []
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        # Make the API request
        headers = {
            "Content-Type": "application/json",
        }
        
        params = {
            "key": self.gemini_api_key
        }
        
        response = requests.post(
            self.gemini_url, 
            headers=headers, 
            params=params,
            json=payload, 
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract the generated text from Gemini response
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    if len(parts) > 0 and 'text' in parts[0]:
                        return parts[0]['text'].strip()
                        
            # Handle case where response structure is different
            logger.warning(f"Unexpected Gemini response structure: {result}")
            raise Exception("Unexpected response format from Gemini")
        
        else:
            error_msg = f"Gemini API error: {response.status_code}"
            if response.text:
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('error', {}).get('message', response.text)}"
                except:
                    error_msg += f" - {response.text}"
            
            logger.error(error_msg)
            raise Exception(error_msg)
    
    def _generate_template_response(self, intent: str, entities: Dict, 
                                  data: Any, style: str) -> str:
        """Generate response using templates (your existing code)"""
        
        template_func = self.templates.get(intent, self.templates['no_data'])
        return template_func(entities, data, style)
    
    # All your existing template methods remain the same
    def _get_player_info_template(self, entities: Dict, data: Any, style: str) -> str:
        """Template for player information"""
        player_name = entities.get('player_name', 'the player')
        
        if not data:
            return f"I couldn't find information about {player_name}. Could you check the spelling or try a different player name?"
        
        # Extract key information
        name = data.get('name', player_name)
        age = data.get('age', 'Unknown')
        position = data.get('position', 'Unknown')
        club = data.get('club', {}).get('name', 'Unknown')
        nationality = data.get('nationality', 'Unknown')
        market_value = data.get('marketValue', 'Unknown')
        
        if style == "Casual":
            response = f"⚽ **{name}**\n\n"
            response += f"Hey! {name} is a {age}-year-old {position} who currently plays for {club}. "
            response += f"He's from {nationality}. "
            if market_value != 'Unknown':
                response += f"His current market value is around {market_value}. "
            response += "Pretty cool player! 🌟"
            
        elif style == "Professional":
            response = f"**Player Profile: {name}**\n\n"
            response += f"**Age:** {age}\n"
            response += f"**Position:** {position}\n"
            response += f"**Current Club:** {club}\n"
            response += f"**Nationality:** {nationality}\n"
            if market_value != 'Unknown':
                response += f"**Market Value:** {market_value}\n"
            
        else:  # Detailed
            response = f"**Comprehensive Profile: {name}**\n\n"
            response += f"This {age}-year-old {position} represents {club} and the {nationality} national team. "
            if market_value != 'Unknown':
                response += f"With a current market valuation of {market_value}, "
            response += f"{name} has established himself as a key player in modern football. "
            response += "His career trajectory shows consistent development and professional growth."
        
        return response
    
    def _get_player_stats_template(self, entities: Dict, data: Any, style: str) -> str:
        """Template for player statistics"""
        player_name = entities.get('player_name', 'the player')
        
        if not data:
            return f"I couldn't find detailed statistics for {player_name} right now. The data might not be available or the player name might need to be spelled differently."
        
        # This would need to be adapted based on actual API response structure
        stats = data.get('stats', {})
        
        if style == "Casual":
            return f"📊 Here are some stats for {player_name}! Unfortunately, I need to check the API structure to show you the exact numbers. The data is there, but I need to format it properly! 🤔"
        else:
            return f"**Statistics for {player_name}**\n\nI have the statistical data, but need to properly parse the API response structure to display meaningful statistics."
    
    def _get_team_info_template(self, entities: Dict, data: Any, style: str) -> str:
        """Template for team information"""
        team_name = entities.get('team_name', 'the team')
        
        if not data:
            return f"I couldn't find information about {team_name}. Please check the team name spelling or try a different team."
        
        name = data.get('name', team_name)
        league = data.get('league', {}).get('name', 'Unknown League')
        founded = data.get('founded', 'Unknown')
        stadium = data.get('stadium', 'Unknown')
        
        if style == "Casual":
            response = f"🏟️ **{name}**\n\n"
            response += f"{name} plays in the {league}. "
            if founded != 'Unknown':
                response += f"They were founded in {founded}. "
            if stadium != 'Unknown':
                response += f"Their home stadium is {stadium}. "
            response += "Great club! ⚽"
        else:
            response = f"**Club Information: {name}**\n\n"
            response += f"**League:** {league}\n"
            response += f"**Founded:** {founded}\n"
            response += f"**Stadium:** {stadium}\n"
        
        return response
    
    def _get_transfers_template(self, entities: Dict, data: Any, style: str) -> str:
        """Template for transfer information"""
        player_name = entities.get('player_name', 'the player')
        
        if not data:
            return f"I couldn't find transfer information for {player_name}. This could be because the player hasn't had recent transfers or the name needs to be spelled differently."
        
        if style == "Casual":
            response = f"🔄 **Transfer History for {player_name}**\n\n"
            if isinstance(data, list) and len(data) > 0:
                response += f"Found {len(data)} transfer records! Here are the most recent ones:\n\n"
                for i, transfer in enumerate(data[:3]):  # Show top 3
                    from_club = transfer.get('from', {}).get('name', 'Unknown')
                    to_club = transfer.get('to', {}).get('name', 'Unknown') 
                    date = transfer.get('date', 'Unknown date')
                    response += f"• {from_club} → {to_club} ({date})\n"
            else:
                response += "No recent transfer data available."
        else:
            response = f"**Transfer History: {player_name}**\n\n"
            response += "Transfer records found, but need to properly format the data structure."
        
        return response
    
    def _get_market_value_template(self, entities: Dict, data: Any, style: str) -> str:
        """Template for market value information"""
        player_name = entities.get('player_name', 'the player')
        
        if not data:
            return f"I couldn't find market value information for {player_name}."
        
        return f"💰 Market value information for {player_name} - data structure needs to be formatted properly based on API response."
    
    def _get_greeting_template(self, entities: Dict, data: Any, style: str) -> str:
        """Template for greetings"""
        greetings = {
            "Casual": "Hey there! ⚽ I'm your football buddy! Ask me about any player, team, transfers, or stats you're curious about!",
            "Professional": "Hello! I'm your football information assistant. I can provide detailed information about players, teams, statistics, and transfers.",
            "Detailed": "Greetings! I'm a comprehensive football database assistant capable of providing extensive information about players, teams, leagues, transfer histories, market valuations, and statistical analyses."
        }
        return greetings.get(style, greetings["Casual"])
    
    def _get_help_template(self, entities: Dict, data: Any, style: str) -> str:
        """Template for help information"""
        help_text = """🆘 **What I can help you with:**

**Player Information:**
- "Tell me about Lionel Messi"
- "Cristiano Ronaldo stats"
- "Kylian Mbappé transfers"

**Team Information:**
- "Tell me about Real Madrid"
- "Barcelona team info"
- "Manchester City squad"

**Other Queries:**
- "Recent transfers"
- "Premier League table"
- "Compare Messi and Ronaldo"

Just ask naturally - I'll understand! ⚽"""
        
        return help_text
    
    def _get_league_table_template(self, entities: Dict, data: Any, style: str) -> str:
        """Template for league table information"""
        league_name = entities.get('league_name', 'the league')
        
        if not data:
            return f"I couldn't find the current table for {league_name}. The league might not be available or the name needs to be adjusted."
        
        return f"📊 **{league_name} Table**\n\nI have the data but need to format it properly based on the API structure."
    
    def _get_comparison_template(self, entities: Dict, data: Any, style: str) -> str:
        """Template for player/team comparisons"""
        return "🆚 **Player Comparison**\n\nI can help compare players, but I need to fetch data for both players first. Try asking about each player individually, then I can help compare them!"
    
    def _get_no_data_template(self, entities: Dict, data: Any, style: str) -> str:
        """Template when no data is available"""
        return "I'm not sure how to help with that specific question. Try asking about:\n• Player information\n• Team details\n• Transfer history\n• Statistics\n\nOr just say 'help' for more options! ⚽"