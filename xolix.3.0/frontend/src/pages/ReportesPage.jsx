import { useState, useEffect } from 'react';
import api from '../api/client';

export default function ReportesPage() {
  const [indicadores, setIndicadores] = useState(null);
  const [derechosFreq, setDerechosFreq] = useState([]);
  const [evolucion, setEvolucion] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/reportes/indicadores'),
      api.get('/reportes/derechos-vulnerados'),
      api.get('/reportes/evolucion-casos'),
    ]).then(([indRes, dvRes, evRes]) => {
      setIndicadores(indRes.data);
      setDerechosFreq(dvRes.data);
      setEvolucion(evRes.data);
      setLoading(false);
    });
  }, []);

  const descargarPDF = () => { window.open('/api/reportes/exportar/casos/pdf', '_blank'); };
  const descargarExcelCasos = () => { window.open('/api/reportes/exportar/casos/excel', '_blank'); };
  const descargarExcelActores = () => { window.open('/api/reportes/exportar/actores/excel', '_blank'); };

  if (loading) return <p style={{ padding: 24 }}>Cargando reportes...</p>;

  const maxFreq = derechosFreq.length > 0 ? Math.max(...derechosFreq.map(d => d.frecuencia)) : 1;

  const MESES = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'];

  return (
    <div style={{ padding: 24, maxWidth: 1100, margin: '0 auto' }}>
      <h2 style={{ marginBottom: 24 }}>Reportes e Indicadores</h2>

      {/* Tarjetas principales */}
      {indicadores && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 16, marginBottom: 32 }}>
          {[
            ['Total Casos', indicadores.total_casos, '#6C3483'],
            ['Casos Activos', indicadores.casos_activos, '#1E8449'],
            ['Casos Cerrados', indicadores.casos_cerrados, '#117A65'],
            ['Actores', indicadores.total_actores, '#1A5276'],
            ['Diagnósticos', indicadores.total_diagnosticos, '#784212'],
          ].map(([label, val, color]) => (
            <div key={label} style={{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.07)', borderTop: `4px solid ${color}` }}>
              <p style={{ margin: 0, fontSize: 32, fontWeight: 800, color }}>{val}</p>
              <p style={{ margin: '4px 0 0', fontSize: 13, color: '#888' }}>{label}</p>
            </div>
          ))}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24, marginBottom: 32 }}>
        {/* Derechos vulnerados */}
        <div style={{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.07)' }}>
          <h3 style={{ marginTop: 0, color: '#6C3483' }}>Derechos más vulnerados</h3>
          {derechosFreq.length === 0 ? (
            <p style={{ color: '#999', fontSize: 14 }}>Sin datos aún.</p>
          ) : (
            derechosFreq.slice(0, 8).map(d => (
              <div key={d.derecho_id} style={{ marginBottom: 10 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 3 }}>
                  <span style={{ color: '#333' }}>{d.nombre}</span>
                  <span style={{ color: '#6C3483', fontWeight: 700 }}>{d.frecuencia}</span>
                </div>
                <div style={{ background: '#E8D5F7', borderRadius: 20, height: 8 }}>
                  <div style={{ background: '#6C3483', borderRadius: 20, height: 8, width: `${(d.frecuencia / maxFreq) * 100}%` }} />
                </div>
              </div>
            ))
          )}
        </div>

        {/* Evolución mensual */}
        <div style={{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.07)' }}>
          <h3 style={{ marginTop: 0, color: '#1A5276' }}>Casos nuevos por mes</h3>
          {evolucion.length === 0 ? (
            <p style={{ color: '#999', fontSize: 14 }}>Sin datos aún.</p>
          ) : (
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 6, height: 140 }}>
              {evolucion.map(e => {
                const maxCant = Math.max(...evolucion.map(x => x.cantidad), 1);
                const h = Math.max((e.cantidad / maxCant) * 120, 4);
                return (
                  <div key={`${e.anio}-${e.mes}`} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', flex: 1 }}>
                    <span style={{ fontSize: 11, color: '#555', marginBottom: 4 }}>{e.cantidad}</span>
                    <div style={{ background: '#1A5276', borderRadius: '4px 4px 0 0', width: '100%', height: h }} />
                    <span style={{ fontSize: 10, color: '#888', marginTop: 3 }}>{MESES[e.mes - 1]}</span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Exportaciones */}
      <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.07)' }}>
        <h3 style={{ marginTop: 0 }}>Exportar datos</h3>
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          <button onClick={descargarPDF} style={{ background: '#E74C3C', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 20px', cursor: 'pointer', fontSize: 14 }}>
            📄 PDF — Casos NNA
          </button>
          <button onClick={descargarExcelCasos} style={{ background: '#1E8449', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 20px', cursor: 'pointer', fontSize: 14 }}>
            📊 Excel — Casos NNA
          </button>
          <button onClick={descargarExcelActores} style={{ background: '#1A5276', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 20px', cursor: 'pointer', fontSize: 14 }}>
            📊 Excel — Actores
          </button>
        </div>
      </div>
    </div>
  );
}
