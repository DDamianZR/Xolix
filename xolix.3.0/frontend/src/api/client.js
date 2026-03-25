const API_BASE = '/api';

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('token');

  const headers = {
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options.headers,
  };

  // Don't set Content-Type for FormData (browser sets it with boundary)
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const config = { headers, ...options };

  const res = await fetch(`${API_BASE}${endpoint}`, config);

  if (res.status === 401) {
    localStorage.removeItem('token');
    localStorage.removeItem('rol');
    window.location.href = '/';
    throw new Error('Sesión expirada');
  }

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || 'Error en la solicitud');
  }

  return data;
}

const api = {
  // Auth
  login: (correo, password) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ correo, password }),
    }),

  // Users
  getUsers: () => request('/usuarios/'),
  getUser: (id) => request(`/usuarios/${id}`),
  createUser: (data) =>
    request('/usuarios/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateUser: (id, data) =>
    request(`/usuarios/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  toggleAccess: (id, activo) =>
    request(`/usuarios/${id}/acceso?activo=${activo}`, {
      method: 'PATCH',
    }),
  deleteUser: (id) =>
    request(`/usuarios/${id}`, {
      method: 'DELETE',
    }),

  // SEPOMEX
  buscarCP: (cp) => request(`/sepomex/cp/${cp}`),

  // Expedientes
  getExpedientesPropios: () => request('/expedientes/propios'),
  getExpedientesCompartidos: () => request('/expedientes/compartidos'),
  uploadExpediente: (formData) =>
    request('/expedientes/', {
      method: 'POST',
      body: formData,
    }),
  downloadExpediente: (id) => `${API_BASE}/expedientes/${id}/descargar`,
  compartirExpediente: (id, formData) =>
    request(`/expedientes/${id}/compartir`, {
      method: 'POST',
      body: formData,
    }),
  deleteExpediente: (id) =>
    request(`/expedientes/${id}`, {
      method: 'DELETE',
    }),

  // Procesos
  getProcesos: () => request('/procesos/'),
  getProceso: (id) => request(`/procesos/${id}`),
  createProceso: (data) =>
    request('/procesos/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateProceso: (id, data) =>
    request(`/procesos/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
  addSubtarea: (procesoId, titulo) =>
    request(`/procesos/${procesoId}/subtareas`, {
      method: 'POST',
      body: JSON.stringify({ titulo }),
    }),
  toggleSubtarea: (subtareaId) =>
    request(`/procesos/subtareas/${subtareaId}/toggle`, {
      method: 'PATCH',
    }),
  deleteProceso: (id) =>
    request(`/procesos/${id}`, {
      method: 'DELETE',
    }),
};

export default api;
