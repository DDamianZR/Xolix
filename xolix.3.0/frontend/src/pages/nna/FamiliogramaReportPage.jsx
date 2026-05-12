import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import api from '../../api/client';

const SIMBOLO_ICON = { normal: '👤', clave: '⭐', fallecido: '✝️', cuidador: '🛡️', agresor: '⚠️' };
const TIPO_REL = {
  biologica: '🔵 Biológica', legal: '🟣 Legal', emocional_positiva: '🟢 Emocional +',
  conflictiva: '🔴 Conflictiva', protectora: '🟩 Protectora',
  dependencia: '🟡 Dependencia', separacion: '⬜ Separación', desconocida: '⚪ Desconocida',
};

export default function FamiliogramaReportPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [datos, setDatos] = useState(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const printRef = useRef(null);

  useEffect(() => { loadData(); }, [id]);

  async function loadData() {
    try {
      const d = await api.exportarFamiliograma(id);
      setDatos(d);
    } catch { alert('Error al cargar el reporte'); }
    finally { setLoading(false); }
  }

  function handleExportJSON() {
    if (!datos) return;
    const blob = new Blob([JSON.stringify(datos, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `familiograma-caso-${id}.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  }

  function handlePrint() {
    window.print();
  }

  if (loading) return <div className="page-dashboard"><Topbar /><div className="container"><div className="status-msg">Cargando reporte...</div></div></div>;
  if (!datos) return null;

  const { caso, personas, relaciones } = datos;

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button className="btn btn-secondary" onClick={() => navigate(`/nna/casos/${id}`)}>← Volver</button>
            <h2 style={{ color: 'var(--text-primary)', fontSize: '20px', fontWeight: 700 }}>
              📄 Reporte del Familiograma
            </h2>
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button className="btn btn-secondary" onClick={handleExportJSON}>⬇ Exportar JSON</button>
            <button className="btn btn-primary" onClick={handlePrint}>🖨 Imprimir / PDF</button>
          </div>
        </div>

        <div ref={printRef}>
          {/* Encabezado del caso */}
          <div className="table-card" style={{ marginBottom: '20px' }}>
            <h3 style={{ marginBottom: '16px', color: 'var(--primary)' }}>ℹ️ Datos del Caso NNA</h3>
            <div className="detail-grid">
              <div className="detail-item"><label>Nombre del NNA</label><span>{caso.nna_nombre}</span></div>
              <div className="detail-item"><label>Edad</label><span>{caso.nna_edad || '—'} años</span></div>
              <div className="detail-item"><label>Género</label><span style={{ textTransform: 'capitalize' }}>{caso.nna_genero || '—'}</span></div>
              <div className="detail-item"><label>Estado del caso</label>
                <span className={`badge ${caso.estado === 'activo' ? 'badge-active' : 'badge-inactive'}`}>{caso.estado}</span>
              </div>
              <div className="detail-item"><label>Fecha de creación</label><span>{new Date(caso.fecha_creacion).toLocaleDateString('es-MX')}</span></div>
              <div className="detail-item"><label>Total de personas</label><span>{personas.length}</span></div>
              <div className="detail-item"><label>Total de relaciones</label><span>{relaciones.length}</span></div>
              <div className="detail-item"><label>Exportado el</label><span>{new Date(datos.exportado_en).toLocaleString('es-MX')}</span></div>
            </div>
          </div>

          {/* Tabla de personas */}
          <div className="table-card" style={{ marginBottom: '20px' }}>
            <h3 style={{ marginBottom: '16px', color: 'var(--primary)' }}>👥 Personas Familiares ({personas.length})</h3>
            {personas.length === 0 ? (
              <div className="status-msg">No hay personas registradas.</div>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead><tr>
                    <th>#</th><th>Tipo</th><th>Nombre</th><th>Edad</th><th>Género</th>
                    <th>Rol</th><th>Ocupación</th><th>Vive con NNA</th><th>Resp. Legal</th>
                  </tr></thead>
                  <tbody>
                    {personas.map((p, i) => (
                      <tr key={p.id}>
                        <td>{i + 1}</td>
                        <td>{SIMBOLO_ICON[p.tipo_simbolo] || '👤'}</td>
                        <td><strong>{p.nombre}</strong></td>
                        <td>{p.edad || '—'}</td>
                        <td style={{ textTransform: 'capitalize' }}>{p.genero || '—'}</td>
                        <td>{p.rol_en_familia || '—'}</td>
                        <td>{p.ocupacion || '—'}</td>
                        <td>{p.vive_con_nna ? '✅' : '—'}</td>
                        <td>{p.es_responsable_legal ? '✅' : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Tabla de relaciones */}
          <div className="table-card" style={{ marginBottom: '20px' }}>
            <h3 style={{ marginBottom: '16px', color: 'var(--primary)' }}>🔗 Relaciones Familiares ({relaciones.length})</h3>
            {relaciones.length === 0 ? (
              <div className="status-msg">No hay relaciones definidas.</div>
            ) : (
              <div className="table-wrap">
                <table>
                  <thead><tr><th>#</th><th>Persona A</th><th>Tipo</th><th>Persona B</th><th>Dirección</th><th>Descripción</th></tr></thead>
                  <tbody>
                    {relaciones.map((r, i) => (
                      <tr key={r.id}>
                        <td>{i + 1}</td>
                        <td><strong>{r.persona_origen}</strong></td>
                        <td>{TIPO_REL[r.tipo_relacion] || r.tipo_relacion}</td>
                        <td><strong>{r.persona_destino}</strong></td>
                        <td>{r.bidireccional ? '↔ Bidireccional' : '→ Unidireccional'}</td>
                        <td>{r.descripcion || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Notas sobre el grafo */}
          {datos.grafo_json && (
            <div className="table-card">
              <h3 style={{ marginBottom: '12px', color: 'var(--primary)' }}>📊 Estado del Grafo Visual</h3>
              <div style={{ display: 'flex', gap: '24px' }}>
                <div className="detail-item">
                  <label>Nodos en el canvas</label>
                  <span style={{ fontSize: '28px', fontWeight: 700, color: 'var(--primary)' }}>
                    {datos.grafo_json?.nodes?.length || 0}
                  </span>
                </div>
                <div className="detail-item">
                  <label>Conexiones visuales</label>
                  <span style={{ fontSize: '28px', fontWeight: 700, color: 'var(--primary)' }}>
                    {datos.grafo_json?.edges?.length || 0}
                  </span>
                </div>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '12px' }}>
                Para ver el familiograma interactivo, visita el <span
                  style={{ cursor: 'pointer', color: 'var(--primary)', textDecoration: 'underline' }}
                  onClick={() => navigate(`/nna/casos/${id}/familiograma`)}>Editor de Familiograma</span>.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
