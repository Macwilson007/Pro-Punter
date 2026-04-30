import joblib
import os
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, log_loss
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from ml.features import get_feature_columns, prepare_training_data
from ml.data_loader import get_matches_for_training

MODELS_DIR = Path(__file__).parent.parent / "models" / "trained"

def train_models(league: str = None, market: str = "1x2") -> dict:
    """Train prediction models"""
    if not MODELS_DIR.exists():
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
    
    matches_df = get_matches_for_training(league)
    
    if len(matches_df) < 50:
        return {"error": "Insufficient training data"}
    
    df = prepare_training_data(matches_df)
    feature_cols = get_feature_columns()
    
    df = df.dropna(subset=feature_cols + ['result'])
    
    X = df[feature_cols]
    
    if market == "1x2":
        y = df['result']
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        model_classes = le.classes_
    elif market == "euro_handicap":
        y = df['euro_handicap']
        le = LabelEncoder()
        y_encoded = le.fit_transform(y)
        model_classes = le.classes_
    elif market == "btts":
        y = df['btts'].astype(int)
        model_classes = [0, 1]
    elif market == "over_25":
        y = df['over_25'].astype(int)
        model_classes = [0, 1]
    elif market == "over_15":
        y = df['over_15'].astype(int)
        model_classes = [0, 1]
    else:
        return {"error": f"Unknown market: {market}"}
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded if market in ["1x2", "euro_handicap"] else y, 
        test_size=0.2, random_state=42
    )
    
    results = {}
    
    xgb = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    xgb.fit(X_train, y_train)
    xgb_pred = xgb.predict(X_test)
    xgb_prob = xgb.predict_proba(X_test)
    
    if market in ["1x2", "euro_handicap"]:
        results['xgb_accuracy'] = accuracy_score(y_test, xgb_pred)
        results['xgb_logloss'] = log_loss(y_test, xgb_prob)
    else:
        results['xgb_accuracy'] = accuracy_score(y_test, xgb_pred)
    
    xgb_path = MODELS_DIR / f"xgb_{market}_{league or 'all'}.joblib"
    joblib.dump(xgb, xgb_path)
    results['xgb_path'] = str(xgb_path)
    
    lgbm = LGBMClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        verbose=-1
    )
    lgbm.fit(X_train, y_train)
    lgbm_pred = lgbm.predict(X_test)
    lgbm_prob = lgbm.predict_proba(X_test)
    
    if market in ["1x2", "euro_handicap"]:
        results['lgbm_accuracy'] = accuracy_score(y_test, lgbm_pred)
        results['lgbm_logloss'] = log_loss(y_test, lgbm_prob)
    else:
        results['lgbm_accuracy'] = accuracy_score(y_test, lgbm_pred)
    
    lgbm_path = MODELS_DIR / f"lgbm_{market}_{league or 'all'}.joblib"
    joblib.dump(lgbm, lgbm_path)
    results['lgbm_path'] = str(lgbm_path)
    
    if market in ["1x2", "euro_handicap"]:
        joblib.dump(le, MODELS_DIR / f"encoder_{league or 'all'}_{market}.joblib")
    
    results['train_size'] = len(X_train)
    results['test_size'] = len(X_test)
    results['model_classes'] = list(model_classes)
    
    return results

def load_model(model_type: str = "xgboost", league: str = None, market: str = "1x2"):
    """Load a trained model"""
    model_path = MODELS_DIR / f"{model_type}_{market}_{league or 'all'}.joblib"
    
    if not model_path.exists():
        return None
    
    return joblib.load(model_path)

def load_encoder(league: str = None, market: str = "1x2"):
    """Load label encoder"""
    encoder_path = MODELS_DIR / f"encoder_{league or 'all'}_{market}.joblib"
    
    # Fallback to old format for backward compatibility
    if not encoder_path.exists():
        old_encoder_path = MODELS_DIR / f"encoder_{league or 'all'}.joblib"
        if old_encoder_path.exists():
            return joblib.load(old_encoder_path)
        return None
        
    return joblib.load(encoder_path)