"""
Centralized league mapping between:
- App league slugs (used in frontend/DB)
- Football-data.co.uk CSV codes (for historical data downloads)
- API-Football v3 league IDs (for live fixtures/odds)
"""

LEAGUE_MAP = {
    # Tier 1: High Predictability
    "premier-league": {
        "name": "Premier League",
        "country": "England",
        "tier": 1,
        "csv_code": "E0",
        "api_football_id": 39,
        "season": 2024,
    },
    "championship": {
        "name": "Championship",
        "country": "England",
        "tier": 1,
        "csv_code": "E1",
        "api_football_id": 40,
        "season": 2024,
    },
    "bundesliga": {
        "name": "Bundesliga",
        "country": "Germany",
        "tier": 1,
        "csv_code": "D1",
        "api_football_id": 78,
        "season": 2024,
    },
    "bundesliga-2": {
        "name": "Bundesliga 2",
        "country": "Germany",
        "tier": 1,
        "csv_code": "D2",
        "api_football_id": 79,
        "season": 2024,
    },
    "la-liga": {
        "name": "La Liga",
        "country": "Spain",
        "tier": 1,
        "csv_code": "SP1",
        "api_football_id": 140,
        "season": 2024,
    },
    "la-liga-2": {
        "name": "La Liga 2",
        "country": "Spain",
        "tier": 1,
        "csv_code": "SP2",
        "api_football_id": 141,
        "season": 2024,
    },
    "ligue-1": {
        "name": "Ligue 1",
        "country": "France",
        "tier": 1,
        "csv_code": "F1",
        "api_football_id": 61,
        "season": 2024,
    },
    "ligue-2": {
        "name": "Ligue 2",
        "country": "France",
        "tier": 1,
        "csv_code": "F2",
        "api_football_id": 62,
        "season": 2024,
    },
    "serie-a": {
        "name": "Serie A",
        "country": "Italy",
        "tier": 1,
        "csv_code": "I1",
        "api_football_id": 135,
        "season": 2024,
    },
    "serie-b": {
        "name": "Serie B",
        "country": "Italy",
        "tier": 1,
        "csv_code": "I2",
        "api_football_id": 136,
        "season": 2024,
    },
    "eredivisie": {
        "name": "Eredivisie",
        "country": "Netherlands",
        "tier": 1,
        "csv_code": "N1",
        "api_football_id": 88,
        "season": 2024,
    },
    "liga-portugal": {
        "name": "Liga Portugal",
        "country": "Portugal",
        "tier": 1,
        "csv_code": "P1",
        "api_football_id": 94,
        "season": 2024,
    },
    "champions-league": {
        "name": "Champions League",
        "country": "Europe",
        "tier": 1,
        "csv_code": None,
        "api_football_id": 2,
        "season": 2024,
    },
    # Tier 2: Medium Predictability
    "scottish-premiership": {
        "name": "Scottish Premiership",
        "country": "Scotland",
        "tier": 2,
        "csv_code": "SC0",
        "api_football_id": 179,
        "season": 2024,
    },
    "scottish-championship": {
        "name": "Scottish Championship",
        "country": "Scotland",
        "tier": 2,
        "csv_code": "SC1",
        "api_football_id": 180,
        "season": 2024,
    },
    "belgian-pro-league": {
        "name": "Belgian Pro League",
        "country": "Belgium",
        "tier": 2,
        "csv_code": "B1",
        "api_football_id": 144,
        "season": 2024,
    },
    "turkish-super-lig": {
        "name": "Turkish Super Lig",
        "country": "Turkey",
        "tier": 2,
        "csv_code": "T1",
        "api_football_id": 203,
        "season": 2024,
    },
    "greek-super-league": {
        "name": "Greek Super League",
        "country": "Greece",
        "tier": 2,
        "csv_code": "G1",
        "api_football_id": 197,
        "season": 2024,
    },
    "swiss-super-league": {
        "name": "Swiss Super League",
        "country": "Switzerland",
        "tier": 2,
        "csv_code": None,
        "api_football_id": 207,
        "season": 2024,
    },
    "danish-superliga": {
        "name": "Danish Superliga",
        "country": "Denmark",
        "tier": 2,
        "csv_code": None,
        "api_football_id": 119,
        "season": 2024,
    },
    "swedish-allsvenskan": {
        "name": "Swedish Allsvenskan",
        "country": "Sweden",
        "tier": 2,
        "csv_code": None,
        "api_football_id": 113,
        "season": 2024,
    },
    "norwegian-eliteserien": {
        "name": "Norwegian Eliteserien",
        "country": "Norway",
        "tier": 2,
        "csv_code": None,
        "api_football_id": 103,
        "season": 2024,
    },
    # Tier 3: High-Value/League-Specific
    "mls": {
        "name": "MLS",
        "country": "USA",
        "tier": 3,
        "csv_code": None,
        "api_football_id": 253,
        "season": 2025,
    },
    "saudi-pro-league": {
        "name": "Saudi Pro League",
        "country": "Saudi Arabia",
        "tier": 3,
        "csv_code": None,
        "api_football_id": 307,
        "season": 2024,
    },
    "brazilian-serie-a": {
        "name": "Brazilian Serie A",
        "country": "Brazil",
        "tier": 3,
        "csv_code": None,
        "api_football_id": 71,
        "season": 2025,
    },
    "j-league": {
        "name": "J-League",
        "country": "Japan",
        "tier": 3,
        "csv_code": None,
        "api_football_id": 98,
        "season": 2025,
    },
}

# Reverse lookup: API-Football ID -> slug
API_ID_TO_SLUG = {v["api_football_id"]: k for k, v in LEAGUE_MAP.items()}

# Reverse lookup: CSV code -> slug
CSV_CODE_TO_SLUG = {v["csv_code"]: k for k, v in LEAGUE_MAP.items() if v["csv_code"]}

# Season codes for football-data.co.uk CSV downloads (e.g. "2425" = 2024-25)
DOWNLOAD_SEASONS = ["2324", "2425"]


def get_leagues_with_csv():
    """Get all leagues that have football-data.co.uk CSV codes"""
    return {k: v for k, v in LEAGUE_MAP.items() if v["csv_code"] is not None}


def get_api_football_id(league_slug: str) -> int:
    """Get API-Football league ID from app slug"""
    if league_slug in LEAGUE_MAP:
        return LEAGUE_MAP[league_slug]["api_football_id"]
    return None


def get_league_slug_from_csv(csv_code: str) -> str:
    """Get app slug from CSV code"""
    return CSV_CODE_TO_SLUG.get(csv_code)


def get_all_api_football_ids() -> list:
    """Get all API-Football league IDs"""
    return [v["api_football_id"] for v in LEAGUE_MAP.values()]
