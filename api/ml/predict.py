import numpy as np
import pandas as pd
from ml.features import extract_features, get_feature_columns
from ml.train import load_model, load_encoder

def predict_match(
    home_team: str, 
    away_team: str, 
    league: str, 
    matches_df: pd.DataFrame,
    market: str = "1x2",
    home_id: Optional[int] = None,
    away_id: Optional[int] = None,
    api_football = None
) -> dict:
    """Generate prediction for a match"""
    
    features = extract_features(
        home_team, away_team, league, matches_df, 
        home_id=home_id, away_id=away_id, api_football=api_football
    )
    feature_cols = get_feature_columns()
    
    feature_df = pd.DataFrame([features], columns=feature_cols).fillna(0)
    
    model_market = "1x2" if market == "double_chance" else market
    
    # Try league-specific model first, then fall back to 'all'
    xgb_model = load_model("xgb", league, model_market) or load_model("xgb", None, model_market)
    
    # LightGBM is optional in production to save space
    try:
        lgbm_model = load_model("lgbm", league, model_market) or load_model("lgbm", None, model_market)
    except Exception:
        lgbm_model = None
    
    if xgb_model is None and lgbm_model is None:
        return _feature_based_prediction(home_team, away_team, league, features, market)
    
    results = {
        "home_team": home_team,
        "away_team": away_team,
        "league": league,
        "market": market,
        "features": features
    }
    
    if market in ["1x2", "euro_handicap", "double_chance"]:
        encoder = load_encoder(league, model_market) or load_encoder(None, model_market)
        if encoder is None:
            return _feature_based_prediction(home_team, away_team, league, features, market)
        
        classes = list(encoder.classes_)
        
        if xgb_model:
            xgb_proba = xgb_model.predict_proba(feature_df)[0]
            results["xgb_prob"] = {cls: float(p) for cls, p in zip(classes, xgb_proba)}
        
        if lgbm_model:
            lgbm_proba = lgbm_model.predict_proba(feature_df)[0]
            results["lgbm_prob"] = {cls: float(p) for cls, p in zip(classes, lgbm_proba)}
        
        if xgb_model and lgbm_model:
            ensemble_proba = (xgb_proba + lgbm_proba) / 2
        elif xgb_model:
            ensemble_proba = xgb_proba
        elif lgbm_model:
            ensemble_proba = lgbm_proba
        else:
            return _feature_based_prediction(home_team, away_team, league, features, market)
            
        results["ensemble_prob"] = {cls: float(p) for cls, p in zip(classes, ensemble_proba)}
        
        if market == "double_chance":
            p_home = results["ensemble_prob"].get("home", 0)
            p_draw = results["ensemble_prob"].get("draw", 0)
            p_away = results["ensemble_prob"].get("away", 0)
            
            dc_probs = {
                "1X": p_home + p_draw,
                "12": p_home + p_away,
                "X2": p_draw + p_away
            }
            results["ensemble_prob"] = dc_probs
            predicted_class = max(dc_probs.items(), key=lambda x: x[1])[0]
            results["prediction"] = predicted_class
            results["confidence"] = dc_probs[predicted_class]
        else:
            predicted_class = classes[np.argmax(ensemble_proba)]
            results["prediction"] = predicted_class
            results["confidence"] = float(max(ensemble_proba))
    
    elif market in ["btts", "over_25", "over_15"]:
        if xgb_model:
            xgb_proba = xgb_model.predict_proba(feature_df)[0]
            # Probabilities for class '1' (Yes)
            p_yes_xgb = float(xgb_proba[1])
            results["xgb_confidence"] = p_yes_xgb
        
        if lgbm_model:
            lgbm_proba = lgbm_model.predict_proba(feature_df)[0]
            p_yes_lgbm = float(lgbm_proba[1])
            results["lgbm_confidence"] = p_yes_lgbm
        
        if xgb_model and lgbm_model:
            ensemble_prob_yes = (results["xgb_confidence"] + results["lgbm_confidence"]) / 2
        elif xgb_model:
            ensemble_prob_yes = results["xgb_confidence"]
        else:
            ensemble_prob_yes = results["lgbm_confidence"]
        
        results["prediction"] = "yes" if ensemble_prob_yes > 0.5 else "no"
        results["confidence"] = ensemble_prob_yes if ensemble_prob_yes > 0.5 else (1 - ensemble_prob_yes)
    
    return results


def get_best_prediction_for_match(
    home_team: str, 
    away_team: str, 
    league: str, 
    matches_df: pd.DataFrame,
    home_id: Optional[int] = None,
    away_id: Optional[int] = None,
    api_football = None
) -> dict:
    """Evaluate all markets and return the single best recommendation for a match"""
    markets = ["1x2", "double_chance", "over_15", "over_25", "euro_handicap", "btts"]
    all_preds = []
    
    for m in markets:
        try:
            pred = predict_match(
                home_team, away_team, league, matches_df, 
                market=m, home_id=home_id, away_id=away_id, 
                api_football=api_football
            )
            # Add market info to the prediction result
            pred["market_id"] = m
            all_preds.append(pred)
        except Exception:
            continue
            
    if not all_preds:
        return {}
        
    # Scoring logic: 
    # We prioritize confidence, but we also favor "safer" markets like double_chance and over_15
    # by giving them a slight weighting bonus in our selection logic.
    def score_prediction(p):
        conf = p.get("confidence", 0)
        market = p.get("market_id")
        
        # Safeness weighting
        if market == "double_chance": return conf * 1.1  # Very safe
        if market == "over_15": return conf * 1.05      # Safe
        if market == "1x2" and p.get("prediction") == "home": return conf * 1.02 # Home advantage bias
        return conf

    best = max(all_preds, key=score_prediction)
    
    return {
        "best_market": best["market_id"],
        "best_prediction": best["prediction"],
        "best_confidence": best["confidence"],
        "all_options": {p["market_id"]: {"prediction": p["prediction"], "confidence": p["confidence"]} for p in all_preds}
    }


def _feature_based_prediction(home_team: str, away_team: str, league: str, 
                               features: dict, market: str) -> dict:
    """Fallback prediction based on features when no trained model is available"""
    result = {
        "home_team": home_team,
        "away_team": away_team,
        "league": league,
        "market": market,
        "features": features,
        "model_used": "feature_heuristic"
    }
    
    if market == "1x2":
        home_strength = features.get("home_win_rate", 0.45) + features.get("elo_diff", 0) / 1000
        away_strength = features.get("away_win_rate", 0.35)
        
        if home_strength > away_strength + 0.15:
            result["prediction"] = "home"
            result["confidence"] = min(0.65, 0.5 + home_strength - away_strength)
        elif away_strength > home_strength + 0.1:
            result["prediction"] = "away"
            result["confidence"] = min(0.60, 0.5 + away_strength - home_strength)
        else:
            result["prediction"] = "draw"
            result["confidence"] = 0.35
    elif market == "euro_handicap":
        home_strength = features.get("home_win_rate", 0.45) + features.get("elo_diff", 0) / 1000
        away_strength = features.get("away_win_rate", 0.35)
        
        if home_strength > away_strength + 0.35:
            result["prediction"] = "home"
            result["confidence"] = 0.55
        elif away_strength > home_strength + 0.1:
            result["prediction"] = "away"
            result["confidence"] = 0.60
        else:
            result["prediction"] = "draw"
            result["confidence"] = 0.35
    elif market == "double_chance":
        home_strength = features.get("home_win_rate", 0.45) + features.get("elo_diff", 0) / 1000
        away_strength = features.get("away_win_rate", 0.35)
        
        if home_strength > away_strength:
            result["prediction"] = "1X"
            result["confidence"] = 0.70
        else:
            result["prediction"] = "X2"
            result["confidence"] = 0.70
    elif market == "btts":
        avg_goals = features.get("home_avg_goals", 1.5) + features.get("away_avg_goals", 1.2)
        result["prediction"] = "yes" if avg_goals > 2.0 else "no"
        result["confidence"] = 0.55
    elif market == "over_25":
        avg_goals = features.get("home_avg_goals", 1.5) + features.get("away_avg_goals", 1.2)
        result["prediction"] = "yes" if avg_goals > 2.5 else "no"
        result["confidence"] = 0.55
    elif market == "over_15":
        avg_goals = features.get("home_avg_goals", 1.5) + features.get("away_avg_goals", 1.2)
        result["prediction"] = "yes" if avg_goals > 1.8 else "no"
        result["confidence"] = 0.65
        
    return result


def calculate_value_bet(
    prediction: dict, 
    odds: dict, 
    threshold: float = 0.05
) -> dict:
    """Calculate value bet and Kelly stake"""
    from app.config import settings
    
    if "prediction" not in prediction:
        return {"value_bet": False, "reason": "No prediction available"}
    
    predicted_outcome = prediction["prediction"]
    model_prob = prediction.get("confidence", 0)
    
    if predicted_outcome not in odds:
        return {"value_bet": False, "reason": "Odds not available"}
    
    bookmaker_odds = odds[predicted_outcome]
    implied_prob = 1 / bookmaker_odds
    
    edge = model_prob - implied_prob
    
    value_bet_detected = edge > threshold
    
    if value_bet_detected:
        kelly_fraction = (model_prob * bookmaker_odds - 1) / (bookmaker_odds - 1)
        kelly_fraction *= settings.KELLY_MULTIPLIER
        kelly_fraction = max(0, min(kelly_fraction, 0.25))
    else:
        kelly_fraction = 0
    
    return {
        "value_bet": value_bet_detected,
        "edge": edge,
        "model_prob": model_prob,
        "implied_prob": implied_prob,
        "bookmaker_odds": bookmaker_odds,
        "kelly_fraction": kelly_fraction,
        "recommendation": predicted_outcome
    }


def get_recommended_bets(predictions: list, max_bets: int = 5) -> list:
    """Get top recommended bets sorted by value"""
    recommended = []
    
    for pred in predictions:
        if pred.get("value_bet"):
            recommended.append(pred)
    
    recommended.sort(key=lambda x: x.get("edge", 0), reverse=True)
    
    return recommended[:max_bets]