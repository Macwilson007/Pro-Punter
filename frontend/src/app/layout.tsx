import type { Metadata } from 'next'
import Link from 'next/link'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Pro Punter - AI Football Predictions',
  description: 'AI-powered football match predictions with value betting detection',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <nav className="navbar">
          <div className="nav-container">
            <Link href="/" className="nav-logo">
              <span className="logo-icon">⚽</span>
              Pro Punter
            </Link>
            <div className="nav-links">
              <Link href="/" className="nav-link">Dashboard</Link>
              <Link href="/predictions" className="nav-link">Predictions</Link>
              <Link href="/performance" className="nav-link">Performance</Link>
              <Link href="/betting" className="nav-link">Betting</Link>
              <Link href="/settings" className="nav-link">Settings</Link>
            </div>
          </div>
        </nav>
        <main className="main-content">
          {children}
        </main>
        <style>{`
          .navbar {
            background: var(--surface);
            border-bottom: 1px solid var(--border);
            padding: 1rem 0;
            position: sticky;
            top: 0;
            z-index: 50;
          }
          .nav-container {
            max-width: 1280px;
            margin: 0 auto;
            padding: 0 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
          }
          .nav-logo {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--primary);
          }
          .logo-icon {
            font-size: 1.5rem;
          }
          .nav-links {
            display: flex;
            gap: 2rem;
          }
          .nav-link {
            color: var(--text-secondary);
            font-size: 0.875rem;
            font-weight: 500;
            transition: color 0.2s;
          }
          .nav-link:hover {
            color: var(--text-primary);
          }
          .main-content {
            max-width: 1280px;
            margin: 0 auto;
            padding: 2rem 1.5rem;
            min-height: calc(100vh - 80px);
          }
          @media (max-width: 768px) {
            .nav-links {
              display: none;
            }
          }
        `}</style>
      </body>
    </html>
  )
}