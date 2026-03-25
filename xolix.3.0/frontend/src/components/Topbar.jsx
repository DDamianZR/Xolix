import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export default function Topbar() {
  const { rol, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/');
  }

  return (
    <div className="topbar">
      <h2 className="topbar-logo">XOLIX</h2>
      <span className="topbar-info">Sesión: {rol || 'usuario'}</span>
      <button className="btn-logout" onClick={handleLogout}>
        Cerrar sesión
      </button>
    </div>
  );
}
