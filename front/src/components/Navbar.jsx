import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import api from '../services/api';

const NAV_LINKS = [
  { label: 'profile', path: '/profile/me', icon: '◈' },
  { label: 'курсы валют', path: '/course/currency', icon: '◎' },
];

export default function Navbar() {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(null);
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    api.get('/profile/me')
      .then(res => setUser(res.data))
      .catch(() => setUser(null));
  }, []);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 8);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Close menu on route change
  useEffect(() => setMenuOpen(false), [location.pathname]);

  const handleLogout = async () => {
    try { await api.post('/auth/logout'); } catch {}
    localStorage.removeItem('token');
    navigate('/auth/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=DM+Sans:wght@400;500;600&display=swap');

        .fx-nav {
          position: sticky;
          top: 0;
          z-index: 100;
          background: #fafafa;
          border-bottom: 1px solid #e5e7eb;
          transition: box-shadow 0.2s ease, background 0.2s ease;
        }
        .fx-nav.scrolled {
          background: rgba(250,250,250,0.92);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
          box-shadow: 0 1px 0 #e5e7eb, 0 4px 24px rgba(0,0,0,0.04);
        }
        .fx-nav-inner {
          max-width: 1200px;
          margin: 0 auto;
          padding: 0 24px;
          height: 52px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 24px;
        }
        .fx-logo {
          font-family: 'IBM Plex Mono', monospace;
          font-weight: 600;
          font-size: 15px;
          letter-spacing: -0.03em;
          color: #111;
          text-decoration: none;
          flex-shrink: 0;
        }
        .fx-logo span { color: #9ca3af; font-weight: 400; }
        .fx-links {
          display: flex;
          align-items: center;
          gap: 2px;
          flex: 1;
        }
        .fx-link {
          display: flex;
          align-items: center;
          gap: 6px;
          padding: 6px 12px;
          border-radius: 6px;
          font-family: 'IBM Plex Mono', monospace;
          font-size: 11px;
          font-weight: 500;
          color: #6b7280;
          text-decoration: none;
          border: 1px solid transparent;
          transition: all 0.15s;
          white-space: nowrap;
          cursor: pointer;
          background: none;
        }
        .fx-link:hover {
          color: #111;
          background: #f3f4f6;
          border-color: #e5e7eb;
        }
        .fx-link.active {
          color: #111;
          background: #fff;
          border-color: #e5e7eb;
          box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        }
        .fx-link-icon {
          font-size: 10px;
          opacity: 0.5;
        }
        .fx-link.active .fx-link-icon { opacity: 1; }

        .fx-right {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-shrink: 0;
        }
        .fx-user-badge {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 5px 10px;
          border-radius: 6px;
          border: 1px solid #e5e7eb;
          background: #fff;
          font-family: 'IBM Plex Mono', monospace;
          font-size: 11px;
          cursor: default;
        }
        .fx-user-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #16a34a;
          flex-shrink: 0;
        }
        .fx-user-login { color: #374151; font-weight: 500; }
        .fx-logout-btn {
          padding: 6px 12px;
          border-radius: 6px;
          border: 1px solid #fecaca;
          background: #fff;
          color: #dc2626;
          font-family: 'IBM Plex Mono', monospace;
          font-size: 11px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.15s;
          letter-spacing: 0.02em;
        }
        .fx-logout-btn:hover {
          background: #fef2f2;
        }

        /* Mobile */
        .fx-burger {
          display: none;
          flex-direction: column;
          gap: 4px;
          background: none;
          border: none;
          cursor: pointer;
          padding: 4px;
        }
        .fx-burger span {
          display: block;
          width: 20px;
          height: 2px;
          background: #111;
          border-radius: 2px;
          transition: all 0.2s;
        }
        .fx-burger.open span:nth-child(1) { transform: translateY(6px) rotate(45deg); }
        .fx-burger.open span:nth-child(2) { opacity: 0; }
        .fx-burger.open span:nth-child(3) { transform: translateY(-6px) rotate(-45deg); }

        .fx-mobile-menu {
          display: none;
          flex-direction: column;
          gap: 2px;
          padding: 12px 24px 16px;
          border-top: 1px solid #e5e7eb;
          background: #fafafa;
          animation: slide-down 0.2s ease;
        }
        .fx-mobile-menu.open { display: flex; }
        @keyframes slide-down { from { opacity: 0; transform: translateY(-6px); } to { opacity: 1; transform: none; } }

        .fx-mobile-link {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 10px 12px;
          border-radius: 6px;
          font-family: 'IBM Plex Mono', monospace;
          font-size: 12px;
          font-weight: 500;
          color: #6b7280;
          text-decoration: none;
          border: 1px solid transparent;
          transition: all 0.15s;
          cursor: pointer;
          background: none;
          width: 100%;
          text-align: left;
        }
        .fx-mobile-link:hover { color: #111; background: #f3f4f6; border-color: #e5e7eb; }
        .fx-mobile-link.active { color: #111; background: #fff; border-color: #e5e7eb; }
        .fx-mobile-link.danger { color: #dc2626; }
        .fx-mobile-link.danger:hover { background: #fef2f2; border-color: #fecaca; }

        @media (max-width: 640px) {
          .fx-links { display: none; }
          .fx-user-badge { display: none; }
          .fx-logout-btn { display: none; }
          .fx-burger { display: flex; }
        }
      `}</style>

      <nav className={`fx-nav${scrolled ? ' scrolled' : ''}`}>
        <div className="fx-nav-inner">

          {/* Logo */}
          <Link to="/profile/me" className="fx-logo">
            fx<span>.platform</span>
          </Link>

          {/* Links */}
          <div className="fx-links">
            {NAV_LINKS.map(({ label, path, icon }) => (
              <Link
                key={path}
                to={path}
                className={`fx-link${isActive(path) ? ' active' : ''}`}
              >
                <span className="fx-link-icon">{icon}</span>
                {label}
              </Link>
            ))}
          </div>

          {/* Right side */}
          <div className="fx-right">
            {user && (
              <div className="fx-user-badge">
                <span className="fx-user-dot" />
                <span className="fx-user-login">{user.login}</span>
              </div>
            )}
            {user && (
              <button className="fx-logout-btn" onClick={handleLogout}>
                выйти
              </button>
            )}
          </div>

          {/* Burger */}
          <button
            className={`fx-burger${menuOpen ? ' open' : ''}`}
            onClick={() => setMenuOpen(v => !v)}
            aria-label="Меню"
          >
            <span /><span /><span />
          </button>
        </div>

        {/* Mobile menu */}
        <div className={`fx-mobile-menu${menuOpen ? ' open' : ''}`}>
          {NAV_LINKS.map(({ label, path, icon }) => (
            <Link
              key={path}
              to={path}
              className={`fx-mobile-link${isActive(path) ? ' active' : ''}`}
            >
              <span>{icon}</span>
              {label}
            </Link>
          ))}
          {user && (
            <>
              <div style={{
                borderTop: '1px solid #e5e7eb',
                margin: '8px 0',
              }} />
              <div style={{
                padding: '6px 12px',
                fontFamily: "'IBM Plex Mono', monospace",
                fontSize: 10,
                color: '#9ca3af',
                display: 'flex',
                alignItems: 'center',
                gap: 6,
              }}>
                <span style={{ width: 5, height: 5, borderRadius: '50%', background: '#16a34a', display: 'inline-block' }} />
                {user.login}
              </div>
              <button className="fx-mobile-link danger" onClick={handleLogout}>
                ⏻ выйти из системы
              </button>
            </>
          )}
        </div>
      </nav>
    </>
  );
}
