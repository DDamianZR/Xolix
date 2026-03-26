import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Topbar() {
  const { rol, logout, theme, toggleTheme } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/');
  }

  return (
    <div className="topbar">
      <h2 className="topbar-logo" onClick={() => navigate('/dashboard')} style={{ cursor: 'pointer' }}>
        XOLIX
      </h2>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <span className="topbar-info">Sesión: {rol || 'usuario'}</span>
        <button
          className="btn-logout"
          onClick={toggleTheme}
          title={theme === 'light' ? 'Activar modo oscuro' : 'Activar modo claro'}
          style={{ color: 'var(--text-secondary)', background: 'var(--bg)', padding: '8px 14px' }}
        >
          {theme === 'light' ? '🌙' : '☀️'}
        </button>
        <button className="btn-logout" onClick={handleLogout}>
          Cerrar sesión
        </button>
      </div>
    </div>
  );
}
