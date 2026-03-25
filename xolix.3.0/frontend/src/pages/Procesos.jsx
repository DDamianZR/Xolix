import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Topbar from '../components/Topbar';
import Modal from '../components/Modal';
import api from '../api/client';

const ESTADOS = {
  pendiente: { label: 'Pendiente', class: 'badge-inactive' },
  en_proceso: { label: 'En proceso', class: 'badge-rol' },
  terminado: { label: 'Terminado', class: 'badge-active' },
};

export default function Procesos() {
  const navigate = useNavigate();
  const [procesos, setProcesos] = useState([]);
  const [selected, setSelected] = useState(null);
  
  // Creation Modal States
  const [showCreate, setShowCreate] = useState(false);
  const [titulo, setTitulo] = useState('');
  const [desc, setDesc] = useState('');
  const [expedienteId, setExpedienteId] = useState('');
  const [selectedUsers, setSelectedUsers] = useState([]);
  
  // Data for Selects
  const [usuariosDisp, setUsuariosDisp] = useState([]);
  const [expedientesDisp, setExpedientesDisp] = useState([]);

  // Subtask & Delete States
  const [newSubtarea, setNewSubtarea] = useState('');
  const [deleteTarget, setDeleteTarget] = useState(null);

  useEffect(() => { 
    loadProcesos(); 
  }, []);

  async function loadProcesos() {
    try {
      const data = await api.getProcesos();
      setProcesos(data);
      // Reload selected item if it exists so we get fresh data
      if (selected) {
        selectProceso(selected.id);
      }
    } catch {}
  }

  async function openCreateModal() {
    try {
      // Parallel fetch users and expedientes
      const [uRes, eRes] = await Promise.all([
        api.getUsers(),
        api.getExpedientesPropios()
      ]);
      setUsuariosDisp(uRes);
      setExpedientesDisp(eRes);
      
      setTitulo(''); setDesc('');
      setExpedienteId(''); setSelectedUsers([]);
      setShowCreate(true);
    } catch (err) {
      alert("Error cargando dependencias para crear proceso.");
    }
  }

  function toggleUserSelection(uid) {
    if (selectedUsers.includes(uid)) {
      setSelectedUsers(selectedUsers.filter(id => id !== uid));
    } else {
      setSelectedUsers([...selectedUsers, uid]);
    }
  }

  async function handleCreate(e) {
    e.preventDefault();
    try {
      await api.createProceso({ 
        titulo, 
        descripcion: desc || null, 
        expediente_id: expedienteId ? parseInt(expedienteId) : null,
        usuario_ids: selectedUsers 
      });
      setShowCreate(false);
      loadProcesos();
    } catch (err) {
      alert("Error al crear el proceso: " + err.message);
    }
  }

  async function selectProceso(id) {
    try {
      const data = await api.getProceso(id);
      setSelected(data);
    } catch {}
  }

  async function handleAddSubtarea(e) {
    e.preventDefault();
    if (!newSubtarea.trim() || !selected) return;
    try {
      await api.addSubtarea(selected.id, newSubtarea);
      setNewSubtarea('');
      loadProcesos(); // also reloads selected implicitly via loadProcesos
    } catch {}
  }

  async function handleToggleSubtarea(subtareaId) {
    try {
      await api.toggleSubtarea(subtareaId);
      loadProcesos(); // updates progress globally and for selected
    } catch {}
  }

  async function handleDelete() {
    try {
      await api.deleteProceso(deleteTarget);
      setDeleteTarget(null);
      if (selected?.id === deleteTarget) setSelected(null);
      loadProcesos();
    } catch {}
  }

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">
        <div className="procesos-layout">
          
          {/* LEFT PANEL: Process List */}
          <div className="table-card proceso-list">
            <div className="table-header" style={{ marginBottom: '10px' }}>
              <h3>📋 Procesos a seguir</h3>
              <div className="table-controls">
                <button className="btn btn-add" onClick={openCreateModal}>+ Nuevo Proceso</button>
                <button className="btn btn-secondary" style={{padding:'10px 16px', fontSize:'13px'}} onClick={() => navigate('/dashboard')}>← Panel</button>
              </div>
            </div>

            {procesos.length === 0 ? (
              <div className="status-msg">No estás participando en ningún proceso.</div>
            ) : (
              <div className="proceso-items">
                {procesos.map(p => (
                  <div key={p.id} className={`proceso-item ${selected?.id === p.id ? 'selected' : ''}`} onClick={() => selectProceso(p.id)}>
                    <div className="proceso-item-header">
                      <strong>{p.titulo}</strong>
                      <span className={`badge ${ESTADOS[p.estado]?.class || ''}`}>{ESTADOS[p.estado]?.label || p.estado}</span>
                    </div>
                    {/* Progress Bar Mini */}
                    <div className="progress-bar" style={{ height: '4px', margin: '8px 0 4px 0' }}>
                      <div className="progress-fill" style={{ width: `${p.progreso}%`, background: p.progreso === 100 ? '#4CAF50' : '#4f46e5' }}></div>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className="progress-text">{p.progreso}% completado</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* RIGHT PANEL: Process Detail (To-Do List Style) */}
          <div className="table-card proceso-detail">
            {!selected ? (
              <div className="status-msg" style={{ display: 'flex', flex: 1, alignItems: 'center', justifyContent: 'center' }}>
                Selecciona un proceso de la izquierda para ver y gestionar subtareas.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                
                {/* Header Info */}
                <div style={{ paddingBottom: '16px', borderBottom: '1px solid var(--border-color)', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <h3 style={{ marginBottom:'8px', fontSize: '1.2rem' }}>{selected.titulo}</h3>
                    <button className="btn-sm btn-delete" onClick={() => setDeleteTarget(selected.id)}>Eliminar</button>
                  </div>
                  
                  {selected.descripcion && <p className="subtitle" style={{marginBottom:'12px'}}>{selected.descripcion}</p>}
                  
                  {selected.expediente_nombre && (
                    <div style={{ marginBottom: '8px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span title="Expediente Relacionado">📁</span>
                      <strong style={{ color: 'var(--primary-color)' }}>{selected.expediente_nombre}</strong>
                    </div>
                  )}

                  {selected.usuarios && selected.usuarios.length > 0 && (
                    <div style={{ marginBottom: '12px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                      <span style={{ marginRight: '8px' }}>👥 Participantes:</span>
                      {selected.usuarios.map(u => (
                        <span key={u.id} className="badge badge-inactive" style={{ marginRight: '4px', display: 'inline-block' }}>
                          {u.nombre} {u.apellido_paterno}
                        </span>
                      ))}
                    </div>
                  )}

                  <div style={{display:'flex', gap:'12px', alignItems:'center'}}>
                    <span className={`badge ${ESTADOS[selected.estado]?.class}`}>{ESTADOS[selected.estado]?.label}</span>
                    <span className="progress-text" style={{fontSize:'13px'}}>{selected.progreso}% Completado</span>
                  </div>
                  
                  <div className="progress-bar" style={{ marginTop: '12px', height: '6px' }}>
                    <div className="progress-fill" style={{ width: `${selected.progreso}%`, background: selected.progreso === 100 ? '#4CAF50' : '#4f46e5' }}></div>
                  </div>
                </div>

                {/* Subtasks List */}
                <h4 style={{marginBottom:'12px', color:'var(--text-secondary)', fontSize:'12px', textTransform:'uppercase', letterSpacing:'1px'}}>
                  Subtareas a realizar
                </h4>

                <div className="subtarea-list" style={{ flex: 1, overflowY: 'auto' }}>
                  {selected.subtareas.length === 0 ? (
                    <p style={{ fontSize: '14px', color: 'var(--text-muted)' }}>No hay subtareas. Agrega una abajo.</p>
                  ) : (
                    selected.subtareas.map(s => (
                      <label key={s.id} className={`subtarea-item ${s.completada ? 'done' : ''}`} style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', background: 'var(--bg-card)', borderRadius: '8px', marginBottom: '8px', border: '1px solid var(--border-color)', transition: 'all 0.2s ease' }}>
                        <input 
                          type="checkbox" 
                          checked={s.completada} 
                          onChange={() => handleToggleSubtarea(s.id)} 
                          style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                        />
                        <span style={{ fontSize: '15px', color: s.completada ? 'var(--text-muted)' : 'var(--text-main)', textDecoration: s.completada ? 'line-through' : 'none' }}>
                          {s.titulo}
                        </span>
                      </label>
                    ))
                  )}
                </div>

                {/* Add new subtask form pinned to bottom */}
                <form onSubmit={handleAddSubtarea} className="subtarea-form" style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '10px' }}>
                  <input 
                    placeholder="Escribe una nueva subtarea..." 
                    value={newSubtarea} 
                    onChange={e => setNewSubtarea(e.target.value)} 
                    style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', outline: 'none' }}
                  />
                  <button type="submit" className="btn btn-primary" style={{padding:'10px 20px', whiteSpace:'nowrap', borderRadius: '8px'}}>+ Agregar</button>
                </form>

              </div>
            )}
          </div>
        </div>
      </div>

      {/* Creation Modal */}
      {showCreate && (
        <div className="modal-overlay active" onClick={() => setShowCreate(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()} style={{ maxWidth: '500px', width: '100%' }}>
            <h3 style={{ marginBottom: '16px' }}>Crear Nuevo Proceso</h3>
            
            <form onSubmit={handleCreate} className="form-stack" style={{textAlign:'left'}}>
              
              <div className="field-group">
                <label className="field-label">TÍTULO DEL PROCESO</label>
                <input placeholder="Ej. Trámite de Visa" value={titulo} onChange={e => setTitulo(e.target.value)} required />
              </div>

              <div className="field-group">
                <label className="field-label">DESCRIPCIÓN (Opcional)</label>
                <textarea 
                  placeholder="Detalles sobre el proceso..." 
                  value={desc} 
                  onChange={e => setDesc(e.target.value)} 
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-color)', minHeight: '80px', resize: 'vertical', fontFamily: 'inherit' }}
                />
              </div>

              <div className="field-group">
                <label className="field-label">VINCULAR EXPEDIENTE (Opcional)</label>
                <select value={expedienteId} onChange={e => setExpedienteId(e.target.value)}>
                  <option value="">-- No vincular ninguno --</option>
                  {expedientesDisp.map(exp => (
                    <option key={exp.id} value={exp.id}>{exp.titulo}</option>
                  ))}
                </select>
              </div>

              <div className="field-group" style={{ marginTop: '8px' }}>
                <label className="field-label">COMPARTIR CON (Opcional)</label>
                <div style={{ maxHeight: '150px', overflowY: 'auto', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '8px' }}>
                  {usuariosDisp.map(u => (
                    <label key={u.id} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px', cursor: 'pointer' }}>
                      <input 
                        type="checkbox" 
                        checked={selectedUsers.includes(u.id)}
                        onChange={() => toggleUserSelection(u.id)}
                      />
                      <span style={{ fontSize: '14px' }}>{u.nombre} {u.apellido_paterno} </span>
                      <span className="badge badge-rol" style={{ fontSize: '10px' }}>{u.rol}</span>
                    </label>
                  ))}
                </div>
                <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Los usuarios seleccionados podrán ver el proceso y marcar subtareas como completadas.
                </p>
              </div>

              <div className="form-actions" style={{ marginTop: '24px' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancelar</button>
                <button type="submit" className="btn btn-primary">Iniciar Proceso</button>
              </div>

            </form>
          </div>
        </div>
      )}

      {/* Deletion Modal */}
      {deleteTarget && (
        <Modal 
          title="¿Eliminar proceso?" 
          message="Se cerrará el proceso para todos los usuarios y se eliminarán todas las subtareas asociadas. Esta acción no se puede deshacer." 
          confirmText="Eliminar permanentemente" 
          danger 
          onConfirm={handleDelete} 
          onCancel={() => setDeleteTarget(null)} 
        />
      )}
    </div>
  );
}
