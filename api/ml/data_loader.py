import pandas as pd
import os
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"

# Column mapping from football-data.co.uk format to our app schema
CSV_COLUMN_MAP = {
    "Date": "date",
    "HomeTeam": "home_team",
    "Home": "home_team",           # Some CSVs use "Home" instead of "HomeTeam"
    "AwayTeam": "away_team",
    "Away": "away_team",           # Some CSVs use "Away"
    "FTHG": "home_goals",
    "HG": "home_goals",           # Alternate column name
    "FTAG": "away_goals",
    "AG": "away_goals",           # Alternate column name
    "FTR": "result",              # Full Time Result: H/D/A
    "B365H": "odds_home",
    "B365D": "odds_draw",
    "B365A": "odds_away",
    "BWH": "odds_home",           # Fallback: Bet&Win odds
    "BWD": "odds_draw",
    "BWA": "odds_away",
    "Div": "division",
}


def load_historical_data(league: str = None) -> pd.DataFrame:
    """Load historical match data from CSV files"""
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        return pd.DataFrame()
    
    csv_files = list(DATA_DIR.glob("*.csv"))
    if not csv_files:
        return pd.DataFrame()
    
    dfs = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding="utf-8", on_bad_lines="skip")
            
            # Filter by league if specified (league slug is in the filename)
            if league and league not in str(csv_file.stem):
                continue
            
            # Extract league slug from filename (e.g. "premier-league_2425.csv")
            filename_parts = csv_file.stem.split("_")
            league_slug = "_".join(filename_parts[:-1]) if len(filename_parts) > 1 else filename_parts[0]
            
            # Map columns to our schema
            df = _map_columns(df)
            
            # Add league info
            df["league"] = league_slug
            
            # Extract season from filename
            if len(filename_parts) > 1:
                season_code = filename_parts[-1]
                df["season"] = f"20{season_code[:2]}-20{season_code[2:]}" if len(season_code) == 4 else season_code
            
            # Drop rows where essential data is missing
            df = df.dropna(subset=["home_team", "away_team"])
            
            dfs.append(df)
        except Exception as e:
            print(f"Warning: Could not load {csv_file.name}: {e}")
            continue
    
    if dfs:
        combined = pd.concat(dfs, ignore_index=True)
        return combined
    return pd.DataFrame()


def _map_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map football-data.co.uk column names to our app schema"""
    mapped = pd.DataFrame()
    
    for csv_col, app_col in CSV_COLUMN_MAP.items():
        if csv_col in df.columns and app_col not in mapped.columns:
            mapped[app_col] = df[csv_col]
    
    # Parse date - football-data.co.uk uses DD/MM/YYYY format
    if "date" in mapped.columns:
        try:
            mapped["date"] = pd.to_datetime(mapped["date"], format="%d/%m/%Y", errors="coerce")
        except Exception:
            try:
                mapped["date"] = pd.to_datetime(mapped["date"], dayfirst=True, errors="coerce")
            except Exception:
                pass
    
    # Ensure numeric types
    for col in ["home_goals", "away_goals", "odds_home", "odds_draw", "odds_away"]:
        if col in mapped.columns:
            mapped[col] = pd.to_numeric(mapped[col], errors="coerce")
    
    return mapped


def save_match_data(df: pd.DataFrame, league: str):
    """Save match data to database"""
    from app.database import get_connection, get_cursor, execute_sql
    
    conn = get_connection()
    cursor = get_cursor(conn)
    
    inserted = 0
    for _, row in df.iterrows():
        try:
            execute_sql(cursor, """
                INSERT INTO matches 
                (league, league_id, season, date, home_team, away_team, 
                 home_goals, away_goals, xG_home, xG_away, 
                 odds_home, odds_draw, odds_away)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                league,
                row.get("league_id"),
                row.get("season"),
                str(row.get("date", "")) if pd.notna(row.get("date")) else None,
                row.get("home_team"),
                row.get("away_team"),
                row.get("home_goals") if pd.notna(row.get("home_goals")) else None,
                row.get("away_goals") if pd.notna(row.get("away_goals")) else None,
                row.get("xG_home") if pd.notna(row.get("xG_home")) else None,
                row.get("xG_away") if pd.notna(row.get("xG_away")) else None,
                row.get("odds_home") if pd.notna(row.get("odds_home")) else None,
                row.get("odds_draw") if pd.notna(row.get("odds_draw")) else None,
                row.get("odds_away") if pd.notna(row.get("odds_away")) else None,
            ))
            inserted += 1
        except Exception as e:
            continue
    
    conn.commit()
    conn.close()
    return inserted


def populate_database():
    """Load all CSV data and insert into the database"""
    from app.database import get_connection
    
    print("\nPopulating database from CSV files...")
    
    df = load_historical_data()
    
    if len(df) == 0:
        print("No CSV data found. Run download_data.py first.")
        return 0
    
    print(f"Loaded {len(df)} matches from CSV files")
    
    # Group by league and insert
    total_inserted = 0
    for league_slug in df["league"].unique():
        league_df = df[df["league"] == league_slug]
        count = save_match_data(league_df, league_slug)
        total_inserted += count
        print(f"  {league_slug}: {count} matches inserted")
    
    # Verify
    conn = get_connection()
    cursor = get_cursor(conn)
    execute_sql(cursor, "SELECT COUNT(*) FROM matches")
    total = cursor.fetchone()[0] if hasattr(cursor, 'fetchone') else list(cursor.fetchone().values())[0]
    conn.close()
    
    print(f"\nTotal matches in database: {total}")
    return total_inserted


def get_matches_for_training(league: str = None, min_games: int = 50) -> pd.DataFrame:
    """Get matches with complete data for training"""
    from app.database import get_connection
    
    conn = get_connection()
    query = """
        SELECT * FROM matches 
        WHERE home_goals IS NOT NULL 
        AND away_goals IS NOT NULL
    """
    params = []
    if league:
        query += " AND league = ?"
        params.append(league)
    
    # pd.read_sql_query handles its own placeholders if we use sqlalchemy, 
    # but since we are using raw connections, we might need a workaround for different drivers.
    # However, for read_sql_query, it's generally better to pass it a query it understands.
    if settings.DATABASE_URL:
        query = query.replace('?', '%s')
    
    df = pd.read_sql_query(query, conn, params=params if params else None)
    conn.close()
    
    if len(df) >= min_games:
        return df
    
    # If filtering by specific league didn't get enough, try all data
    if league and len(df) < min_games:
        conn = get_connection()
        df_all = pd.read_sql_query("""
            SELECT * FROM matches 
            WHERE home_goals IS NOT NULL 
            AND away_goals IS NOT NULL
            ORDER BY date ASC
        """, conn)
        conn.close()
        if len(df_all) >= min_games:
            return df_all
    
    return pd.DataFrame()


def get_league_teams(league: str) -> list:
    """Get unique teams for a league"""
    from app.database import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    execute_sql(cursor, """
        SELECT DISTINCT home_team FROM matches WHERE league = ?
        UNION
        SELECT DISTINCT away_team FROM matches WHERE league = ?
    """, (league, league))
    
    results = cursor.fetchall()
    teams = [row[0] if isinstance(row, tuple) else list(row.values())[0] for row in results]
    conn.close()
    return teams


def get_recent_form(team: str, league: str, n: int = 5) -> dict:
    """Calculate recent form for a team"""
    from app.database import get_connection
    
    conn = get_connection()
    cursor = conn.cursor()
    
    execute_sql(cursor, """
        SELECT home_team, away_team, home_goals, away_goals 
        FROM matches 
        WHERE league = ? AND (home_team = ? OR away_team = ?)
        ORDER BY date DESC
        LIMIT ?
    """, (league, team, team, n))
    
    matches_raw = cursor.fetchall()
    conn.close()
    
    # Normalize match rows
    matches = []
    for row in matches_raw:
        if isinstance(row, tuple):
            matches.append(row)
        else:
            # Postgres dict row
            matches.append((row['home_team'], row['away_team'], row['home_goals'], row['away_goals']))
    
    wins = 0
    draws = 0
    losses = 0
    goals_for = 0
    goals_against = 0
    
    for match in matches:
        if match[0] == team:
            goals_for += match[2]
            goals_against += match[3]
            if match[2] > match[3]:
                wins += 1
            elif match[2] == match[3]:
                draws += 1
            else:
                losses += 1
        else:
            goals_for += match[3]
            goals_against += match[2]
            if match[3] > match[2]:
                wins += 1
            elif match[3] == match[2]:
                draws += 1
            else:
                losses += 1
    
    total = wins + draws + losses
    if total == 0:
        return {"wins": 0, "draws": 0, "losses": 0, "points": 0, "gf": 0, "ga": 0}
    
    return {
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "points": wins * 3 + draws,
        "gf": goals_for,
        "ga": goals_against,
        "gd": goals_for - goals_against
    }