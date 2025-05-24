import requests
import json
import time
import os
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class FootballDataFetcher:
    """Handles all football data retrieval from Transfermarkt API"""
    
    def __init__(self):
        self.base_url = "https://transfermarkt-api.fly.dev"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Football-Chatbot/1.0',
            'Accept': 'application/json'
        })
        self.cache = {}
        self.cache_timeout = 3600  # 1 hour cache
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with error handling and caching"""
        cache_key = f"{endpoint}_{str(params)}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_timeout:
                return cached_data
        
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache the result
            self.cache[cache_key] = (data, time.time())
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return None
    
    def search_player(self, player_name: str) -> Optional[List[Dict]]:
        """Search for players by name"""
        data = self._make_request("/players/search", {"query": player_name})
        return data.get("results", []) if data else []
    
    def get_player_info(self, player_name: str) -> Optional[Dict]:
        """Get detailed player information"""
        # First search for the player
        players = self.search_player(player_name)
        if not players:
            return None
        
        # Get the first matching player
        player_id = players[0].get("id")
        if not player_id:
            return None
        
        # Get detailed player info
        player_data = self._make_request(f"/players/{player_id}")
        
        if player_data:
            # Enrich with search results data
            player_data.update(players[0])
        
        return player_data
    
    def get_player_transfers(self, player_name: str) -> Optional[List[Dict]]:
        """Get player transfer history"""
        # First get player info to get ID
        players = self.search_player(player_name)
        if not players:
            return None
        
        player_id = players[0].get("id")
        if not player_id:
            return None
        
        # Get transfer history
        transfers_data = self._make_request(f"/players/{player_id}/transfers")
        return transfers_data.get("transfers", []) if transfers_data else []
    
    def search_club(self, club_name: str) -> Optional[List[Dict]]:
        """Search for clubs by name"""
        data = self._make_request("/clubs/search", {"query": club_name})
        return data.get("results", []) if data else []
    
    def get_team_info(self, team_name: str) -> Optional[Dict]:
        """Get detailed team information"""
        clubs = self.search_club(team_name)
        if not clubs:
            return None
        
        club_id = clubs[0].get("id")
        if not club_id:
            return None
        
        # Get detailed club info
        club_data = self._make_request(f"/clubs/{club_id}")
        
        if club_data:
            # Enrich with search results data
            club_data.update(clubs[0])
        
        return club_data
    
    def get_team_players(self, team_name: str) -> Optional[List[Dict]]:
        """Get team's current squad"""
        clubs = self.search_club(team_name)
        if not clubs:
            return None
        
        club_id = clubs[0].get("id")
        if not club_id:
            return None
        
        players_data = self._make_request(f"/clubs/{club_id}/players")
        return players_data.get("players", []) if players_data else []
    
    def get_competitions(self) -> Optional[List[Dict]]:
        """Get list of available competitions"""
        data = self._make_request("/competitions")
        return data.get("competitions", []) if data else []
    
    def get_league_table(self, league_name: str) -> Optional[Dict]:
        """Get league table (this might need adjustment based on actual API structure)"""
        # This is a placeholder - you'll need to check the actual API documentation
        # for how to get league tables
        competitions = self.get_competitions()
        if not competitions:
            return None
        
        # Find matching competition
        matching_comp = None
        for comp in competitions:
            if league_name.lower() in comp.get("name", "").lower():
                matching_comp = comp
                break
        
        if not matching_comp:
            return None
        
        comp_id = matching_comp.get("id")
        if comp_id:
            table_data = self._make_request(f"/competitions/{comp_id}/tables")
            return table_data
        
        return None
    
    def get_player_market_value(self, player_name: str) -> Optional[Dict]:
        """Get player's market value history"""
        players = self.search_player(player_name)
        if not players:
            return None
        
        player_id = players[0].get("id")
        if not player_id:
            return None
        
        market_value_data = self._make_request(f"/players/{player_id}/market-value")
        return market_value_data if market_value_data else None
    
    def get_recent_transfers(self, limit: int = 10) -> Optional[List[Dict]]:
        """Get recent transfers (if available in API)"""
        # This endpoint might not exist - check API documentation
        data = self._make_request("/transfers/recent", {"limit": limit})
        return data.get("transfers", []) if data else []
    
    def clear_cache(self):
        """Clear the data cache"""
        self.cache.clear()
        logger.info("Data cache cleared")
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "cached_items": len(self.cache),
            "cache_timeout": self.cache_timeout
        }