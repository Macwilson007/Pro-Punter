# SPEC.md: Pro Punter - Football Prediction Platform

---

### 1. Project Overview

| Field | Details |
|-------|---------|
| **Project Name** | Pro Punter |
| **Type** | Full-stack Web Application |
| **Core Functionality** | AI-powered football match predictions with value betting detection and Kelly criterion staking |
| **Target Users** | Football bettors using Bet9ja, Sportybet, 1xBet, Betking |
| **Deployment** | Vercel |
| **Data Sources** | API-Football (free tier) + football-data.co.uk |

---

### 2. Technical Stack

| Component | Technology |
|-----------|------------|
| Frontend | Next.js 14 (React 18) + TypeScript |
| Styling | Tailwind CSS |
| Backend API | FastAPI (Python) |
| ML Models | XGBoost, LightGBM, scikit-learn |
| Database | SQLite (local) / PostgreSQL (Supabase ready) |
| Data (Historical) | football-data.co.uk (free CSV) |
| Data (Live) | API-Football free tier |
| Authentication | NextAuth.js (credentials) |
| Deployment | Vercel |

---

### 3. Supported Leagues (30)

Organized by **predictability tier**:

#### Tier 1: High Predictability (55-65%)
| # | League | Country | Predictability |
|---|--------|---------|---------------|
| 1 | Premier League | England | 55.7% |
| 2 | Championship | England | 63.8% |
| 3 | Bundesliga | Germany | 59.6% |
| 4 | Bundesliga 2 | Germany | 53.0% |
| 5 | La Liga | Spain | 57.0% |
| 6 | La Liga 2 | Spain | 52.0% |
| 7 | Ligue 1 | France | 60.3% |
| 8 | Ligue 2 | France | 54.1% |
| 9 | Serie A | Italy | 58.5% |
| 10 | Serie B | Italy | 49.9% |
| 11 | Eredivisie | Netherlands | 52-60% |
| 12 | Liga Portugal | Portugal | 59.6% |

#### Tier 2: Medium Predictability (50-55%)
| # | League | Country | Predictability |
|---|--------|---------|---------------|
| 13 | Scottish Premiership | Scotland | ~52% |
| 14 | Scottish Championship | Scotland | ~50% |
| 15 | Belgian Pro League | Belgium | ~54% |
| 16 | Turkish Super Lig | Turkey | ~53% |
| 17 | Greek Super League | Greece | ~51% |
| 18 | Polish Ekstraklasa | Poland | ~50% |
| 19 | Austrian Bundesliga | Austria | ~52% |
| 20 | Swiss Super League | Switzerland | ~51% |
| 21 | Danish Superliga | Denmark | ~52% |
| 22 | Swedish Allsvenskan | Sweden | 58.8% |
| 23 | Norwegian Eliteserien | Norway | 64.0% |
| 24 | Czech Liga | Czech Republic | ~50% |

#### Tier 3: High-Value/League-Specific
| # | League | Country | Notes |
|---|--------|---------|-------|
| 25 | MLS | USA | High scoring |
| 26 | Saudi Pro League | Saudi Arabia | Big money league |
| 27 | Argentinian Liga Argentina | Argentina | High home advantage |
| 28 | Brazilian Serie A | Brazil | 52.7% |
| 29 | J-League | Japan | 50.7% |
| 30 | Chinese Super League | China | 60.9% |

---

### 4. Betting Markets

| Market | Description | Target Accuracy |
|--------|-------------|------------------|
| 1X2 | Match Result (Home/Draw/Away) | 52-56% |
| BTS | Both Teams To Score | 65-71% |
| Over 2.5 | Over 2.5 Goals | 68-74% |
| Double Chance | 1X, 12, X2 | 70-78% |

---

### 5. ML Architecture

#### Features (Input Variables)
- **Team Strength:** Elo ratings, xG differential
- **Form:** Rolling 5-match home/away wins
- **Head-to-Head:** Last 5 H2H results
- **Home/Away:** Home win %, Away win %
- **Injury Count:** Sidelined players per team
- **Market Odds:** Pre-match odds (converted to implied prob)

#### Models
| Model | Use Case |
|-------|----------|
| XGBoost | Primary classifier (best accuracy) |
| LightGBM | Probability calibration (best log loss) |
| Ensemble | Weighted average of XGB + LGBM |

#### Training Pipeline
```
Historical Data (football-data.co.uk)
    ↓
Feature Engineering
    ↓
Train/Test Split (80/20)
    ↓
Model Training (XGBoost + LightGBM)
    ↓
Model Evaluation (accuracy, ROI, log loss)
    ↓
Save Model (.joblib)
```

---

### 6. Value Bet Detection

| Concept | Formula |
|---------|---------|
| **Model Probability** | P(home win) from XGBoost |
| **Implied Probability** | 1 / decimal_odds |
| **Expected Value (EV)** | (P × odds) - 1 |
| **Value Bet Condition** | Model prob > Implied prob + threshold |

#### Kelly Criterion Staking
```
Stake = (Bankroll × Kelly%) × Edge

Kelly% = (P × odds - 1) / (odds - 1) × Kelly multiplier
Kelly multiplier = 0.25 (recommended for safety)
```

---

### 7. API-Football Integration (Free Tier)

| Endpoint | Calls/Day | Purpose |
|----------|-----------|---------|
| `get_events` (fixtures) | 10-15 | Get upcoming matches |
| `get_predictions` | 5-10 | xG predictions |
| `get_odds` | 5-10 | Live odds |
| `get_sidelined` | 5 | Injuries |
| **Total** | ~25-40/day | Within 100 limit |

#### API Response Caching
- Store fetched data in SQLite
- Cache TTL: 1 hour for fixtures, 6 hours for odds
- Reduces duplicate API calls

---

### 8. Frontend (Next.js)

#### Pages & Routes
| Route | Page | Description |
|-------|------|-------------|
| `/` | Home | Dashboard with today's predictions |
| `/predictions` | Predictions | Filter by league, date, market |
| `/performance` | Model Performance | Accuracy stats, ROI tracking |
| `/betting` | Betting History | Track placed bets |
| `/settings` | Settings | API key, platform preferences |

#### Components
- `PredictionCard` - Display single prediction
- `LeagueFilter` - Filter by league
- `DatePicker` - Select date range
- `BetBuilder` - Build bet slip
- `StatsChart` - Performance charts

#### Betting Platform Links
| Platform | URL Template |
|----------|---------------|
| Bet9ja | `bet9ja.com/football/{league_id}` |
| Sportybet | `sportybet.com/sport/football/{league_id}` |
| 1xBet | `1xbet.com/en/line/football/{league_id}` |
| Betking | `betking.com/sports/football/{league_id}` |

---

### 9. Backend API (FastAPI)

#### Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/predictions` | Get today's predictions |
| GET | `/api/predictions/{league}` | Get predictions by league |
| POST | `/api/predict` | Generate new prediction |
| GET | `/api/odds/{match_id}` | Get live odds |
| GET | `/api/leagues` | List supported leagues |
| POST | `/api/bets` | Record placed bet |
| GET | `/api/bets` | Get bet history |
| GET | `/api/performance` | Model performance stats |
| POST | `/api/train` | Retrain model |

---

### 10. Database Schema

```sql
-- Matches (training data)
CREATE TABLE matches (
    id INTEGER PRIMARY KEY,
    league TEXT,
    season TEXT,
    date DATE,
    home_team TEXT,
    away_team TEXT,
    home_goals INTEGER,
    away_goals INTEGER,
    xG_home REAL,
    xG_away REAL,
    odds_home REAL,
    odds_draw REAL,
    odds_away REAL
);

-- Predictions (generated)
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY,
    match_id INTEGER,
    league TEXT,
    date DATE,
    home_team TEXT,
    away_team TEXT,
    predicted_outcome TEXT,
    confidence REAL,
    model_prob REAL,
    odds REAL,
    value_bet BOOLEAN,
    actual_result TEXT,
    created_at TIMESTAMP
);

-- Bet History
CREATE TABLE bets (
    id INTEGER PRIMARY KEY,
    prediction_id INTEGER,
    platform TEXT,
    market TEXT,
    selection TEXT,
    stake REAL,
    odds REAL,
    status TEXT,
    profit REAL,
    bet_date TIMESTAMP
);

-- Models
CREATE TABLE models (
    id INTEGER PRIMARY KEY,
    name TEXT,
    league TEXT,
    created_at TIMESTAMP,
    accuracy REAL,
    path TEXT
);

-- Settings
CREATE TABLE settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
```

---

### 11. Project Structure

```
pro-punter/
├��─ frontend/                    # Next.js app
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── globals.css
│   │   │   ├── predictions/
│   │   │   │   └── page.tsx
│   │   │   ├── performance/
│   │   │   │   └── page.tsx
│   │   │   ├── betting/
│   │   │   │   └── page.tsx
│   │   │   └── settings/
│   │   │       └── page.tsx
│   │   ├── components/
│   │   │   ├── PredictionCard.tsx
│   │   │   ├── LeagueFilter.tsx
│   │   │   ├── DatePicker.tsx
│   │   │   ├── BetBuilder.tsx
│   │   │   ├── StatsChart.tsx
│   │   │   ├── Navbar.tsx
│   │   │   └── Footer.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   ├── utils.ts
│   │   │   └── auth.ts
│   │   └── types/
│   │       └── index.ts
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   └── .env.local.example
├── backend/                     # FastAPI app
│   ├── app/
│   │   ├── main.py              # FastAPI entry
│   │   ├── config.py           # Settings
│   │   ├── database.py          # SQLite setup
│   │   └── router.py           # API routes
│   ├── api/
│   │   ├── football.py          # API-Football client
│   │   └── predictions.py      # Prediction endpoints
│   ├── ml/
│   │   ├── data_loader.py      # football-data.co.uk
│   │   ├── features.py        # Feature engineering
│   │   ├── train.py           # Model training
│   │   └── predict.py          # Inference
│   ├── models/
│   │   └── trained/            # Saved models
│   ├── data/
│   │   ├── raw/               # CSV downloads
│   │   └── cache/             # SQLite DB
│   ├── requirements.txt
│   └── vercel.json
├── SPEC.md
└── README.md
```

---

### 12. Deployment (Vercel)

#### Frontend (Next.js)
```json
// frontend/vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "framework": "nextjs"
}
```

#### Backend (Python)
```json
// backend/vercel.json
{
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "app/main.py"
    }
  ]
}
```

#### Environment Variables

```bash
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Backend (.env)
API_FOOTBALL_KEY=your_api_key_here
FOOTBALL_DATA_API_KEY=optional
DATABASE_PATH=data/pro punter.db
KELLY_MULTIPLIER=0.25
```

---

### 13. Development Timeline

| Phase | Tasks | Duration |
|-------|-------|----------|
| **Phase 1** | Project setup, data pipeline, API integration | Week 1-2 |
| **Phase 2** | Feature engineering, model training | Week 3 |
| **Phase 3** | FastAPI endpoints, value bet logic | Week 4 |
| **Phase 4** | Next.js frontend components | Week 5 |
| **Phase 5** | Pages, routing, styling | Week 6 |
| **Phase 6** | Testing, deployment | Week 7 |

---

### 14. Known Limitations

1. **Accuracy ceiling:** ~52-56% for 1X2 is the realistic ceiling
2. **API limits:** Free tier limited to ~50 calls/day
3. **No live betting:** Pre-match predictions only
4. **Historical data:** Need to download CSV manually for training
5. **No guarantees:** Betting involves risk; user bears responsibility

---

### 15. Next Steps

1. **Initialize frontend** - `npx create-next-app@latest frontend`
2. **Initialize backend** - Create FastAPI structure
3. **Get API keys** - Register for API-Football free tier
4. **Download historical data** - football-data.co.uk CSV