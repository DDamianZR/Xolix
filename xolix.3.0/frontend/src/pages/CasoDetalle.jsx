import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Topbar from '../components/Topbar';
import api from '../api/client';

const ESTADOS = {
  activo: { label: 'Activo', color: '#4caf50', bg: 'var(--success-bg)' },
  seguimiento: { label: 'Seguimiento', color: '#1976d2', bg: 'var(--info-bg)' },
  cerrado: { label: 'Cerrado', color: '#9e9e9e', bg: '#eee' },
  urgente: { label: '⚠ Urgente', color: '#e53935', bg: 'var(--danger-bg)' },
};

const RIESGOS = {
  bajo: { label: 'Bajo', color: '#4caf50', emoji: '🟢' },
  medio: { label: 'Medio', color: '#f9a825', emoji: '🟡' },
  alto: { label: 'Alto', color: '#ff5722', emoji: '🟠' },
  critico: { label: 'Crítico', color: '#e53935', emoji: '🔴' },
};

const AREAS = {
  general: { label: 'General', icon: '📋', color: 'var(--primary)' },
  psicologia: { label: 'Psicología', icon: '🧠', color: '#9c27b0' },
  legal: { label: 'Legal', icon: '⚖️', color: '#1976d2' },
  trabajo_social: { label: 'Trabajo Social', icon: '🏠', color: '#ff9800' },
  medico: { label: 'Médico', icon: '🏥', color: '#e53935' },
  analisis: { label: 'Análisis', icon: '📊', color: '#607d8b' },
};

const CATEGORIAS_DOC = [
  { value: 'legal', label: '⚖️ Legal' },
  { value: 'medico', label: '🏥 Médico' },
  { value: 'evidencia', label: '📸 Evidencia' },
  { value: 'psicologico', label: '🧠 Psicológico' },
  { value: 'social', label: '🏠 Social' },
  { value: 'otro', label: '📎 Otro' },
];

const ETIQUETAS_DISP = ['urgente', 'seguimiento', 'riesgo_alto', 'revisión', 'pendiente', 'resuelto'];

function formatDate(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('es-MX', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export default function CasoDetalle() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [caso, setCaso] = useState(null);
  const [tab, setTab] = useState('info');
  const [loading, setLoading] = useState(true);

  // Nota form
  const [notaArea, setNotaArea] = useState('general');
  const [notaContenido, setNotaContenido] = useState('');
  const [notaPrivada, setNotaPrivada] = useState(false);
  const [notaEtiquetas, setNotaEtiquetas] = useState([]);
  const [filtroArea, setFiltroArea] = useState('todas');

  // Doc upload
  const [docNombre, setDocNombre] = useState('');
  const [docCategoria, setDocCategoria] = useState('otro');
  const [docFile, setDocFile] = useState(null);

  // Participante
  const [usuarios, setUsuarios] = useState([]);
  const [partUserId, setPartUserId] = useState('');
  const [partArea, setPartArea] = useState('general');

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { loadCaso(); }, [id]);

  async function loadCaso() {
    try {
      setLoading(true);
      const data = await api.getCaso(id);
      setCaso(data);
    } catch {
      alert('Error cargando caso');
      navigate('/expedientes');
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateNota(e) {
    e.preventDefault();
    if (!notaContenido.trim()) return;
    try {
      await api.createNota(id, {
        area: notaArea,
        contenido: notaContenido,
        privada: notaPrivada,
        etiquetas: notaEtiquetas,
      });
      setNotaContenido('');
      setNotaPrivada(false);
      setNotaEtiquetas([]);
      loadCaso();
    } catch (err) {
      console.error(err);
    }
  }

  async function handleUploadDoc(e) {
    e.preventDefault();
    if (!docFile || !docNombre.trim()) return;
    try {
      const formData = new FormData();
      formData.append('archivo', docFile);
      formData.append('nombre', docNombre);
      formData.append('categoria', docCategoria);
      await api.uploadDocumentoCaso(id, formData);
      setDocNombre('');
      setDocFile(null);
      setDocCategoria('otro');
      loadCaso();
    } catch (err) {
      console.error(err);
    }
  }

  async function handleAddParticipante(e) {
    e.preventDefault();
    if (!partUserId) return;
    try {
      await api.addParticipante(id, { usuario_id: parseInt(partUserId), area: partArea });
      setPartUserId('');
      loadCaso();
    } catch (err) {
      alert(err.message);
    }
  }

  async function loadUsers() {
    try {
      const data = await api.getUsers();
      setUsuarios(data);
    } catch (err) {
      console.error(err);
    }
  }

  function toggleEtiqueta(tag) {
    setNotaEtiquetas(prev => prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]);
  }

  if (loading) return <div className="page-dashboard"><Topbar /><div className="container"><p style={{ textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>Cargando caso...</p></div></div>;
  if (!caso) return null;

  const est = ESTADOS[caso.estado] || ESTADOS.activo;
  const risk = RIESGOS[caso.nivel_riesgo] || RIESGOS.medio;
  const hv = caso.hecho_victimal;
  const notasFiltradas = filtroArea === 'todas' ? caso.notas : caso.notas.filter(n => n.area === filtroArea);

  const inputStyle = { background: 'var(--bg-light)', color: 'var(--text-primary)', border: '1px solid var(--border)', borderRadius: '8px', padding: '10px', width: '100%', fontFamily: 'inherit', fontSize: '13px' };
  const tabBtnStyle = (active) => ({
    padding: '10px 16px', border: 'none', cursor: 'pointer', fontSize: '13px', fontWeight: 600,
    borderRadius: '10px', transition: 'all 0.2s ease',
    background: active ? 'var(--primary)' : 'transparent',
    color: active ? '#fff' : 'var(--text-secondary)',
    display: 'flex', alignItems: 'center', gap: '6px',
  });

  const TABS = [
    { key: 'info', icon: '📋', label: 'Información' },
    { key: 'notas', icon: '📝', label: `Notas (${caso.notas.length})` },
    { key: 'docs', icon: '📎', label: `Documentos (${caso.documentos.length})` },
    { key: 'equipo', icon: '👥', label: `Equipo (${caso.participantes.length})` },
  ];

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">

        {/* Back + Header */}
        <button className="btn btn-secondary" onClick={() => navigate('/expedientes')} style={{ marginBottom: '16px', padding: '8px 16px', fontSize: '13px' }}>
          ← Volver a Expedientes
        </button>

        <div className="table-card" style={{ marginBottom: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <span style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', letterSpacing: '1px' }}>{caso.folio}</span>
              <h2 style={{ fontSize: '1.4rem', marginTop: '4px', marginBottom: '8px' }}>{caso.titulo}</h2>
              {caso.descripcion && <p className="subtitle" style={{ marginBottom: '12px', maxWidth: '600px' }}>{caso.descripcion}</p>}
            </div>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
              <span style={{ fontSize: '12px', padding: '5px 14px', borderRadius: '20px', background: est.bg, color: est.color, fontWeight: 600 }}>
                {est.label}
              </span>
              <span style={{ fontSize: '12px', padding: '5px 14px', borderRadius: '20px', background: risk.color + '20', color: risk.color, fontWeight: 600 }}>
                {risk.emoji} Riesgo {risk.label}
              </span>
            </div>
          </div>
        </div>

        {/* Tabs + Content */}
        <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr', gap: '16px', minHeight: '500px' }}>

          {/* Sidebar Tabs */}
          <div className="table-card" style={{ padding: '12px', display: 'flex', flexDirection: 'column', gap: '4px', height: 'fit-content' }}>
            {TABS.map(t => (
              <button key={t.key} style={tabBtnStyle(tab === t.key)} onClick={() => { setTab(t.key); if (t.key === 'equipo') loadUsers(); }}>
                <span>{t.icon}</span> {t.label}
              </button>
            ))}
          </div>

          {/* Content Area */}
          <div className="table-card" style={{ minHeight: '400px' }}>

            {/* ═══ TAB: INFO ═══ */}
            {tab === 'info' && (
              <div>
                <h3 style={{ marginBottom: '20px', fontSize: '1.1rem' }}>📋 Información del Caso</h3>

                {!hv ? (
                  <p style={{ color: 'var(--text-muted)', fontSize: '14px' }}>No se han registrado datos del hecho victimal.</p>
                ) : (
                  <div>
                    {/* Víctima */}
                    <p style={{ fontSize: '11px', fontWeight: 700, color: '#e53935', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '10px' }}>🔒 Víctima / Madre / Tutor</p>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                      {[
                        ['Nombre(s)', hv.victima_nombres],
                        ['Apellido Paterno', hv.victima_apellido_paterno],
                        ['Apellido Materno', hv.victima_apellido_materno],
                      ].filter(([, v]) => v).map(([label, value]) => (
                        <div key={label} style={{ padding: '12px', borderRadius: '10px', background: 'var(--bg)', border: '1px solid var(--border)' }}>
                          <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{label}</span>
                          <span style={{ fontSize: '14px', fontWeight: 500 }}>{value}</span>
                        </div>
                      ))}
                    </div>
                    {hv.victima_curp && (
                      <div style={{ padding: '12px', borderRadius: '10px', background: 'var(--bg)', border: '1px solid var(--border)', marginBottom: '16px' }}>
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', textTransform: 'uppercase' }}>CURP</span>
                        <span style={{ fontSize: '14px', fontWeight: 500, fontFamily: 'monospace', letterSpacing: '1px' }}>{hv.victima_curp}</span>
                      </div>
                    )}

                    {/* Menor */}
                    <p style={{ fontSize: '11px', fontWeight: 700, color: '#1976d2', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '10px', marginTop: '20px' }}>👶 Datos del Menor</p>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                      {[
                        ['Nombre(s)', hv.menor_nombres],
                        ['Apellido Paterno', hv.menor_apellido_paterno],
                        ['Apellido Materno', hv.menor_apellido_materno],
                        ['Edad', hv.edad_menor ? `${hv.edad_menor} años` : null],
                      ].filter(([, v]) => v).map(([label, value]) => (
                        <div key={label} style={{ padding: '12px', borderRadius: '10px', background: 'var(--bg)', border: '1px solid var(--border)' }}>
                          <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{label}</span>
                          <span style={{ fontSize: '14px', fontWeight: 500 }}>{value}</span>
                        </div>
                      ))}
                    </div>
                    {hv.menor_curp && (
                      <div style={{ padding: '12px', borderRadius: '10px', background: 'var(--bg)', border: '1px solid var(--border)', marginBottom: '16px' }}>
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', textTransform: 'uppercase' }}>CURP DEL MENOR</span>
                        <span style={{ fontSize: '14px', fontWeight: 500, fontFamily: 'monospace', letterSpacing: '1px' }}>{hv.menor_curp}</span>
                      </div>
                    )}

                    {/* Datos del hecho */}
                    <p style={{ fontSize: '11px', fontWeight: 700, color: '#ff5722', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '10px', marginTop: '20px' }}>📌 Datos del Hecho</p>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '16px' }}>
                      {[
                        ['Fecha del incidente', hv.fecha_incidente],
                        ['Ubicación', hv.ubicacion],
                        ['Tipo de violencia', hv.tipo_violencia],
                        ['Referencia jurídica', hv.referencia_juridica],
                        ['Referencia FUD', hv.referencia_fud],
                      ].filter(([, v]) => v).map(([label, value]) => (
                        <div key={label} style={{ padding: '12px', borderRadius: '10px', background: 'var(--bg)', border: '1px solid var(--border)' }}>
                          <span style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{label}</span>
                          <span style={{ fontSize: '14px', fontWeight: 500 }}>{value}</span>
                        </div>
                      ))}
                    </div>
                    {hv.descripcion_delito && (
                      <div style={{ gridColumn: 'span 2', padding: '12px', borderRadius: '10px', background: 'var(--danger-bg)', border: '1px solid rgba(229,57,53,0.2)', marginBottom: '16px' }}>
                        <span style={{ fontSize: '11px', color: '#e53935', display: 'block', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Descripción del delito</span>
                        <span style={{ fontSize: '14px' }}>{hv.descripcion_delito}</span>
                      </div>
                    )}

                    {/* Consideraciones */}
                    {hv.consideraciones && (
                      <>
                        <p style={{ fontSize: '11px', fontWeight: 700, color: '#607d8b', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '10px', marginTop: '20px' }}>📝 Consideraciones</p>
                        <div style={{ padding: '12px', borderRadius: '10px', background: 'var(--bg)', border: '1px solid var(--border)', marginBottom: '16px' }}>
                          <span style={{ fontSize: '14px', whiteSpace: 'pre-wrap' }}>{hv.consideraciones}</span>
                        </div>
                      </>
                    )}
                  </div>
                )}

                <div style={{ marginTop: '24px', padding: '12px', borderRadius: '10px', background: 'var(--bg)', fontSize: '12px', color: 'var(--text-muted)', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Caso creado el {formatDate(caso.fecha_creacion)}</span>
                  {hv?.fecha_creacion_expediente && <span>Expediente registrado: {formatDate(hv.fecha_creacion_expediente)}</span>}
                </div>
              </div>
            )}

            {/* ═══ TAB: NOTAS ═══ */}
            {tab === 'notas' && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
                  <h3 style={{ fontSize: '1.1rem' }}>📝 Notas del Caso</h3>
                  {/* Area filter */}
                  <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                    <button onClick={() => setFiltroArea('todas')} style={{ ...tabBtnStyle(filtroArea === 'todas'), padding: '5px 10px', fontSize: '11px', borderRadius: '15px' }}>Todas</button>
                    {Object.entries(AREAS).map(([key, a]) => (
                      <button key={key} onClick={() => setFiltroArea(key)} style={{ ...tabBtnStyle(filtroArea === key), padding: '5px 10px', fontSize: '11px', borderRadius: '15px', background: filtroArea === key ? a.color : 'transparent' }}>
                        {a.icon}
                      </button>
                    ))}
                  </div>
                </div>

                {/* New note form */}
                <form onSubmit={handleCreateNota} style={{ marginBottom: '20px', padding: '16px', borderRadius: '12px', background: 'var(--bg)', border: '1px solid var(--border)' }}>
                  <div style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                    <select value={notaArea} onChange={e => setNotaArea(e.target.value)} style={{ ...inputStyle, maxWidth: '180px' }}>
                      {Object.entries(AREAS).map(([key, a]) => (
                        <option key={key} value={key}>{a.icon} {a.label}</option>
                      ))}
                    </select>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', color: 'var(--text-secondary)', cursor: 'pointer', whiteSpace: 'nowrap' }}>
                      <input type="checkbox" checked={notaPrivada} onChange={e => setNotaPrivada(e.target.checked)} />
                      🔒 Privada
                    </label>
                  </div>
                  <textarea
                    placeholder="Escribe una nota sobre el caso..."
                    value={notaContenido}
                    onChange={e => setNotaContenido(e.target.value)}
                    style={{ ...inputStyle, minHeight: '80px', resize: 'vertical', marginBottom: '10px' }}
                  />
                  {/* Tags */}
                  <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginBottom: '10px' }}>
                    {ETIQUETAS_DISP.map(tag => (
                      <button key={tag} type="button" onClick={() => toggleEtiqueta(tag)} style={{
                        padding: '3px 10px', borderRadius: '12px', border: '1px solid var(--border)', cursor: 'pointer', fontSize: '11px',
                        background: notaEtiquetas.includes(tag) ? 'var(--primary)' : 'transparent',
                        color: notaEtiquetas.includes(tag) ? '#fff' : 'var(--text-muted)',
                      }}>
                        #{tag}
                      </button>
                    ))}
                  </div>
                  <button type="submit" className="btn btn-primary" style={{ padding: '8px 20px', fontSize: '13px' }}>Publicar nota</button>
                </form>

                {/* Notes Timeline */}
                <div style={{ borderLeft: '2px solid var(--border)', paddingLeft: '20px', marginLeft: '10px' }}>
                  {notasFiltradas.length === 0 ? (
                    <p style={{ color: 'var(--text-muted)', fontSize: '14px', padding: '20px 0' }}>No hay notas en este caso aún.</p>
                  ) : (
                    notasFiltradas.map(n => {
                      const area = AREAS[n.area] || AREAS.general;
                      return (
                        <div key={n.id} style={{ position: 'relative', marginBottom: '20px', padding: '16px', borderRadius: '12px', background: 'var(--bg-light)', border: `1px solid ${n.privada ? '#e5393530' : 'var(--border)'}` }}>
                          {/* Timeline dot */}
                          <div style={{ position: 'absolute', left: '-28px', top: '20px', width: '12px', height: '12px', borderRadius: '50%', background: area.color, border: '2px solid var(--bg-light)' }}></div>

                          {/* Header */}
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <span style={{ fontSize: '12px', padding: '2px 8px', borderRadius: '8px', background: area.color + '20', color: area.color, fontWeight: 600 }}>
                                {area.icon} {area.label}
                              </span>
                              {n.privada && <span style={{ fontSize: '10px', padding: '2px 6px', borderRadius: '6px', background: 'var(--danger-bg)', color: '#e53935' }}>🔒 Privada</span>}
                            </div>
                            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{formatDate(n.fecha_creacion)}</span>
                          </div>

                          {/* Author */}
                          <span style={{ fontSize: '12px', color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>
                            {n.autor_nombre || 'Usuario'}
                          </span>

                          {/* Content */}
                          <p style={{ fontSize: '14px', lineHeight: 1.6, whiteSpace: 'pre-wrap' }}>{n.contenido}</p>

                          {/* Tags */}
                          {n.etiquetas && n.etiquetas.length > 0 && (
                            <div style={{ display: 'flex', gap: '4px', marginTop: '10px', flexWrap: 'wrap' }}>
                              {n.etiquetas.map(tag => (
                                <span key={tag} style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '10px', background: 'var(--bg)', color: 'var(--text-muted)', border: '1px solid var(--border)' }}>
                                  #{tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      );
                    })
                  )}
                </div>
              </div>
            )}

            {/* ═══ TAB: DOCUMENTOS ═══ */}
            {tab === 'docs' && (
              <div>
                <h3 style={{ marginBottom: '16px', fontSize: '1.1rem' }}>📎 Documentos del Caso</h3>

                {/* Upload form */}
                <form onSubmit={handleUploadDoc} style={{ display: 'flex', gap: '10px', marginBottom: '20px', padding: '16px', borderRadius: '12px', background: 'var(--bg)', border: '1px solid var(--border)', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                  <div style={{ flex: '1 1 200px' }}>
                    <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>NOMBRE</label>
                    <input placeholder="Nombre del documento" value={docNombre} onChange={e => setDocNombre(e.target.value)} style={inputStyle} />
                  </div>
                  <div style={{ flex: '0 0 160px' }}>
                    <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>CATEGORÍA</label>
                    <select value={docCategoria} onChange={e => setDocCategoria(e.target.value)} style={inputStyle}>
                      {CATEGORIAS_DOC.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
                    </select>
                  </div>
                  <div style={{ flex: '1 1 200px' }}>
                    <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>ARCHIVO</label>
                    <input type="file" onChange={e => setDocFile(e.target.files?.[0] || null)} style={{ ...inputStyle, padding: '7px' }} />
                  </div>
                  <button type="submit" className="btn btn-primary" style={{ padding: '10px 20px', fontSize: '13px', whiteSpace: 'nowrap' }}>Subir</button>
                </form>

                {/* Document grid */}
                {caso.documentos.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)', fontSize: '14px', textAlign: 'center', padding: '40px' }}>No hay documentos aún.</p>
                ) : (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '12px' }}>
                    {caso.documentos.map(d => {
                      const cat = CATEGORIAS_DOC.find(c => c.value === d.categoria);
                      return (
                        <div key={d.id} style={{ padding: '16px', borderRadius: '12px', background: 'var(--bg)', border: '1px solid var(--border)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                            <span style={{ fontSize: '20px' }}>📄</span>
                            <span style={{ fontSize: '10px', padding: '2px 8px', borderRadius: '8px', background: 'var(--bg-light)', color: 'var(--text-secondary)' }}>
                              {cat?.label || d.categoria}
                            </span>
                          </div>
                          <p style={{ fontSize: '14px', fontWeight: 500, marginBottom: '4px' }}>{d.nombre}</p>
                          <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                            {d.subido_por_nombre} · {formatDate(d.fecha_subida)}
                          </p>
                          <p style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '4px' }}>
                            v{d.version} · .{d.tipo_archivo}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* ═══ TAB: EQUIPO ═══ */}
            {tab === 'equipo' && (
              <div>
                <h3 style={{ marginBottom: '16px', fontSize: '1.1rem' }}>👥 Equipo Multidisciplinario</h3>

                {/* Add participant form */}
                <form onSubmit={handleAddParticipante} style={{ display: 'flex', gap: '10px', marginBottom: '20px', padding: '16px', borderRadius: '12px', background: 'var(--bg)', border: '1px solid var(--border)', flexWrap: 'wrap', alignItems: 'flex-end' }}>
                  <div style={{ flex: '1 1 200px' }}>
                    <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>USUARIO</label>
                    <select value={partUserId} onChange={e => setPartUserId(e.target.value)} style={inputStyle}>
                      <option value="">-- Seleccionar --</option>
                      {usuarios.filter(u => !caso.participantes.some(p => p.usuario_id === u.id)).map(u => (
                        <option key={u.id} value={u.id}>{u.nombre} {u.apellido_paterno} ({u.rol})</option>
                      ))}
                    </select>
                  </div>
                  <div style={{ flex: '0 0 180px' }}>
                    <label style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'block', marginBottom: '4px' }}>ÁREA</label>
                    <select value={partArea} onChange={e => setPartArea(e.target.value)} style={inputStyle}>
                      {Object.entries(AREAS).map(([key, a]) => (
                        <option key={key} value={key}>{a.icon} {a.label}</option>
                      ))}
                    </select>
                  </div>
                  <button type="submit" className="btn btn-primary" style={{ padding: '10px 20px', fontSize: '13px' }}>Agregar</button>
                </form>

                {/* Participants list */}
                <div style={{ display: 'grid', gap: '10px' }}>
                  {caso.participantes.map(p => {
                    const area = AREAS[p.area] || AREAS.general;
                    return (
                      <div key={p.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '14px', borderRadius: '12px', background: 'var(--bg)', border: '1px solid var(--border)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: area.color + '20', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '18px' }}>
                            {area.icon}
                          </div>
                          <div>
                            <p style={{ fontSize: '14px', fontWeight: 500 }}>{p.usuario_nombre}</p>
                            <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{area.label} · {p.permiso}</p>
                          </div>
                        </div>
                        {p.permiso !== 'admin_caso' && (
                          <button
                            className="btn-sm btn-delete"
                            onClick={async () => {
                              try {
                                await api.removeParticipante(id, p.usuario_id);
                                loadCaso();
                              } catch (err) {
      console.error(err);
    }
                            }}
                            style={{ fontSize: '11px' }}
                          >
                            Remover
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

          </div>
        </div>

      </div>
    </div>
  );
}
