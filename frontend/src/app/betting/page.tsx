'use client';

import { useState, useEffect } from 'react';
import api, { PLATFORMS } from '@/lib/api';
import { Bet } from '@/types';
import { formatDate, formatCurrency, getStatusColor, getPlatformUrl } from '@/lib/utils';

export default function BettingPage() {
  const [bets, setBets] = useState<Bet[]>([]);
  const [loading, setLoading] = useState(true);
  const [platformFilter, setPlatformFilter] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');

  useEffect(() => {
    loadBets();
  }, [platformFilter, statusFilter]);

  const loadBets = async () => {
    setLoading(true);
    try {
      const data = await api.getBets(platformFilter || undefined, statusFilter || undefined);
      setBets(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdate = async (betId: number, status: string, profit?: number) => {
    try {
      await api.updateBet(betId, status, profit);
      loadBets();
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className="betting-page">
      <header className="page-header">
        <h1 className="page-title">Betting History</h1>
        <p className="page-subtitle">Track and manage your placed bets</p>
      </header>

      <div className="filters">
        <select
          value={platformFilter}
          onChange={(e) => setPlatformFilter(e.target.value)}
          className="input"
        >
          <option value="">All Platforms</option>
          {PLATFORMS.map(p => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>

        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="input"
        >
          <option value="">All Status</option>
          <option value="pending">Pending</option>
          <option value="won">Won</option>
          <option value="lost">Lost</option>
        </select>
      </div>

      {loading ? (
        <div className="loading-state">
          <div className="spinner"></div>
        </div>
      ) : bets.length === 0 ? (
        <div className="empty-state">
          <p>No bets recorded yet.</p>
          <p className="hint">Place a bet and record it here.</p>
        </div>
      ) : (
        <div className="bets-table">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Platform</th>
                <th>Selection</th>
                <th>Stake</th>
                <th>Odds</th>
                <th>Status</th>
                <th>Profit</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {bets.map(bet => (
                <tr key={bet.id}>
                  <td>{formatDate(bet.bet_date)}</td>
                  <td>{PLATFORMS.find(p => p.id === bet.platform)?.name || bet.platform}</td>
                  <td>{bet.selection}</td>
                  <td>{formatCurrency(bet.stake)}</td>
                  <td>{bet.odds.toFixed(2)}</td>
                  <td>
                    <span className={`badge ${getStatusColor(bet.status)}`}>
                      {bet.status}
                    </span>
                  </td>
                  <td className={(bet.profit || 0) > 0 ? 'profit-positive' : (bet.profit || 0) < 0 ? 'profit-negative' : ''}>
                    {bet.profit !== undefined ? formatCurrency(bet.profit) : 'N/A'}
                  </td>
                  <td>
                    {bet.status === 'pending' && (
                      <div className="action-buttons">
                        <button
                          className="btn btn-small btn-success"
                          onClick={() => handleStatusUpdate(bet.id, 'won', bet.stake * (bet.odds - 1))}
                        >
                          Won
                        </button>
                        <button
                          className="btn btn-small btn-error"
                          onClick={() => handleStatusUpdate(bet.id, 'lost', -bet.stake)}
                        >
                          Lost
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="platform-links">
        <h2>Quick Links</h2>
        <div className="links-grid">
          {PLATFORMS.map(platform => (
            <a
              key={platform.id}
              href={platform.url}
              target="_blank"
              rel="noopener noreferrer"
              className="platform-link"
            >
              {platform.name} →
            </a>
          ))}
        </div>
      </div>

      <style>{`
        .betting-page {
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
        .filters {
          display: flex;
          gap: 1rem;
        }
        .filters select {
          min-width: 150px;
        }
        .loading-state, .empty-state {
          text-align: center;
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
          margin: 0 auto;
        }
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        .hint {
          font-size: 0.875rem;
          color: var(--text-muted);
          margin-top: 0.5rem;
        }
        .bets-table {
          background: var(--surface);
          border-radius: 0.75rem;
          border: 1px solid var(--border);
          overflow: hidden;
        }
        table {
          width: 100%;
          border-collapse: collapse;
        }
        th, td {
          padding: 1rem;
          text-align: left;
          border-bottom: 1px solid var(--border);
        }
        th {
          background: var(--surface-light);
          font-size: 0.75rem;
          text-transform: uppercase;
          color: var(--text-muted);
        }
        td {
          font-size: 0.875rem;
        }
        .profit-positive {
          color: var(--success);
        }
        .profit-negative {
          color: var(--error);
        }
        .action-buttons {
          display: flex;
          gap: 0.5rem;
        }
        .btn-small {
          padding: 0.25rem 0.5rem;
          font-size: 0.75rem;
        }
        .btn-success {
          background: var(--success);
          color: #000;
        }
        .btn-error {
          background: var(--error);
          color: #fff;
        }
        .platform-links {
          margin-top: 2rem;
          padding: 1.5rem;
          background: var(--surface);
          border-radius: 0.75rem;
          border: 1px solid var(--border);
        }
        .platform-links h2 {
          font-size: 1rem;
          margin-bottom: 1rem;
        }
        .links-grid {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
        }
        .platform-link {
          padding: 0.5rem 1rem;
          background: var(--surface-light);
          border-radius: 0.5rem;
          color: var(--primary);
          font-weight: 500;
        }
        .platform-link:hover {
          background: var(--primary);
          color: #000;
        }
      `}</style>
    </div>
  );
}