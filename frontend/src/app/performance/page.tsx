'use client';

import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { Performance } from '@/types';
import { formatPercentage, formatCurrency } from '@/lib/utils';

export default function PerformancePage() {
  const [performance, setPerformance] = useState<Performance | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);

  useEffect(() => {
    loadPerformance();
  }, []);

  const loadPerformance = async () => {
    setLoading(true);
    try {
      const data = await api.getPerformance();
      setPerformance(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSyncResults = async () => {
    setSyncing(true);
    try {
      await api.syncResults();
      await loadPerformance();
    } catch (error) {
      console.error(error);
      alert('Failed to sync results. Check backend logs.');
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="performance-page">
      <header className="page-header">
        <div>
          <h1 className="page-title">Model Performance</h1>
          <p className="page-subtitle">Track prediction accuracy and ROI</p>
        </div>
        <button 
          className="btn btn-primary"
          onClick={handleSyncResults}
          disabled={syncing}
        >
          {syncing ? 'Syncing...' : 'Sync Actual Results'}
        </button>
      </header>

      <div className="stats-grid">
        <div className="stat-card">
          <span className="stat-label">Total Predictions</span>
          <span className="stat-value">{performance?.total_predictions || 0}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Correct Predictions</span>
          <span className="stat-value">{performance?.correct || 0}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Accuracy</span>
          <span className="stat-value">
            {formatPercentage(performance?.accuracy || 0)}
          </span>
        </div>
        <div className="stat-card">
          <span className="stat-label">ROI</span>
          <span className="stat-value">
            {formatCurrency(performance?.roi || 0)}
          </span>
        </div>
      </div>

      <div className="info-card">
        <h2>How It Works</h2>
        <ul>
          <li>
            <strong>1X2 Market:</strong> Predicts home win, draw, or away win
          </li>
          <li>
            <strong>BTS:</strong> Both Teams To Score (yes/no)
          </li>
          <li>
            <strong>Over 2.5:</strong> Total goals over 2.5 (yes/no)
          </li>
          <li>
            <strong>Value Bet:</strong> Model probability &gt; implied odds &gt; 5% edge
          </li>
          <li>
            <strong>Kelly Staking:</strong> Optimal stake based on bankroll and edge
          </li>
        </ul>
      </div>

      <style>{`
        .performance-page {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }
        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
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
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 1rem;
        }
        .stat-card {
          background: var(--surface);
          border-radius: 0.75rem;
          padding: 1.5rem;
          border: 1px solid var(--border);
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .stat-label {
          font-size: 0.875rem;
          color: var(--text-secondary);
        }
        .stat-value {
          font-size: 1.5rem;
          font-weight: 700;
          color: var(--primary);
        }
        .info-card {
          background: var(--surface);
          border-radius: 0.75rem;
          padding: 1.5rem;
          border: 1px solid var(--border);
        }
        .info-card h2 {
          font-size: 1.25rem;
          margin-bottom: 1rem;
        }
        .info-card ul {
          list-style: none;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }
        .info-card li {
          color: var(--text-secondary);
        }
        .info-card strong {
          color: var(--text-primary);
        }
      `}</style>
    </div>
  );
}