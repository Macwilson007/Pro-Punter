'use client';

import { useState, useEffect } from 'react';
import PredictionCard from '@/components/PredictionCard';
import api, { MARKETS } from '@/lib/api';
import { Prediction } from '@/types';

export default function Home() {
  const [predictions, setPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [market, setMarket] = useState('1x2');

  useEffect(() => {
    fetchPredictions();
  }, [market]);

  const fetchPredictions = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getPredictions(undefined, market);
      if (data.predictions) {
        setPredictions(data.predictions);
      } else {
        setError(data.message || 'No predictions available');
      }
    } catch (err) {
      setError('Failed to fetch predictions. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <header className="page-header">
        <div>
          <h1 className="page-title">Dashboard</h1>
          <p className="page-subtitle">Today&apos;s AI Football Predictions</p>
        </div>
        <div className="market-selector">
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
      </header>

      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading predictions...</p>
        </div>
      )}

      {error && (
        <div className="error-state">
          <p>{error}</p>
          <button className="btn btn-primary" onClick={fetchPredictions}>
            Retry
          </button>
        </div>
      )}

      {!loading && !error && predictions.length === 0 && (
        <div className="empty-state">
          <p>No predictions available yet.</p>
          <p className="hint">Train the model first to get predictions.</p>
        </div>
      )}

      <div className="predictions-grid">
        {predictions.map((pred, idx) => (
          <PredictionCard key={idx} prediction={pred} showOdds />
        ))}
      </div>

      <style>{`
        .dashboard {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
        }
        .page-title {
          font-size: 1.875rem;
          font-weight: 700;
        }
        .page-subtitle {
          color: var(--text-secondary);
          margin-top: 0.25rem;
        }
        .market-selector select {
          min-width: 180px;
        }
        .loading-state, .error-state, .empty-state {
          text-align: center;
          padding: 4rem 2rem;
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
          margin: 0 auto 1rem;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        .hint {
          font-size: 0.875rem;
          color: var(--text-muted);
          margin-top: 0.5rem;
        }
        .predictions-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
          gap: 1rem;
        }
      `}</style>
    </div>
  );
}