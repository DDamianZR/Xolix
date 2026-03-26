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

const PRIORIDADES = {
  alta: { label: '🔴 Alta', class: 'badge-danger', color: '#e53935' },
  media: { label: '🟡 Media', class: 'badge-warning', color: '#f9a825' },
  baja: { label: '🟢 Baja', class: 'badge-success', color: '#4caf50' },
};

function formatDate(dateStr) {
  if (!dateStr) return null;
  const d = new Date(dateStr);
  return d.toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric' });
}

function getDaysLeft(dateStr) {
  if (!dateStr) return null;
  const now = new Date();
  const target = new Date(dateStr);
  const diff = Math.ceil((target - now) / (1000 * 60 * 60 * 24));
  return diff;
}

function getDeadlineBadge(dateStr) {
  const days = getDaysLeft(dateStr);
  if (days === null) return null;
  if (days < 0) return { text: `Vencido (${Math.abs(days)}d)`, color: '#e53935', bg: 'var(--danger-bg)' };
  if (days === 0) return { text: 'Vence hoy', color: '#f9a825', bg: 'var(--warning-bg)' };
  if (days <= 3) return { text: `${days}d restantes`, color: '#f9a825', bg: 'var(--warning-bg)' };
  return { text: `${days}d restantes`, color: '#4caf50', bg: 'var(--success-bg)' };
}

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
  const [prioridad, setPrioridad] = useState('media');
  const [fechaVencimiento, setFechaVencimiento] = useState('');
  
  // Data for Selects
  const [usuariosDisp, setUsuariosDisp] = useState([]);
  const [expedientesDisp, setExpedientesDisp] = useState([]);

  // Subtask & Delete States
  const [newSubtarea, setNewSubtarea] = useState('');
  const [newSubFecha, setNewSubFecha] = useState('');
  const [deleteTarget, setDeleteTarget] = useState(null);

  useEffect(() => { 
    loadProcesos(); 
  }, []);

  async function loadProcesos() {
    try {
      const data = await api.getProcesos();
      setProcesos(data);
      if (selected) {
        const fresh = await api.getProceso(selected.id);
        setSelected(fresh);
      }
    } catch {}
  }

  async function openCreateModal() {
    try {
      const [uRes, eRes] = await Promise.all([
        api.getUsers(),
        api.getExpedientesPropios()
      ]);
      setUsuariosDisp(uRes);
      setExpedientesDisp(eRes);
      
      setTitulo(''); setDesc('');
      setExpedienteId(''); setSelectedUsers([]);
      setPrioridad('media'); setFechaVencimiento('');
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
        usuario_ids: selectedUsers,
        prioridad,
        fecha_vencimiento: fechaVencimiento || null,
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
      await api.addSubtarea(selected.id, newSubtarea, newSubFecha || null);
      setNewSubtarea('');
      setNewSubFecha('');
      loadProcesos();
    } catch {}
  }

  async function handleToggleSubtarea(subtareaId) {
    try {
      await api.toggleSubtarea(subtareaId);
      loadProcesos();
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
                {procesos.map(p => {
                  const prio = PRIORIDADES[p.prioridad] || PRIORIDADES.media;
                  const deadline = getDeadlineBadge(p.fecha_vencimiento);
                  return (
                    <div key={p.id} className={`proceso-item ${selected?.id === p.id ? 'selected' : ''}`} onClick={() => selectProceso(p.id)}>
                      <div className="proceso-item-header">
                        <strong>{p.titulo}</strong>
                        <span className={`badge ${ESTADOS[p.estado]?.class || ''}`}>{ESTADOS[p.estado]?.label || p.estado}</span>
                      </div>
                      {/* Priority and Deadline row */}
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '6px', flexWrap: 'wrap' }}>
                        <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '6px', background: prio.color + '20', color: prio.color, fontWeight: 600 }}>
                          {prio.label}
                        </span>
                        {deadline && (
                          <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '6px', background: deadline.bg, color: deadline.color, fontWeight: 500 }}>
                            📅 {deadline.text}
                          </span>
                        )}
                      </div>
                      {/* Progress Bar Mini */}
                      <div className="progress-bar" style={{ height: '4px', margin: '8px 0 4px 0' }}>
                        <div className="progress-fill" style={{ width: `${p.progreso}%`, background: p.progreso === 100 ? '#4CAF50' : 'var(--primary)' }}></div>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span className="progress-text">{p.progreso}% completado</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* RIGHT PANEL: Process Detail */}
          <div className="table-card proceso-detail">
            {!selected ? (
              <div className="status-msg" style={{ display: 'flex', flex: 1, alignItems: 'center', justifyContent: 'center' }}>
                Selecciona un proceso de la izquierda para ver y gestionar subtareas.
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                
                {/* Header Info */}
                <div style={{ paddingBottom: '16px', borderBottom: '1px solid var(--border)', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <h3 style={{ marginBottom:'8px', fontSize: '1.2rem' }}>{selected.titulo}</h3>
                    <button className="btn-sm btn-delete" onClick={() => setDeleteTarget(selected.id)}>Eliminar</button>
                  </div>
                  
                  {selected.descripcion && <p className="subtitle" style={{marginBottom:'12px'}}>{selected.descripcion}</p>}
                  
                  {/* Priority & Deadline Info */}
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap' }}>
                    {(() => {
                      const prio = PRIORIDADES[selected.prioridad] || PRIORIDADES.media;
                      return (
                        <span style={{ fontSize: '12px', padding: '4px 12px', borderRadius: '8px', background: prio.color + '20', color: prio.color, fontWeight: 600 }}>
                          Prioridad: {prio.label}
                        </span>
                      );
                    })()}
                    {selected.fecha_vencimiento && (() => {
                      const dl = getDeadlineBadge(selected.fecha_vencimiento);
                      return (
                        <span style={{ fontSize: '12px', padding: '4px 12px', borderRadius: '8px', background: dl.bg, color: dl.color, fontWeight: 500 }}>
                          📅 Entrega: {formatDate(selected.fecha_vencimiento)} — {dl.text}
                        </span>
                      );
                    })()}
                  </div>

                  {selected.expediente_nombre && (
                    <div style={{ marginBottom: '8px', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span title="Expediente Relacionado">📁</span>
                      <strong style={{ color: 'var(--primary)' }}>{selected.expediente_nombre}</strong>
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
                    <div className="progress-fill" style={{ width: `${selected.progreso}%`, background: selected.progreso === 100 ? '#4CAF50' : 'var(--primary)' }}></div>
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
                    selected.subtareas.map(s => {
                      const subDl = getDeadlineBadge(s.fecha_vencimiento);
                      return (
                        <label key={s.id} className={`subtarea-item ${s.completada ? 'done' : ''}`} style={{ 
                          cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '12px', padding: '12px', 
                          background: 'var(--bg-light)', borderRadius: '8px', marginBottom: '8px', 
                          border: `1px solid ${subDl && subDl.color === '#e53935' && !s.completada ? '#e5393555' : 'var(--border)'}`,
                          transition: 'all 0.2s ease',
                          opacity: s.completada ? 0.6 : 1,
                        }}>
                          <input 
                            type="checkbox" 
                            checked={s.completada} 
                            onChange={() => handleToggleSubtarea(s.id)} 
                            style={{ width: '18px', height: '18px', cursor: 'pointer', accentColor: 'var(--primary)' }}
                          />
                          <div style={{ flex: 1 }}>
                            <span style={{ fontSize: '14px', color: s.completada ? 'var(--text-muted)' : 'var(--text-primary)', textDecoration: s.completada ? 'line-through' : 'none' }}>
                              {s.titulo}
                            </span>
                            {subDl && !s.completada && (
                              <div style={{ marginTop: '4px' }}>
                                <span style={{ fontSize: '10px', padding: '2px 6px', borderRadius: '4px', background: subDl.bg, color: subDl.color, fontWeight: 500 }}>
                                  📅 {subDl.text}
                                  {s.fecha_vencimiento && ` · ${formatDate(s.fecha_vencimiento)}`}
                                </span>
                              </div>
                            )}
                          </div>
                        </label>
                      );
                    })
                  )}
                </div>

                {/* Add new subtask form */}
                <form onSubmit={handleAddSubtarea} style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', gap: '10px', marginBottom: '8px' }}>
                    <input 
                      placeholder="Escribe una nueva subtarea..." 
                      value={newSubtarea} 
                      onChange={e => setNewSubtarea(e.target.value)} 
                      style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid var(--border)', outline: 'none', background: 'var(--bg-light)', color: 'var(--text-primary)' }}
                    />
                    <button type="submit" className="btn btn-primary" style={{padding:'10px 20px', whiteSpace:'nowrap', borderRadius: '8px'}}>+ Agregar</button>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <label style={{ fontSize: '12px', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>📅 Fecha límite:</label>
                    <input 
                      type="datetime-local" 
                      value={newSubFecha} 
                      onChange={e => setNewSubFecha(e.target.value)} 
                      style={{ flex: 1, padding: '8px', borderRadius: '8px', border: '1px solid var(--border)', fontSize: '12px', background: 'var(--bg-light)', color: 'var(--text-primary)' }}
                    />
                  </div>
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
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border)', minHeight: '80px', resize: 'vertical', fontFamily: 'inherit', background: 'var(--bg-light)', color: 'var(--text-primary)' }}
                />
              </div>

              {/* Priority & Deadline Row */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="field-group">
                  <label className="field-label">PRIORIDAD</label>
                  <select value={prioridad} onChange={e => setPrioridad(e.target.value)} style={{ background: 'var(--bg-light)', color: 'var(--text-primary)' }}>
                    <option value="baja">🟢 Baja</option>
                    <option value="media">🟡 Media</option>
                    <option value="alta">🔴 Alta</option>
                  </select>
                </div>
                <div className="field-group">
                  <label className="field-label">FECHA DE ENTREGA</label>
                  <input 
                    type="datetime-local" 
                    value={fechaVencimiento} 
                    onChange={e => setFechaVencimiento(e.target.value)}
                    style={{ background: 'var(--bg-light)', color: 'var(--text-primary)' }}
                  />
                </div>
              </div>

              <div className="field-group">
                <label className="field-label">VINCULAR EXPEDIENTE (Opcional)</label>
                <select value={expedienteId} onChange={e => setExpedienteId(e.target.value)} style={{ background: 'var(--bg-light)', color: 'var(--text-primary)' }}>
                  <option value="">-- No vincular ninguno --</option>
                  {expedientesDisp.map(exp => (
                    <option key={exp.id} value={exp.id}>{exp.nombre}</option>
                  ))}
                </select>
              </div>

              <div className="field-group" style={{ marginTop: '8px' }}>
                <label className="field-label">COMPARTIR CON (Opcional)</label>
                <div style={{ maxHeight: '150px', overflowY: 'auto', border: '1px solid var(--border)', borderRadius: '8px', padding: '8px' }}>
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
