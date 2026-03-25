import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

export default function UserEdit() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [msgColor, setMsgColor] = useState('');

  const [form, setForm] = useState({
    nombre: '',
    apellido_paterno: '',
    apellido_materno: '',
    correo: '',
    rfc: '',
    curp: '',
    sexo: '',
    fecha_nacimiento: '',
    estado: '',
    municipio: '',
    colonia: '',
    calle: '',
    numero: '',
    codigo_postal: '',
    calles_aledanas: '',
    tipo_personal: '',
    rol: '',
    password: '',
  });

  useEffect(() => {
    if (!isAdmin) {
      navigate('/dashboard');
      return;
    }
    async function load() {
      try {
        const u = await api.getUser(id);
        setForm({
          nombre: u.nombre || '',
          apellido_paterno: u.apellido_paterno || '',
          apellido_materno: u.apellido_materno || '',
          correo: u.correo || '',
          rfc: u.rfc || '',
          curp: u.curp || '',
          sexo: u.sexo || '',
          fecha_nacimiento: u.fecha_nacimiento || '',
          estado: u.estado || '',
          municipio: u.municipio || '',
          colonia: u.colonia || '',
          calle: u.calle || '',
          numero: u.numero || '',
          codigo_postal: u.codigo_postal || '',
          calles_aledanas: u.calles_aledanas || '',
          tipo_personal: u.tipo_personal || '',
          rol: u.rol || '',
          password: '',
        });
      } catch {
        setMensaje('Error al cargar usuario.');
        setMsgColor('error');
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id, isAdmin, navigate]);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: name === 'rfc' || name === 'curp' ? value.toUpperCase() : value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setMensaje('Guardando...');
    setMsgColor('info');

    const datos = { ...form };
    if (!datos.password) delete datos.password;

    try {
      await api.updateUser(id, datos);
      setMensaje('Cambios guardados correctamente ✓');
      setMsgColor('success');
      setTimeout(() => navigate(`/usuario/${id}`), 1000);
    } catch (err) {
      setMensaje(err.message);
      setMsgColor('error');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="page-center">
        <div className="neo-card">
          <h2 className="logo">XOLIX</h2>
          <p className="subtitle">Cargando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="page-center" style={{ margin: '2rem 0' }}>
      <div className="neo-card wide" style={{ maxWidth: '800px' }}>
        <h1 className="logo">XOLIX</h1>
        <p className="subtitle">Modificar datos del personal</p>

        <form onSubmit={handleSubmit} className="form-stack">
          
          <h3 className="section-title">Datos Personales</h3>
          <div className="form-row">
            <input name="nombre" placeholder="Nombre(s)" value={form.nombre} onChange={handleChange} required />
            <input name="apellido_paterno" placeholder="Apellido Paterno" value={form.apellido_paterno} onChange={handleChange} required />
            <input name="apellido_materno" placeholder="Apellido Materno" value={form.apellido_materno} onChange={handleChange} required />
          </div>

          <div className="form-row">
            <div className="field-group">
              <label className="field-label">FECHA DE NACIMIENTO</label>
              <input name="fecha_nacimiento" type="date" value={form.fecha_nacimiento} onChange={handleChange} required />
            </div>
            <div className="field-group">
              <label className="field-label">SEXO</label>
              <select name="sexo" value={form.sexo} onChange={handleChange} required>
                <option value="M">Masculino</option>
                <option value="F">Femenino</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <input name="rfc" placeholder="RFC" maxLength={13} value={form.rfc} onChange={handleChange} required />
            <input name="curp" placeholder="CURP" maxLength={18} value={form.curp} onChange={handleChange} required />
          </div>

          <h3 className="section-title">Dirección</h3>
          <div className="form-row">
            <div className="field-group">
              <input name="codigo_postal" placeholder="C.P." maxLength={5} value={form.codigo_postal} onChange={handleChange} required />
            </div>
            <div className="field-group">
              <input name="estado" placeholder="Estado" value={form.estado} onChange={handleChange} required />
            </div>
            <div className="field-group">
              <input name="municipio" placeholder="Municipio" value={form.municipio} onChange={handleChange} required />
            </div>
          </div>

          <div className="form-row">
            <div className="field-group" style={{ flex: 2 }}>
              <input name="colonia" placeholder="Colonia" value={form.colonia} onChange={handleChange} required />
            </div>
            <div className="field-group" style={{ flex: 2 }}>
              <input name="calle" placeholder="Calle" value={form.calle} onChange={handleChange} required />
            </div>
            <div className="field-group" style={{ flex: 1 }}>
              <input name="numero" placeholder="Núm" value={form.numero} onChange={handleChange} required />
            </div>
          </div>
          <input name="calles_aledanas" placeholder="Entre calles o referencias (opcional)" value={form.calles_aledanas} onChange={handleChange} />

          <h3 className="section-title">Institucional</h3>
          <input name="correo" type="email" placeholder="Correo electrónico" value={form.correo} onChange={handleChange} required />

          <div className="form-row">
            <div className="field-group">
              <label className="field-label">TIPO DE PERSONAL</label>
              <select name="tipo_personal" value={form.tipo_personal} onChange={handleChange} required>
                <option value="empleado">Empleado</option>
                <option value="voluntario">Voluntario</option>
              </select>
            </div>
            <div className="field-group">
              <label className="field-label">ROL</label>
              <select name="rol" value={form.rol} onChange={handleChange} required>
                <option value="director">Director</option>
                <option value="coordinador">Coordinador</option>
                <option value="psicologo">Psicólogo</option>
                <option value="doctor">Doctor</option>
                <option value="abogado">Abogado</option>
                <option value="trabajador social">Trabajador social</option>
                <option value="analista">Analista</option>
              </select>
            </div>
          </div>

          <input name="password" type="password" placeholder="Nueva contraseña (opcional)" value={form.password} onChange={handleChange} />

          <div className="form-actions" style={{ marginTop: '2rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => navigate(`/usuario/${id}`)}>Cancelar</button>
            <button type="submit" className="btn btn-primary" disabled={saving}>
              {saving ? 'Guardando...' : 'Guardar cambios'}
            </button>
          </div>
        </form>

        {mensaje && <div className={`mensaje ${msgColor}`}>{mensaje}</div>}
      </div>
      <style>{`
        .section-title { font-size: 0.9rem; color: var(--text-muted); margin-top: 1.5rem; margin-bottom: 0.5rem; text-transform: uppercase; letter-spacing: 1px; }
      `}</style>
    </div>
  );
}
