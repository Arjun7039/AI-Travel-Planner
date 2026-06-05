/**
 * Navbar — Top navigation bar with logo and auth controls.
 */

import { useNavigate } from 'react-router-dom';

interface NavbarProps {
  userName: string;
  isLoggedIn: boolean;
  onNewTrip: () => void;
}

export function Navbar({ userName, isLoggedIn, onNewTrip }: NavbarProps) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('voyagr_token');
    localStorage.removeItem('voyagr_name');
    window.location.reload();
  };

  return (
    <nav style={{
      position: 'sticky', top: 0, zIndex: 50,
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '12px 24px',
      background: 'rgba(10, 10, 10, 0.8)',
      backdropFilter: 'blur(12px)',
      borderBottom: '1px solid var(--border)',
    }}>
      {/* Logo */}
      <div
        style={{ display: 'flex', alignItems: 'center', gap: 10, cursor: 'pointer' }}
        onClick={onNewTrip}
      >
        <div style={{
          width: 32, height: 32, borderRadius: 'var(--radius-sm)',
          background: 'var(--accent)', display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 16,
        }}>
          ✈️
        </div>
        <span style={{ fontFamily: 'var(--font-display)', fontWeight: 800, fontSize: 18 }}>
          Voyagr
        </span>
        <span style={{
          fontSize: 9, fontWeight: 700, padding: '2px 6px', background: 'var(--accent-muted)',
          border: '1px solid rgba(200,255,0,0.2)', borderRadius: 'var(--radius-full)',
          color: 'var(--accent)', textTransform: 'uppercase', letterSpacing: '0.1em',
        }}>
          AI
        </span>
      </div>

      {/* Auth controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        {isLoggedIn ? (
          <>
            <span style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 500 }}>
              Hi, {userName || 'User'} 👋
            </span>
            <button
              onClick={handleLogout}
              style={{
                padding: '7px 14px', background: 'transparent', border: '1px solid var(--border)',
                borderRadius: 'var(--radius-sm)', color: 'var(--text-muted)', fontWeight: 600,
                fontSize: 12, cursor: 'pointer', fontFamily: 'var(--font-body)',
              }}
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <button
              onClick={() => navigate('/login')}
              style={{
                padding: '7px 14px', background: 'transparent', border: '1px solid var(--border)',
                borderRadius: 'var(--radius-sm)', color: 'var(--text-secondary)', fontWeight: 600,
                fontSize: 12, cursor: 'pointer', fontFamily: 'var(--font-body)',
              }}
            >
              Log in
            </button>
            <button
              onClick={() => navigate('/signup')}
              style={{
                padding: '7px 14px', background: 'var(--accent)', color: '#000',
                border: 'none', borderRadius: 'var(--radius-sm)', fontWeight: 700,
                fontSize: 12, cursor: 'pointer', fontFamily: 'var(--font-body)',
              }}
            >
              Sign up free
            </button>
          </>
        )}
      </div>
    </nav>
  );
}
