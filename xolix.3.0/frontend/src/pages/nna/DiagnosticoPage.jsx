import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../api/client';

const TIPOS_DIAG = [
  { value: 'inicial', label: 'Diagnóstico Inicial' },
  { value: 'nna', label: 'Diagnóstico del NNA' },
  { value: 'tutor', label: 'Diagnóstico del Tutor' },
  { value: 'entorno', label: 'Diagnóstico del Entorno' },
];

export default function DiagnosticoPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [diagnosticos, setDiagnosticos] = useState([]);
  const [derechos, setDerechos] = useState([]);
  const [indicadores, setIndicadores] = useState([]);
  const [resumenDerechos, setResumenDerechos] = useState([]);
  const [mostrarForm, setMostrarForm] = useState(false);
  const [form, setForm] = useState({ tipo: 'inicial', fecha: new Date().toISOString().slice(0,10), observaciones: '', indicadores: [] });
  const [saving, setSaving] = useState(false);

  const cargar = async () => {
    const [diagRes, resumenRes] = await Promise.all([
      api.get(`/diagnosticos/caso/${id}`),
      api.get(`/diagnosticos/caso/${id}/resumen-derechos`),
    ]);
    setDiagnosticos(diagRes.data);
    setResumenDerechos(resumenRes.data);
  };

  useEffect(() => {
    cargar();
    api.get('/catalogo/derechos').then(r => setDerechos(r.data));
    api.get('/catalogo/indicadores').then(r => setIndicadores(r.data));
  }, [id]);

  const toggleIndicador = (ind_id) => {
    setForm(f => {
      const exists = f.indicadores.find(i => i.indicador_id === ind_id);
      if (exists) {
        return { ...f, indicadores: f.indicadores.filter(i => i.indicador_id !== ind_id) };
      }
      return { ...f, indicadores: [...f.indicadores, { indicador_id: ind_id, valor: 'si', vulnerado: false }] };
    });
  };

  const setVulnerado = (ind_id, val) => {
    setForm(f => ({
      ...f,
      indicadores: f.indicadores.map(i => i.indicador_id === ind_id ? { ...i, vulnerado: val } : i),
    }));
  };

  const handleSubmit = async e => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.post('/diagnosticos/', { ...form, caso_nna_id: parseInt(id) });
      setMostrarForm(false);
      setForm({ tipo: 'inicial', fecha: new Date().toISOString().slice(0,10), observaciones: '', indicadores: [] });
      await cargar();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error al guardar');
    } finally {
      setSaving(false);
    }
  };

  const severidadColor = { leve: '#D5F5E3', moderada: '#FEF9E7', grave: '#FDEBD0', critica: '#FADBD8' };

  return (
    <div style={{ padding: 24, maxWidth: 950, margin: '0 auto' }}>
      <button onClick={() => navigate(`/nna/casos/${id}/resumen`)} style={{ background: 'none', border: 'none', color: '#6C3483', cursor: 'pointer', fontSize: 14, marginBottom: 16 }}>
        ← Volver al resumen
      </button>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2 style={{ margin: 0 }}>Módulo de Diagnóstico</h2>
        <button onClick={() => setMostrarForm(!mostrarForm)} style={{ background: '#6C3483', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 18px', cursor: 'pointer' }}>
          {mostrarForm ? 'Cancelar' : '+ Nuevo Diagnóstico'}
        </button>
      </div>

      {mostrarForm && (
        <form onSubmit={handleSubmit} style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.08)', marginBottom: 24 }}>
          <h3 style={{ marginTop: 0, color: '#6C3483' }}>Captura de Diagnóstico</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 16 }}>
            <div>
              <label style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 4 }}>Tipo *</label>
              <select required style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #ccc' }} value={form.tipo} onChange={e => setForm(f => ({ ...f, tipo: e.target.value }))}>
                {TIPOS_DIAG.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
              </select>
            </div>
            <div>
              <label style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 4 }}>Fecha *</label>
              <input required type="date" style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #ccc', boxSizing: 'border-box' }} value={form.fecha} onChange={e => setForm(f => ({ ...f, fecha: e.target.value }))} />
            </div>
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 4 }}>Observaciones</label>
            <textarea style={{ width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #ccc', minHeight: 60, boxSizing: 'border-box', resize: 'vertical' }} value={form.observaciones} onChange={e => setForm(f => ({ ...f, observaciones: e.target.value }))} />
          </div>

          <h4 style={{ color: '#6C3483' }}>Indicadores evaluados</h4>
          {derechos.map(d => (
            <div key={d.id} style={{ marginBottom: 16 }}>
              <p style={{ fontWeight: 600, margin: '0 0 8px', fontSize: 14 }}>{d.nombre}</p>
              {indicadores.filter(i => i.derecho_id === d.id).map(ind => {
                const seleccionado = form.indicadores.find(i => i.indicador_id === ind.id);
                return (
                  <div key={ind.id} style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 6, padding: '6px 10px', background: seleccionado ? '#F5EEF8' : '#fafafa', borderRadius: 6 }}>
                    <input type="checkbox" checked={!!seleccionado} onChange={() => toggleIndicador(ind.id)} />
                    <span style={{ flex: 1, fontSize: 13 }}>{ind.nombre}</span>
                    {seleccionado && (
                      <label style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, color: '#c0392b' }}>
                        <input type="checkbox" checked={seleccionado.vulnerado} onChange={e => setVulnerado(ind.id, e.target.checked)} />
                        Vulnerado
                      </label>
                    )}
                  </div>
                );
              })}
            </div>
          ))}

          <button type="submit" disabled={saving} style={{ background: '#6C3483', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 24px', cursor: 'pointer', marginTop: 8 }}>
            {saving ? 'Guardando...' : 'Guardar Diagnóstico'}
          </button>
        </form>
      )}

      {resumenDerechos.length > 0 && (
        <div style={{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.07)', marginBottom: 24 }}>
          <h3 style={{ marginTop: 0, color: '#6C3483' }}>Resumen de Derechos Vulnerados</h3>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
            {resumenDerechos.map(dv => (
              <div key={dv.derecho_id} style={{ background: '#F5EEF8', borderRadius: 10, padding: '8px 16px', textAlign: 'center', minWidth: 140 }}>
                <p style={{ margin: 0, fontWeight: 700, fontSize: 22, color: '#6C3483' }}>{dv.cantidad_ocurrencias}</p>
                <p style={{ margin: 0, fontSize: 12 }}>{dv.nombre}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <h3 style={{ color: '#6C3483' }}>Historial de Diagnósticos</h3>
        {diagnosticos.length === 0 ? (
          <p style={{ color: '#999' }}>No hay diagnósticos registrados.</p>
        ) : (
          diagnosticos.map(d => (
            <div key={d.id} style={{ background: '#fff', borderRadius: 10, padding: 18, boxShadow: '0 1px 6px rgba(0,0,0,0.06)', marginBottom: 14 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8 }}>
                <strong style={{ color: '#6C3483' }}>{TIPOS_DIAG.find(t => t.value === d.tipo)?.label || d.tipo}</strong>
                <span style={{ fontSize: 13, color: '#888' }}>{d.fecha}</span>
              </div>
              {d.observaciones && <p style={{ margin: '0 0 8px', fontSize: 13, color: '#555' }}>{d.observaciones}</p>}
              {d.derechos_vulnerados?.length > 0 && (
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginTop: 8 }}>
                  {d.derechos_vulnerados.map(dv => (
                    <span key={dv.id} style={{ background: severidadColor[dv.severidad] || '#eee', borderRadius: 10, padding: '2px 10px', fontSize: 12 }}>
                      {dv.derecho_id} — {dv.severidad}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
