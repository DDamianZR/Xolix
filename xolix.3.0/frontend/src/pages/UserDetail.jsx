import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

export default function UserDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const [user, setUser] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const data = await api.getUser(id);
        setUser(data);
      } catch {
        setError(true);
      }
    }
    load();
  }, [id]);

  if (error) {
    return (
      <div className="page-center">
        <div className="neo-card">
          <h2 className="logo">XOLIX</h2>
          <p className="subtitle" style={{ color: '#E57373' }}>Usuario no encontrado.</p>
          <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
            ← Volver
          </button>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="page-center">
        <div className="neo-card">
          <h2 className="logo">XOLIX</h2>
          <p className="subtitle">Cargando información...</p>
        </div>
      </div>
    );
  }

  const fields = [
    { label: 'Nombre Completo', value: `${user.nombre} ${user.apellido_paterno} ${user.apellido_materno}` },
    { label: 'Correo', value: user.correo },
    { label: 'RFC', value: user.rfc },
    { label: 'CURP', value: user.curp },
    { label: 'Sexo', value: user.sexo === 'M' ? 'Masculino' : 'Femenino' },
    { label: 'Edad', value: `${user.edad} años` },
    { label: 'Dirección', value: `${user.calle} ${user.numero}, Col. ${user.colonia}, ${user.municipio}, ${user.estado}. C.P. ${user.codigo_postal}`, full: true },
    { label: 'Referencias', value: user.calles_aledanas || 'N/A', full: true },
    { label: 'Tipo de personal', value: user.tipo_personal },
    { label: 'Rol', value: user.rol },
    {
      label: 'Estado',
      value: user.activo ? 'Activo' : 'Inactivo',
      badge: user.activo ? 'badge-active' : 'badge-inactive',
    },
    {
      label: 'Fecha de registro',
      value: user.fecha_creacion
        ? new Date(user.fecha_creacion).toLocaleDateString('es-MX')
        : 'N/A',
    },
  ];

  return (
    <div className="page-center">
      <div className="neo-card full">
        <h2 className="logo">XOLIX</h2>
        <p className="subtitle">Datos del personal</p>

        <div className="detail-grid">
          {fields.map((f) => (
            <div key={f.label} className={`detail-item ${f.full ? 'full-width' : ''}`}>
              <label>{f.label}</label>
              {f.badge ? (
                <span className={`badge ${f.badge}`}>{f.value}</span>
              ) : (
                <span style={{ textTransform: f.label === 'Tipo de personal' || f.label === 'Rol' ? 'capitalize' : 'none' }}>
                  {f.value}
                </span>
              )}
            </div>
          ))}
        </div>

        <div className="form-actions">
          <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
            ← Volver
          </button>
          {isAdmin && (
            <button className="btn btn-primary" onClick={() => navigate(`/editar/${id}`)}>
              Editar
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
