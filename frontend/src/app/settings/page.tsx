'use client';

import { useState, useEffect } from 'react';
import api, { PLATFORMS } from '@/lib/api';

export default function SettingsPage() {
  const [config, setConfig] = useState<any>({});
  const [apiKey, setApiKey] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<{ type: string; text: string } | null>(null);

  useEffect(() => {
    api.getConfig()
      .then(setConfig)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleSaveApiKey = async () => {
    if (!apiKey.trim()) return;
    
    setSaving(true);
    setMessage(null);
    
    try {
      await api.updateConfig('API_FOOTBALL_KEY', apiKey);
      setMessage({ type: 'success', text: 'API key saved successfully!' });
      setApiKey('');
      const updatedConfig = await api.getConfig();
      setConfig(updatedConfig);
    } catch (err) {
      setMessage({ type: 'error', text: 'Failed to save API key.' });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="settings-page">
      <header className="page-header">
        <h1 className="page-title">Settings</h1>
        <p className="page-subtitle">Configure your API keys and preferences</p>
      </header>

      <section className="settings-section">
        <h2>API Configuration</h2>
        
        <div className="setting-item">
          <div className="setting-info">
            <h3>API-Football Key</h3>
            <p>Get your free API key at{' '}
              <a href="https://api-football.com" target="_blank" rel="noopener noreferrer">
                api-football.com
              </a>
            </p>
          </div>
          
          <div className="setting-status">
            {config.api_key_configured ? (
              <span className="badge badge-success">Configured</span>
            ) : (
              <span className="badge badge-warning">Not configured</span>
            )}
          </div>
        </div>
        
        <div className="api-key-input">
          <input
            type="password"
            placeholder="Enter your API-Football key"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="input"
          />
          <button
            className="btn btn-primary"
            onClick={handleSaveApiKey}
            disabled={saving || !apiKey.trim()}
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
        
        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}
      </section>

      <section className="settings-section">
        <h2>Betting Platforms</h2>
        <p className="section-description">
          Quick links to your preferred betting platforms
        </p>
        
        <div className="platforms-grid">
          {PLATFORMS.map(platform => (
            <a
              key={platform.id}
              href={platform.url}
              target="_blank"
              rel="noopener noreferrer"
              className="platform-card"
            >
              <span className="platform-name">{platform.name}</span>
              <span className="platform-arrow">→</span>
            </a>
          ))}
        </div>
      </section>

      <section className="settings-section">
        <h2>Staking Configuration</h2>
        
        <div className="setting-item">
          <div className="setting-info">
            <h3>Kelly Multiplier</h3>
            <p>The fraction of bankroll to stake (0.25 = 25% recommended for safety)</p>
          </div>
          <div className="setting-value">
            <span className="value">{config.kelly_multiplier || 0.25}</span>
          </div>
        </div>
        
        <div className="setting-item">
          <div className="setting-info">
            <h3>Value Bet Threshold</h3>
            <p>Minimum edge required to classify as a value bet</p>
          </div>
          <div className="setting-value">
            <span className="value">5%</span>
          </div>
        </div>
      </section>

      <section className="settings-section">
        <h2>Data Information</h2>
        
        <div className="setting-item">
          <div className="setting-info">
            <h3>Database Location</h3>
            <p>SQLite database storing predictions and bet history</p>
          </div>
          <div className="setting-value">
            <span className="value">{config.database_path || 'data/pro_punter.db'}</span>
          </div>
        </div>
      </section>

      <style>{`
        .settings-page {
          display: flex;
          flex-direction: column;
          gap: 2rem;
          max-width: 800px;
        }
        .page-header {
          margin-bottom: 0;
        }
        .page-title {
          font-size: 1.875rem;
          font-weight: 700;
        }
        .page-subtitle {
          color: var(--text-secondary);
          margin-top: 0.25rem;
        }
        .settings-section {
          background: var(--surface);
          border-radius: 0.75rem;
          padding: 1.5rem;
          border: 1px solid var(--border);
        }
        .settings-section h2 {
          font-size: 1.25rem;
          margin-bottom: 1rem;
        }
        .section-description {
          color: var(--text-secondary);
          font-size: 0.875rem;
          margin-bottom: 1rem;
        }
        .setting-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem 0;
          border-bottom: 1px solid var(--border);
        }
        .setting-item:last-child {
          border-bottom: none;
        }
        .setting-info h3 {
          font-size: 0.875rem;
          font-weight: 600;
          margin-bottom: 0.25rem;
        }
        .setting-info p {
          font-size: 0.75rem;
          color: var(--text-muted);
        }
        .setting-info a {
          color: var(--primary);
        }
        .setting-value .value {
          font-size: 0.875rem;
          color: var(--text-secondary);
          background: var(--surface-light);
          padding: 0.25rem 0.5rem;
          border-radius: 0.25rem;
        }
        .api-key-input {
          display: flex;
          gap: 0.5rem;
          margin-top: 1rem;
        }
        .api-key-input input {
          flex: 1;
        }
        .message {
          margin-top: 1rem;
          padding: 0.75rem 1rem;
          border-radius: 0.5rem;
          font-size: 0.875rem;
        }
        .message.success {
          background: rgba(34, 197, 94, 0.1);
          color: var(--success);
          border: 1px solid var(--success);
        }
        .message.error {
          background: rgba(239, 68, 68, 0.1);
          color: var(--error);
          border: 1px solid var(--error);
        }
        .platforms-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 1rem;
        }
        .platform-card {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background: var(--surface-light);
          border-radius: 0.5rem;
          transition: all 0.2s;
        }
        .platform-card:hover {
          background: var(--primary);
          color: #000;
        }
        .platform-name {
          font-weight: 500;
        }
        .platform-arrow {
          font-size: 1.25rem;
        }
      `}</style>
    </div>
  );
}