import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';

const ROLES_EQUIPO = [
  'psicologo','trabajador_social','legal','medico','voluntario_apoyo','coordinador','otro'
];

const CONFIANZA_COLOR = { 1:'#e53e3e', 2:'#dd6b20', 3:'#d69e2e', 4:'#38a169', 5:'#2b6cb0' };
const CONFIANZA_LABEL = { 1:'Muy Bajo', 2:'Bajo', 3:'Medio', 4:'Alto', 5:'Muy Alto' };

function NivelConfianza({ nivel }) {
  const n = nivel || 3;
  return (
    <span style={{
      background: CONFIANZA_COLOR[n], color: '#fff',
      borderRadius: '12px', padding: '2px 10px', fontSize: '12px', fontWeight: 700,
    }}>
      {'★'.repeat(n)}{'☆'.repeat(5 - n)} {CONFIANZA_LABEL[n]}
    </span>
  );
}

export default function EquipoCasoPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { rol } = useAuth();
  const [currentUserId, setCurrentUserId] = useState(null);
  const [caso, setCaso] = useState(null);
  const [equipo, setEquipo] = useState([]);
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ usuario_id: '', rol_en_equipo: 'psicologo', observaciones: '' });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  const esResponsableOSuperior = (
    ['director','coordinador'].includes(rol) ||
    (rol === 'trabajador_social' && caso?.responsable_id === currentUserId)
  );

  useEffect(() => { loadData(); }, [id]);

  async function loadData() {
    try {
      const [casoData, equipoData, usersData, meData] = await Promise.all([
        api.getNnaCaso(id),
        api.get(`/api/nna/casos/${id}/equipo`),
        api.get('/api/usuarios/'),
        api.get('/api/auth/me'),
      ]);
      setCaso(casoData);
      setEquipo(equipoData);
      setUsuarios(usersData.filter(u => u.activo));
      setCurrentUserId(meData.id);
    } catch (e) {
      setError('Error al cargar datos');
    } finally {
      setLoading(false);
    }
  }

  async function handleAgregar(e) {
    e.preventDefault();
    if (!form.usuario_id) return;
    setSaving(true);
    try {
      await api.post(`/api/nna/casos/${id}/equipo`, {
        usuario_id: parseInt(form.usuario_id),
        rol_en_equipo: form.rol_en_equipo,
        observaciones: form.observaciones || null,
      });
      setShowModal(false);
      setForm({ usuario_id: '', rol_en_equipo: 'psicologo', observaciones: '' });
      await loadData();
    } catch (e) {
      setError(e.message || 'Error al agregar miembro');
    } finally {
      setSaving(false);
    }
  }

  async function handleQuitar(usuarioId, nombre) {
    if (!confirm(`¿Quitar a ${nombre} del equipo?`)) return;
    try {
      await api.delete(`/api/nna/casos/${id}/equipo/${usuarioId}`);
      await loadData();
    } catch (e) {
      setError(e.message || 'Error al quitar miembro');
    }
  }

  const responsable = usuarios.find(u => u.id === caso?.responsable_id);
  const miembrosIds = new Set(equipo.map(m => m.usuario_id));
  const disponibles = usuarios.filter(u => !miembrosIds.has(u.id) && u.id !== caso?.responsable_id);

  if (loading) return <div className="page-dashboard"><Topbar /><div className="container">Cargando equipo...</div></div>;

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">
        <button className="btn btn-secondary" style={{ marginBottom: '16px' }}
          onClick={() => navigate(`/nna/casos/${id}`)}>
          ← Volver al caso
        </button>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2 style={{ margin: 0 }}>👥 Equipo Multidisciplinario</h2>
            <div style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
              Caso: <strong>{caso?.nna_nombre}</strong> · NNA-{id}
            </div>
          </div>
          {esResponsableOSuperior && (
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>
              + Agregar Miembro
            </button>
          )}
        </div>

        {error && (
          <div style={{ background: '#fff5f5', border: '1px solid #fc8181', borderRadius: '8px', padding: '12px 16px', marginBottom: '16px', color: '#c53030' }}>
            {error} <button onClick={() => setError('')} style={{ float: 'right', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 700 }}>✕</button>
          </div>
        )}

        {/* Responsable */}
        <div className="table-card" style={{ marginBottom: '20px', padding: '20px' }}>
          <h3 style={{ margin: '0 0 16px 0', color: 'var(--primary)', fontSize: '15px' }}>
            Trabajador Social Responsable
          </h3>
          {responsable ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
              <div style={{
                width: '48px', height: '48px', borderRadius: '50%', background: 'var(--primary)',
                color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 800, fontSize: '18px', flexShrink: 0,
              }}>
                {responsable.nombre[0]}{responsable.apellido_paterno[0]}
              </div>
              <div>
                <div style={{ fontWeight: 700, fontSize: '16px' }}>
                  {responsable.nombre} {responsable.apellido_paterno}
                </div>
                <div style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{responsable.correo}</div>
              </div>
              <NivelConfianza nivel={responsable.nivel_confianza} />
              <span style={{ background: responsable.tipo_colaboracion === 'planta' ? '#ebf8ff' : '#fff3cd',
                color: responsable.tipo_colaboracion === 'planta' ? '#2b6cb0' : '#856404',
                borderRadius: '12px', padding: '2px 10px', fontSize: '12px', fontWeight: 600,
              }}>
                {responsable.tipo_colaboracion === 'planta' ? 'Personal de Planta' : 'Voluntario'}
              </span>
            </div>
          ) : (
            <div style={{ color: 'var(--text-secondary)', fontStyle: 'italic' }}>
              Sin responsable asignado. Un director o coordinador puede asignar uno.
            </div>
          )}
        </div>

        {/* Miembros del equipo */}
        <div className="table-card" style={{ padding: '20px' }}>
          <h3 style={{ margin: '0 0 16px 0', color: 'var(--primary)', fontSize: '15px' }}>
            Miembros del Equipo ({equipo.length})
          </h3>
          {equipo.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
              No hay miembros en el equipo aún.
              {esResponsableOSuperior && ' Usa "+ Agregar Miembro" para comenzar.'}
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '14px' }}>
              {equipo.map(m => {
                const u = m.usuario || usuarios.find(x => x.id === m.usuario_id);
                return (
                  <div key={m.id} style={{
                    background: 'var(--bg)', borderRadius: 'var(--radius-sm)', padding: '16px',
                    border: '1px solid var(--border)', boxShadow: 'var(--neo-shadow-sm)',
                    display: 'flex', flexDirection: 'column', gap: '10px',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                      <div style={{
                        width: '40px', height: '40px', borderRadius: '50%', background: '#667eea',
                        color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontWeight: 700, flexShrink: 0,
                      }}>
                        {u ? `${u.nombre[0]}${u.apellido_paterno[0]}` : '?'}
                      </div>
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <div style={{ fontWeight: 700, fontSize: '14px' }}>
                          {u ? `${u.nombre} ${u.apellido_paterno}` : `Usuario ${m.usuario_id}`}
                        </div>
                        <div style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>{u?.correo}</div>
                      </div>
                    </div>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', alignItems: 'center' }}>
                      <span style={{ background: '#e9f7ef', color: '#27ae60', borderRadius: '12px', padding: '2px 10px', fontSize: '12px', fontWeight: 600, textTransform: 'capitalize' }}>
                        {m.rol_en_equipo.replace('_', ' ')}
                      </span>
                      {u && <NivelConfianza nivel={u.nivel_confianza} />}
                      {u && (
                        <span style={{ background: u.tipo_colaboracion === 'planta' ? '#ebf8ff' : '#fff3cd',
                          color: u.tipo_colaboracion === 'planta' ? '#2b6cb0' : '#856404',
                          borderRadius: '12px', padding: '2px 10px', fontSize: '11px', fontWeight: 600,
                        }}>
                          {u.tipo_colaboracion === 'planta' ? 'Planta' : 'Voluntario'}
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                      Asignado: {new Date(m.fecha_asignacion).toLocaleDateString('es-MX')}
                    </div>
                    {m.observaciones && (
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)', fontStyle: 'italic', borderTop: '1px solid var(--border)', paddingTop: '8px' }}>
                        {m.observaciones}
                      </div>
                    )}
                    {esResponsableOSuperior && (
                      <button
                        onClick={() => handleQuitar(m.usuario_id, u ? `${u.nombre} ${u.apellido_paterno}` : 'este miembro')}
                        style={{ alignSelf: 'flex-end', background: 'none', border: '1px solid #fc8181', color: '#e53e3e', borderRadius: '6px', padding: '4px 12px', cursor: 'pointer', fontSize: '12px' }}>
                        Quitar
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Modal agregar miembro */}
      {showModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '20px' }}>
          <div style={{ background: '#fff', borderRadius: '12px', padding: '28px', width: '100%', maxWidth: '480px', boxShadow: '0 20px 60px rgba(0,0,0,0.3)' }}>
            <h3 style={{ margin: '0 0 20px 0' }}>Agregar Miembro al Equipo</h3>
            <form onSubmit={handleAgregar}>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: '6px', fontSize: '14px' }}>
                  Colaborador *
                </label>
                <select
                  value={form.usuario_id}
                  onChange={e => setForm(f => ({ ...f, usuario_id: e.target.value }))}
                  required
                  style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '14px' }}>
                  <option value="">-- Seleccionar colaborador --</option>
                  {disponibles.map(u => (
                    <option key={u.id} value={u.id}>
                      {u.nombre} {u.apellido_paterno} — {u.rol}
                      {u.tipo_colaboracion === 'voluntario' ? ' (Voluntario)' : ''}
                    </option>
                  ))}
                </select>
              </div>
              <div style={{ marginBottom: '16px' }}>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: '6px', fontSize: '14px' }}>
                  Rol en el equipo *
                </label>
                <select
                  value={form.rol_en_equipo}
                  onChange={e => setForm(f => ({ ...f, rol_en_equipo: e.target.value }))}
                  style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '14px' }}>
                  {ROLES_EQUIPO.map(r => (
                    <option key={r} value={r}>{r.replace('_', ' ')}</option>
                  ))}
                </select>
              </div>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', fontWeight: 600, marginBottom: '6px', fontSize: '14px' }}>
                  Observaciones (opcional)
                </label>
                <textarea
                  value={form.observaciones}
                  onChange={e => setForm(f => ({ ...f, observaciones: e.target.value }))}
                  rows={2}
                  placeholder="Notas sobre la participación en el caso..."
                  style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '14px', resize: 'vertical' }} />
              </div>
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancelar
                </button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? 'Guardando...' : 'Agregar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
