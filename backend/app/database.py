import sqlite3
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from pathlib import Path
from app.config import settings

def get_db_path():
    db_dir = Path(settings.DATABASE_PATH).parent
    db_dir.mkdir(parents=True, exist_ok=True)
    return settings.DATABASE_PATH

def get_connection():
    if settings.DATABASE_URL:
        # PostgreSQL (Supabase/Neon)
        conn = psycopg2.connect(settings.DATABASE_URL)
        return conn
    
    # Local SQLite
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

def get_cursor(conn):
    """Returns a cursor that works similarly across SQLite and Postgres"""
    if settings.DATABASE_URL:
        return conn.cursor(cursor_factory=RealDictCursor)
    return conn.cursor()

def execute_sql(cursor, query, params=None):
    """Executes SQL with placeholder compatibility (? for SQLite, %s for Postgres)"""
    if settings.DATABASE_URL:
        query = query.replace('?', '%s')
        # Also handle AUTOINCREMENT vs SERIAL if needed, but here we mostly care about queries
        query = query.replace('INTEGER PRIMARY KEY AUTOINCREMENT', 'SERIAL PRIMARY KEY')
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
    return cursor

def init_db():
    conn = get_connection()
    cursor = get_cursor(conn)
    
    execute_sql(cursor, """
        CREATE TABLE IF NOT EXISTS matches (
            id SERIAL PRIMARY KEY,
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
    
    execute_sql(cursor, """
        CREATE TABLE IF NOT EXISTS predictions (
            id SERIAL PRIMARY KEY,
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
            value_bet BOOLEAN DEFAULT FALSE,
            kelly_stake REAL,
            actual_result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    execute_sql(cursor, """
        CREATE TABLE IF NOT EXISTS bets (
            id SERIAL PRIMARY KEY,
            prediction_id INTEGER,
            platform TEXT NOT NULL,
            market TEXT,
            selection TEXT,
            stake REAL,
            odds REAL,
            status TEXT DEFAULT 'pending',
            profit REAL,
            bet_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    execute_sql(cursor, """
        CREATE TABLE IF NOT EXISTS models (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            league TEXT,
            market TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            accuracy REAL,
            path TEXT
        )
    """)
    
    execute_sql(cursor, """
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    execute_sql(cursor, """
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