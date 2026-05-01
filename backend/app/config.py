import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_FOOTBALL_KEY: str = os.getenv("API_FOOTBALL_KEY", "")
    FOOTBALL_DATA_KEY: str = os.getenv("FOOTBALL_DATA_KEY", "")
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/pro_punter.db")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    KELLY_MULTIPLIER: float = float(os.getenv("KELLY_MULTIPLIER", "0.25"))
    API_BASE_URL: str = "https://v3.football.api-sports.io/"
    FOOTBALL_DATA_URL: str = "https://api.football-data-org/v4"
    API_HEADER: str = "x-apisports-key"
    
settings = Settings()