import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Topbar from '../components/Topbar';
import Modal from '../components/Modal';
import api from '../api/client';

const ESTADOS = {
  activo: { label: 'Activo', color: '#4caf50', bg: 'var(--success-bg)' },
  seguimiento: { label: 'Seguimiento', color: '#1976d2', bg: 'var(--info-bg)' },
  cerrado: { label: 'Cerrado', color: '#9e9e9e', bg: '#eee' },
  urgente: { label: '⚠ Urgente', color: '#e53935', bg: 'var(--danger-bg)' },
};

const RIESGOS = {
  bajo: { label: 'Bajo', color: '#4caf50', width: '25%' },
  medio: { label: 'Medio', color: '#f9a825', width: '50%' },
  alto: { label: 'Alto', color: '#ff5722', width: '75%' },
  critico: { label: 'Crítico', color: '#e53935', width: '100%' },
};

const TIPOS_VIOLENCIA = [
  { value: 'fisica', label: 'Física' },
  { value: 'psicologica', label: 'Psicológica' },
  { value: 'sexual', label: 'Sexual' },
  { value: 'abandono', label: 'Abandono' },
  { value: 'negligencia', label: 'Negligencia' },
  { value: 'otro', label: 'Otro' },
];

export default function Expedientes() {
  const navigate = useNavigate();
  const [casos, setCasos] = useState([]);
  const [showCreate, setShowCreate] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [filtroEstado, setFiltroEstado] = useState('todos');
  const [busqueda, setBusqueda] = useState('');

  // Create form
  const [titulo, setTitulo] = useState('');
  const [desc, setDesc] = useState('');
  const [estado, setEstado] = useState('activo');
  const [nivelRiesgo, setNivelRiesgo] = useState('medio');
  // Hecho victimal - Víctima
  const [vicNombres, setVicNombres] = useState('');
  const [vicApPaterno, setVicApPaterno] = useState('');
  const [vicApMaterno, setVicApMaterno] = useState('');
  const [vicCurp, setVicCurp] = useState('');
  // Hecho victimal - Menor
  const [menNombres, setMenNombres] = useState('');
  const [menApPaterno, setMenApPaterno] = useState('');
  const [menApMaterno, setMenApMaterno] = useState('');
  const [menCurp, setMenCurp] = useState('');
  const [edadMenor, setEdadMenor] = useState('');
  // Hecho victimal - Hecho
  const [fechaIncidente, setFechaIncidente] = useState('');
  const [ubicacion, setUbicacion] = useState('');
  const [descDelito, setDescDelito] = useState('');
  const [tipoViolencia, setTipoViolencia] = useState('');
  const [refJuridica, setRefJuridica] = useState('');
  const [refFud, setRefFud] = useState('');
  const [consideraciones, setConsideraciones] = useState('');

  async function loadCasos() {
    try {
      const data = await api.getCasos();
      setCasos(data);
    } catch (err) {
      console.error('Error cargando casos:', err);
    }
  }

  useEffect(() => { loadCasos(); }, []);

  function resetForm() {
    setTitulo(''); setDesc(''); setEstado('activo'); setNivelRiesgo('medio');
    setVicNombres(''); setVicApPaterno(''); setVicApMaterno(''); setVicCurp('');
    setMenNombres(''); setMenApPaterno(''); setMenApMaterno(''); setMenCurp('');
    setEdadMenor(''); setFechaIncidente(''); setUbicacion(''); setDescDelito('');
    setTipoViolencia(''); setRefJuridica(''); setRefFud(''); setConsideraciones('');
  }

  async function handleCreate(e) {
    e.preventDefault();
    try {
      const hasHecho = vicNombres || menNombres;
      const hechoVictimal = hasHecho ? {
        victima_nombres: vicNombres || null,
        victima_apellido_paterno: vicApPaterno || null,
        victima_apellido_materno: vicApMaterno || null,
        victima_curp: vicCurp || null,
        menor_nombres: menNombres || null,
        menor_apellido_paterno: menApPaterno || null,
        menor_apellido_materno: menApMaterno || null,
        menor_curp: menCurp || null,
        edad_menor: edadMenor ? parseInt(edadMenor) : null,
        fecha_incidente: fechaIncidente || null,
        ubicacion: ubicacion || null,
        descripcion_delito: descDelito || null,
        tipo_violencia: tipoViolencia || null,
        referencia_juridica: refJuridica || null,
        referencia_fud: refFud || null,
        consideraciones: consideraciones || null,
      } : null;

      await api.createCaso({
        titulo,
        descripcion: desc || null,
        estado,
        nivel_riesgo: nivelRiesgo,
        hecho_victimal: hechoVictimal,
      });
      setShowCreate(false);
      resetForm();
      loadCasos();
    } catch (err) {
      alert("Error al crear el caso: " + err.message);
    }
  }

  async function handleDelete() {
    try {
      await api.deleteCaso(deleteTarget);
      setDeleteTarget(null);
      loadCasos();
    } catch (err) {
      console.error('Error eliminando caso:', err);
    }
  }

  const casosFiltrados = casos.filter(c => {
    if (filtroEstado !== 'todos' && c.estado !== filtroEstado) return false;
    if (busqueda && !c.titulo.toLowerCase().includes(busqueda.toLowerCase()) && !c.folio.toLowerCase().includes(busqueda.toLowerCase())) return false;
    return true;
  });

  const inputStyle = { background: 'var(--bg-light)', color: 'var(--text-primary)', border: '1px solid var(--border)', borderRadius: '8px', padding: '10px', width: '100%', fontFamily: 'inherit', fontSize: '13px' };

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">
        
        {/* Header */}
        <div className="table-card" style={{ marginBottom: '20px' }}>
          <div className="table-header">
            <div>
              <h3 style={{ fontSize: '1.3rem' }}>🗂️ Gestión de Expedientes</h3>
              <p className="subtitle" style={{ marginTop: '4px' }}>Sistema integral de gestión de casos multidisciplinarios</p>
            </div>
            <div className="table-controls" style={{ gap: '10px' }}>
              <button className="btn btn-add" onClick={() => { resetForm(); setShowCreate(true); }}>+ Nuevo Caso</button>
              <button className="btn btn-secondary" style={{ padding: '10px 16px', fontSize: '13px' }} onClick={() => navigate('/dashboard')}>← Panel</button>
            </div>
          </div>

          {/* Filters */}
          <div style={{ display: 'flex', gap: '12px', marginTop: '16px', flexWrap: 'wrap', alignItems: 'center' }}>
            <input
              placeholder="🔍 Buscar por folio o título..."
              value={busqueda}
              onChange={e => setBusqueda(e.target.value)}
              style={{ ...inputStyle, maxWidth: '300px' }}
            />
            <div style={{ display: 'flex', gap: '6px' }}>
              {['todos', 'urgente', 'activo', 'seguimiento', 'cerrado'].map(f => (
                <button
                  key={f}
                  onClick={() => setFiltroEstado(f)}
                  style={{
                    padding: '6px 14px', borderRadius: '20px', border: 'none', cursor: 'pointer', fontSize: '12px', fontWeight: 600,
                    background: filtroEstado === f ? 'var(--primary)' : 'var(--bg-light)',
                    color: filtroEstado === f ? '#fff' : 'var(--text-secondary)',
                    transition: 'all 0.2s ease',
                  }}
                >
                  {f === 'todos' ? 'Todos' : ESTADOS[f]?.label || f}
                </button>
              ))}
            </div>
            <span style={{ fontSize: '12px', color: 'var(--text-muted)', marginLeft: 'auto' }}>
              {casosFiltrados.length} caso{casosFiltrados.length !== 1 ? 's' : ''}
            </span>
          </div>
        </div>

        {/* Cases Grid */}
        {casosFiltrados.length === 0 ? (
          <div className="table-card" style={{ textAlign: 'center', padding: '60px 20px' }}>
            <p style={{ fontSize: '18px', marginBottom: '8px' }}>📂</p>
            <p style={{ color: 'var(--text-muted)' }}>No hay casos que mostrar. Crea uno nuevo para comenzar.</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '16px' }}>
            {casosFiltrados.map(c => {
              const est = ESTADOS[c.estado] || ESTADOS.activo;
              const risk = RIESGOS[c.nivel_riesgo] || RIESGOS.medio;
              return (
                <div key={c.id} className="table-card" style={{ cursor: 'pointer', transition: 'transform 0.2s ease, box-shadow 0.2s ease', padding: '20px' }}
                  onClick={() => navigate(`/casos/${c.id}`)}
                  onMouseOver={e => { e.currentTarget.style.transform = 'translateY(-2px)'; }}
                  onMouseOut={e => { e.currentTarget.style.transform = 'translateY(0)'; }}
                >
                  {/* Top row: folio + estado */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', letterSpacing: '0.5px' }}>{c.folio}</span>
                    <span style={{ fontSize: '11px', padding: '3px 10px', borderRadius: '12px', background: est.bg, color: est.color, fontWeight: 600 }}>
                      {est.label}
                    </span>
                  </div>

                  {/* Title */}
                  <h4 style={{ fontSize: '15px', marginBottom: '12px', lineHeight: 1.3 }}>{c.titulo}</h4>

                  {/* Risk bar */}
                  <div style={{ marginBottom: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Nivel de riesgo</span>
                      <span style={{ fontSize: '11px', fontWeight: 600, color: risk.color }}>{risk.label}</span>
                    </div>
                    <div style={{ height: '4px', borderRadius: '4px', background: 'var(--border)' }}>
                      <div style={{ height: '100%', borderRadius: '4px', width: risk.width, background: risk.color, transition: 'width 0.3s ease' }}></div>
                    </div>
                  </div>

                  {/* Stats row */}
                  <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                    <span>👥 {c.participantes_count}</span>
                    <span>📝 {c.notas_count}</span>
                    <span>📎 {c.documentos_count}</span>
                  </div>

                  {/* Delete button */}
                  <div style={{ marginTop: '12px', textAlign: 'right' }}>
                    <button
                      className="btn-sm btn-delete"
                      onClick={e => { e.stopPropagation(); setDeleteTarget(c.id); }}
                      style={{ fontSize: '11px' }}
                    >
                      Eliminar
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* ── Creation Modal ── */}
      {showCreate && (
        <div className="modal-overlay active" onClick={() => setShowCreate(false)}>
          <div className="modal-box" onClick={e => e.stopPropagation()} style={{ maxWidth: '680px', width: '100%', maxHeight: '85vh', overflowY: 'auto' }}>
            <h3 style={{ marginBottom: '20px' }}>📋 Crear Nuevo Caso</h3>

            <form onSubmit={handleCreate} className="form-stack" style={{ textAlign: 'left' }}>

              {/* Section: General */}
              <p style={{ fontSize: '12px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '8px' }}>Información General</p>

              <div className="field-group">
                <label className="field-label">TÍTULO DEL CASO</label>
                <input placeholder="Ej. Caso de violencia familiar — Familia Rodríguez" value={titulo} onChange={e => setTitulo(e.target.value)} required style={inputStyle} />
              </div>

              <div className="field-group">
                <label className="field-label">DESCRIPCIÓN</label>
                <textarea placeholder="Contexto del caso..." value={desc} onChange={e => setDesc(e.target.value)} style={{ ...inputStyle, minHeight: '70px', resize: 'vertical' }} />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="field-group">
                  <label className="field-label">ESTADO</label>
                  <select value={estado} onChange={e => setEstado(e.target.value)} style={inputStyle}>
                    <option value="activo">🟢 Activo</option>
                    <option value="seguimiento">🔵 Seguimiento</option>
                    <option value="urgente">🔴 Urgente</option>
                    <option value="cerrado">⚪ Cerrado</option>
                  </select>
                </div>
                <div className="field-group">
                  <label className="field-label">NIVEL DE RIESGO</label>
                  <select value={nivelRiesgo} onChange={e => setNivelRiesgo(e.target.value)} style={inputStyle}>
                    <option value="bajo">🟢 Bajo</option>
                    <option value="medio">🟡 Medio</option>
                    <option value="alto">🟠 Alto</option>
                    <option value="critico">🔴 Crítico</option>
                  </select>
                </div>
              </div>

              {/* Section: Hecho Victimal */}
              <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '16px 0' }} />
              <p style={{ fontSize: '12px', fontWeight: 700, color: '#e53935', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '8px' }}>🔒 Datos de la Víctima / Madre / Tutor (Confidencial)</p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                <div className="field-group">
                  <label className="field-label">NOMBRE(S)</label>
                  <input placeholder="Nombre(s)" value={vicNombres} onChange={e => setVicNombres(e.target.value)} style={inputStyle} />
                </div>
                <div className="field-group">
                  <label className="field-label">APELLIDO PATERNO</label>
                  <input placeholder="Apellido paterno" value={vicApPaterno} onChange={e => setVicApPaterno(e.target.value)} style={inputStyle} />
                </div>
                <div className="field-group">
                  <label className="field-label">APELLIDO MATERNO</label>
                  <input placeholder="Apellido materno" value={vicApMaterno} onChange={e => setVicApMaterno(e.target.value)} style={inputStyle} />
                </div>
              </div>
              <div className="field-group">
                <label className="field-label">CURP DE LA VÍCTIMA</label>
                <input placeholder="18 caracteres" maxLength={18} value={vicCurp} onChange={e => setVicCurp(e.target.value.toUpperCase())} style={{ ...inputStyle, fontFamily: 'monospace', letterSpacing: '1px' }} />
              </div>

              <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '16px 0' }} />
              <p style={{ fontSize: '12px', fontWeight: 700, color: '#1976d2', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '8px' }}>👶 Datos del Menor</p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                <div className="field-group">
                  <label className="field-label">NOMBRE(S)</label>
                  <input placeholder="Nombre(s)" value={menNombres} onChange={e => setMenNombres(e.target.value)} style={inputStyle} />
                </div>
                <div className="field-group">
                  <label className="field-label">APELLIDO PATERNO</label>
                  <input placeholder="Apellido paterno" value={menApPaterno} onChange={e => setMenApPaterno(e.target.value)} style={inputStyle} />
                </div>
                <div className="field-group">
                  <label className="field-label">APELLIDO MATERNO</label>
                  <input placeholder="Apellido materno" value={menApMaterno} onChange={e => setMenApMaterno(e.target.value)} style={inputStyle} />
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '12px' }}>
                <div className="field-group">
                  <label className="field-label">CURP DEL MENOR</label>
                  <input placeholder="18 caracteres" maxLength={18} value={menCurp} onChange={e => setMenCurp(e.target.value.toUpperCase())} style={{ ...inputStyle, fontFamily: 'monospace', letterSpacing: '1px' }} />
                </div>
                <div className="field-group">
                  <label className="field-label">EDAD DEL MENOR</label>
                  <input type="number" min="0" max="17" placeholder="Años" value={edadMenor} onChange={e => setEdadMenor(e.target.value)} style={inputStyle} />
                </div>
              </div>

              <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '16px 0' }} />
              <p style={{ fontSize: '12px', fontWeight: 700, color: '#ff5722', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '8px' }}>📌 Datos del Hecho</p>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                <div className="field-group">
                  <label className="field-label">FECHA DEL INCIDENTE</label>
                  <input type="date" value={fechaIncidente} onChange={e => setFechaIncidente(e.target.value)} style={inputStyle} />
                </div>
                <div className="field-group">
                  <label className="field-label">TIPO DE VIOLENCIA</label>
                  <select value={tipoViolencia} onChange={e => setTipoViolencia(e.target.value)} style={inputStyle}>
                    <option value="">-- Seleccionar --</option>
                    {TIPOS_VIOLENCIA.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
                  </select>
                </div>
                <div className="field-group">
                  <label className="field-label">UBICACIÓN</label>
                  <input placeholder="Dirección o referencia" value={ubicacion} onChange={e => setUbicacion(e.target.value)} style={inputStyle} />
                </div>
              </div>

              <div className="field-group">
                <label className="field-label">DESCRIPCIÓN DEL DELITO O SITUACIÓN</label>
                <textarea placeholder="Detalle de los hechos..." value={descDelito} onChange={e => setDescDelito(e.target.value)} style={{ ...inputStyle, minHeight: '60px', resize: 'vertical' }} />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                <div className="field-group">
                  <label className="field-label">REFERENCIA JURÍDICA</label>
                  <input placeholder="No. expediente legal" value={refJuridica} onChange={e => setRefJuridica(e.target.value)} style={inputStyle} />
                </div>
                <div className="field-group">
                  <label className="field-label">REFERENCIA FUD</label>
                  <input placeholder="Formato Único de Declaración" value={refFud} onChange={e => setRefFud(e.target.value)} style={inputStyle} />
                </div>
              </div>

              {/* Section: Consideraciones */}
              <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '16px 0' }} />
              <p style={{ fontSize: '12px', fontWeight: 700, color: '#607d8b', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '8px' }}>📝 Consideraciones Adicionales</p>

              <div className="field-group">
                <label className="field-label">CONSIDERACIONES</label>
                <textarea placeholder="Observaciones, antecedentes relevantes, condiciones especiales..." value={consideraciones} onChange={e => setConsideraciones(e.target.value)} style={{ ...inputStyle, minHeight: '80px', resize: 'vertical' }} />
              </div>

              <div className="form-actions" style={{ marginTop: '24px' }}>
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancelar</button>
                <button type="submit" className="btn btn-primary">Crear Caso</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {deleteTarget && (
        <Modal
          title="¿Eliminar caso?"
          message="Se eliminará permanentemente el caso y todos sus datos asociados (notas, documentos, participantes). Esta acción es irreversible."
          confirmText="Eliminar permanentemente"
          danger
          onConfirm={handleDelete}
          onCancel={() => setDeleteTarget(null)}
        />
      )}
    </div>
  );
}
