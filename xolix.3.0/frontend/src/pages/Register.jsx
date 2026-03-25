import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/client';

export default function Register() {
  const { isAdmin } = useAuth();
  const navigate = useNavigate();
  const [mensaje, setMensaje] = useState('');
  const [msgColor, setMsgColor] = useState('');
  const [loading, setLoading] = useState(false);
  const [cargandoCP, setCargandoCP] = useState(false);
  const [colonias, setColonias] = useState([]);

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

  function handleChange(e) {
    const { name, value } = e.target;
    setForm(prev => ({ ...prev, [name]: name === 'rfc' || name === 'curp' ? value.toUpperCase() : value }));
  }

  async function handleCPBlur() {
    if (form.codigo_postal.length === 5) {
      setCargandoCP(true);
      setMensaje('');
      try {
        // Fetch SEPOMEX data
        const res = await api.client.get(`/sepomex/cp/${form.codigo_postal}`);
        const data = res.data;
        setForm(prev => ({
          ...prev,
          estado: data.estado,
          municipio: data.municipio,
          colonia: data.colonias.length === 1 ? data.colonias[0] : ''
        }));
        setColonias(data.colonias);
      } catch (err) {
        setColonias([]);
        setMensaje('No se encontró el código postal.');
        setMsgColor('error');
      } finally {
        setCargandoCP(false);
      }
    } else {
      setColonias([]);
    }
  }

  function validateFrontEnd() {
    // Validar RFC
    const rfcRegex = /^[A-ZÑ&]{3,4}\d{6}[A-Z\d]{3}$/i;
    if (!rfcRegex.test(form.rfc)) return "El formato del RFC es incorrecto.";
    
    // Validar CURP
    const curpRegex = /^[A-Z][AEIOUX][A-Z]{2}\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])[HM][A-Z]{2}[B-DF-HJ-NP-TV-Z]{3}[A-Z\d]\d$/i;
    if (!curpRegex.test(form.curp)) return "El formato de la CURP es incorrecto.";

    // Validar concordancia Fecha y CURP
    if (form.fecha_nacimiento && form.curp.length >= 10) {
      const yearStr = form.fecha_nacimiento.substring(2, 4);
      const monthStr = form.fecha_nacimiento.substring(5, 7);
      const dayStr = form.fecha_nacimiento.substring(8, 10);
      const curpDateStr = form.curp.substring(4, 10);
      if (`${yearStr}${monthStr}${dayStr}` !== curpDateStr) {
        return "La fecha de nacimiento no coincide con la CURP.";
      }
    }
    return null;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setMensaje('');
    
    const errorValidacion = validateFrontEnd();
    if (errorValidacion) {
      setMensaje(errorValidacion);
      setMsgColor('error');
      return;
    }

    setLoading(true);

    try {
      await api.createUser(form);
      setMensaje('Usuario registrado correctamente ✓');
      setMsgColor('success');
      setTimeout(() => navigate('/dashboard'), 1200);
    } catch (err) {
      setMensaje(err.message);
      setMsgColor('error');
    } finally {
      setLoading(false);
    }
  }

  if (!isAdmin) {
    return (
      <div className="page-center">
        <div className="neo-card">
          <h2 className="logo">XOLIX</h2>
          <p className="subtitle">No tienes permisos para registrar personal.</p>
          <button className="btn btn-secondary" onClick={() => navigate('/dashboard')}>
            Volver al Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-center" style={{ margin: '2rem 0' }}>
      <div className="neo-card wide" style={{ maxWidth: '800px' }}>
        <h1 className="logo">XOLIX</h1>
        <p className="subtitle">Registro Estructurado de Personal</p>

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
                <option value="" disabled>Seleccionar</option>
                <option value="M">Masculino</option>
                <option value="F">Femenino</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <input name="rfc" placeholder="RFC (13 caract.)" maxLength={13} value={form.rfc} onChange={handleChange} required />
            <input name="curp" placeholder="CURP (18 caract.)" maxLength={18} value={form.curp} onChange={handleChange} required />
          </div>

          <h3 className="section-title">Dirección</h3>
          <div className="form-row">
            <div className="field-group">
              <input 
                name="codigo_postal" 
                placeholder={cargandoCP ? "Buscando CP..." : "C.P. (Ej. 07320)"} 
                maxLength={5} 
                value={form.codigo_postal} 
                onChange={handleChange} 
                onBlur={handleCPBlur}
                required 
              />
            </div>
            <div className="field-group">
              <input name="estado" placeholder="Estado" value={form.estado} onChange={handleChange} readOnly={colonias.length > 0} required />
            </div>
            <div className="field-group">
              <input name="municipio" placeholder="Municipio / Alcaldía" value={form.municipio} onChange={handleChange} readOnly={colonias.length > 0} required />
            </div>
          </div>

          <div className="form-row">
            <div className="field-group" style={{ flex: 2 }}>
              {colonias.length > 0 ? (
                <select name="colonia" value={form.colonia} onChange={handleChange} required>
                  <option value="" disabled>Selecciona una colonia</option>
                  {colonias.map(col => <option key={col} value={col}>{col}</option>)}
                </select>
              ) : (
                <input name="colonia" placeholder="Colonia" value={form.colonia} onChange={handleChange} required />
              )}
            </div>
            <div className="field-group" style={{ flex: 2 }}>
              <input name="calle" placeholder="Calle" value={form.calle} onChange={handleChange} required />
            </div>
            <div className="field-group" style={{ flex: 1 }}>
              <input name="numero" placeholder="Núm Ext/Int" value={form.numero} onChange={handleChange} required />
            </div>
          </div>
          
          <input name="calles_aledanas" placeholder="Entre calles o referencias (opcional)" value={form.calles_aledanas} onChange={handleChange} />

          <h3 className="section-title">Datos Institucionales</h3>
          <input name="correo" type="email" placeholder="Correo electrónico institucional" value={form.correo} onChange={handleChange} required />

          <div className="form-row">
            <div className="field-group">
              <label className="field-label">TIPO DE PERSONAL</label>
              <select name="tipo_personal" value={form.tipo_personal} onChange={handleChange} required>
                <option value="" disabled>Seleccionar</option>
                <option value="empleado">Empleado</option>
                <option value="voluntario">Voluntario</option>
              </select>
            </div>
            <div className="field-group">
              <label className="field-label">ROL</label>
              <select name="rol" value={form.rol} onChange={handleChange} required>
                <option value="" disabled>Seleccionar</option>
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

          <input name="password" type="password" placeholder="Contraseña segura" value={form.password} onChange={handleChange} required />

          <div className="form-actions" style={{ marginTop: '2rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => navigate('/dashboard')}>Cancelar</button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Registrando...' : 'Registrar Usuario'}
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
