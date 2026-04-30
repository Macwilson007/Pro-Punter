import sys
import os
import pandas as pd
from typing import Optional

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from ml.predict import get_best_prediction_for_match

# Mock data
matches_df = pd.DataFrame([
    {"home_team": "Team A", "away_team": "Team B", "home_goals": 2, "away_goals": 1, "league": "test", "date": "2024-01-01"},
    {"home_team": "Team A", "away_team": "Team C", "home_goals": 3, "away_goals": 0, "league": "test", "date": "2024-01-05"},
    {"home_team": "Team D", "away_team": "Team B", "home_goals": 1, "away_goals": 1, "league": "test", "date": "2024-01-10"},
])

print("Testing Best Pick logic...")
best = get_best_prediction_for_match("Team A", "Team B", "test", matches_df)
print(f"Best Market: {best['best_market']}")
print(f"Best Prediction: {best['best_prediction']}")
print(f"Confidence: {best['best_confidence']}")
print(f"All Options: {best['all_options'].keys()}")
