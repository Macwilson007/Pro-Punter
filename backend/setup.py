"""
Pro Punter - One-shot Setup Script

Run this once to:
1. Download historical CSV data from football-data.co.uk
2. Import data into the SQLite database
3. Train ML models (XGBoost + LightGBM)

Usage: py setup.py
       py setup.py --train-only   (skip download/import if already done)
"""

import sys
import os
from pathlib import Path

# Ensure we can import from the backend root
os.chdir(Path(__file__).parent)
sys.path.insert(0, str(Path(__file__).parent))

def main():
    train_only = "--train-only" in sys.argv
    
    print("=" * 60)
    print("  Pro Punter - Setup")
    print("=" * 60)
    
    # Step 1: Initialize database
    print("\n[1/4] Initializing database...")
    from app.database import init_db
    init_db()
    print("  Database initialized.")
    
    if not train_only:
        # Step 2: Download historical data
        print("\n[2/4] Downloading historical match data...")
        from ml.download_data import download_all
        downloaded = download_all()
        
        if downloaded == 0:
            print("\n  WARNING: No CSV files downloaded. Check your internet connection.")
        
        # Step 3: Import data into database
        print("\n[3/4] Importing data into database...")
        from ml.data_loader import populate_database
        imported = populate_database()
        
        if imported == 0:
            print("\n  WARNING: No matches imported.")
    else:
        print("\n[2/4] Skipping download (--train-only)")
        print("[3/4] Skipping import (--train-only)")
    
    # Check we have enough data
    from app.database import get_connection
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM matches")
    total_matches = cursor.fetchone()[0]
    conn.close()
    
    if total_matches < 50:
        print(f"\n  ERROR: Only {total_matches} matches in database. Need at least 50.")
        return
    
    print(f"\n  Database has {total_matches} matches — ready for training.")
    
    # Step 4: Train models
    print("\n[4/4] Training ML models...")
    from ml.train import train_models
    
    markets = ["1x2", "btts", "over_25"]
    for market in markets:
        print(f"\n  Training {market} model...")
        result = train_models(league=None, market=market)
        
        if "error" in result:
            print(f"  ERROR: {result['error']}")
        else:
            accuracy = result.get("xgb_accuracy", 0)
            lgbm_acc = result.get("lgbm_accuracy", 0)
            train_size = result.get("train_size", 0)
            test_size = result.get("test_size", 0)
            print(f"  XGBoost accuracy:  {accuracy:.2%}")
            print(f"  LightGBM accuracy: {lgbm_acc:.2%}")
            print(f"  Training samples:  {train_size}")
            print(f"  Test samples:      {test_size}")
    
    # Summary
    print("\n" + "=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    
    models_dir = Path(__file__).parent / "models" / "trained"
    model_files = list(models_dir.glob("*.joblib")) if models_dir.exists() else []
    
    print(f"\n  Matches in database: {total_matches}")
    print(f"  Trained models:     {len(model_files)}")
    for f in model_files:
        print(f"    - {f.name}")
    
    print(f"\n  Next steps:")
    print(f"  1. Start the backend:  py -m uvicorn app.main:app --reload --port 8000")
    print(f"  2. Start the frontend: cd frontend && npx next dev")
    print(f"  3. Or just run:        start.bat")
    print(f"\n  API docs: http://localhost:8000/docs")


if __name__ == "__main__":
    main()
