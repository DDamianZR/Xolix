import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import Modal from '../../components/Modal';
import api from '../../api/client';

const TIPO_RELACION_LABELS = {
  biologica: 'Biológica', legal: 'Legal',
  emocional_positiva: 'Emocional positiva', conflictiva: 'Conflictiva',
  protectora: 'Protectora', dependencia: 'Dependencia',
  separacion: 'Separación', desconocida: 'Desconocida',
};
const TIPO_RELACION_COLORS = {
  biologica: '#6c63ff', legal: '#1976d2', emocional_positiva: '#4caf50',
  conflictiva: '#e53935', protectora: '#00897b', dependencia: '#f9a825',
  separacion: '#757575', desconocida: '#9aa3b2',
};

const emptyForm = {
  persona_origen_id: '', persona_destino_id: '',
  tipo_relacion: 'biologica', descripcion: '', bidireccional: true
};

export default function RelacionesFamiliaresPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [relaciones, setRelaciones] = useState([]);
  const [personas, setPersonas] = useState([]);
  const [caso, setCaso] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editTarget, setEditTarget] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => { loadData(); }, [id]);

  async function loadData() {
    try {
      const [c, r, p] = await Promise.all([
        api.getNnaCaso(id), api.getNnaRelaciones(id), api.getNnaPersonas(id)
      ]);
      setCaso(c); setRelaciones(r); setPersonas(p);
    } catch { setMsg('Error al cargar datos'); }
    finally { setLoading(false); }
  }

  function openNew() { setForm(emptyForm); setEditTarget(null); setShowForm(true); setMsg(''); }
  function openEdit(r) {
    setForm({
      persona_origen_id: r.persona_origen_id, persona_destino_id: r.persona_destino_id,
      tipo_relacion: r.tipo_relacion, descripcion: r.descripcion || '', bidireccional: r.bidireccional,
    });
    setEditTarget(r); setShowForm(true); setMsg('');
  }

  async function handleSave(e) {
    e.preventDefault();
    if (!form.persona_origen_id || !form.persona_destino_id) { setMsg('Selecciona ambas personas'); return; }
    if (+form.persona_origen_id === +form.persona_destino_id) { setMsg('Las personas deben ser diferentes'); return; }
    setSaving(true);
    try {
      const payload = { ...form, persona_origen_id: +form.persona_origen_id, persona_destino_id: +form.persona_destino_id };
      if (editTarget) await api.updateNnaRelacion(id, editTarget.id, payload);
      else await api.createNnaRelacion(id, payload);
      setShowForm(false); await loadData();
    } catch (err) { setMsg(err.message || 'Error al guardar'); }
    finally { setSaving(false); }
  }

  async function handleDelete() {
    try { await api.deleteNnaRelacion(id, deleteTarget); setDeleteTarget(null); await loadData(); }
    catch { alert('Error al eliminar relación'); }
  }

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px', flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={() => navigate(`/nna/casos/${id}`)}>← Volver al Caso</button>
          {caso && <h2 style={{ color: 'var(--text-primary)', fontSize: '20px', fontWeight: 700 }}>
            🔗 Relaciones Familiares — {caso.nna_nombre}
          </h2>}
        </div>

        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
          {Object.entries(TIPO_RELACION_LABELS).map(([key, label]) => (
            <span key={key} style={{
              padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 600,
              background: TIPO_RELACION_COLORS[key] + '22', color: TIPO_RELACION_COLORS[key],
              border: `1px solid ${TIPO_RELACION_COLORS[key]}44`
            }}>{label}</span>
          ))}
        </div>

        <div className="table-card">
          <div className="table-header">
            <h3>Relaciones ({relaciones.length})</h3>
            <button className="btn btn-add" onClick={openNew} disabled={personas.length < 2}>+ Nueva relación</button>
          </div>
          {personas.length < 2 && !loading && (
            <div className="mensaje info" style={{ marginBottom: '12px' }}>
              ⚠️ Se necesitan al menos 2 personas.{' '}
              <span style={{ cursor: 'pointer', color: 'var(--primary)', textDecoration: 'underline' }}
                onClick={() => navigate(`/nna/casos/${id}/personas`)}>Agregar personas →</span>
            </div>
          )}
          {loading && <div className="status-msg">Cargando...</div>}
          {!loading && relaciones.length === 0 && <div className="status-msg">No hay relaciones definidas.</div>}
          {!loading && relaciones.map(r => (
            <div key={r.id} style={{
              background: 'var(--bg)', borderRadius: 'var(--radius-sm)', padding: '16px 20px',
              boxShadow: 'var(--neo-shadow-sm)', display: 'flex', alignItems: 'center',
              gap: '16px', flexWrap: 'wrap', marginBottom: '10px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1 }}>
                <strong>{r.persona_origen_nombre}</strong>
                <span style={{ color: TIPO_RELACION_COLORS[r.tipo_relacion], fontSize: '18px' }}>
                  {r.bidireccional ? '↔' : '→'}
                </span>
                <strong>{r.persona_destino_nombre}</strong>
              </div>
              <span className="badge" style={{
                background: TIPO_RELACION_COLORS[r.tipo_relacion] + '22',
                color: TIPO_RELACION_COLORS[r.tipo_relacion],
                border: `1px solid ${TIPO_RELACION_COLORS[r.tipo_relacion]}44`
              }}>{TIPO_RELACION_LABELS[r.tipo_relacion] || r.tipo_relacion}</span>
              {r.descripcion && <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{r.descripcion}</span>}
              <div className="btn-actions">
                <button className="btn-sm btn-edit" onClick={() => openEdit(r)}>Editar</button>
                <button className="btn-sm btn-delete" onClick={() => setDeleteTarget(r.id)}>Eliminar</button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {showForm && (
        <div className="modal-overlay active" onClick={e => e.target === e.currentTarget && setShowForm(false)}>
          <div className="modal-box" style={{ width: '500px', maxWidth: '95vw', textAlign: 'left' }}>
            <h3 style={{ marginBottom: '20px' }}>{editTarget ? 'Editar Relación' : 'Nueva Relación Familiar'}</h3>
            <form onSubmit={handleSave}>
              <div className="field-group">
                <label className="field-label">Persona origen *</label>
                <select value={form.persona_origen_id} onChange={e => setForm({ ...form, persona_origen_id: e.target.value })} disabled={!!editTarget}>
                  <option value="">Seleccionar...</option>
                  {personas.map(p => <option key={p.id} value={p.id}>{p.nombre}</option>)}
                </select>
              </div>
              <div className="field-group">
                <label className="field-label">Tipo de relación *</label>
                <select value={form.tipo_relacion} onChange={e => setForm({ ...form, tipo_relacion: e.target.value })}>
                  {Object.entries(TIPO_RELACION_LABELS).map(([v, l]) => <option key={v} value={v}>{l}</option>)}
                </select>
              </div>
              <div className="field-group">
                <label className="field-label">Persona destino *</label>
                <select value={form.persona_destino_id} onChange={e => setForm({ ...form, persona_destino_id: e.target.value })} disabled={!!editTarget}>
                  <option value="">Seleccionar...</option>
                  {personas.filter(p => p.id !== +form.persona_origen_id).map(p => (
                    <option key={p.id} value={p.id}>{p.nombre}</option>
                  ))}
                </select>
              </div>
              <div className="field-group">
                <label className="field-label">Descripción</label>
                <input value={form.descripcion} onChange={e => setForm({ ...form, descripcion: e.target.value })} placeholder="Descripción opcional..." />
              </div>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', marginBottom: '16px' }}>
                <input type="checkbox" checked={form.bidireccional} onChange={e => setForm({ ...form, bidireccional: e.target.checked })} style={{ width: 'auto', marginBottom: 0 }} />
                Relación bidireccional (↔)
              </label>
              {msg && <div className="mensaje error">{msg}</div>}
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowForm(false)}>Cancelar</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Guardando...' : 'Guardar'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {deleteTarget && (
        <Modal title="¿Eliminar relación?" message="Esta relación familiar será eliminada permanentemente."
          confirmText="Eliminar" danger onConfirm={handleDelete} onCancel={() => setDeleteTarget(null)} />
      )}
    </div>
  );
}
