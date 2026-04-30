export interface League {
  id: string;
  name: string;
  country: string;
  tier: number;
}

export interface Prediction {
  id?: number;
  home_team: string;
  away_team: string;
  league: string;
  market: string;
  kickoff?: string;
  match_date?: string;
  prediction: string;
  confidence: number;
  model_prob?: { [key: string]: number };
  xgb_prob?: { [key: string]: number };
  lgbm_prob?: { [key: string]: number };
  ensemble_prob?: { [key: string]: number };
  odds?: { [key: string]: number };
  value_bet?: boolean;
  kelly_stake?: number;
  edge?: number;
  actual_result?: string;
  best_pick?: {
    best_market: string;
    best_prediction: string;
    best_confidence: number;
    all_options: { [key: string]: { prediction: string, confidence: number } };
  };
  created_at?: string;
}

export interface Bet {
  id: number;
  prediction_id: number;
  platform: string;
  market: string;
  selection: string;
  stake: number;
  odds: number;
  status: 'pending' | 'won' | 'lost';
  profit?: number;
  bet_date: string;
}

export interface Performance {
  total_predictions: number;
  correct: number;
  accuracy: number;
  roi?: number;
}

export interface TeamForm {
  wins: number;
  draws: number;
  losses: number;
  points: number;
  gf: number;
  ga: number;
  gd: number;
}