import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import Modal from '../../components/Modal';
import api from '../../api/client';

export default function HistorialFamiliogramaPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [historial, setHistorial] = useState([]);
  const [caso, setCaso] = useState(null);
  const [loading, setLoading] = useState(true);
  const [restaurarTarget, setRestaurarTarget] = useState(null);
  const [restoring, setRestoring] = useState(false);
  const [expandedId, setExpandedId] = useState(null);
  const [msg, setMsg] = useState('');

  useEffect(() => { loadData(); }, [id]);

  async function loadData() {
    try {
      const [c, h] = await Promise.all([api.getNnaCaso(id), api.getNnaFamiliogramaHistorial(id)]);
      setCaso(c); setHistorial(h);
    } catch { setMsg('Error al cargar historial'); }
    finally { setLoading(false); }
  }

  async function handleRestaurar() {
    setRestoring(true);
    try {
      await api.restaurarVersionFamiliograma(id, restaurarTarget.id);
      setRestaurarTarget(null);
      setMsg('✅ Versión restaurada correctamente.');
      await loadData();
    } catch (err) { setMsg(err.message || 'Error al restaurar'); }
    finally { setRestoring(false); }
  }

  const formatFecha = (f) => f ? new Date(f).toLocaleString('es-MX') : '—';
  const countNodes = (g) => g?.nodes?.length || 0;
  const countEdges = (g) => g?.edges?.length || 0;

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px', flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={() => navigate(`/nna/casos/${id}/familiograma`)}>← Volver al Editor</button>
          {caso && <h2 style={{ color: 'var(--text-primary)', fontSize: '20px', fontWeight: 700 }}>
            🕘 Historial del Familiograma — {caso.nna_nombre}
          </h2>}
        </div>

        {msg && <div className={`mensaje ${msg.startsWith('✅') ? 'success' : 'error'}`}>{msg}</div>}

        <div className="table-card">
          <div className="table-header">
            <h3>Versiones guardadas ({historial.length})</h3>
            <button className="btn btn-secondary" onClick={() => navigate(`/nna/casos/${id}/familiograma`)}>
              ✏️ Ir al editor
            </button>
          </div>

          {loading && <div className="status-msg">Cargando...</div>}
          {!loading && historial.length === 0 && (
            <div className="status-msg">
              No hay versiones guardadas aún. El historial se genera automáticamente cada vez que guardas el familiograma.
            </div>
          )}

          {!loading && historial.map(h => (
            <div key={h.id} style={{
              background: 'var(--bg)', borderRadius: 'var(--radius-sm)', padding: '16px 20px',
              boxShadow: 'var(--neo-shadow-sm)', marginBottom: '10px', border: '1px solid var(--border)'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span style={{
                    background: 'var(--primary)', color: 'white', borderRadius: '50%',
                    width: '36px', height: '36px', display: 'flex', alignItems: 'center',
                    justifyContent: 'center', fontWeight: 700, fontSize: '14px', flexShrink: 0
                  }}>v{h.version}</span>
                  <div>
                    <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{h.notas_version || `Versión ${h.version}`}</div>
                    <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                      {formatFecha(h.fecha)} · por {h.modificado_por_nombre || 'Sistema'}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
                      {countNodes(h.grafo_json)} personas · {countEdges(h.grafo_json)} conexiones
                    </div>
                  </div>
                </div>
                <div className="btn-actions">
                  <button className="btn-sm btn-view" onClick={() => setExpandedId(expandedId === h.id ? null : h.id)}>
                    {expandedId === h.id ? 'Ocultar JSON' : 'Ver JSON'}
                  </button>
                  <button className="btn-sm btn-edit" onClick={() => setRestaurarTarget(h)}>
                    ↩ Restaurar
                  </button>
                </div>
              </div>

              {expandedId === h.id && (
                <div style={{
                  marginTop: '12px', background: 'var(--bg-dark)', borderRadius: 'var(--radius-sm)',
                  padding: '12px', overflowX: 'auto', maxHeight: '200px', overflowY: 'auto'
                }}>
                  <pre style={{ fontSize: '11px', color: 'var(--text-secondary)', margin: 0 }}>
                    {JSON.stringify(h.grafo_json, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {restaurarTarget && (
        <Modal
          title={`¿Restaurar versión ${restaurarTarget.version}?`}
          message={`Esto sobrescribirá el familiograma actual con la versión "${restaurarTarget.notas_version}". La versión actual se guardará en el historial antes de restaurar.`}
          confirmText={restoring ? 'Restaurando...' : 'Restaurar'}
          onConfirm={handleRestaurar}
          onCancel={() => setRestaurarTarget(null)}
        />
      )}
    </div>
  );
}
