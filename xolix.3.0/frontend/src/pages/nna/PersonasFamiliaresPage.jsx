import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import Modal from '../../components/Modal';
import api from '../../api/client';

const SIMBOLO_LABELS = {
  normal: 'Normal', clave: 'NNA Clave', fallecido: 'Fallecido/a',
  cuidador: 'Cuidador/a', agresor: 'Agresor/a',
};
const SIMBOLO_COLORS = {
  normal: '#6c63ff', clave: '#1976d2', fallecido: '#757575',
  cuidador: '#4caf50', agresor: '#e53935',
};
const GENERO_LABELS = { masculino: 'Masculino', femenino: 'Femenino', no_binario: 'No binario', otro: 'Otro' };

const emptyForm = {
  nombre: '', edad: '', genero: '', rol_en_familia: '', tipo_simbolo: 'normal',
  observaciones: '', telefono: '', direccion: '', ocupacion: '',
  escolaridad: '', estado_salud: '', vive_con_nna: false, es_responsable_legal: false,
};

export default function PersonasFamiliaresPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [personas, setPersonas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editTarget, setEditTarget] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');
  const [busqueda, setBusqueda] = useState('');
  const [caso, setCaso] = useState(null);

  useEffect(() => { loadData(); }, [id]);

  async function loadData() {
    try {
      const [c, p] = await Promise.all([api.getNnaCaso(id), api.getNnaPersonas(id)]);
      setCaso(c); setPersonas(p);
    } catch { setMsg('Error al cargar datos'); }
    finally { setLoading(false); }
  }

  function openNew() { setForm(emptyForm); setEditTarget(null); setShowForm(true); setMsg(''); }
  function openEdit(p) {
    setForm({
      nombre: p.nombre || '', edad: p.edad || '', genero: p.genero || '',
      rol_en_familia: p.rol_en_familia || '', tipo_simbolo: p.tipo_simbolo || 'normal',
      observaciones: p.observaciones || '', telefono: p.telefono || '',
      direccion: p.direccion || '', ocupacion: p.ocupacion || '',
      escolaridad: p.escolaridad || '', estado_salud: p.estado_salud || '',
      vive_con_nna: p.vive_con_nna || false, es_responsable_legal: p.es_responsable_legal || false,
    });
    setEditTarget(p); setShowForm(true); setMsg('');
  }

  async function handleSave(e) {
    e.preventDefault();
    if (!form.nombre.trim()) { setMsg('El nombre es obligatorio'); return; }
    setSaving(true);
    try {
      const payload = { ...form, edad: form.edad ? parseInt(form.edad) : null };
      if (editTarget) await api.updateNnaPersona(id, editTarget.id, payload);
      else await api.createNnaPersona(id, payload);
      setShowForm(false); await loadData();
    } catch (err) { setMsg(err.message || 'Error al guardar'); }
    finally { setSaving(false); }
  }

  async function handleDelete() {
    try { await api.deleteNnaPersona(id, deleteTarget); setDeleteTarget(null); await loadData(); }
    catch { alert('Error al eliminar persona'); }
  }

  const filtered = personas.filter(p =>
    p.nombre.toLowerCase().includes(busqueda.toLowerCase()) ||
    (p.rol_en_familia || '').toLowerCase().includes(busqueda.toLowerCase())
  );

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px', flexWrap: 'wrap' }}>
          <button className="btn btn-secondary" onClick={() => navigate(`/nna/casos/${id}`)}>← Volver al Caso</button>
          {caso && <h2 style={{ color: 'var(--text-primary)', fontSize: '20px', fontWeight: 700 }}>
            👨‍👩‍👧 Personas Familiares — {caso.nna_nombre}
          </h2>}
        </div>

        <div className="table-card">
          <div className="table-header">
            <h3>Personas registradas ({personas.length})</h3>
            <div className="table-controls">
              <input className="search-box" placeholder="Buscar por nombre o rol..."
                value={busqueda} onChange={e => setBusqueda(e.target.value)} />
              <button className="btn btn-add" onClick={openNew}>+ Nueva persona</button>
            </div>
          </div>

          {loading && <div className="status-msg">Cargando...</div>}
          {!loading && filtered.length === 0 && (
            <div className="status-msg">No hay personas registradas. Agrega la primera.</div>
          )}

          {!loading && filtered.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead><tr>
                  <th>#</th><th>Nombre</th><th>Edad</th><th>Género</th><th>Rol</th>
                  <th>Tipo</th><th>Vive con NNA</th><th>Responsable legal</th><th>Acciones</th>
                </tr></thead>
                <tbody>
                  {filtered.map((p, i) => (
                    <tr key={p.id}>
                      <td>{i + 1}</td>
                      <td><strong>{p.nombre}</strong></td>
                      <td>{p.edad || '—'}</td>
                      <td>{GENERO_LABELS[p.genero] || '—'}</td>
                      <td>{p.rol_en_familia || '—'}</td>
                      <td>
                        <span className="badge" style={{
                          background: SIMBOLO_COLORS[p.tipo_simbolo] + '22',
                          color: SIMBOLO_COLORS[p.tipo_simbolo], border: `1px solid ${SIMBOLO_COLORS[p.tipo_simbolo]}44`
                        }}>
                          {SIMBOLO_LABELS[p.tipo_simbolo] || p.tipo_simbolo}
                        </span>
                      </td>
                      <td><span className={`badge ${p.vive_con_nna ? 'badge-active' : 'badge-inactive'}`}>{p.vive_con_nna ? 'Sí' : 'No'}</span></td>
                      <td><span className={`badge ${p.es_responsable_legal ? 'badge-active' : 'badge-inactive'}`}>{p.es_responsable_legal ? 'Sí' : 'No'}</span></td>
                      <td>
                        <div className="btn-actions">
                          <button className="btn-sm btn-edit" onClick={() => openEdit(p)}>Editar</button>
                          <button className="btn-sm btn-delete" onClick={() => setDeleteTarget(p.id)}>Eliminar</button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Form Modal */}
      {showForm && (
        <div className="modal-overlay active" onClick={e => e.target === e.currentTarget && setShowForm(false)}>
          <div className="modal-box" style={{ width: '680px', maxWidth: '95vw', textAlign: 'left', maxHeight: '90vh', overflowY: 'auto' }}>
            <h3 style={{ marginBottom: '20px' }}>{editTarget ? 'Editar Persona' : 'Nueva Persona Familiar'}</h3>
            <form onSubmit={handleSave}>
              <div className="form-row">
                <div className="field-group" style={{ flex: 2 }}>
                  <label className="field-label">Nombre completo *</label>
                  <input value={form.nombre} onChange={e => setForm({ ...form, nombre: e.target.value })} placeholder="Nombre de la persona" />
                </div>
                <div className="field-group">
                  <label className="field-label">Edad</label>
                  <input type="number" min="0" max="120" value={form.edad} onChange={e => setForm({ ...form, edad: e.target.value })} placeholder="Años" />
                </div>
              </div>
              <div className="form-row">
                <div className="field-group">
                  <label className="field-label">Género</label>
                  <select value={form.genero} onChange={e => setForm({ ...form, genero: e.target.value })}>
                    <option value="">Sin especificar</option>
                    <option value="masculino">Masculino</option>
                    <option value="femenino">Femenino</option>
                    <option value="no_binario">No binario</option>
                    <option value="otro">Otro</option>
                  </select>
                </div>
                <div className="field-group">
                  <label className="field-label">Rol en la familia</label>
                  <input value={form.rol_en_familia} onChange={e => setForm({ ...form, rol_en_familia: e.target.value })} placeholder="Ej: Madre, Padre, Abuelo..." />
                </div>
                <div className="field-group">
                  <label className="field-label">Tipo / Símbolo</label>
                  <select value={form.tipo_simbolo} onChange={e => setForm({ ...form, tipo_simbolo: e.target.value })}>
                    <option value="normal">Normal</option>
                    <option value="clave">NNA Clave</option>
                    <option value="cuidador">Cuidador/a</option>
                    <option value="agresor">Agresor/a</option>
                    <option value="fallecido">Fallecido/a</option>
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="field-group">
                  <label className="field-label">Teléfono</label>
                  <input value={form.telefono} onChange={e => setForm({ ...form, telefono: e.target.value })} placeholder="555-000-0000" />
                </div>
                <div className="field-group" style={{ flex: 2 }}>
                  <label className="field-label">Dirección</label>
                  <input value={form.direccion} onChange={e => setForm({ ...form, direccion: e.target.value })} placeholder="Calle, colonia, municipio..." />
                </div>
              </div>
              <div className="form-row">
                <div className="field-group">
                  <label className="field-label">Ocupación</label>
                  <input value={form.ocupacion} onChange={e => setForm({ ...form, ocupacion: e.target.value })} placeholder="Ej: Empleada, Estudiante..." />
                </div>
                <div className="field-group">
                  <label className="field-label">Escolaridad</label>
                  <input value={form.escolaridad} onChange={e => setForm({ ...form, escolaridad: e.target.value })} placeholder="Ej: Primaria, Secundaria..." />
                </div>
                <div className="field-group">
                  <label className="field-label">Estado de salud</label>
                  <input value={form.estado_salud} onChange={e => setForm({ ...form, estado_salud: e.target.value })} placeholder="Observaciones de salud" />
                </div>
              </div>
              <div className="form-row" style={{ gap: '24px', marginBottom: '16px' }}>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontWeight: 500 }}>
                  <input type="checkbox" checked={form.vive_con_nna} onChange={e => setForm({ ...form, vive_con_nna: e.target.checked })} style={{ width: 'auto', marginBottom: 0 }} />
                  Vive con el/la NNA
                </label>
                <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', fontWeight: 500 }}>
                  <input type="checkbox" checked={form.es_responsable_legal} onChange={e => setForm({ ...form, es_responsable_legal: e.target.checked })} style={{ width: 'auto', marginBottom: 0 }} />
                  Responsable legal
                </label>
              </div>
              <div className="field-group">
                <label className="field-label">Observaciones</label>
                <textarea rows={3} value={form.observaciones} onChange={e => setForm({ ...form, observaciones: e.target.value })} placeholder="Notas adicionales sobre la persona..." />
              </div>
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
        <Modal title="¿Eliminar persona?" message="Esta persona será eliminada del familiograma y sus relaciones asociadas también se eliminarán."
          confirmText="Eliminar" danger onConfirm={handleDelete} onCancel={() => setDeleteTarget(null)} />
      )}
    </div>
  );
}
