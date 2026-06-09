import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Topbar from '../components/Topbar';
import api from '../api/client';

const CONFIANZA_COLOR = { 1:'#e53e3e', 2:'#dd6b20', 3:'#d69e2e', 4:'#38a169', 5:'#2b6cb0' };
const CONFIANZA_LABEL = { 1:'Muy Bajo', 2:'Bajo', 3:'Medio', 4:'Alto', 5:'Muy Alto' };

function ConfianzaBadge({ nivel }) {
  const n = nivel || 3;
  return (
    <span style={{
      background: CONFIANZA_COLOR[n], color: '#fff', borderRadius: '12px',
      padding: '2px 10px', fontSize: '12px', fontWeight: 700,
    }}>
      {'★'.repeat(n)}{'☆'.repeat(5 - n)} {CONFIANZA_LABEL[n]}
    </span>
  );
}

export default function ColaboradoresPage() {
  const navigate = useNavigate();
  const [colaboradores, setColaboradores] = useState([]);
  const [pendientes, setPendientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtros, setFiltros] = useState({ tipo: '', confianza_min: '', rol: '' });
  const [tab, setTab] = useState('todos');
  const [evalModal, setEvalModal] = useState(null);
  const [evalForm, setEvalForm] = useState({ nivel_nuevo: 3, justificacion: '' });
  const [historialModal, setHistorialModal] = useState(null);
  const [historial, setHistorial] = useState([]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => { loadData(); }, [filtros]);

  async function loadData() {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filtros.tipo) params.append('tipo', filtros.tipo);
      if (filtros.confianza_min) params.append('confianza_min', filtros.confianza_min);
      if (filtros.rol) params.append('rol', filtros.rol);

      const [colab, pend] = await Promise.all([
        api.get(`/api/colaboradores/?${params}`),
        api.get('/api/colaboradores/pendientes-revision'),
      ]);
      setColaboradores(colab);
      setPendientes(pend);
    } catch (e) {
      setError('Error al cargar colaboradores');
    } finally {
      setLoading(false);
    }
  }

  async function handleEvaluar(e) {
    e.preventDefault();
    if (!evalModal) return;
    if (evalForm.justificacion.trim().length < 10) {
      setError('La justificación debe tener al menos 10 caracteres');
      return;
    }
    setSaving(true);
    try {
      await api.post(`/api/colaboradores/${evalModal.id}/evaluar-confianza`, {
        nivel_nuevo: parseInt(evalForm.nivel_nuevo),
        justificacion: evalForm.justificacion,
      });
      setEvalModal(null);
      setEvalForm({ nivel_nuevo: 3, justificacion: '' });
      await loadData();
    } catch (e) {
      setError(e.message || 'Error al guardar evaluación');
    } finally {
      setSaving(false);
    }
  }

  async function verHistorial(colaborador) {
    try {
      const data = await api.get(`/api/colaboradores/${colaborador.id}/historial-confianza`);
      setHistorial(data);
      setHistorialModal(colaborador);
    } catch {
      setError('Error al cargar historial');
    }
  }

  const lista = tab === 'pendientes' ? pendientes : colaboradores;

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2 style={{ margin: 0 }}>👤 Colaboradores</h2>
            <div style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
              Directorio de personal de planta y voluntarios
            </div>
          </div>
          {pendientes.length > 0 && (
            <div style={{ background: '#fff3cd', border: '1px solid #ffc107', borderRadius: '8px', padding: '8px 16px', fontSize: '13px', fontWeight: 600, color: '#856404' }}>
              ⚠️ {pendientes.length} colaborador(es) pendiente(s) de evaluación
            </div>
          )}
        </div>

        {error && (
          <div style={{ background: '#fff5f5', border: '1px solid #fc8181', borderRadius: '8px', padding: '12px 16px', marginBottom: '16px', color: '#c53030' }}>
            {error}
            <button onClick={() => setError('')} style={{ float: 'right', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 700 }}>✕</button>
          </div>
        )}

        {/* Tabs */}
        <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
          {[['todos', `Todos (${colaboradores.length})`], ['pendientes', `Pendientes de Revisión (${pendientes.length})`]].map(([key, label]) => (
            <button key={key} onClick={() => setTab(key)}
              style={{
                padding: '8px 18px', borderRadius: '8px', border: 'none', cursor: 'pointer',
                fontWeight: 600, fontSize: '14px',
                background: tab === key ? 'var(--primary)' : 'var(--bg)',
                color: tab === key ? '#fff' : 'var(--text-primary)',
                boxShadow: 'var(--neo-shadow-sm)',
              }}>
              {label}
            </button>
          ))}
        </div>

        {/* Filtros */}
        {tab === 'todos' && (
          <div className="table-card" style={{ padding: '16px 20px', marginBottom: '20px' }}>
            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'flex-end' }}>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>Tipo</label>
                <select value={filtros.tipo} onChange={e => setFiltros(f => ({ ...f, tipo: e.target.value }))}
                  style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '13px' }}>
                  <option value="">Todos</option>
                  <option value="planta">Planta</option>
                  <option value="voluntario">Voluntario</option>
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>Confianza mínima</label>
                <select value={filtros.confianza_min} onChange={e => setFiltros(f => ({ ...f, confianza_min: e.target.value }))}
                  style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '13px' }}>
                  <option value="">Cualquiera</option>
                  {[1,2,3,4,5].map(n => <option key={n} value={n}>{n} - {CONFIANZA_LABEL[n]}</option>)}
                </select>
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, marginBottom: '4px' }}>Rol</label>
                <select value={filtros.rol} onChange={e => setFiltros(f => ({ ...f, rol: e.target.value }))}
                  style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '13px' }}>
                  <option value="">Todos</option>
                  {['director','coordinador','psicologo','trabajador_social','legal'].map(r => (
                    <option key={r} value={r}>{r.replace('_',' ')}</option>
                  ))}
                </select>
              </div>
              <button className="btn btn-secondary" onClick={() => setFiltros({ tipo: '', confianza_min: '', rol: '' })}>
                Limpiar
              </button>
            </div>
          </div>
        )}

        {loading ? (
          <div className="table-card" style={{ padding: '40px', textAlign: 'center' }}>Cargando...</div>
        ) : lista.length === 0 ? (
          <div className="table-card" style={{ padding: '40px', textAlign: 'center', color: 'var(--text-secondary)' }}>
            {tab === 'pendientes' ? '✅ Todos los colaboradores han sido evaluados recientemente.' : 'No hay colaboradores que coincidan con los filtros.'}
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '16px' }}>
            {lista.map(c => (
              <div key={c.id} className="table-card" style={{ padding: '18px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                  <div style={{
                    width: '44px', height: '44px', borderRadius: '50%', flexShrink: 0,
                    background: c.tipo_colaboracion === 'voluntario' ? '#fed7aa' : 'var(--primary)',
                    color: c.tipo_colaboracion === 'voluntario' ? '#c05621' : '#fff',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 800, fontSize: '16px',
                  }}>
                    {c.nombre[0]}{c.apellido_paterno[0]}
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontWeight: 700, fontSize: '15px' }}>
                      {c.nombre} {c.apellido_paterno} {c.apellido_materno}
                    </div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>{c.correo}</div>
                  </div>
                  <span style={{
                    background: c.tipo_colaboracion === 'planta' ? '#ebf8ff' : '#fff3cd',
                    color: c.tipo_colaboracion === 'planta' ? '#2b6cb0' : '#856404',
                    borderRadius: '12px', padding: '3px 10px', fontSize: '11px', fontWeight: 700, flexShrink: 0,
                  }}>
                    {c.tipo_colaboracion === 'planta' ? 'Planta' : 'Voluntario'}
                  </span>
                </div>

                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', alignItems: 'center' }}>
                  <span style={{ background: '#e9ecef', borderRadius: '12px', padding: '2px 10px', fontSize: '12px', fontWeight: 600, textTransform: 'capitalize' }}>
                    {c.rol?.replace('_',' ')}
                  </span>
                  <ConfianzaBadge nivel={c.nivel_confianza} />
                </div>

                <div style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                  {c.fecha_ingreso && <span>Ingreso: {new Date(c.fecha_ingreso).toLocaleDateString('es-MX')}</span>}
                  {c.fecha_ultima_evaluacion ? (
                    <span>Última eval: {new Date(c.fecha_ultima_evaluacion).toLocaleDateString('es-MX')}</span>
                  ) : (
                    <span style={{ color: '#e53e3e', fontWeight: 600 }}>⚠ Sin evaluar</span>
                  )}
                </div>

                <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end', borderTop: '1px solid var(--border)', paddingTop: '10px' }}>
                  <button
                    onClick={() => verHistorial(c)}
                    style={{ background: 'none', border: '1px solid var(--border)', borderRadius: '6px', padding: '5px 12px', cursor: 'pointer', fontSize: '12px' }}>
                    Historial
                  </button>
                  <button
                    onClick={() => { setEvalModal(c); setEvalForm({ nivel_nuevo: c.nivel_confianza || 3, justificacion: '' }); }}
                    className="btn btn-primary" style={{ fontSize: '12px', padding: '5px 14px' }}>
                    Evaluar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Modal evaluar confianza */}
      {evalModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ background: '#fff', borderRadius: '12px', padding: '28px', width: '100%', maxWidth: '440px', boxShadow: '0 20px 60px rgba(0,0,0,0.3)' }}>
            <h3 style={{ margin: '0 0 6px 0' }}>Evaluar Nivel de Confianza</h3>
            <div style={{ color: 'var(--text-secondary)', fontSize: '13px', marginBottom: '20px' }}>
              {evalModal.nombre} {evalModal.apellido_paterno}
            </div>
            <form onSubmit={handleEvaluar}>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: '12px', fontSize: '14px' }}>
                  Nivel de Confianza *
                </label>
                <div style={{ display: 'flex', gap: '8px' }}>
                  {[1,2,3,4,5].map(n => (
                    <button key={n} type="button"
                      onClick={() => setEvalForm(f => ({ ...f, nivel_nuevo: n }))}
                      style={{
                        flex: 1, padding: '10px 4px', borderRadius: '8px', border: '2px solid',
                        borderColor: evalForm.nivel_nuevo === n ? CONFIANZA_COLOR[n] : 'var(--border)',
                        background: evalForm.nivel_nuevo === n ? CONFIANZA_COLOR[n] : '#fff',
                        color: evalForm.nivel_nuevo === n ? '#fff' : CONFIANZA_COLOR[n],
                        cursor: 'pointer', fontWeight: 700, fontSize: '13px',
                        transition: 'all 0.15s',
                      }}>
                      {n}<br/><span style={{ fontSize: '10px', fontWeight: 400 }}>{CONFIANZA_LABEL[n]}</span>
                    </button>
                  ))}
                </div>
              </div>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: '6px', fontSize: '14px' }}>
                  Justificación * <span style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 400 }}>(mín. 10 caracteres)</span>
                </label>
                <textarea
                  value={evalForm.justificacion}
                  onChange={e => setEvalForm(f => ({ ...f, justificacion: e.target.value }))}
                  required
                  rows={3}
                  placeholder="Describe el motivo de esta evaluación..."
                  style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '14px', resize: 'vertical' }} />
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setEvalModal(null)}>Cancelar</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Guardando...' : 'Guardar Evaluación'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal historial */}
      {historialModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ background: '#fff', borderRadius: '12px', padding: '28px', width: '100%', maxWidth: '500px', maxHeight: '80vh', overflowY: 'auto', boxShadow: '0 20px 60px rgba(0,0,0,0.3)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0 }}>Historial de Confianza</h3>
              <button onClick={() => setHistorialModal(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '20px' }}>✕</button>
            </div>
            <div style={{ fontWeight: 600, marginBottom: '16px', color: 'var(--text-secondary)' }}>
              {historialModal.nombre} {historialModal.apellido_paterno}
            </div>
            {historial.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>Sin evaluaciones previas.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {historial.map(h => (
                  <div key={h.id} style={{ background: 'var(--bg)', borderRadius: '8px', padding: '14px', border: '1px solid var(--border)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                        <ConfianzaBadge nivel={h.nivel_anterior} />
                        <span style={{ color: 'var(--text-secondary)' }}>→</span>
                        <ConfianzaBadge nivel={h.nivel_nuevo} />
                      </div>
                      <span style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
                        {new Date(h.fecha).toLocaleDateString('es-MX')}
                      </span>
                    </div>
                    <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>
                      <strong>Evaluador:</strong> {h.evaluador ? `${h.evaluador.nombre} ${h.evaluador.apellido_paterno}` : `#${h.evaluador_id}`}
                    </div>
                    <div style={{ fontSize: '13px', marginTop: '6px', fontStyle: 'italic' }}>{h.justificacion}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
