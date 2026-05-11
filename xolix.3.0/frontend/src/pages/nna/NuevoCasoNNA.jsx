import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import api from '../../api/client';

export default function NuevoCasoNNA() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    nna_nombre: '',
    nna_edad: '',
    nna_genero: 'masculino'
  });
  const [saving, setSaving] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    try {
      const payload = {
        ...formData,
        nna_edad: formData.nna_edad ? parseInt(formData.nna_edad) : null
      };
      const res = await api.createNnaCaso(payload);
      navigate(`/nna/casos/${res.id}`);
    } catch (err) {
      alert(err.message || 'Error al crear caso');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container" style={{ maxWidth: '600px' }}>
        <button className="btn btn-secondary" style={{ marginBottom: '16px' }} onClick={() => navigate('/nna')}>
          ← Volver
        </button>
        <div className="form-card">
          <h2 style={{ marginBottom: '24px' }}>Apertura de Caso NNA</h2>
          <form onSubmit={handleSubmit} className="form-group">
            <div>
              <label>Nombre completo de la NNA *</label>
              <input
                type="text"
                required
                value={formData.nna_nombre}
                onChange={e => setFormData({ ...formData, nna_nombre: e.target.value })}
              />
            </div>
            <div>
              <label>Edad</label>
              <input
                type="number"
                min="0"
                max="17"
                value={formData.nna_edad}
                onChange={e => setFormData({ ...formData, nna_edad: e.target.value })}
              />
            </div>
            <div>
              <label>Género</label>
              <select
                value={formData.nna_genero}
                onChange={e => setFormData({ ...formData, nna_genero: e.target.value })}
              >
                <option value="masculino">Masculino</option>
                <option value="femenino">Femenino</option>
                <option value="no_binario">No binario</option>
                <option value="otro">Otro</option>
              </select>
            </div>
            <button type="submit" className="btn btn-primary" disabled={saving} style={{ width: '100%', marginTop: '16px' }}>
              {saving ? 'Guardando...' : 'Crear Caso'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
