import logging
import os
from datetime import datetime
from typing import Dict, Any
import json

def setup_logging():
    """Setup logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(f'logs/chatbot_{datetime.now().strftime("%Y%m%d")}.log'),
            logging.StreamHandler()
        ]
    )

def format_currency(amount: str) -> str:
    """Format currency values"""
    if not amount or amount == 'Unknown':
        return 'Not disclosed'
    
    # Handle different currency formats
    if '€' in amount:
        return amount
    elif '$' in amount:
        return amount
    elif 'm' in amount.lower():
        return f"€{amount}"
    else:
        return f"€{amount}"

def format_date(date_str: str) -> str:
    """Format date strings for better readability"""
    if not date_str or date_str == 'Unknown':
        return 'Unknown date'
    
    try:
        # Try to parse and reformat the date
        # This will depend on the API's date format
        return date_str
    except:
        return date_str

def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return ''
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters that might cause issues
    text = text.replace('\n', ' ').replace('\r', ' ')
    
    return text.strip()

def extract_numbers(text: str) -> list:
    """Extract numbers from text"""
    import re
    return re.findall(r'\d+(?:\.\d+)?', text)

def is_valid_player_name(name: str) -> bool:
    """Validate if a string could be a player name"""
    if not name or len(name.strip()) < 2:
        return False
    
    # Check for reasonable length
    if len(name) > 50:
        return False
    
    # Should contain only letters, spaces, hyphens, and apostrophes
    import re
    if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
        return False
    
    return True

def is_valid_team_name(name: str) -> bool:
    """Validate if a string could be a team name"""
    if not name or len(name.strip()) < 2:
        return False
    
    # Check for reasonable length
    if len(name) > 100:
        return False
    
    return True

def safe_get(data: Dict, *keys, default=None) -> Any:
    """Safely get nested dictionary values"""
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current

def format_list(items: list, conjunction: str = 'and') -> str:
    """Format a list into a readable string"""
    if not items:
        return ''
    
    if len(items) == 1:
        return str(items[0])
    
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    
    return f"{', '.join(str(item) for item in items[:-1])}, {conjunction} {items[-1]}"

def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length-3] + '...'

def parse_position(position: str) -> str:
    """Parse and standardize player positions"""
    if not position:
        return 'Unknown'
    
    position_mapping = {
        'gk': 'Goalkeeper',
        'goalkeeper': 'Goalkeeper',
        'cb': 'Centre-Back',
        'centre-back': 'Centre-Back',
        'lb': 'Left-Back',
        'left-back': 'Left-Back',
        'rb': 'Right-Back',
        'right-back': 'Right-Back',
        'dm': 'Defensive Midfielder',
        'cdm': 'Defensive Midfielder',
        'cm': 'Central Midfielder',
        'am': 'Attacking Midfielder',
        'cam': 'Attacking Midfielder',
        'lm': 'Left Midfielder',
        'rm': 'Right Midfielder',
        'lw': 'Left Winger',
        'rw': 'Right Winger',
        'cf': 'Centre-Forward',
        'st': 'Striker',
        'striker': 'Striker'
    }
    
    position_lower = position.lower().strip()
    return position_mapping.get(position_lower, position.title())

def calculate_age(birth_date: str) -> int:
    """Calculate age from birth date"""
    try:
        from datetime import datetime
        birth = datetime.strptime(birth_date, '%Y-%m-%d')
        today = datetime.now()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        return age
    except:
        return 0

def format_transfer_fee(fee: str) -> str:
    """Format transfer fee for display"""
    if not fee or fee.lower() in ['free', 'loan', 'unknown']:
        return fee.title() if fee else 'Undisclosed'
    
    # Add currency symbol if missing
    if fee.isdigit():
        return f'€{fee}M'
    
    return fee

def get_flag_emoji(country: str) -> str:
    """Get flag emoji for country (basic implementation)"""
    flag_mapping = {
        'argentina': '🇦🇷',
        'brazil': '🇧🇷',
        'france': '🇫🇷',
        'spain': '🇪🇸',
        'portugal': '🇵🇹',
        'england': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
        'germany': '🇩🇪',
        'italy': '🇮🇹',
        'netherlands': '🇳🇱',
        'belgium': '🇧🇪'
    }
    
    return flag_mapping.get(country.lower(), '🌍')

def log_interaction(user_input: str, intent: str, entities: Dict, response_length: int):
    """Log user interactions for analytics"""
    logger = logging.getLogger('interaction')
    
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'user_input': user_input,
        'intent': intent,
        'entities': entities,
        'response_length': response_length
    }
    
    logger.info(f"Interaction: {json.dumps(log_data)}")

def validate_api_response(response: Dict) -> bool:
    """Validate API response structure"""
    if not isinstance(response, dict):
        return False
    
    # Basic validation - can be extended based on API structure
    return True

def handle_rate_limit(func):
    """Decorator to handle API rate limiting"""
    import time
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if 'rate limit' in str(e).lower() and attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                raise e
        
        return None
    
    return wrapper

def create_quick_replies(intent: str, entities: Dict) -> list:
    """Generate quick reply suggestions based on context"""
    quick_replies = []
    
    if intent == 'player_info' and entities.get('player_name'):
        player = entities['player_name']
        quick_replies = [
            f"{player} stats",
            f"{player} transfers", 
            f"{player} market value"
        ]
    elif intent == 'team_info' and entities.get('team_name'):
        team = entities['team_name']
        quick_replies = [
            f"{team} squad",
            f"{team} recent transfers",
            f"{team} league position"
        ]
    else:
        # Default suggestions
        quick_replies = [
            "Tell me about Messi",
            "Real Madrid info", 
            "Recent transfers"
        ]
    
    return quick_replies[:3]  # Limit to 3 suggestions