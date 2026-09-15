import React from 'react';
import { Link } from 'react-router-dom';

const YEAR = new Date().getFullYear();

export default function Footer() {
  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=DM+Sans:wght@400;500;600&display=swap');

        .fx-footer {
          border-top: 1px solid #e5e7eb;
          background: #fafafa;
          margin-top: auto;
        }
        .fx-footer-inner {
          max-width: 1200px;
          margin: 0 auto;
          padding: 28px 24px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 24px;
          flex-wrap: wrap;
        }
        .fx-footer-left {
          display: flex;
          flex-direction: column;
          gap: 4px;
        }
        .fx-footer-logo {
          font-family: 'IBM Plex Mono', monospace;
          font-weight: 600;
          font-size: 13px;
          letter-spacing: -0.03em;
          color: #111;
          text-decoration: none;
        }
        .fx-footer-logo span { color: #9ca3af; font-weight: 400; }
        .fx-footer-copy {
          font-family: 'IBM Plex Mono', monospace;
          font-size: 10px;
          color: #d1d5db;
          letter-spacing: 0.02em;
        }
        .fx-footer-status {
          display: flex;
          align-items: center;
          gap: 6px;
          font-family: 'IBM Plex Mono', monospace;
          font-size: 10px;
          color: #9ca3af;
        }
        .fx-footer-status-dot {
          width: 5px;
          height: 5px;
          border-radius: 50%;
          background: #16a34a;
          flex-shrink: 0;
          animation: pulse-dot 2.4s infinite;
          box-shadow: 0 0 0 2px rgba(22,163,74,0.2);
        }
        @keyframes pulse-dot {
          0%, 100% { box-shadow: 0 0 0 2px rgba(22,163,74,0.15); }
          50%       { box-shadow: 0 0 0 4px rgba(22,163,74,0.05); }
        }

        @media (max-width: 640px) {
          .fx-footer-inner {
            flex-direction: column;
            align-items: flex-start;
            gap: 12px;
            padding: 20px 24px;
          }
        }
      `}</style>

      <footer className="fx-footer">
        <div className="fx-footer-inner">
          <div className="fx-footer-left">
            <Link to="/profile/me" className="fx-footer-logo">
              fx<span>.platform</span>
            </Link>
            <div className="fx-footer-copy">
              © {YEAR} · аналитика валютных курсов
            </div>
          </div>

          <div className="fx-footer-status">
            <span className="fx-footer-status-dot" />
            все системы работают
          </div>
        </div>
      </footer>
    </>
  );
}
