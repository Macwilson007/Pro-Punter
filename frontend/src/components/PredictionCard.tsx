'use client';

import { Prediction } from '@/types';
import { formatPercentage, getConfidenceColor, getOutcomeColor } from '@/lib/utils';

interface PredictionCardProps {
  prediction: Prediction;
  onSelect?: (prediction: Prediction) => void;
  showOdds?: boolean;
}

export default function PredictionCard({ prediction, onSelect, showOdds = false }: PredictionCardProps) {
  return (
    <div className="prediction-card">
      <div className="card-header">
        <span className="league-badge">{prediction.league}</span>
        {prediction.kickoff && (
          <span className="time-badge">
            {new Date(prediction.kickoff).toLocaleString(undefined, {
              weekday: 'short', month: 'short', day: 'numeric',
              hour: '2-digit', minute: '2-digit'
            })}
          </span>
        )}
        <span className="market-badge">{prediction.market}</span>
      </div>
      
      <div className="teams">
        <div className="team home-team">
          <span className="team-name">{prediction.home_team}</span>
        </div>
        <div className="vs">vs</div>
        <div className="team away-team">
          <span className="team-name">{prediction.away_team}</span>
        </div>
      </div>
      
      <div className="prediction-content">
        <div className="prediction-main">
          <span className="prediction-label">Prediction</span>
          <div className="prediction-with-result">
            <span className={`prediction-value ${getOutcomeColor(prediction.prediction)}`}>
              {prediction.prediction.toUpperCase()}
            </span>
            {prediction.actual_result && (
              <span className={`result-badge ${prediction.actual_result === prediction.prediction ? 'won' : 'lost'}`}>
                {prediction.actual_result === prediction.prediction ? 'WON' : 'LOST'}
              </span>
            )}
          </div>
        </div>
        
        <div className="confidence">
          <span className="confidence-label">Confidence</span>
          <span className={`confidence-value ${getConfidenceColor(prediction.confidence)}`}>
            {formatPercentage(prediction.confidence)}
          </span>
        </div>
      </div>
      
      {showOdds && prediction.odds && (
        <div className="odds-section">
          <span className="odds-label">Odds</span>
          <div className="odds-grid">
            {Object.entries(prediction.odds).map(([key, value]) => (
              <span key={key} className={`odd ${key === prediction.prediction ? 'active' : ''}`}>
                {key}: {value.toFixed(2)}
              </span>
            ))}
          </div>
        </div>
      )}
      
      {prediction.best_pick && (
        <div className="best-pick-section">
          <div className="best-pick-badge">
            <span className="sparkle">✨</span>
            Pro Punter's Choice
          </div>
          <div className="best-pick-details">
            <span className="market">{prediction.best_pick.best_market.replace('_', ' ').toUpperCase()}</span>
            <span className="divider">:</span>
            <span className="value">{prediction.best_pick.best_prediction.toUpperCase()}</span>
            <span className="confidence-badge">
              {formatPercentage(prediction.best_pick.best_confidence)}
            </span>
          </div>
        </div>
      )}

      {prediction.value_bet && (
        <div className="value-badge">
          <span>💎 Value Bet</span>
          <span className="edge">Edge: {formatPercentage(prediction.edge || 0)}</span>
        </div>
      )}
      
      {onSelect && (
        <button className="btn btn-primary select-btn" onClick={() => onSelect(prediction)}>
          Select for Bet
        </button>
      )}
      
      <style>{`
        .prediction-card {
          background: var(--surface);
          border-radius: 0.75rem;
          padding: 1.5rem;
          border: 1px solid var(--border);
        }
        .card-header {
          display: flex;
          justify-content: space-between;
          margin-bottom: 1rem;
        }
        .league-badge, .market-badge, .time-badge {
          font-size: 0.75rem;
          padding: 0.25rem 0.5rem;
          border-radius: 0.25rem;
          background: var(--surface-light);
          color: var(--text-secondary);
        }
        .time-badge {
          font-weight: 500;
          color: var(--primary);
        }
        .teams {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 1rem;
        }
        .team {
          flex: 1;
          text-align: center;
        }
        .team-name {
          font-size: 1rem;
          font-weight: 600;
        }
        .vs {
          font-size: 0.875rem;
          color: var(--text-muted);
          padding: 0 1rem;
        }
        .prediction-content {
          display: flex;
          justify-content: space-between;
          padding-top: 1rem;
          border-top: 1px solid var(--border);
        }
        .prediction-main, .confidence {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        .prediction-label, .confidence-label {
          font-size: 0.75rem;
          color: var(--text-muted);
        }
        .prediction-value {
          font-size: 1.25rem;
          font-weight: 700;
        }
        .confidence-value {
          font-size: 1.25rem;
          font-weight: 700;
        }
        .odds-section {
          margin-top: 1rem;
          padding-top: 1rem;
          border-top: 1px solid var(--border);
        }
        .odds-label {
          font-size: 0.75rem;
          color: var(--text-muted);
          margin-bottom: 0.5rem;
          display: block;
        }
        .odds-grid {
          display: flex;
          gap: 0.5rem;
        }
        .odd {
          font-size: 0.875rem;
          padding: 0.25rem 0.5rem;
          border-radius: 0.25rem;
          background: var(--surface-light);
          color: var(--text-secondary);
        }
        .odd.active {
          background: var(--primary);
          color: #000;
        }
        .value-badge {
          margin-top: 1rem;
          padding: 0.75rem;
          border-radius: 0.5rem;
          background: rgba(34, 197, 94, 0.1);
          border: 1px solid var(--primary);
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
        .value-badge span:first-child {
          color: var(--primary);
          font-weight: 600;
        }
        .edge {
          color: var(--text-secondary);
          font-size: 0.875rem;
        }
        .select-btn {
          width: 100%;
          margin-top: 1rem;
        }
        .prediction-with-result {
          display: flex;
          align-items: center;
          gap: 0.75rem;
        }
        .result-badge {
          font-size: 0.7rem;
          font-weight: 800;
          padding: 0.125rem 0.4rem;
          border-radius: 0.25rem;
          letter-spacing: 0.05em;
        }
        .result-badge.won {
          background: rgba(34, 197, 94, 0.2);
          color: #22c55e;
          border: 1px solid #22c55e;
        }
        .result-badge.lost {
          background: rgba(239, 68, 68, 0.2);
          color: #ef4444;
          border: 1px solid #ef4444;
        }
        .best-pick-section {
          margin-top: 1rem;
          padding: 1rem;
          background: linear-gradient(135deg, rgba(234, 179, 8, 0.1), rgba(234, 179, 8, 0.05));
          border: 1px solid rgba(234, 179, 8, 0.3);
          border-radius: 0.75rem;
          position: relative;
          overflow: hidden;
        }
        .best-pick-badge {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.75rem;
          font-weight: 700;
          color: #eab308;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-bottom: 0.5rem;
        }
        .best-pick-details {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-weight: 600;
        }
        .best-pick-details .market {
          color: var(--text-secondary);
          font-size: 0.875rem;
        }
        .best-pick-details .value {
          color: var(--text-primary);
          font-size: 1rem;
        }
        .confidence-badge {
          margin-left: auto;
          background: #eab308;
          color: #000;
          padding: 0.125rem 0.5rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 800;
        }
        .sparkle {
          animation: pulse 2s infinite;
        }
        @keyframes pulse {
          0% { transform: scale(1); opacity: 1; }
          50% { transform: scale(1.2); opacity: 0.8; }
          100% { transform: scale(1); opacity: 1; }
        }
      `}</style>
    </div>
  );
}