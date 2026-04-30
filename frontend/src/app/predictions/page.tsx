'use client';

import { useState, useEffect } from 'react';
import PredictionCard from '@/components/PredictionCard';
import LeagueFilter from '@/components/LeagueFilter';
import api, { MARKETS } from '@/lib/api';
import { Prediction, League } from '@/types';

export default function PredictionsPage() {
  const [leagues, setLeagues] = useState<League[]>([]);
  const [selectedLeague, setSelectedLeague] = useState<string | null>(null);
  const [market, setMarket] = useState('1x2');
  const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getLeagues().then(setLeagues).catch(console.error);
  }, []);

  useEffect(() => {
    setLoading(true);
    api.getPredictions(selectedLeague || undefined, market, date)
      .then(data => {
        if (data && data.predictions) {
          setPredictions(data.predictions);
        } else {
          setPredictions([]);
        }
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [selectedLeague, market, date]);

  return (
    <div className="predictions-page">
      <header className="page-header">
        <h1 className="page-title">Predictions</h1>
        <p className="page-subtitle">Filter by league and market</p>
      </header>

      <div className="page-content">
        <aside className="filters-sidebar">
          <LeagueFilter
            leagues={leagues}
            selected={selectedLeague}
            onChange={setSelectedLeague}
          />
          <div className="market-filter" style={{ marginBottom: '1rem' }}>
            <h3 className="filter-title">Date</h3>
            <input 
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="input"
              style={{ width: '100%' }}
            />
          </div>
          <div className="market-filter">
            <h3 className="filter-title">Market</h3>
            <select
              value={market}
              onChange={(e) => setMarket(e.target.value)}
              className="input"
            >
              {MARKETS.map(m => (
                <option key={m.id} value={m.id}>{m.name}</option>
              ))}
            </select>
          </div>
        </aside>

        <main className="predictions-main">
          {loading ? (
            <div className="loading-state">
              <div className="spinner"></div>
            </div>
          ) : predictions.length > 0 ? (
            <div className="predictions-grid">
              {predictions.map((pred, idx) => (
                <PredictionCard key={idx} prediction={pred} showOdds />
              ))}
            </div>
          ) : (
            <div className="empty-state">
              <p>{selectedLeague ? "No predictions for this league." : "No predictions available for today."}</p>
            </div>
          )}
        </main>
      </div>

      <style>{`
        .predictions-page {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .page-header {
          margin-bottom: 1rem;
        }
        .page-title {
          font-size: 1.875rem;
          font-weight: 700;
        }
        .page-subtitle {
          color: var(--text-secondary);
          margin-top: 0.25rem;
        }
        .page-content {
          display: grid;
          grid-template-columns: 280px 1fr;
          gap: 2rem;
        }
        .filters-sidebar {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .filter-title {
          font-size: 0.75rem;
          color: var(--text-muted);
          margin-bottom: 0.5rem;
          text-transform: uppercase;
        }
        .market-filter {
          margin-top: 1rem;
        }
        .predictions-main {
          min-height: 400px;
        }
        .loading-state, .empty-state {
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 4rem;
          background: var(--surface);
          border-radius: 0.75rem;
          border: 1px solid var(--border);
        }
        .spinner {
          width: 40px;
          height: 40px;
          border: 3px solid var(--border);
          border-top-color: var(--primary);
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        .predictions-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1rem;
        }
        @media (max-width: 768px) {
          .page-content {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
}