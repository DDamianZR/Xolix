import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import api from '../../api/client';

const ESTADO_CONFIG = {
  activo: { label: 'Activo', color: '#4caf50', bg: '#e8f5e9' },
  cerrado: { label: 'Cerrado', color: '#757575', bg: '#f5f5f5' },
};

function StatCard({ icon, label, value, color, onClick }) {
  return (
    <div onClick={onClick} style={{
      background: 'var(--bg)', borderRadius: 'var(--radius)', padding: '20px 24px',
      boxShadow: 'var(--neo-shadow)', cursor: onClick ? 'pointer' : 'default',
      transition: 'transform 0.2s, box-shadow 0.2s', display: 'flex', alignItems: 'center', gap: '16px',
      flex: '1 1 200px', minWidth: '180px',
    }}
      onMouseEnter={e => onClick && (e.currentTarget.style.transform = 'translateY(-3px)')}
      onMouseLeave={e => onClick && (e.currentTarget.style.transform = '')}
    >
      <div style={{ fontSize: '32px' }}>{icon}</div>
      <div>
        <div style={{ fontSize: '28px', fontWeight: 800, color: color || 'var(--primary)' }}>{value}</div>
        <div style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 500 }}>{label}</div>
      </div>
    </div>
  );
}

function ModuleLink({ icon, label, desc, path, navigate }) {
  return (
    <div onClick={() => navigate(path)} style={{
      background: 'var(--bg)', borderRadius: 'var(--radius-sm)', padding: '16px 20px',
      boxShadow: 'var(--neo-shadow-sm)', cursor: 'pointer', transition: 'transform 0.2s',
      display: 'flex', gap: '14px', alignItems: 'center',
    }}
      onMouseEnter={e => e.currentTarget.style.transform = 'translateY(-2px)'}
      onMouseLeave={e => e.currentTarget.style.transform = ''}
    >
      <span style={{ fontSize: '24px' }}>{icon}</span>
      <div>
        <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{label}</div>
        <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>{desc}</div>
      </div>
      <span style={{ marginLeft: 'auto', color: 'var(--primary)', fontSize: '18px' }}>→</span>
    </div>
  );
}

export default function ResumenCasoNNAPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [caso, setCaso] = useState(null);
  const [personas, setPersonas] = useState([]);
  const [relaciones, setRelaciones] = useState([]);
  const [entrevista, setEntrevista] = useState(null);
  const [observaciones, setObservaciones] = useState([]);
  const [plan, setPlan] = useState(null);
  const [familiograma, setFamiliograma] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadAll(); }, [id]);

  async function loadAll() {
    try {
      const [c, p, r, e, obs, pl, f] = await Promise.all([
        api.getNnaCaso(id),
        api.getNnaPersonas(id),
        api.getNnaRelaciones(id),
        api.getNnaEntrevista(id).catch(() => null),
        api.getNnaObservaciones(id).catch(() => []),
        api.getNnaPlanAccion(id).catch(() => null),
        api.getNnaFamiliograma(id).catch(() => null),
      ]);
      setCaso(c); setPersonas(p); setRelaciones(r);
      setEntrevista(e); setObservaciones(obs || []); setPlan(pl); setFamiliograma(f);
    } catch { /* show partial data */ }
    finally { setLoading(false); }
  }

  if (loading) return <div className="page-dashboard"><Topbar /><div className="container"><div className="status-msg">Cargando resumen...</div></div></div>;
  if (!caso) return null;

  const estadoConf = ESTADO_CONFIG[caso.estado] || ESTADO_CONFIG.activo;
  const nodosFamiliogrma = familiograma?.grafo_json?.nodes?.length || 0;
  const nivelNegacion = entrevista?.grado_negacion;
  const negacionLabels = { 1: '🟢 Nivel 1 — Colaboración', 2: '🟡 Nivel 2 — Resistencia', 3: '🔴 Nivel 3 — Negación total' };

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button className="btn btn-secondary" onClick={() => navigate('/nna')}>← Dashboard NNA</button>
            <div>
              <h2 style={{ fontSize: '22px', fontWeight: 800, color: 'var(--text-primary)', margin: 0 }}>
                🛡️ {caso.nna_nombre}
              </h2>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginTop: '4px' }}>
                <span className="badge" style={{ background: estadoConf.bg, color: estadoConf.color }}>
                  {estadoConf.label}
                </span>
                {caso.nna_edad && <span style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{caso.nna_edad} años</span>}
                {caso.nna_genero && <span style={{ color: 'var(--text-secondary)', fontSize: '13px', textTransform: 'capitalize' }}>{caso.nna_genero}</span>}
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button className="btn btn-secondary" onClick={() => navigate(`/nna/casos/${id}`)}>Ver detalle completo</button>
            <button className="btn btn-secondary" onClick={() => navigate(`/nna/casos/${id}/reporte`)}>📄 Reporte</button>
          </div>
        </div>

        {/* Stats Cards */}
        <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', marginBottom: '20px' }}>
          <StatCard icon="👨‍👩‍👧" label="Personas familiares" value={personas.length}
            onClick={() => navigate(`/nna/casos/${id}/personas`)} />
          <StatCard icon="🔗" label="Relaciones definidas" value={relaciones.length}
            onClick={() => navigate(`/nna/casos/${id}/relaciones`)} />
          <StatCard icon="🗺️" label="Nodos en familiograma" value={nodosFamiliogrma}
            onClick={() => navigate(`/nna/casos/${id}/familiograma`)} />
          <StatCard icon="👁️" label="Observaciones" value={observaciones.length} color="#1976d2"
            onClick={() => navigate(`/nna/casos/${id}/observaciones`)} />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', alignItems: 'start' }}>
          {/* Entrevista */}
          <div className="table-card">
            <h3 style={{ marginBottom: '14px', color: 'var(--primary)' }}>📝 Entrevista Familiar</h3>
            {!entrevista ? (
              <div>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '12px' }}>No se ha realizado la entrevista aún.</p>
                <button className="btn btn-primary" onClick={() => navigate(`/nna/casos/${id}/entrevista`)}>Iniciar entrevista</button>
              </div>
            ) : (
              <div>
                <div className="detail-grid" style={{ gridTemplateColumns: '1fr', gap: '10px' }}>
                  <div className="detail-item">
                    <label>Estado</label>
                    <span className={`badge ${entrevista.completada ? 'badge-active' : 'badge-inactive'}`}>
                      {entrevista.completada ? '✅ Completada' : '⏳ En progreso'}
                    </span>
                  </div>
                  {nivelNegacion && (
                    <div className="detail-item">
                      <label>Grado de negación</label>
                      <span>{negacionLabels[nivelNegacion] || `Nivel ${nivelNegacion}`}</span>
                    </div>
                  )}
                  {entrevista.frases_comunicadas && (
                    <div className="detail-item">
                      <label>Frases comunicadas</label>
                      <span>{entrevista.frases_comunicadas.filter(f => f.comunicada).length} / {entrevista.frases_comunicadas.length}</span>
                    </div>
                  )}
                </div>
                <button className="btn btn-secondary" style={{ marginTop: '12px', padding: '8px 16px', fontSize: '13px' }}
                  onClick={() => navigate(`/nna/casos/${id}/entrevista`)}>Ver entrevista</button>
              </div>
            )}
          </div>

          {/* Plan de Acción */}
          <div className="table-card">
            <h3 style={{ marginBottom: '14px', color: 'var(--primary)' }}>📋 Plan de Acción</h3>
            {!plan ? (
              <div>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '12px' }}>
                  {entrevista ? 'El plan puede generarse automáticamente.' : 'Completa la entrevista primero.'}
                </p>
                <button className="btn btn-primary" disabled={!entrevista}
                  onClick={() => navigate(`/nna/casos/${id}/plan`)}>
                  {entrevista ? 'Generar plan' : 'Sin entrevista'}
                </button>
              </div>
            ) : (
              <div>
                <div className="detail-item" style={{ marginBottom: '10px' }}>
                  <label>Proceso vinculado</label>
                  <span style={{ fontWeight: 600 }}>{plan.titulo}</span>
                </div>
                <div className="detail-item" style={{ marginBottom: '10px' }}>
                  <label>Estado</label>
                  <span className="badge badge-rol" style={{ textTransform: 'capitalize' }}>{plan.estado}</span>
                </div>
                <div className="detail-item" style={{ marginBottom: '12px' }}>
                  <label>Progreso</label>
                  <div className="progress-bar" style={{ marginTop: '4px' }}>
                    <div className="progress-fill" style={{ width: `${plan.progreso || 0}%` }} />
                  </div>
                  <span className="progress-text">{Math.round(plan.progreso || 0)}%</span>
                </div>
                <button className="btn btn-secondary" style={{ padding: '8px 16px', fontSize: '13px' }}
                  onClick={() => navigate(`/nna/casos/${id}/plan`)}>Ver plan completo</button>
              </div>
            )}
          </div>

          {/* Observaciones recientes */}
          <div className="table-card">
            <h3 style={{ marginBottom: '14px', color: 'var(--primary)' }}>👁️ Observaciones recientes</h3>
            {observaciones.length === 0 ? (
              <p style={{ color: 'var(--text-secondary)' }}>No hay observaciones registradas.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {observaciones.slice(0, 3).map(obs => (
                  <div key={obs.id} style={{ padding: '10px', background: 'var(--bg-dark, #f0f4fd)', borderRadius: 'var(--radius-sm)', fontSize: '13px' }}>
                    <strong>{obs.persona_nombre}</strong>
                    {obs.postura && <span style={{ color: 'var(--text-secondary)' }}> · {obs.postura}</span>}
                  </div>
                ))}
                {observaciones.length > 3 && (
                  <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>+{observaciones.length - 3} más...</span>
                )}
              </div>
            )}
            <button className="btn btn-secondary" style={{ marginTop: '12px', padding: '8px 16px', fontSize: '13px' }}
              onClick={() => navigate(`/nna/casos/${id}/observaciones`)}>Ver todas</button>
          </div>

          {/* Accesos rápidos */}
          <div className="table-card">
            <h3 style={{ marginBottom: '14px', color: 'var(--primary)' }}>⚡ Accesos rápidos</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <ModuleLink icon="👨‍👩‍👧" label="Personas familiares" desc="Gestionar miembros del núcleo familiar" path={`/nna/casos/${id}/personas`} navigate={navigate} />
              <ModuleLink icon="🔗" label="Relaciones" desc="Definir vínculos entre personas" path={`/nna/casos/${id}/relaciones`} navigate={navigate} />
              <ModuleLink icon="🗺️" label="Editor de familiograma" desc="Canvas interactivo del grafo familiar" path={`/nna/casos/${id}/familiograma`} navigate={navigate} />
              <ModuleLink icon="🕘" label="Historial de versiones" desc="Versiones anteriores del familiograma" path={`/nna/casos/${id}/historial-familiograma`} navigate={navigate} />
              <ModuleLink icon="📄" label="Reporte completo" desc="Exportar datos del caso" path={`/nna/casos/${id}/reporte`} navigate={navigate} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
