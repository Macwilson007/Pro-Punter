import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleDateString('en-US', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

export function formatTime(date: string | Date): string {
  const d = new Date(date);
  return d.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function formatOdds(odds: number): string {
  return odds.toFixed(2);
}

export function formatPercentage(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

export function getOutcomeColor(outcome: string): string {
  const colors: Record<string, string> = {
    home: 'text-green-400',
    away: 'text-red-400',
    draw: 'text-yellow-400',
    yes: 'text-green-400',
    no: 'text-red-400',
  };
  return colors[outcome] || 'text-gray-400';
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    pending: 'badge-warning',
    won: 'badge-success',
    lost: 'badge-error',
  };
  return colors[status] || 'badge-warning';
}

export function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.7) return 'text-green-400';
  if (confidence >= 0.5) return 'text-yellow-400';
  return 'text-red-400';
}

export function getPlatformUrl(platform: string, leagueId?: string): string {
  const urls: Record<string, string> = {
    bet9ja: `https://bet9ja.com/football${leagueId ? `/${leagueId}` : ''}`,
    sportybet: `https://sportybet.com/sport/football${leagueId ? `/${leagueId}` : ''}`,
    '1xbet': `https://1xbet.com/en/line/football${leagueId ? `/${leagueId}` : ''}`,
    betking: `https://betking.com/sports/football${leagueId ? `/${leagueId}` : ''}`,
  };
  return urls[platform] || '#';
}

export const TIERS = [
  { tier: 1, label: 'High Predictability', color: 'bg-green-500' },
  { tier: 2, label: 'Medium Predictability', color: 'bg-yellow-500' },
  { tier: 3, label: 'High Value', color: 'bg-blue-500' },
];