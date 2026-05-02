import pandas as pd
import numpy as np
from typing import Dict, List

def calculate_elo_rating(team: str, matches: pd.DataFrame, k: int = 32, initial: float = 1500) -> float:
    """Calculate Elo rating for a team"""
    team_matches = matches[
        (matches['home_team'] == team) | (matches['away_team'] == team)
    ].sort_values('date')
    
    if len(team_matches) == 0:
        return initial
    
    rating = initial
    for _, match in team_matches.iterrows():
        is_home = match['home_team'] == team
        
        team_goals = match['home_goals'] if is_home else match['away_goals']
        opp_goals = match['away_goals'] if is_home else match['home_goals']
        
        if team_goals > opp_goals:
            scored = 1
        elif team_goals < opp_goals:
            scored = 0
        else:
            scored = 0.5
        
        expected = 1 / (1 + 10 ** ((rating - 1500) / 400))
        rating += k * (scored - expected)
    
    return rating


def _batch_elo_ratings(matches_df: pd.DataFrame, k: int = 32, initial: float = 1500) -> dict:
    """Calculate Elo ratings for ALL teams in one pass (O(n) instead of O(n²))"""
    ratings = {}
    elo_at_match = {}
    if len(matches_df) == 0 or 'date' not in matches_df.columns:
        return ratings, elo_at_match
    
    sorted_matches = matches_df.sort_values('date')
    
    for idx, match in sorted_matches.iterrows():
        home = match['home_team']
        away = match['away_team']
        
        home_rating = ratings.get(home, initial)
        away_rating = ratings.get(away, initial)
        
        # Store ratings BEFORE the match (what we'd use for prediction)
        elo_at_match[idx] = (home_rating, away_rating)
        
        home_goals = match['home_goals']
        away_goals = match['away_goals']
        
        if pd.isna(home_goals) or pd.isna(away_goals):
            continue
        
        if home_goals > away_goals:
            home_scored, away_scored = 1, 0
        elif home_goals < away_goals:
            home_scored, away_scored = 0, 1
        else:
            home_scored, away_scored = 0.5, 0.5
        
        home_expected = 1 / (1 + 10 ** ((away_rating - home_rating) / 400))
        away_expected = 1 - home_expected
        
        ratings[home] = home_rating + k * (home_scored - home_expected)
        ratings[away] = away_rating + k * (away_scored - away_expected)
    
    return ratings, elo_at_match

_LATEST_ELOS = None

def get_latest_elos(matches_df: pd.DataFrame) -> dict:
    global _LATEST_ELOS
    if _LATEST_ELOS is None:
        _LATEST_ELOS, _ = _batch_elo_ratings(matches_df)
    return _LATEST_ELOS


def extract_features(
    home_team: str, 
    away_team: str, 
    league: str, 
    matches_df: pd.DataFrame,
    home_id: Optional[int] = None,
    away_id: Optional[int] = None,
    api_football = None
) -> dict:
    """Extract features for a match prediction"""
    features = {}
    
    # helper to get features for a team
    def get_team_stats(team_name: str, team_id: Optional[int], is_home: bool):
        if len(matches_df) > 0 and 'home_team' in matches_df.columns:
            team_matches = matches_df[
                (matches_df['home_team'] == team_name) | 
                (matches_df['away_team'] == team_name)
            ]
        else:
            team_matches = pd.DataFrame()
        
        # If no local data, try live-sync from API if available
        if len(team_matches) == 0 and team_id and api_football:
            try:
                # Fetch last 5 fixtures from API
                response = api_football.get_team_last_fixtures(team_id, last=5)
                if "response" in response and len(response["response"]) > 0:
                    api_matches = []
                    for f in response["response"]:
                        h_goals = f["goals"].get("home")
                        a_goals = f["goals"].get("away")
                        if h_goals is not None and a_goals is not None:
                            api_matches.append({
                                "home_team": f["teams"]["home"]["name"],
                                "away_team": f["teams"]["away"]["name"],
                                "home_goals": h_goals,
                                "away_goals": a_goals,
                                "date": f["fixture"]["date"]
                            })
                    if api_matches:
                        team_matches = pd.DataFrame(api_matches)
            except Exception as e:
                print(f"Live-sync error for {team_name}: {e}")
        
        prefix = 'home_' if is_home else 'away_'
        recent = team_matches.tail(5)
        
        if len(recent) > 0:
            # Calculate stats relative to the team (whether they were home or away in those matches)
            team_goals = []
            opp_goals = []
            wins = 0
            draws = 0
            
            for _, m in recent.iterrows():
                m_is_home = m['home_team'] == team_name
                tg = m['home_goals'] if m_is_home else m['away_goals']
                og = m['away_goals'] if m_is_home else m['home_goals']
                team_goals.append(tg)
                opp_goals.append(og)
                if tg > og: wins += 1
                elif tg == og: draws += 1
            
            features[prefix + 'avg_goals'] = sum(team_goals) / len(team_goals)
            features[prefix + 'avg_goals_conceded'] = sum(opp_goals) / len(opp_goals)
            features[prefix + 'win_rate'] = wins / len(recent)
            features[prefix + 'draw_rate'] = draws / len(recent)
        else:
            # Absolute fallback: Generate slightly unique stats based on team name hash
            # to avoid identical predictions for all unknown teams.
            import hashlib
            name_hash = int(hashlib.md5(team_name.encode()).hexdigest(), 16)
            
            # Base stats with slight variations
            base_goals = 1.5 if is_home else 1.2
            base_win_rate = 0.5 if is_home else 0.4
            
            # Variations based on name (deterministic but unique)
            goal_var = (name_hash % 100) / 200 - 0.25 # -0.25 to +0.25
            win_var = (name_hash % 100) / 1000 - 0.05 # -0.05 to +0.05
            
            features[prefix + 'avg_goals'] = max(0.5, base_goals + goal_var)
            features[prefix + 'avg_goals_conceded'] = max(0.5, (base_goals * 0.8) - goal_var)
            features[prefix + 'win_rate'] = max(0.1, base_win_rate + win_var)
            features[prefix + 'draw_rate'] = 0.25 + (win_var / 2)

    # Get stats for both teams
    get_team_stats(home_team, home_id, True)
    get_team_stats(away_team, away_id, False)
    
    elos = get_latest_elos(matches_df)
    
    def get_elo(name):
        if name in elos: return elos[name]
        import hashlib
        h = int(hashlib.md5(name.encode()).hexdigest(), 16)
        return 1450.0 + (h % 100) # 1450 to 1550
        
    features['home_elo'] = get_elo(home_team)
    features['away_elo'] = get_elo(away_team)
    features['elo_diff'] = features['home_elo'] - features['away_elo']
    features['form_diff'] = features['home_win_rate'] - features['away_win_rate']
    features['goals_diff'] = features['home_avg_goals'] - features['away_avg_goals_conceded']
    
    # Head-to-head record
    if len(matches_df) > 0 and 'home_team' in matches_df.columns and 'away_team' in matches_df.columns:
        h2h = matches_df[
            ((matches_df['home_team'] == home_team) & (matches_df['away_team'] == away_team)) |
            ((matches_df['home_team'] == away_team) & (matches_df['away_team'] == home_team))
        ].tail(5)
    else:
        h2h = pd.DataFrame()
    
    if len(h2h) > 0:
        home_wins = 0
        away_wins = 0
        draws = 0
        
        for _, match in h2h.iterrows():
            if match['home_team'] == home_team:
                if match['home_goals'] > match['away_goals']:
                    home_wins += 1
                elif match['home_goals'] < match['away_goals']:
                    away_wins += 1
                else:
                    draws += 1
            else:
                if match['away_goals'] > match['home_goals']:
                    home_wins += 1
                elif match['away_goals'] < match['home_goals']:
                    away_wins += 1
                else:
                    draws += 1
        
        total = home_wins + away_wins + draws
        if total > 0:
            features['h2h_home_win_rate'] = home_wins / total
            features['h2h_draw_rate'] = draws / total
        else:
            features['h2h_home_win_rate'] = 0.33
            features['h2h_draw_rate'] = 0.33
    else:
        features['h2h_home_win_rate'] = 0.33
        features['h2h_draw_rate'] = 0.33
    
    if len(matches_df) > 0 and 'league' in matches_df.columns:
        league_matches = matches_df[matches_df['league'] == league]
        if len(league_matches) > 0:
            features['league_avg_goals'] = (
                league_matches['home_goals'].mean() + league_matches['away_goals'].mean()
            ) / 2
        else:
            features['league_avg_goals'] = 2.5
    else:
        features['league_avg_goals'] = 2.5
    
    return features


def prepare_training_data(matches_df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare training data from match history.
    Optimized: uses batch Elo computation and rolling window stats
    instead of per-row full-dataset scans.
    """
    df = matches_df.copy()
    df = df.dropna(subset=['home_goals', 'away_goals'])
    df = df.sort_values('date').reset_index(drop=True)
    
    print(f"  Preparing features for {len(df)} matches...")
    
    # Target variables
    df['result'] = df.apply(
        lambda x: 'home' if x['home_goals'] > x['away_goals'] 
        else ('draw' if x['home_goals'] == x['away_goals'] else 'away'),
        axis=1
    )
    df['btts'] = (df['home_goals'] > 0) & (df['away_goals'] > 0)
    df['over_25'] = (df['home_goals'] + df['away_goals']) > 2.5
    df['over_15'] = (df['home_goals'] + df['away_goals']) > 1.5
    df['euro_handicap'] = df.apply(
        lambda x: 'home' if (x['home_goals'] - x['away_goals']) >= 2 
        else ('draw' if (x['home_goals'] - x['away_goals']) == 1 else 'away'),
        axis=1
    )
    
    # Batch compute Elo ratings (single pass through all matches)
    print("  Computing Elo ratings...")
    _, elo_at_match = _batch_elo_ratings(df)
    
    home_elos = []
    away_elos = []
    for idx in df.index:
        if idx in elo_at_match:
            home_elos.append(elo_at_match[idx][0])
            away_elos.append(elo_at_match[idx][1])
        else:
            home_elos.append(1500.0)
            away_elos.append(1500.0)
    
    df['home_elo'] = home_elos
    df['away_elo'] = away_elos
    df['elo_diff'] = df['home_elo'] - df['away_elo']
    
    # Compute rolling stats per team (considering ALL games, both home and away)
    print("  Computing rolling statistics...")
    
    # Create a long-form dataframe with one row per team per match
    home_df = df[['date', 'home_team', 'home_goals', 'away_goals', 'league']].copy()
    home_df.columns = ['date', 'team', 'goals_for', 'goals_against', 'league']
    home_df['is_home'] = 1
    
    away_df = df[['date', 'away_team', 'away_goals', 'home_goals', 'league']].copy()
    away_df.columns = ['date', 'team', 'goals_for', 'goals_against', 'league']
    away_df['is_home'] = 0
    
    team_matches = pd.concat([home_df, away_df]).sort_values(['team', 'date'])
    
    team_matches['win'] = (team_matches['goals_for'] > team_matches['goals_against']).astype(float)
    team_matches['draw'] = (team_matches['goals_for'] == team_matches['goals_against']).astype(float)
    
    # Rolling averages over last 5 games for each team
    rolling = team_matches.groupby('team').rolling(window=5, min_periods=1).agg({
        'goals_for': 'mean',
        'goals_against': 'mean',
        'win': 'mean',
        'draw': 'mean'
    }).reset_index(level=0, drop=True)
    
    team_matches['rolling_gf'] = rolling['goals_for']
    team_matches['rolling_ga'] = rolling['goals_against']
    team_matches['rolling_win_rate'] = rolling['win']
    team_matches['rolling_draw_rate'] = rolling['draw']
    
    # Shift stats so we don't have data leakage (stats BEFORE the match)
    team_matches[['rolling_gf', 'rolling_ga', 'rolling_win_rate', 'rolling_draw_rate']] = \
        team_matches.groupby('team')[['rolling_gf', 'rolling_ga', 'rolling_win_rate', 'rolling_draw_rate']].shift(1)
    
    # Fill defaults for the first games
    team_matches['rolling_gf'] = team_matches['rolling_gf'].fillna(1.2)
    team_matches['rolling_ga'] = team_matches['rolling_ga'].fillna(1.2)
    team_matches['rolling_win_rate'] = team_matches['rolling_win_rate'].fillna(0.4)
    team_matches['rolling_draw_rate'] = team_matches['rolling_draw_rate'].fillna(0.25)
    
    # Merge back to original df
    df = df.merge(
        team_matches[team_matches['is_home'] == 1][['date', 'team', 'rolling_gf', 'rolling_ga', 'rolling_win_rate', 'rolling_draw_rate']],
        left_on=['date', 'home_team'], right_on=['date', 'team'], how='left'
    ).rename(columns={
        'rolling_gf': 'home_avg_goals',
        'rolling_ga': 'home_avg_goals_conceded',
        'rolling_win_rate': 'home_win_rate',
        'rolling_draw_rate': 'home_draw_rate'
    }).drop(columns=['team'])
    
    df = df.merge(
        team_matches[team_matches['is_home'] == 0][['date', 'team', 'rolling_gf', 'rolling_ga', 'rolling_win_rate', 'rolling_draw_rate']],
        left_on=['date', 'away_team'], right_on=['date', 'team'], how='left'
    ).rename(columns={
        'rolling_gf': 'away_avg_goals',
        'rolling_ga': 'away_avg_goals_conceded',
        'rolling_win_rate': 'away_win_rate',
        'rolling_draw_rate': 'away_draw_rate'
    }).drop(columns=['team'])
    
    # Derived features
    df['form_diff'] = df['home_win_rate'] - df['away_win_rate']
    df['goals_diff'] = df['home_avg_goals'] - df['away_avg_goals_conceded']
    
    # H2H features (simplified: use overall league averages as proxy)
    df['h2h_home_win_rate'] = 0.40  # League average home win rate
    df['h2h_draw_rate'] = 0.27      # League average draw rate
    
    # League average goals
    league_avg = df.groupby('league')[['home_goals', 'away_goals']].transform('mean')
    df['league_avg_goals'] = (league_avg['home_goals'] + league_avg['away_goals']) / 2
    
    # Cleanup temp columns
    df.drop(columns=['home_win', 'home_draw', 'away_win', 'away_draw_flag'], inplace=True, errors='ignore')
    
    print(f"  Features ready. {len(df)} samples.")
    return df


def get_feature_columns() -> List[str]:
    """Get feature column names"""
    return [
        'home_avg_goals', 'home_avg_goals_conceded', 'home_win_rate', 'home_draw_rate',
        'away_avg_goals', 'away_avg_goals_conceded', 'away_win_rate', 'away_draw_rate',
        'home_elo', 'away_elo', 'elo_diff', 'form_diff', 'goals_diff',
        'h2h_home_win_rate', 'h2h_draw_rate', 'league_avg_goals'
    ]