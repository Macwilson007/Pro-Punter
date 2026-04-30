'use client';

import { useState } from 'react';
import { League } from '@/types';

interface LeagueFilterProps {
  leagues: League[];
  selected: string | null;
  onChange: (leagueId: string | null) => void;
}

export default function LeagueFilter({ leagues, selected, onChange }: LeagueFilterProps) {
  const [search, setSearch] = useState('');
  
  const filteredLeagues = leagues.filter(league => 
    league.name.toLowerCase().includes(search.toLowerCase()) ||
    league.country.toLowerCase().includes(search.toLowerCase())
  );
  
  const groupedLeagues = filteredLeagues.reduce((acc, league) => {
    const tier = league.tier;
    if (!acc[tier]) acc[tier] = [];
    acc[tier].push(league);
    return acc;
  }, {} as Record<number, League[]>);
  
  return (
    <div className="league-filter">
      <input
        type="text"
        placeholder="Search leagues..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="input search-input"
      />
      
      <div className="tier-section">
        <button
          className={`tier-btn ${selected === null ? 'active' : ''}`}
          onClick={() => onChange(null)}
        >
          All Leagues
        </button>
      </div>
      
      {Object.entries(groupedLeagues).map(([tier, tierLeagues]) => (
        <div key={tier} className="tier-section">
          <h3 className="tier-title">Tier {tier}</h3>
          <div className="league-grid">
            {tierLeagues.map(league => (
              <button
                key={league.id}
                className={`league-btn ${selected === league.id ? 'active' : ''}`}
                onClick={() => onChange(league.id)}
              >
                <span className="league-name">{league.name}</span>
                <span className="league-country">{league.country}</span>
              </button>
            ))}
          </div>
        </div>
      ))}
      
      <style>{`
        .league-filter {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }
        .search-input {
          width: 100%;
        }
        .tier-section {
          margin-bottom: 1rem;
        }
        .tier-title {
          font-size: 0.75rem;
          color: var(--text-muted);
          margin-bottom: 0.5rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
        .tier-btn {
          width: 100%;
          padding: 0.75rem 1rem;
          border-radius: 0.5rem;
          background: var(--surface-light);
          border: 1px solid var(--border);
          color: var(--text-primary);
          text-align: left;
          cursor: pointer;
          transition: all 0.2s;
        }
        .tier-btn:hover, .tier-btn.active {
          border-color: var(--primary);
          background: rgba(34, 197, 94, 0.1);
        }
        .league-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 0.5rem;
        }
        .league-btn {
          padding: 0.75rem;
          border-radius: 0.5rem;
          background: var(--surface-light);
          border: 1px solid var(--border);
          color: var(--text-primary);
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
        }
        .league-btn:hover, .league-btn.active {
          border-color: var(--primary);
          background: rgba(34, 197, 94, 0.1);
        }
        .league-name {
          font-size: 0.875rem;
          font-weight: 500;
        }
        .league-country {
          font-size: 0.75rem;
          color: var(--text-muted);
        }
      `}</style>
    </div>
  );
}