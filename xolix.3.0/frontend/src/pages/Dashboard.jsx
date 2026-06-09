import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Topbar from '../components/Topbar';
import Modal from '../components/Modal';
import api from '../api/client';

export default function Dashboard() {
  const { isAdmin } = useAuth();
  const navigate = useNavigate();
  const [usuarios, setUsuarios] = useState([]);
  const [busqueda, setBusqueda] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleteTarget, setDeleteTarget] = useState(null);

  useEffect(() => {
    loadUsers();
  }, []);

  async function loadUsers() {
    try {
      const data = await api.getUsers();
      setUsuarios(data);
    } catch {
      setError('Error al cargar usuarios.');
    } finally {
      setLoading(false);
    }
  }

  async function handleToggleAccess(id, currentStatus) {
    try {
      await api.toggleAccess(id, !currentStatus);
      loadUsers();
    } catch {
      alert('Error al cambiar acceso');
    }
  }

  async function handleDelete() {
    if (!deleteTarget) return;
    try {
      await api.deleteUser(deleteTarget);
      setDeleteTarget(null);
      loadUsers();
    } catch {
      alert('Error al eliminar usuario');
    }
  }

  const filtered = usuarios.filter((u) => {
    const q = busqueda.toLowerCase();
    const fullName = `${u.nombre} ${u.apellido_paterno} ${u.apellido_materno}`.toLowerCase();
    return (
      fullName.includes(q) ||
      u.correo.toLowerCase().includes(q) ||
      u.rol.toLowerCase().includes(q)
    );
  });

  return (
    <div className="page-dashboard">
      <Topbar />

      <div className="container">
        {/* Quick nav cards */}
        <div className="quick-nav">
          <div className="quick-nav-card" onClick={() => navigate('/expedientes')}>
            <span className="quick-nav-icon">📁</span>
            <span className="quick-nav-text">Expedientes</span>
          </div>
          <div className="quick-nav-card" onClick={() => navigate('/procesos')}>
            <span className="quick-nav-icon">📋</span>
            <span className="quick-nav-text">Procesos</span>
          </div>
          <div className="quick-nav-card" onClick={() => navigate('/nna')}>
            <span className="quick-nav-icon">🛡️</span>
            <span className="quick-nav-text">Protección NNA</span>
          </div>
          <div className="quick-nav-card" onClick={() => navigate('/actores')}>
            <span className="quick-nav-icon">🤝</span>
            <span className="quick-nav-text">Actores</span>
          </div>
          <div className="quick-nav-card" onClick={() => navigate('/reportes')}>
            <span className="quick-nav-icon">📊</span>
            <span className="quick-nav-text">Reportes</span>
          </div>
          <div className="quick-nav-card" onClick={() => navigate('/colaboradores')}>
            <span className="quick-nav-icon">👤</span>
            <span className="quick-nav-text">Colaboradores</span>
          </div>
        </div>

        <div className="table-card">
          <div className="table-header">
            <h3>Personal registrado</h3>
            <div className="table-controls">
              <input
                className="search-box"
                type="text"
                placeholder="Buscar por nombre, correo o rol..."
                value={busqueda}
                onChange={(e) => setBusqueda(e.target.value)}
              />
              {isAdmin && (
                <button className="btn btn-add" onClick={() => navigate('/registro')}>
                  + Agregar personal
                </button>
              )}
            </div>
          </div>

          {loading && <div className="status-msg">Cargando...</div>}
          {error && <div className="status-msg error">{error}</div>}

          {!loading && !error && filtered.length === 0 && (
            <div className="status-msg">No se encontraron usuarios.</div>
          )}

          {!loading && !error && filtered.length > 0 && (
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Nombre</th>
                    <th>Correo</th>
                    <th>Rol</th>
                    <th>Tipo</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((u, i) => (
                    <tr key={u.id}>
                      <td>{i + 1}</td>
                      <td><strong>{u.nombre} {u.apellido_paterno} {u.apellido_materno}</strong></td>
                      <td>{u.correo}</td>
                      <td><span className="badge badge-rol">{u.rol}</span></td>
                      <td>{u.tipo_personal}</td>
                      <td>
                        <span className={`badge ${u.activo ? 'badge-active' : 'badge-inactive'}`}>
                          {u.activo ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td>
                        <div className="btn-actions">
                          <button className="btn-sm btn-view" onClick={() => navigate(`/usuario/${u.id}`)}>
                            Ver
                          </button>
                          {isAdmin && (
                            <>
                              <button className="btn-sm btn-edit" onClick={() => navigate(`/editar/${u.id}`)}>
                                Editar
                              </button>
                              <button
                                className={`btn-sm ${u.activo ? 'btn-toggle-on' : 'btn-toggle-off'}`}
                                onClick={() => handleToggleAccess(u.id, u.activo)}
                              >
                                {u.activo ? 'Revocar' : 'Activar'}
                              </button>
                              <button className="btn-sm btn-delete" onClick={() => setDeleteTarget(u.id)}>
                                Eliminar
                              </button>
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

      {deleteTarget && (
        <Modal
          title="¿Eliminar usuario?"
          message="Esta acción no se puede deshacer. El registro será eliminado permanentemente."
          confirmText="Eliminar"
          danger
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  );
}
