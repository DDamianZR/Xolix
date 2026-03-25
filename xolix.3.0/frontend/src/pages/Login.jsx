import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

export default function Login() {
  const [correo, setCorreo] = useState('');
  const [password, setPassword] = useState('');
  const [mensaje, setMensaje] = useState('');
  const [msgColor, setMsgColor] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setMensaje('Verificando...');
    setMsgColor('info');
    setLoading(true);

    try {
      const data = await api.login(correo, password);
      login(data.access_token, data.rol);
      setMensaje('Login exitoso ✓');
      setMsgColor('success');
      setTimeout(() => navigate('/dashboard'), 600);
    } catch (err) {
      setMensaje(err.message);
      setMsgColor('error');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-center">
      <div className="neo-card">
        <div className="card-header">
          <h1 className="logo">XOLIX</h1>
          <p className="subtitle">Sistema de Gestión</p>
        </div>

        <form onSubmit={handleSubmit} className="form-stack">
          <input
            type="email"
            placeholder="Correo electrónico"
            value={correo}
            onChange={(e) => setCorreo(e.target.value)}
            required
            autoFocus
          />
          <input
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Verificando...' : 'Iniciar sesión'}
          </button>
        </form>

        {mensaje && <div className={`mensaje ${msgColor}`}>{mensaje}</div>}
      </div>
    </div>
  );
}
