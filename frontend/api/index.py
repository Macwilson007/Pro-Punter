from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date, timedelta
import pandas as pd

from app.config import settings
from app.database import get_connection, init_db, get_cursor, execute_sql
from api.football import api_football
from api.leagues import LEAGUE_MAP, get_api_football_id
from ml.data_loader import get_matches_for_training, get_recent_form, populate_database
from ml.features import extract_features
from ml.train import train_models
from ml.predict import predict_match, get_best_prediction_for_match, calculate_value_bet, _feature_based_prediction
from ml.aviator import aviator_predictor

app = FastAPI(title="Pro Punter API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.responses import JSONResponse
import traceback

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": traceback.format_exc()}
    )

init_db()

class PredictionRequest(BaseModel):
    home_team: str
    away_team: str
    league: str
    market: str = "1x2"

class BetRecord(BaseModel):
    prediction_id: int
    platform: str
    market: str
    selection: str
    stake: float
    odds: float
    status: str = "pending"

class TrainingRequest(BaseModel):
    league: Optional[str] = None
    market: str = "1x2"

class AviatorRequest(BaseModel):
    history: List[float] = []

@app.get("/")
async def root():
    return {"message": "Pro Punter API", "version": "1.0.0"}

@app.get("/api/leagues")
async def get_leagues():
    leagues = []
    for slug, info in LEAGUE_MAP.items():
        leagues.append({
            "id": slug,
            "name": info["name"],
            "country": info["country"],
            "tier": info["tier"],
            "api_football_id": info["api_football_id"],
        })
    return leagues

@app.get("/api/predictions/today")
async def get_todays_predictions(
    date: Optional[str] = Query(None),
    league: Optional[str] = Query(None),
    market: str = Query("1x2")
):
    """Get predictions for today's actual matches"""
    
    # Load training data for the prediction model
    matches_df = get_matches_for_training(league)
    
    # Try to get today's fixtures from API-Football
    predictions = []
    api_fixtures_found = False
    
    try:
        api_football_id = None
        if league and league in LEAGUE_MAP:
            api_football_id = LEAGUE_MAP[league]["api_football_id"]
        
        target_date = date if date else datetime.now().date().isoformat()
        season = LEAGUE_MAP[league]["season"] if league and league in LEAGUE_MAP else None
        fixtures_response = api_football.get_fixtures(
            league_id=api_football_id, 
            fixture_date=target_date,
            season=season
        )
        
        if "response" in fixtures_response and len(fixtures_response["response"]) > 0:
            api_fixtures_found = True
            
            for fixture in fixtures_response["response"]:
                try:
                    home_team = fixture["teams"]["home"]["name"]
                    away_team = fixture["teams"]["away"]["name"]
                    fixture_id = fixture["fixture"]["id"]
                    fixture_date = fixture["fixture"]["date"]
                    fixture_status = fixture["fixture"]["status"]["short"]
                    
                    # Determine league slug from API-Football ID
                    fixture_league_id = fixture["league"]["id"]
                    fixture_league_name = fixture["league"]["name"]
                    
                    fixture_league_slug = next(
                        (k for k, v in LEAGUE_MAP.items() if v["api_football_id"] == fixture_league_id), 
                        None
                    )
                    
                    # Skip matches that are not in our supported leagues
                    if fixture_league_slug is None:
                        continue
                    
                    # Generate prediction using our model
                    if len(matches_df) > 0:
                        home_id = fixture["teams"]["home"]["id"]
                        away_id = fixture["teams"]["away"]["id"]
                        pred = predict_match(
                            home_team, away_team, fixture_league_slug, 
                            matches_df, market, 
                            home_id=home_id, away_id=away_id, api_football=api_football
                        )
                        
                        # Add "Best Pick" recommendation
                        best = get_best_prediction_for_match(
                            home_team, away_team, fixture_league_slug, 
                            matches_df, home_id=home_id, away_id=away_id, 
                            api_football=api_football
                        )
                        pred["best_pick"] = best
                    else:
                        # Feature-based fallback if no training data
                        # Still extract features using API if possible
                        home_id = fixture["teams"]["home"]["id"]
                        away_id = fixture["teams"]["away"]["id"]
                        features = extract_features(
                            home_team, away_team, fixture_league_slug, 
                            matches_df, home_id=home_id, away_id=away_id, 
                            api_football=api_football
                        )
                        pred = _feature_based_prediction(home_team, away_team, fixture_league_slug, features, market)
                    
                    pred["fixture_id"] = fixture_id
                    pred["kickoff"] = fixture_date
                    pred["status"] = fixture_status
                    pred["league_name"] = fixture_league_name
                    pred["league_id"] = fixture_league_slug
                    
                    # Add goals if match is in progress or finished
                    if fixture.get("goals"):
                        pred["live_home_goals"] = fixture["goals"].get("home")
                        pred["live_away_goals"] = fixture["goals"].get("away")
                    
                    predictions.append(pred)
                except (KeyError, TypeError) as e:
                    continue
    except Exception as e:
        print(f"API-Football error: {e}")
    
    # Fallback: if API didn't return fixtures, use historical data to demo predictions
    if not api_fixtures_found and len(matches_df) > 0:
        # Filter by requested league if specified
        if league:
            fallback_df = matches_df[matches_df['league'] == league]
        else:
            fallback_df = matches_df
            
        if len(fallback_df) > 0:
            # Use recent matches to generate sample predictions
            recent = fallback_df.tail(10)
            for _, match in recent.iterrows():
                pred = predict_match(
                    match['home_team'],
                    match['away_team'],
                    match.get('league', league or 'unknown'),
                    matches_df,
                    market
                )
                # Add "Best Pick" recommendation even in demo mode
                best = get_best_prediction_for_match(
                    match['home_team'],
                    match['away_team'],
                    match.get('league', league or 'unknown'),
                    matches_df
                )
                pred["best_pick"] = best
                pred["source"] = "historical_demo"
                pred["date"] = str(match.get("date", ""))
                predictions.append(pred)
    
    if not predictions:
        return {
            "predictions": [], 
            "count": 0,
            "message": "No fixtures found for today. Train models first and ensure API key is configured.",
            "api_key_configured": bool(settings.API_FOOTBALL_KEY),
            "training_data_available": len(matches_df) > 0
        }
    
    return {
        "predictions": predictions, 
        "count": len(predictions),
        "source": "api_football" if api_fixtures_found else "historical_demo",
        "date": target_date
    }

@app.post("/api/predict")
async def create_prediction(request: PredictionRequest):
    matches_df = get_matches_for_training(request.league)
    
    if len(matches_df) == 0:
        raise HTTPException(status_code=400, detail="No training data available. Run setup first.")
    
    prediction = predict_match(
        request.home_team,
        request.away_team,
        request.league,
        matches_df,
        request.market
    )
    
    conn = get_connection()
    cursor = get_cursor(conn)
    
    execute_sql(cursor, """
        INSERT INTO predictions (league, home_team, away_team, predicted_outcome, market, confidence, model_prob)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        request.league,
        request.home_team,
        request.away_team,
        prediction.get("prediction"),
        request.market,
        prediction.get("confidence"),
        prediction.get("ensemble_prob", {}).get(prediction.get("prediction"), 0) if isinstance(prediction.get("ensemble_prob"), dict) else 0
    ))
    
    # Get last row id (works for both sqlite and postgres)
    if settings.DATABASE_URL:
        cursor.execute("SELECT LASTVAL()")
        prediction_id = cursor.fetchone()[0] if hasattr(cursor, 'fetchone') else cursor.fetchone()['lastval']
    else:
        prediction_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    prediction["id"] = prediction_id
    
    return prediction

@app.post("/api/aviator/predict")
async def predict_aviator(request: AviatorRequest):
    """Generate Aviator signal based on multiplier history"""
    return aviator_predictor.calculate_signal(request.history)

@app.get("/api/predictions/{league_id}")
async def get_predictions_by_league(
    league_id: str,
    date: Optional[str] = Query(None)
):
    conn = get_connection()
    
    query = "SELECT * FROM predictions WHERE league = ?"
    params = [league_id]
    
    if date:
        query += " AND date = ?"
        params.append(date)
    
    query += " ORDER BY created_at DESC LIMIT 50"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df.to_dict(orient="records")

@app.post("/api/train")
async def train_model(request: TrainingRequest):
    result = train_models(request.league, request.market)
    return result

@app.get("/api/odds/{match_id}")
async def get_odds(match_id: str, league_id: Optional[str] = Query(None)):
    fixture_id = int(match_id) if match_id.isdigit() else None
    if fixture_id:
        odds_data = api_football.get_odds(fixture_id=fixture_id)
    else:
        odds_data = {"error": "Invalid match ID"}
    return odds_data

@app.get("/api/performance")
async def get_performance(league: Optional[str] = Query(None)):
    conn = get_connection()
    
    query = """
        SELECT 
            COUNT(*) as total_predictions,
            SUM(CASE WHEN actual_result = predicted_outcome THEN 1 ELSE 0 END) as correct,
            AVG(CASE WHEN actual_result = predicted_outcome THEN 1.0 ELSE 0.0 END) as accuracy
        FROM predictions
        WHERE actual_result IS NOT NULL
    """
    params = []
    if league:
        query += " AND league = ?"
        params.append(league)
    
    df = pd.read_sql_query(query, conn, params=params if params else None)
    conn.close()
    
    if len(df) > 0:
        return df.to_dict(orient="records")[0]
    return {"total_predictions": 0, "correct": 0, "accuracy": 0}

@app.post("/api/predictions/sync-results")
async def sync_prediction_results(league: Optional[str] = Query(None)):
    """Fetch actual results for past fixtures and update predictions table"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get predictions that don't have results yet
    query = "SELECT id, fixture_id, market FROM predictions WHERE actual_result IS NULL AND fixture_id IS NOT NULL"
    params = []
    if league:
        query += " AND league = ?"
        params.append(league)
    
    execute_sql(cursor, query, params)
    pending = cursor.fetchall()
    
    updated_count = 0
    errors = []
    
    for row in pending:
        pred_id, fixture_id, market = row['id'], row['fixture_id'], row['market']
        
        try:
            # Check if we have this fixture in our matches table first (maybe it was updated)
            cursor.execute("SELECT home_goals, away_goals FROM matches WHERE league_id = ?", (fixture_id,))
            match_row = cursor.fetchone()
            
            home_goals = None
            away_goals = None
            
            if match_row and match_row['home_goals'] is not None:
                home_goals = match_row['home_goals']
                away_goals = match_row['away_goals']
            else:
                # Fetch from API-Football
                fixture_response = api_football._make_request(f"fixtures", {"id": fixture_id})
                if "response" in fixture_response and len(fixture_response["response"]) > 0:
                    fixture_data = fixture_response["response"][0]
                    status = fixture_data["fixture"]["status"]["short"]
                    
                    # Only update if match is finished
                    if status in ["FT", "AET", "PEN"]:
                        home_goals = fixture_data["goals"].get("home")
                        away_goals = fixture_data["goals"].get("away")
                        
                        # Also update matches table for future training
                        execute_sql(cursor, """
                            INSERT INTO matches (league, league_id, home_team, away_team, home_goals, away_goals, date)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (
                            fixture_data["league"]["name"],
                            fixture_id,
                            fixture_data["teams"]["home"]["name"],
                            fixture_data["teams"]["away"]["name"],
                            home_goals,
                            away_goals,
                            fixture_data["fixture"]["date"]
                        ))
            
            if home_goals is not None and away_goals is not None:
                # Determine actual result based on market
                actual = None
                if market == "1x2":
                    if home_goals > away_goals: actual = "home"
                    elif home_goals < away_goals: actual = "away"
                    else: actual = "draw"
                elif market == "over_25":
                    actual = "yes" if (home_goals + away_goals) > 2.5 else "no"
                elif market == "over_15":
                    actual = "yes" if (home_goals + away_goals) > 1.5 else "no"
                elif market == "btts":
                    actual = "yes" if (home_goals > 0 and away_goals > 0) else "no"
                elif market == "double_chance":
                    if home_goals > away_goals: actual = ["1X", "12"]
                    elif home_goals < away_goals: actual = ["X2", "12"]
                    else: actual = ["1X", "X2"]
                
                if actual:
                    # Special handling for double_chance (it can match multiple)
                    if market == "double_chance":
                        cursor.execute("SELECT predicted_outcome FROM predictions WHERE id = ?", (pred_id,))
                        predicted = cursor.fetchone()['predicted_outcome']
                        is_correct = predicted in actual
                        # We store the 'correct' one if it matches, otherwise just store first one
                        final_actual = predicted if is_correct else actual[0]
                    else:
                        final_actual = actual
                    
                        execute_sql(cursor, "UPDATE predictions SET actual_result = ? WHERE id = ?", (final_actual, pred_id))
                        updated_count += 1
                    
        except Exception as e:
            errors.append(f"Error updating fixture {fixture_id}: {str(e)}")
            continue
            
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "updated": updated_count,
        "total_checked": len(pending),
        "errors": errors
    }

@app.post("/api/bets")
async def record_bet(bet: BetRecord):
    conn = get_connection()
    cursor = conn.cursor()
    
    execute_sql(cursor, """
        INSERT INTO bets (prediction_id, platform, market, selection, stake, odds, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        bet.prediction_id,
        bet.platform,
        bet.market,
        bet.selection,
        bet.stake,
        bet.odds,
        bet.status
    ))
    
    if settings.DATABASE_URL:
        cursor.execute("SELECT LASTVAL()")
        bet_id = cursor.fetchone()[0] if hasattr(cursor, 'fetchone') else cursor.fetchone()['lastval']
    else:
        bet_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"id": bet_id, "message": "Bet recorded successfully"}

@app.get("/api/bets")
async def get_bets(
    platform: Optional[str] = Query(None),
    status: Optional[str] = Query(None)
):
    conn = get_connection()
    
    query = "SELECT * FROM bets WHERE 1=1"
    params = []
    
    if platform:
        query += " AND platform = ?"
        params.append(platform)
    
    if status:
        query += " AND status = ?"
        params.append(status)
    
    query += " ORDER BY bet_date DESC LIMIT 100"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df.to_dict(orient="records")

@app.put("/api/bets/{bet_id}")
async def update_bet(bet_id: int, status: str, profit: Optional[float] = None):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE bets SET status = ?, profit = ? WHERE id = ?
    """, (status, profit, bet_id))
    
    conn.commit()
    conn.close()
    
    return {"message": "Bet updated successfully"}

@app.get("/api/config")
async def get_config():
    return {
        "api_key_configured": bool(settings.API_FOOTBALL_KEY),
        "kelly_multiplier": settings.KELLY_MULTIPLIER,
        "database_path": settings.DATABASE_PATH
    }

@app.post("/api/config")
async def update_config(key: str, value: str):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
    """, (key, value))
    
    conn.commit()
    conn.close()
    
    return {"message": "Config updated successfully"}

@app.post("/api/data/populate")
async def populate_data():
    """Download CSVs and populate the database"""
    try:
        from ml.download_data import download_all
        downloaded = download_all()
        imported = populate_database()
        return {
            "message": "Data populated successfully",
            "csvs_downloaded": downloaded,
            "matches_imported": imported
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_status():
    """Get system status: data, models, API"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM matches")
    match_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM predictions")
    pred_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM models")
    model_count = cursor.fetchone()[0]
    
    conn.close()
    
    # Check for trained model files
    from pathlib import Path
    models_dir = Path(__file__).parent.parent / "models" / "trained"
    model_files = list(models_dir.glob("*.joblib")) if models_dir.exists() else []
    
    return {
        "matches_in_db": match_count,
        "predictions_generated": pred_count,
        "models_in_db": model_count,
        "model_files": [f.name for f in model_files],
        "api_key_configured": bool(settings.API_FOOTBALL_KEY),
        "ready_for_predictions": match_count >= 50 and len(model_files) > 0
    }