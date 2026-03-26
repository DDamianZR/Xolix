import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';

const API_BASE = '/api';

export default function Verificar() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');
  
  const [estado, setEstado] = useState('verificando'); // verificando, exito, error
  const [mensaje, setMensaje] = useState('');

  useEffect(() => {
    if (!token) {
      setEstado('error');
      setMensaje('No se proporcionó un token de verificación en la URL.');
      return;
    }

    verificarToken(token);
  }, [token]);

  async function verificarToken(tok) {
    try {
      const res = await fetch(`${API_BASE}/auth/verificar/${tok}`);
      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.detail || 'Error al verificar la cuenta');
      }

      setEstado('exito');
      setMensaje(data.mensaje || 'Cuenta verificada con éxito.');
    } catch (err) {
      setEstado('error');
      setMensaje(err.message);
    }
  }

  return (
    <div className="page-center">
      <div className="neo-card" style={{ maxWidth: '400px', textAlign: 'center' }}>
        <h2 className="logo" style={{ marginBottom: '1.5rem' }}>XOLIX</h2>
        
        {estado === 'verificando' && (
          <div>
            <div className="loader" style={{ margin: '0 auto 1rem auto' }}></div>
            <p className="subtitle">Verificando tu cuenta...</p>
          </div>
        )}

        {estado === 'exito' && (
          <div>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
            <h3 style={{ marginBottom: '1rem', color: 'var(--text-main)' }}>¡Verificación Exitosa!</h3>
            <p className="subtitle" style={{ marginBottom: '2rem' }}>
              {mensaje}
            </p>
            <button className="btn btn-primary" onClick={() => navigate('/')} style={{ width: '100%' }}>
              Iniciar Sesión
            </button>
          </div>
        )}

        {estado === 'error' && (
          <div>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>❌</div>
            <h3 style={{ marginBottom: '1rem', color: '#ff4d4f' }}>Error de Verificación</h3>
            <p className="subtitle" style={{ marginBottom: '2rem' }}>
              {mensaje}
            </p>
            <Link to="/" className="btn btn-secondary" style={{ display: 'block', width: '100%' }}>
              Volver al Inicio
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
