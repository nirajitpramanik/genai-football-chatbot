import re
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class IntentProcessor:
    """Processes user questions to understand intent and extract entities"""
    
    def __init__(self):
        # Define intent patterns with proper capture groups where needed
        self.intent_patterns = {
            'player_info': [
                r'tell me about (.+)',
                r'who is (.+)',
                r'information about (.+)',
                r'details about (.+)',
                r'(.+) profile',
                r'(.+) bio',
                r'(.+) career'
            ],
            'player_stats': [
                r'(.+) stats',
                r'(.+) statistics',
                r'(.+) goals',
                r'(.+) assists',
                r'(.+) performance',
                r'how many goals (.+)',
                r'(.+) season stats'
            ],
            'team_info': [
                r'tell me about (.+) team',
                r'(.+) club info',
                r'(.+) team details',
                r'information about (.+) fc',
                r'(.+) football club'
            ],
            'team_stats': [
                r'(.+) team stats',
                r'(.+) club statistics',
                r'(.+) performance this season',
                r'how is (.+) doing'
            ],
            'transfers': [
                r'(.+) transfers',
                r'(.+) transfer history',
                r'where did (.+) play',
                r'(.+) clubs',
                r'(.+) career moves',
                r'who bought (.+)',
                r'(.+) transfer news'
            ],
            'market_value': [
                r'(.+) market value',
                r'(.+) worth',
                r'(.+) price',
                r'(.+) value',
                r'how much is (.+) worth'
            ],
            'comparison': [
                r'(.+) vs (.+)',
                r'compare (.+) and (.+)',
                r'(.+) or (.+)',
                r'who is better (.+) or (.+)'
            ],
            'league_table': [
                r'(.+) table',
                r'(.+) standings',
                r'(.+) league table',
                r'(.+) position',
                r'who is top of (.+)',
                r'(.+) league standings'
            ],
            # These intents don't need capture groups - no specific entities to extract
            'recent_transfers': [
                r'\brecent transfers?\b',
                r'\blatest transfers?\b',
                r'\btransfer news\b',
                r'who (?:has )?moved recently\??',
                r'who transferred recently\??',
                r'\bnew signings?\b',
                r'\brecent signings?\b',
                r'\blatest moves?\b'
            ],
            'greeting': [
                r'\bhello\b',
                r'\bhi\b',
                r'\bhey\b',
                r'good morning',
                r'good afternoon',
                r'good evening',
                r'greetings'
            ],
            'help': [
                r'\bhelp\b',
                r'what can you do\??',
                r'how do(?:es)? (?:this|you) work\??',
                r'(?:show me )?(?:the )?commands\??',
                r'(?:what are my )?options\??',
                r'what are your capabilities\??',
                r'how to use (?:this|you)\??'
            ]
        }
        
        # Define which intents expect player names (have capture groups)
        self.player_name_intents = {
            'player_info', 'player_stats', 'transfers', 'market_value'
        }
        
        # Define which intents expect team names (have capture groups)
        self.team_name_intents = {
            'team_info', 'team_stats'
        }
        
        # Define which intents expect league names (have capture groups)
        self.league_name_intents = {
            'league_table'
        }
        
        # Common football entities
        self.team_keywords = [
            'fc', 'football club', 'soccer club', 'club', 'team',
            'real madrid', 'barcelona', 'manchester united', 'manchester city',
            'liverpool', 'chelsea', 'arsenal', 'tottenham', 'bayern munich',
            'psg', 'juventus', 'ac milan', 'inter milan', 'atletico madrid',
            'borussia dortmund', 'ajax', 'porto', 'benfica'
        ]
        
        self.league_keywords = [
            'premier league', 'la liga', 'bundesliga', 'serie a', 'ligue 1',
            'champions league', 'europa league', 'world cup', 'euros',
            'uefa', 'fifa', 'copa america', 'conference league'
        ]
        
        self.position_keywords = [
            'goalkeeper', 'defender', 'midfielder', 'forward', 'striker',
            'winger', 'centre-back', 'center-back', 'full-back', 'fullback',
            'attacking midfielder', 'defensive midfielder', 'left-back',
            'right-back', 'centre-forward', 'center-forward'
        ]
    
    def process(self, user_input: str, context: Dict = None) -> Dict:
        """Main processing function with comprehensive error handling"""
        try:
            if not user_input or not isinstance(user_input, str):
                logger.warning(f"Invalid input received: {user_input}")
                return self._get_default_response("Invalid input")
            
            user_input = user_input.lower().strip()
            
            if not user_input:
                logger.warning("Empty input after processing")
                return self._get_default_response("Empty input")
            
            # Extract intent
            intent = self._extract_intent(user_input)
            logger.debug(f"Extracted intent: {intent}")
            
            # Extract entities
            entities = self._extract_entities(user_input, intent)
            logger.debug(f"Extracted entities: {entities}")
            
            # Apply context if available
            if context and isinstance(context, dict):
                entities = self._apply_context(entities, context)
            
            # Calculate confidence
            confidence = self._calculate_confidence(intent, entities)
            
            result = {
                'intent': intent,
                'entities': entities,
                'original_text': user_input,
                'confidence': confidence,
                'success': True
            }
            
            logger.debug(f"Processing result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}", exc_info=True)
            return self._get_error_response(str(e))
    
    def _get_default_response(self, reason: str) -> Dict:
        """Get default response for invalid inputs"""
        return {
            'intent': 'general_question',
            'entities': {},
            'original_text': '',
            'confidence': 0.0,
            'success': False,
            'error': reason
        }
    
    def _get_error_response(self, error_msg: str) -> Dict:
        """Get error response"""
        return {
            'intent': 'error',
            'entities': {},
            'original_text': '',
            'confidence': 0.0,
            'success': False,
            'error': error_msg
        }
    
    def _extract_intent(self, text: str) -> str:
        """Extract intent from user input with error handling"""
        try:
            logger.debug(f"Processing text for intent: '{text}'")
            
            for intent, patterns in self.intent_patterns.items():
                for pattern in patterns:
                    try:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            logger.debug(f"Matched intent '{intent}' with pattern '{pattern}'")
                            return intent
                    except re.error as e:
                        logger.warning(f"Regex error in pattern '{pattern}': {str(e)}")
                        continue
            
            logger.debug("No intent matched, returning 'general_question'")
            return 'general_question'
            
        except Exception as e:
            logger.error(f"Error in intent extraction: {str(e)}")
            return 'general_question'
    
    def _extract_entities(self, text: str, intent: str) -> Dict:
        """Extract entities from user input with error handling"""
        entities = {}
        
        try:
            # Extract player names (only for relevant intents)
            if intent in self.player_name_intents:
                player_match = self._extract_player_name(text, intent)
                if player_match:
                    entities['player_name'] = player_match
            
            # Extract team names
            team_match = self._extract_team_name(text, intent)
            if team_match:
                entities['team_name'] = team_match
            
            # Extract league names
            league_match = self._extract_league_name(text, intent)
            if league_match:
                entities['league_name'] = league_match
            
            # Extract positions
            position_match = self._extract_position(text)
            if position_match:
                entities['position'] = position_match
            
            # Extract numbers (for stats, years, etc.)
            try:
                numbers = re.findall(r'\b\d+\b', text)
                if numbers:
                    entities['numbers'] = numbers
            except re.error as e:
                logger.warning(f"Error extracting numbers: {str(e)}")
            
            # Extract comparison entities for comparison intent
            if intent == 'comparison':
                comparison_entities = self._extract_comparison_entities(text)
                if comparison_entities:
                    entities.update(comparison_entities)
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
        
        return entities
    
    def _extract_player_name(self, text: str, intent: str) -> Optional[str]:
        """Extract player name from text with proper error handling"""
        try:
            # Only process intents that expect player names
            if intent not in self.player_name_intents:
                return None
            
            # Try to match against intent patterns first
            for pattern in self.intent_patterns.get(intent, []):
                try:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match:
                        # Check if pattern has capture groups
                        if match.groups():
                            potential_name = match.group(1).strip()
                            # Clean up the name
                            potential_name = self._clean_name(potential_name)
                            if self._is_likely_player_name(potential_name):
                                return potential_name
                except (IndexError, AttributeError) as e:
                    logger.debug(f"Pattern '{pattern}' doesn't have capture group or other error: {str(e)}")
                    continue
                except re.error as e:
                    logger.warning(f"Regex error with pattern '{pattern}': {str(e)}")
                    continue
            
            # Fallback: look for capitalized words that could be names
            return self._extract_name_fallback(text)
            
        except Exception as e:
            logger.error(f"Error extracting player name: {str(e)}")
            return None
    
    def _extract_name_fallback(self, text: str) -> Optional[str]:
        """Fallback method to extract names from text"""
        try:
            words = text.split()
            potential_names = []
            
            for i, word in enumerate(words):
                if word.lower() not in ['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with']:
                    # Look for sequences of 2-3 words that could be names
                    if i < len(words) - 1:
                        two_word = f"{word} {words[i+1]}"
                        if self._is_likely_player_name(two_word):
                            potential_names.append(two_word)
                    
                    if i < len(words) - 2:
                        three_word = f"{word} {words[i+1]} {words[i+2]}"
                        if self._is_likely_player_name(three_word):
                            potential_names.append(three_word)
            
            return potential_names[0] if potential_names else None
            
        except Exception as e:
            logger.error(f"Error in name fallback extraction: {str(e)}")
            return None
    
    def _extract_team_name(self, text: str, intent: str) -> Optional[str]:
        """Extract team name from text with error handling"""
        try:
            # First check for known team names
            known_teams = [
                'real madrid', 'barcelona', 'manchester united', 'manchester city',
                'liverpool', 'chelsea', 'arsenal', 'tottenham', 'bayern munich',
                'psg', 'juventus', 'ac milan', 'inter milan', 'atletico madrid',
                'borussia dortmund', 'ajax', 'porto', 'benfica'
            ]
            
            for team in known_teams:
                if team in text.lower():
                    return team.title()
            
            # Then look for team keywords
            for keyword in self.team_keywords:
                if keyword in text.lower():
                    # Try to extract the team name around the keyword
                    try:
                        pattern = rf'(\w+(?:\s+\w+)*)\s+{re.escape(keyword)}'
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match:
                            return match.group(1).strip().title()
                    except re.error as e:
                        logger.warning(f"Regex error extracting team name: {str(e)}")
                        continue
            
            # For team-related intents, try to extract from patterns
            if intent in self.team_name_intents:
                for pattern in self.intent_patterns.get(intent, []):
                    try:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match and match.groups():
                            potential_team = self._clean_name(match.group(1))
                            if self._is_likely_team_name(potential_team):
                                return potential_team
                    except (IndexError, re.error) as e:
                        continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting team name: {str(e)}")
            return None
    
    def _extract_league_name(self, text: str, intent: str) -> Optional[str]:
        """Extract league name from text with error handling"""
        try:
            for league in self.league_keywords:
                if league in text.lower():
                    return league.title()
            
            # For league-related intents, try to extract from patterns
            if intent in self.league_name_intents:
                for pattern in self.intent_patterns.get(intent, []):
                    try:
                        match = re.search(pattern, text, re.IGNORECASE)
                        if match and match.groups():
                            potential_league = self._clean_name(match.group(1))
                            if self._is_likely_league_name(potential_league):
                                return potential_league
                    except (IndexError, re.error) as e:
                        continue
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting league name: {str(e)}")
            return None
    
    def _extract_position(self, text: str) -> Optional[str]:
        """Extract player position from text with error handling"""
        try:
            for position in self.position_keywords:
                if position in text.lower():
                    return position.title()
            return None
        except Exception as e:
            logger.error(f"Error extracting position: {str(e)}")
            return None
    
    def _extract_comparison_entities(self, text: str) -> Dict:
        """Extract entities for comparison queries"""
        try:
            entities = {}
            
            # Try to extract two entities being compared
            comparison_patterns = [
                r'(.+) vs (.+)',
                r'compare (.+) and (.+)',
                r'(.+) or (.+)',
                r'who is better (.+) or (.+)'
            ]
            
            for pattern in comparison_patterns:
                try:
                    match = re.search(pattern, text, re.IGNORECASE)
                    if match and len(match.groups()) >= 2:
                        entity1 = self._clean_name(match.group(1))
                        entity2 = self._clean_name(match.group(2))
                        
                        if entity1 and entity2:
                            entities['entity1'] = entity1
                            entities['entity2'] = entity2
                            break
                except (IndexError, re.error) as e:
                    continue
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting comparison entities: {str(e)}")
            return {}
    
    def _clean_name(self, name: str) -> str:
        """Clean up extracted name with error handling"""
        try:
            if not name:
                return ""
            
            # Remove common words that aren't part of names
            stop_words = ['about', 'info', 'information', 'details', 'stats', 'statistics', 'the']
            words = name.split()
            cleaned_words = [word for word in words if word.lower() not in stop_words]
            return ' '.join(cleaned_words).title()
            
        except Exception as e:
            logger.error(f"Error cleaning name: {str(e)}")
            return name if isinstance(name, str) else ""
    
    def _is_likely_player_name(self, name: str) -> bool:
        """Check if extracted text is likely a player name"""
        try:
            if not name or not isinstance(name, str) or len(name.strip()) < 2:
                return False
            
            # Check if it contains only valid characters
            if not re.match(r'^[a-zA-Z\s\-\.\'\u00C0-\u017F]+$', name):
                return False
            
            # Check word count (player names are usually 1-4 words)
            words = name.split()
            if len(words) > 4 or len(words) < 1:
                return False
            
            # Check if all words are too short
            if all(len(word) < 2 for word in words):
                return False
            
            # Check against common non-name words
            non_name_words = ['stats', 'info', 'about', 'player', 'team', 'club', 'season', 'football', 'soccer']
            if any(word.lower() in non_name_words for word in words):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking if likely player name: {str(e)}")
            return False
    
    def _is_likely_team_name(self, name: str) -> bool:
        """Check if extracted text is likely a team name"""
        try:
            if not name or not isinstance(name, str) or len(name.strip()) < 2:
                return False
            
            words = name.split()
            if len(words) > 5:
                return False
            
            # Common team name indicators
            team_indicators = ['fc', 'club', 'united', 'city', 'real', 'athletic']
            if any(indicator in name.lower() for indicator in team_indicators):
                return True
            
            # Check if it's a known team
            if name.lower() in [team.lower() for team in self.team_keywords]:
                return True
            
            return len(words) <= 3  # Most team names are 1-3 words
            
        except Exception as e:
            logger.error(f"Error checking if likely team name: {str(e)}")
            return False
    
    def _is_likely_league_name(self, name: str) -> bool:
        """Check if extracted text is likely a league name"""
        try:
            if not name or not isinstance(name, str):
                return False
            
            league_indicators = ['league', 'cup', 'championship', 'serie', 'bundesliga', 'liga']
            return any(indicator in name.lower() for indicator in league_indicators)
            
        except Exception as e:
            logger.error(f"Error checking if likely league name: {str(e)}")
            return False
    
    def _apply_context(self, entities: Dict, context: Dict) -> Dict:
        """Apply conversation context to entities with error handling"""
        try:
            if not isinstance(context, dict) or not isinstance(entities, dict):
                return entities
            
            # If no player name found but we have context from previous conversation
            if not entities.get('player_name') and context.get('last_entities', {}).get('player_name'):
                # Check if the current question could be about the same player
                if context.get('last_intent') in ['player_info', 'player_stats', 'transfers', 'market_value']:
                    entities['player_name'] = context['last_entities']['player_name']
            
            # Similar logic for teams and leagues
            if not entities.get('team_name') and context.get('last_entities', {}).get('team_name'):
                if context.get('last_intent') in ['team_info', 'team_stats']:
                    entities['team_name'] = context['last_entities']['team_name']
            
            if not entities.get('league_name') and context.get('last_entities', {}).get('league_name'):
                if context.get('last_intent') in ['league_table']:
                    entities['league_name'] = context['last_entities']['league_name']
            
            return entities
            
        except Exception as e:
            logger.error(f"Error applying context: {str(e)}")
            return entities
    
    def _calculate_confidence(self, intent: str, entities: Dict) -> float:
        """Calculate confidence score for the intent and entity extraction"""
        try:
            confidence = 0.5  # Base confidence
            
            # Boost confidence if we found relevant entities
            if intent in ['player_info', 'player_stats', 'transfers', 'market_value'] and entities.get('player_name'):
                confidence += 0.3
            elif intent in ['team_info', 'team_stats'] and entities.get('team_name'):
                confidence += 0.3
            elif intent == 'league_table' and entities.get('league_name'):
                confidence += 0.3
            elif intent == 'comparison' and entities.get('entity1') and entities.get('entity2'):
                confidence += 0.3
            
            # Boost for specific intents that don't need entities
            if intent in ['greeting', 'help', 'recent_transfers']:
                confidence += 0.4
            
            # Cap at 1.0
            return min(confidence, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {str(e)}")
            return 0.3  # Default low confidence
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intents"""
        try:
            return list(self.intent_patterns.keys())
        except Exception as e:
            logger.error(f"Error getting supported intents: {str(e)}")
            return []
    
    def add_custom_pattern(self, intent: str, pattern: str) -> bool:
        """Add custom pattern for intent recognition with validation"""
        try:
            if not intent or not pattern:
                logger.warning("Intent and pattern must be non-empty")
                return False
            
            # Validate regex pattern
            try:
                re.compile(pattern)
            except re.error as e:
                logger.error(f"Invalid regex pattern '{pattern}': {str(e)}")
                return False
            
            if intent not in self.intent_patterns:
                self.intent_patterns[intent] = []
            
            self.intent_patterns[intent].append(pattern)
            logger.info(f"Added custom pattern '{pattern}' for intent '{intent}'")
            return True
            
        except Exception as e:
            logger.error(f"Error adding custom pattern: {str(e)}")
            return False
    
    def validate_input(self, user_input: str) -> Tuple[bool, str]:
        """Validate user input"""
        try:
            if not user_input:
                return False, "Input is empty"
            
            if not isinstance(user_input, str):
                return False, "Input must be a string"
            
            if len(user_input.strip()) == 0:
                return False, "Input contains only whitespace"
            
            if len(user_input) > 1000:  # Reasonable limit
                return False, "Input is too long"
            
            return True, "Valid input"
            
        except Exception as e:
            logger.error(f"Error validating input: {str(e)}")
            return False, f"Validation error: {str(e)}"