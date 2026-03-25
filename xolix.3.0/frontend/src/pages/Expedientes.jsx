import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Topbar from '../components/Topbar';
import Modal from '../components/Modal';
import api from '../api/client';

export default function Expedientes() {
  const navigate = useNavigate();
  const [propios, setPropios] = useState([]);
  const [compartidos, setCompartidos] = useState([]);
  const [tab, setTab] = useState('propios');
  const [showUpload, setShowUpload] = useState(false);
  const [showShare, setShowShare] = useState(null);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [nombre, setNombre] = useState('');
  const [descripcion, setDescripcion] = useState('');
  const [archivo, setArchivo] = useState(null);
  const [shareEmail, setShareEmail] = useState('');
  const [sharePermiso, setSharePermiso] = useState('lectura');
  const [mensaje, setMensaje] = useState('');

  useEffect(() => { load(); }, []);

  async function load() {
    try {
      const [p, c] = await Promise.all([api.getExpedientesPropios(), api.getExpedientesCompartidos()]);
      setPropios(p);
      setCompartidos(c);
    } catch {}
  }

  async function handleUpload(e) {
    e.preventDefault();
    if (!archivo) return;
    const fd = new FormData();
    fd.append('nombre', nombre);
    fd.append('descripcion', descripcion);
    fd.append('archivo', archivo);
    try {
      await api.uploadExpediente(fd);
      setShowUpload(false);
      setNombre(''); setDescripcion(''); setArchivo(null);
      load();
    } catch (err) {
      setMensaje(err.message);
    }
  }

  async function handleShare(e) {
    e.preventDefault();
    const fd = new FormData();
    fd.append('correo_destino', shareEmail);
    fd.append('permiso', sharePermiso);
    try {
      await api.compartirExpediente(showShare, fd);
      setShowShare(null);
      setShareEmail(''); setSharePermiso('lectura');
      setMensaje('Expediente compartido ✓');
    } catch (err) {
      setMensaje(err.message);
    }
  }

  async function handleDelete() {
    try {
      await api.deleteExpediente(deleteTarget);
      setDeleteTarget(null);
      load();
    } catch {}
  }

  const items = tab === 'propios' ? propios : compartidos;

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">
        <div className="table-card">
          <div className="table-header">
            <h3>📁 Expedientes</h3>
            <div className="table-controls">
              <div className="tab-group">
                <button className={`tab-btn ${tab === 'propios' ? 'active' : ''}`} onClick={() => setTab('propios')}>Mis expedientes</button>
                <button className={`tab-btn ${tab === 'compartidos' ? 'active' : ''}`} onClick={() => setTab('compartidos')}>Compartidos conmigo</button>
              </div>
              <button className="btn btn-add" onClick={() => setShowUpload(true)}>+ Subir expediente</button>
              <button className="btn btn-secondary" style={{padding:'10px 16px', fontSize:'13px'}} onClick={() => navigate('/dashboard')}>← Dashboard</button>
            </div>
          </div>

          {mensaje && <div className="mensaje success" style={{marginBottom:'16px'}}>{mensaje}</div>}

          {items.length === 0 ? (
            <div className="status-msg">No hay expedientes.</div>
          ) : (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Nombre</th>
                    <th>Descripción</th>
                    <th>Tipo</th>
                    {tab === 'compartidos' && <th>Permiso</th>}
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((e, i) => (
                    <tr key={e.id}>
                      <td>{i + 1}</td>
                      <td><strong>{e.nombre}</strong></td>
                      <td>{e.descripcion || '—'}</td>
                      <td><span className="badge badge-rol">{e.tipo_archivo?.toUpperCase()}</span></td>
                      {tab === 'compartidos' && (
                        <td><span className={`badge ${e.permiso === 'edicion' ? 'badge-active' : 'badge-inactive'}`}>{e.permiso}</span></td>
                      )}
                      <td>
                        <div className="btn-actions">
                          <a className="btn-sm btn-view" href={api.downloadExpediente(e.id)} target="_blank" rel="noreferrer">Descargar</a>
                          {tab === 'propios' && (
                            <>
                              <button className="btn-sm btn-edit" onClick={() => setShowShare(e.id)}>Compartir</button>
                              <button className="btn-sm btn-delete" onClick={() => setDeleteTarget(e.id)}>Eliminar</button>
                            </>
                          )}
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

      {/* Upload Modal */}
      {showUpload && (
        <div className="modal-overlay active" onClick={() => setShowUpload(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <h3>Subir Expediente</h3>
            <form onSubmit={handleUpload} className="form-stack" style={{textAlign:'left', marginTop:'16px'}}>
              <input placeholder="Nombre del expediente" value={nombre} onChange={e => setNombre(e.target.value)} required />
              <input placeholder="Descripción (opcional)" value={descripcion} onChange={e => setDescripcion(e.target.value)} />
              <input type="file" accept=".pdf,.doc,.docx,.jpg,.png" onChange={e => setArchivo(e.target.files[0])} required />
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowUpload(false)}>Cancelar</button>
                <button type="submit" className="btn btn-primary">Subir</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Share Modal */}
      {showShare && (
        <div className="modal-overlay active" onClick={() => setShowShare(null)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <h3>Compartir Expediente</h3>
            <form onSubmit={handleShare} className="form-stack" style={{textAlign:'left', marginTop:'16px'}}>
              <input type="email" placeholder="Correo del destinatario" value={shareEmail} onChange={e => setShareEmail(e.target.value)} required />
              <div className="field-group">
                <label className="field-label">PERMISO</label>
                <select value={sharePermiso} onChange={e => setSharePermiso(e.target.value)}>
                  <option value="lectura">Lectura</option>
                  <option value="edicion">Edición</option>
                </select>
              </div>
              <div className="form-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowShare(null)}>Cancelar</button>
                <button type="submit" className="btn btn-primary">Compartir</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {deleteTarget && (
        <Modal title="¿Eliminar expediente?" message="El archivo será eliminado permanentemente." confirmText="Eliminar" danger onConfirm={handleDelete} onCancel={() => setDeleteTarget(null)} />
      )}
    </div>
  );
}
