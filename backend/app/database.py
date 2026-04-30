import sqlite3
import os
from pathlib import Path
from app.config import settings

def get_db_path():
    db_dir = Path(settings.DATABASE_PATH).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    return settings.DATABASE_PATH

def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            league TEXT NOT NULL,
            league_id TEXT,
            season TEXT,
            date TEXT,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            home_goals INTEGER,
            away_goals INTEGER,
            xG_home REAL,
            xG_away REAL,
            odds_home REAL,
            odds_draw REAL,
            odds_away REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            match_id INTEGER,
            league TEXT NOT NULL,
            league_id TEXT,
            date TEXT,
            home_team TEXT NOT NULL,
            away_team TEXT NOT NULL,
            predicted_outcome TEXT,
            market TEXT,
            confidence REAL,
            model_prob REAL,
            odds REAL,
            value_bet BOOLEAN DEFAULT 0,
            kelly_stake REAL,
            actual_result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (match_id) REFERENCES matches (id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prediction_id INTEGER,
            platform TEXT NOT NULL,
            market TEXT,
            selection TEXT,
            stake REAL,
            odds REAL,
            status TEXT DEFAULT 'pending',
            profit REAL,
            bet_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (prediction_id) REFERENCES predictions (id)
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            league TEXT,
            market TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accuracy REAL,
            path TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            data TEXT,
            expires_at TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")