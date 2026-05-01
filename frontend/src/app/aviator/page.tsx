'use client';

import { useState, useEffect, useRef } from 'react';
import api from '@/lib/api';

interface AviatorSignal {
  recommended_cashout: number;
  confidence_score: number;
  risk_level: string;
  next_multiplier_range: string;
  is_gold_signal: boolean;
  timestamp: string;
}

export default function AviatorPage() {
  const [history, setHistory] = useState<number[]>([1.24, 3.56, 1.10, 2.45, 1.88]);
  const [newVal, setNewVal] = useState<string>('');
  const [signal, setSignal] = useState<AviatorSignal | null>(null);
  const [loading, setLoading] = useState(false);
  const [animating, setAnimating] = useState(false);
  const [planePosition, setPlanePosition] = useState(0);

  useEffect(() => {
    generateSignal();
  }, []);

  const generateSignal = async () => {
    setLoading(true);
    try {
      const data = await api.getAviatorPrediction(history);
      setSignal(data);
      // Trigger animation
      setAnimating(true);
      setPlanePosition(0);
      let pos = 0;
      const interval = setInterval(() => {
        pos += 2;
        setPlanePosition(pos);
        if (pos >= 100) {
          clearInterval(interval);
          setAnimating(false);
        }
      }, 20);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const addHistory = (e: React.FormEvent) => {
    e.preventDefault();
    const val = parseFloat(newVal);
    if (!isNaN(val) && val > 0) {
      const newHistory = [...history, val].slice(-10);
      setHistory(newHistory);
      setNewVal('');
      generateSignal();
    }
  };

  return (
    <div className="aviator-container">
      <header className="page-header">
        <div>
          <h1 className="page-title text-gradient">Aviator Predictor</h1>
          <p className="page-subtitle">AI-Powered Crash Game Signal Generator</p>
        </div>
        <div className={`status-badge ${signal?.is_gold_signal ? 'gold' : ''}`}>
          {signal?.is_gold_signal ? '⭐ GOLD SIGNAL' : 'STANDARD SIGNAL'}
        </div>
      </header>

      <div className="main-grid">
        {/* Left: Signal Display */}
        <div className="card signal-card">
          <div className="plane-track">
             <div 
              className="plane" 
              style={{ 
                left: `${planePosition}%`, 
                bottom: `${Math.pow(planePosition/10, 1.5)}px`,
                opacity: animating ? 1 : 0.5
              }}
            >
              ✈️
            </div>
            <div className="trail" style={{ width: `${planePosition}%` }}></div>
          </div>

          <div className="signal-content">
            <div className="multiplier-display">
              <span className="label">Recommended Cashout</span>
              <h2 className="value">{signal?.recommended_cashout.toFixed(2)}x</h2>
            </div>

            <div className="stats-row">
              <div className="stat">
                <span className="stat-label">Confidence</span>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${signal?.confidence_score}%`, background: signal?.confidence_score! > 80 ? '#fbbf24' : '#3b82f6' }}
                  ></div>
                </div>
                <span className="stat-value">{signal?.confidence_score}%</span>
              </div>
              <div className="stat">
                <span className="stat-label">Risk Level</span>
                <span className={`risk-badge ${signal?.risk_level.toLowerCase()}`}>
                  {signal?.risk_level}
                </span>
              </div>
            </div>

            <div className="range-box">
              <span className="stat-label">Expected Range</span>
              <p className="range-value">{signal?.next_multiplier_range}</p>
            </div>

            <button 
              className="btn btn-primary btn-glow" 
              onClick={generateSignal}
              disabled={loading || animating}
            >
              {loading ? 'Analyzing...' : 'Refresh Signal'}
            </button>
          </div>
        </div>

        {/* Right: History & Input */}
        <div className="card history-card">
          <h3 className="card-title">Recent History</h3>
          <div className="history-list">
            {history.slice().reverse().map((val, i) => (
              <div key={i} className="history-item">
                <span className="index">Round {history.length - i}</span>
                <span className={`val ${val > 2 ? 'high' : val > 1.5 ? 'med' : 'low'}`}>
                  {val.toFixed(2)}x
                </span>
              </div>
            ))}
          </div>

          <form onSubmit={addHistory} className="input-group">
            <input 
              type="number" 
              step="0.01" 
              placeholder="Enter last multiplier..." 
              value={newVal}
              onChange={(e) => setNewVal(e.target.value)}
              className="input"
            />
            <button type="submit" className="btn btn-secondary">Add</button>
          </form>
          <p className="helper-text">Add recent results to improve AI accuracy</p>
        </div>
      </div>

      <style jsx>{`
        .aviator-container {
          display: flex;
          flex-direction: column;
          gap: 2rem;
          padding-bottom: 2rem;
        }
        .text-gradient {
          background: linear-gradient(135deg, #fff 0%, #94a3b8 100%);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
        }
        .status-badge {
          padding: 0.5rem 1rem;
          background: rgba(255, 255, 255, 0.05);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 2rem;
          font-size: 0.75rem;
          font-weight: 600;
          letter-spacing: 0.05em;
        }
        .status-badge.gold {
          background: rgba(251, 191, 36, 0.1);
          border-color: rgba(251, 191, 36, 0.3);
          color: #fbbf24;
          box-shadow: 0 0 15px rgba(251, 191, 36, 0.1);
        }
        .main-grid {
          display: grid;
          grid-template-columns: 1.5fr 1fr;
          gap: 1.5rem;
        }
        @media (max-width: 900px) {
          .main-grid { grid-template-columns: 1fr; }
        }
        .card {
          background: rgba(15, 23, 42, 0.6);
          backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.08);
          border-radius: 1.5rem;
          padding: 2rem;
          display: flex;
          flex-direction: column;
        }
        .signal-card {
          position: relative;
          overflow: hidden;
          min-height: 400px;
        }
        .plane-track {
          height: 120px;
          border-bottom: 2px dashed rgba(255, 255, 255, 0.1);
          position: relative;
          margin-bottom: 2rem;
        }
        .plane {
          position: absolute;
          font-size: 2rem;
          transition: all 0.05s linear;
          z-index: 10;
        }
        .trail {
          position: absolute;
          bottom: -2px;
          left: 0;
          height: 3px;
          background: linear-gradient(90deg, transparent, #ef4444);
          box-shadow: 0 0 10px #ef4444;
        }
        .multiplier-display {
          text-align: center;
          margin-bottom: 2rem;
        }
        .multiplier-display .label {
          font-size: 0.875rem;
          color: #94a3b8;
          text-transform: uppercase;
          letter-spacing: 0.1em;
        }
        .multiplier-display .value {
          font-size: 4rem;
          font-weight: 800;
          color: #ef4444;
          text-shadow: 0 0 30px rgba(239, 68, 68, 0.3);
          margin-top: 0.5rem;
        }
        .stats-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 2rem;
          margin-bottom: 1.5rem;
        }
        .stat {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }
        .stat-label {
          font-size: 0.75rem;
          color: #64748b;
          text-transform: uppercase;
        }
        .progress-bar {
          height: 6px;
          background: rgba(255, 255, 255, 0.05);
          border-radius: 10px;
          overflow: hidden;
        }
        .progress-fill {
          height: 100%;
          transition: width 0.5s ease-out;
        }
        .stat-value {
          font-size: 1rem;
          font-weight: 600;
        }
        .risk-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 0.5rem;
          font-size: 0.875rem;
          font-weight: 600;
          width: fit-content;
        }
        .risk-badge.low { background: rgba(34, 197, 94, 0.1); color: #22c55e; }
        .risk-badge.medium { background: rgba(234, 179, 8, 0.1); color: #eab308; }
        .risk-badge.high { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
        
        .range-box {
          background: rgba(255, 255, 255, 0.03);
          padding: 1rem;
          border-radius: 1rem;
          margin-bottom: 2rem;
          border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .range-value {
          font-size: 1.25rem;
          font-weight: 700;
          color: #f8fafc;
          margin-top: 0.25rem;
        }
        .btn-glow {
          box-shadow: 0 0 20px rgba(239, 68, 68, 0.2);
        }
        .btn-glow:hover {
          box-shadow: 0 0 30px rgba(239, 68, 68, 0.4);
        }
        
        .history-list {
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          margin: 1.5rem 0;
          max-height: 300px;
          overflow-y: auto;
          padding-right: 0.5rem;
        }
        .history-item {
          display: flex;
          justify-content: space-between;
          padding: 0.75rem 1rem;
          background: rgba(255, 255, 255, 0.02);
          border-radius: 0.75rem;
          border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .history-item .val { font-weight: 700; }
        .val.high { color: #fbbf24; }
        .val.med { color: #3b82f6; }
        .val.low { color: #94a3b8; }
        
        .input-group {
          display: flex;
          gap: 0.5rem;
        }
        .helper-text {
          font-size: 0.75rem;
          color: #64748b;
          margin-top: 0.75rem;
          text-align: center;
        }
      `}</style>
    </div>
  );
}
