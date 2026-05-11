import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import api from '../../api/client';

export default function CasoNNADetalle() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [caso, setCaso] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('resumen');

  useEffect(() => {
    loadCaso();
  }, [id]);

  async function loadCaso() {
    try {
      const data = await api.getNnaCaso(id);
      setCaso(data);
    } catch (err) {
      alert('Error al cargar caso NNA');
      navigate('/nna');
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className="page-dashboard"><Topbar /><div className="container">Cargando...</div></div>;
  if (!caso) return null;

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">
        <button className="btn btn-secondary" style={{ marginBottom: '16px' }} onClick={() => navigate('/nna')}>
          ← Volver a Casos
        </button>

        <div className="table-card" style={{ marginBottom: '24px', padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h2 style={{ margin: '0 0 8px 0' }}>{caso.nna_nombre}</h2>
              <div style={{ color: 'var(--text-secondary)' }}>
                Edad: {caso.nna_edad || 'N/A'} • Género: {caso.nna_genero || 'N/A'} • Folio: NNA-{caso.id}
              </div>
            </div>
            <span className={`badge ${caso.estado === 'activo' ? 'badge-active' : 'badge-inactive'}`}>
              {caso.estado === 'activo' ? 'Activo' : 'Cerrado'}
            </span>
          </div>
        </div>

        <div className="tabs" style={{ display: 'flex', gap: '8px', marginBottom: '24px', borderBottom: '1px solid var(--border)' }}>
          {['resumen', 'entrevista', 'familiograma', 'observaciones', 'plan'].map(tab => (
            <button
              key={tab}
              style={{
                padding: '12px 24px',
                background: 'none',
                border: 'none',
                borderBottom: activeTab === tab ? '3px solid var(--primary)' : '3px solid transparent',
                color: activeTab === tab ? 'var(--primary)' : 'var(--text)',
                fontWeight: activeTab === tab ? 'bold' : 'normal',
                cursor: 'pointer',
                textTransform: 'capitalize'
              }}
              onClick={() => setActiveTab(tab)}
            >
              {tab.replace('-', ' ')}
            </button>
          ))}
        </div>

        <div className="tab-content">
          {activeTab === 'resumen' && (
            <div className="table-card" style={{ padding: '24px' }}>
              <h3>Resumen del Caso</h3>
              <p>Este panel consolida la información de protección.</p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '24px' }}>
                <div style={{ padding: '16px', border: '1px solid var(--border)', borderRadius: '8px' }}>
                  <h4>Entrevista Inicial</h4>
                  <button className="btn-sm btn-primary" style={{ marginTop: '12px' }} onClick={() => navigate(`/nna/casos/${id}/entrevista`)}>
                    Ir al Wizard
                  </button>
                </div>
                <div style={{ padding: '16px', border: '1px solid var(--border)', borderRadius: '8px' }}>
                  <h4>Familiograma</h4>
                  <button className="btn-sm btn-primary" style={{ marginTop: '12px' }} onClick={() => navigate(`/nna/casos/${id}/familiograma`)}>
                    Abrir Editor
                  </button>
                </div>
                <div style={{ padding: '16px', border: '1px solid var(--border)', borderRadius: '8px' }}>
                  <h4>Observaciones No Verbales</h4>
                  <button className="btn-sm btn-primary" style={{ marginTop: '12px' }} onClick={() => navigate(`/nna/casos/${id}/observaciones`)}>
                    Ver Registro
                  </button>
                </div>
                <div style={{ padding: '16px', border: '1px solid var(--border)', borderRadius: '8px' }}>
                  <h4>Plan de Acción</h4>
                  <button className="btn-sm btn-primary" style={{ marginTop: '12px' }} onClick={() => navigate(`/nna/casos/${id}/plan`)}>
                    Ver Progreso
                  </button>
                </div>
              </div>
            </div>
          )}
          {/* We use navigation instead of inline components for the complex modules to give them full screen space */}
          {activeTab !== 'resumen' && (
            <div className="status-msg">
              Seleccione la opción desde el Resumen o use los botones de navegación.
              (Redirigiendo...)
              {setTimeout(() => navigate(`/nna/casos/${id}/${activeTab}`), 500)}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
