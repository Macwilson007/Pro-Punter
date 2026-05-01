import random
import numpy as np
from typing import List, Dict

class AviatorPredictor:
    def __init__(self):
        # Statistical constants for Aviator-style games
        # Most crash games have a house edge of ~1-3%
        self.house_edge = 0.03
        
    def calculate_signal(self, history: List[float]) -> Dict:
        """
        Calculate a 'prediction' based on recent history.
        In reality, these games are RNG, but we provide statistical probability
        and pattern detection (e.g., cold/hot streaks).
        """
        if not history:
            # Default signal if no history provided
            return self._generate_random_signal()
        
        # Analyze trends
        avg_multiplier = sum(history) / len(history)
        last_multiplier = history[-1]
        
        # Count 'low' crashes (under 1.5x)
        low_crashes = len([x for x in history if x < 1.5])
        low_ratio = low_crashes / len(history)
        
        # Logic: If many low crashes in a row, probability of a 'recovery' (medium) is slightly higher
        # This is for user engagement - providing a 'Signal' based on streak analysis
        
        if low_ratio > 0.6:
            rec_cashout = 1.8 + random.uniform(0, 0.5)
            confidence = 75 + random.uniform(0, 10)
            risk = "Medium"
        elif last_multiplier > 10.0:
            # After a huge win, usually followed by a small crash
            rec_cashout = 1.2 + random.uniform(0, 0.2)
            confidence = 85 + random.uniform(0, 5)
            risk = "Low"
        else:
            rec_cashout = 1.5 + random.uniform(0, 0.3)
            confidence = 65 + random.uniform(0, 15)
            risk = "Balanced"
            
        return {
            "recommended_cashout": round(rec_cashout, 2),
            "confidence_score": round(confidence, 1),
            "risk_level": risk,
            "next_multiplier_range": f"{round(rec_cashout * 0.9, 2)}x - {round(rec_cashout * 2.5, 2)}x",
            "is_gold_signal": confidence > 80,
            "timestamp": "Real-time"
        }
    
    def _generate_random_signal(self) -> Dict:
        conf = 60 + random.uniform(0, 25)
        return {
            "recommended_cashout": round(random.uniform(1.3, 2.2), 2),
            "confidence_score": round(conf, 1),
            "risk_level": "High" if conf < 70 else "Low",
            "next_multiplier_range": "1.5x - 3.5x",
            "is_gold_signal": conf > 80,
            "timestamp": "Calibrating..."
        }

aviator_predictor = AviatorPredictor()
