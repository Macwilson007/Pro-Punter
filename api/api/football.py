import requests
import time
import json
from datetime import datetime, date
from typing import Optional
from app.config import settings

class APIFootball:
    def __init__(self):
        self.api_key = settings.API_FOOTBALL_KEY
        self.base_url = settings.API_BASE_URL.rstrip("/")
        self.header_name = settings.API_HEADER
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour
        
    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Make a request to API-Football v3 using path-based endpoints"""
        if not self.api_key:
            return {"error": "API key not configured"}
        
        params = params or {}
        
        # Build cache key
        cache_key = f"{endpoint}_{json.dumps(params, sort_keys=True)}"
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                return cached_data
        
        url = f"{self.base_url}/{endpoint}"
        headers = {self.header_name: self.api_key}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.cache[cache_key] = (data, time.time())
                return data
            else:
                return {"error": f"API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_fixtures(self, league_id: Optional[int] = None, season: Optional[int] = None,
                     from_date: Optional[str] = None, to_date: Optional[str] = None,
                     fixture_date: Optional[str] = None, timezone: str = "Africa/Lagos"):
        """Get fixtures/matches"""
        params = {}
        if league_id:
            params["league"] = league_id
        if season:
            params["season"] = season
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        if fixture_date:
            params["date"] = fixture_date
        if timezone:
            params["timezone"] = timezone
        return self._make_request("fixtures", params)
    
    def get_todays_fixtures(self, league_id: Optional[int] = None):
        """Get today's fixtures, optionally filtered by league"""
        today = date.today().isoformat()
        return self.get_fixtures(league_id=league_id, fixture_date=today)
    
    def get_predictions(self, fixture_id: int):
        """Get predictions for a specific fixture"""
        params = {"fixture": fixture_id}
        return self._make_request("predictions", params)
    
    def get_odds(self, fixture_id: Optional[int] = None, league_id: Optional[int] = None,
                 season: Optional[int] = None):
        """Get betting odds"""
        params = {}
        if fixture_id:
            params["fixture"] = fixture_id
        if league_id:
            params["league"] = league_id
        if season:
            params["season"] = season
        return self._make_request("odds", params)
    
    def get_leagues(self, country: Optional[str] = None):
        """Get available leagues"""
        params = {}
        if country:
            params["country"] = country
        return self._make_request("leagues", params)
    
    def get_teams(self, league_id: int, season: Optional[int] = None):
        """Get teams in a league"""
        params = {"league": league_id, "season": season or 2024}
        return self._make_request("teams", params)
    
    def get_sidelined(self, player_id: Optional[int] = None):
        """Get sidelined/injured players"""
        params = {}
        if player_id:
            params["player"] = player_id
        return self._make_request("sidelined", params)

    def get_team_last_fixtures(self, team_id: int, last: int = 5):
        """Get the last N fixtures for a team to calculate recent form"""
        params = {"team": team_id, "last": last}
        return self._make_request("fixtures", params)
    
    def get_countries(self):
        """Get available countries"""
        return self._make_request("countries")
    
    def get_standings(self, league_id: int, season: Optional[int] = None):
        """Get league standings"""
        params = {"league": league_id, "season": season or 2024}
        return self._make_request("standings", params)
    
    def check_status(self):
        """Check API status and remaining requests"""
        return self._make_request("status")

api_football = APIFootball()