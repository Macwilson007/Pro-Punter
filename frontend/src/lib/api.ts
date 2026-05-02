const NEXT_PUBLIC_API_URL = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost' ? '/api' : 'http://localhost:8000');

// Handle the case where NEXT_PUBLIC_API_URL is '/api' to avoid double slashes or redundant prefixes
const API_URL = NEXT_PUBLIC_API_URL.startsWith('/') ? '' : NEXT_PUBLIC_API_URL;

async function fetchAPI(endpoint: string, options?: RequestInit) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`);
  }

  return response.json();
}

export const api = {
  getLeagues: () => fetchAPI('/api/leagues'),
  
  getPredictions: (league?: string, market?: string, date?: string) => {
    let url = `/api/predictions/today?league=${league || ''}&market=${market || '1x2'}`;
    if (date) url += `&date=${date}`;
    return fetchAPI(url);
  },
  
  getPredictionsByLeague: (leagueId: string, date?: string) => 
    fetchAPI(`/api/predictions/${leagueId}${date ? `?date=${date}` : ''}`),
  
  createPrediction: (data: {
    home_team: string;
    away_team: string;
    league: string;
    market: string;
  }) => fetchAPI('/api/predict', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  getOdds: (matchId: string, leagueId?: string) => 
    fetchAPI(`/api/odds/${matchId}${leagueId ? `?league_id=${leagueId}` : ''}`),
  
  trainModel: (league?: string, market?: string) => fetchAPI('/api/train', {
    method: 'POST',
    body: JSON.stringify({ league, market }),
  }),
  
  getPerformance: (league?: string) => 
    fetchAPI(`/api/performance${league ? `?league=${league}` : ''}`),
  
  recordBet: (data: {
    prediction_id: number;
    platform: string;
    market: string;
    selection: string;
    stake: number;
    odds: number;
  }) => fetchAPI('/api/bets', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  getBets: (platform?: string, status?: string) => 
    fetchAPI(`/api/bets?platform=${platform || ''}&status=${status || ''}`),
  
  updateBet: (betId: number, status: string, profit?: number) => fetchAPI(`/api/bets/${betId}`, {
    method: 'PUT',
    body: JSON.stringify({ status, profit }),
  }),
  
  getConfig: () => fetchAPI('/api/config'),
  
  updateConfig: (key: string, value: string) => fetchAPI('/api/config', {
    method: 'POST',
    body: JSON.stringify({ key, value }),
  }),
  
  syncResults: (league?: string) => fetchAPI(`/api/predictions/sync-results${league ? `?league=${league}` : ''}`, {
    method: 'POST',
  }),
  
  getAviatorPrediction: (history: number[]) => fetchAPI('/api/aviator/predict', {
    method: 'POST',
    body: JSON.stringify({ history }),
  }),
};

export const PLATFORMS = [
  { id: 'bet9ja', name: 'Bet9ja', url: 'https://bet9ja.com' },
  { id: 'sportybet', name: 'Sportybet', url: 'https://sportybet.com' },
  { id: '1xbet', name: '1xBet', url: 'https://1xbet.com' },
  { id: 'betking', name: 'Betking', url: 'https://betking.com' },
];

export const MARKETS = [
  { id: '1x2', name: 'Match Result', options: ['home', 'draw', 'away'] },
  { id: 'double_chance', name: 'Double Chance', options: ['1X', '12', 'X2'] },
  { id: 'euro_handicap', name: 'Handicap (1X2)', options: ['home', 'draw', 'away'] },
  { id: 'btts', name: 'Both Teams To Score', options: ['yes', 'no'] },
  { id: 'over_25', name: 'Over 2.5 Goals', options: ['yes', 'no'] },
  { id: 'over_15', name: 'Over 1.5 Goals', options: ['yes', 'no'] },
];

export default api;