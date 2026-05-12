import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import api from '../../api/client';

const NAV_ITEMS = [
  { key: 'resumen',                icon: '📊', label: 'Resumen',          desc: 'Vista consolidada del caso' },
  { key: 'entrevista',             icon: '📝', label: 'Entrevista',        desc: 'Wizard de entrevista familiar' },
  { key: 'personas',               icon: '👨‍👩‍👧', label: 'Personas',         desc: 'Gestión de miembros familiares' },
  { key: 'relaciones',             icon: '🔗', label: 'Relaciones',        desc: 'Vínculos entre personas' },
  { key: 'familiograma',           icon: '🗺️', label: 'Familiograma',      desc: 'Editor interactivo del grafo' },
  { key: 'historial-familiograma', icon: '🕘', label: 'Historial',         desc: 'Versiones del familiograma' },
  { key: 'observaciones',          icon: '👁️', label: 'Observaciones',     desc: 'Conducta no verbal' },
  { key: 'plan',                   icon: '📋', label: 'Plan de Acción',    desc: 'Seguimiento y tareas' },
  { key: 'reporte',                icon: '📄', label: 'Reporte',           desc: 'Exportar datos completos' },
];

export default function CasoNNADetalle() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [caso, setCaso] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadCaso(); }, [id]);

  async function loadCaso() {
    try {
      const data = await api.getNnaCaso(id);
      setCaso(data);
    } catch {
      alert('Error al cargar caso NNA');
      navigate('/nna');
    } finally { setLoading(false); }
  }

  if (loading) return <div className="page-dashboard"><Topbar /><div className="container">Cargando...</div></div>;
  if (!caso) return null;

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">
        <button className="btn btn-secondary" style={{ marginBottom: '16px' }} onClick={() => navigate('/nna')}>
          ← Volver a Casos NNA
        </button>

        {/* Header del caso */}
        <div className="table-card" style={{ marginBottom: '24px', padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h2 style={{ margin: '0 0 6px 0', fontSize: '22px', fontWeight: 800 }}>🛡️ {caso.nna_nombre}</h2>
              <div style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>
                Edad: <strong>{caso.nna_edad || 'N/A'}</strong> ·{' '}
                Género: <strong style={{ textTransform: 'capitalize' }}>{caso.nna_genero || 'N/A'}</strong> ·{' '}
                Folio: <strong>NNA-{caso.id}</strong>
              </div>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                Creado: {new Date(caso.fecha_creacion).toLocaleDateString('es-MX')}
              </div>
            </div>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
              <span className={`badge ${caso.estado === 'activo' ? 'badge-active' : 'badge-inactive'}`}>
                {caso.estado === 'activo' ? 'Activo' : 'Cerrado'}
              </span>
              <button className="btn btn-primary" style={{ fontSize: '13px', padding: '8px 18px' }}
                onClick={() => navigate(`/nna/casos/${id}/resumen`)}>
                Ver Resumen Completo →
              </button>
            </div>
          </div>
        </div>

        {/* Módulos del caso */}
        <div className="table-card">
          <h3 style={{ marginBottom: '20px', color: 'var(--primary)' }}>Módulos del caso</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '14px' }}>
            {NAV_ITEMS.map(item => (
              <div
                key={item.key}
                onClick={() => navigate(`/nna/casos/${id}/${item.key}`)}
                style={{
                  background: 'var(--bg)', borderRadius: 'var(--radius-sm)', padding: '18px 20px',
                  boxShadow: 'var(--neo-shadow-sm)', cursor: 'pointer',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  display: 'flex', gap: '14px', alignItems: 'center', border: '1px solid var(--border)',
                }}
                onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = 'var(--neo-shadow)'; }}
                onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = 'var(--neo-shadow-sm)'; }}
              >
                <span style={{ fontSize: '28px', flexShrink: 0 }}>{item.icon}</span>
                <div>
                  <div style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '15px' }}>{item.label}</div>
                  <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '2px' }}>{item.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
