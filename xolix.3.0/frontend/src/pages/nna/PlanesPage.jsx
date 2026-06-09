import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../api/client';

const ESTADO_COLOR = { borrador: '#F8F9FA', activo: '#D5F5E3', pausado: '#FEF9E7', completado: '#D6EAF8', cancelado: '#FADBD8' };
const TIPO_MEDIDA = ['psicologica', 'legal', 'medica', 'educativa', 'social', 'economica', 'otra'];

export default function PlanesPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [planes, setPlanes] = useState([]);
  const [derechos, setDerechos] = useState([]);
  const [planSeleccionado, setPlanSeleccionado] = useState(null);
  const [mostrarFormPlan, setMostrarFormPlan] = useState(false);
  const [formPlan, setFormPlan] = useState({ objetivo: '', fecha_inicio: '', fecha_termino: '', observaciones: '', medidas: [] });
  const [formSeguimiento, setFormSeguimiento] = useState({ medida_id: null, fecha_seguimiento: '', descripcion_avance: '', porcentaje_cumplimiento: 0 });
  const [saving, setSaving] = useState(false);

  const cargar = async () => {
    const [planesRes, derechosRes] = await Promise.all([
      api.get(`/planes/caso/${id}`),
      api.get('/catalogo/derechos'),
    ]);
    setPlanes(planesRes.data);
    setDerechos(derechosRes.data);
  };

  useEffect(() => { cargar(); }, [id]);

  const addMedida = () => setFormPlan(f => ({ ...f, medidas: [...f.medidas, { tipo: 'otra', descripcion: '', recursos_requeridos: '' }] }));

  const handleCrearPlan = async e => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.post('/planes/', { ...formPlan, caso_nna_id: parseInt(id) });
      setMostrarFormPlan(false);
      setFormPlan({ objetivo: '', fecha_inicio: '', fecha_termino: '', observaciones: '', medidas: [] });
      await cargar();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error al crear plan');
    } finally {
      setSaving(false);
    }
  };

  const handleSeguimiento = async e => {
    e.preventDefault();
    setSaving(true);
    try {
      await api.post(`/planes/medidas/${formSeguimiento.medida_id}/seguimientos`, formSeguimiento);
      setFormSeguimiento({ medida_id: null, fecha_seguimiento: '', descripcion_avance: '', porcentaje_cumplimiento: 0 });
      const plan = await api.get(`/planes/${planSeleccionado.id}`);
      setPlanSeleccionado(plan.data);
      await cargar();
    } catch (err) {
      alert(err.response?.data?.detail || 'Error al registrar seguimiento');
    } finally {
      setSaving(false);
    }
  };

  const cambiarEstado = async (planId, estado) => {
    await api.put(`/planes/${planId}`, { estado });
    await cargar();
    if (planSeleccionado?.id === planId) {
      const p = await api.get(`/planes/${planId}`);
      setPlanSeleccionado(p.data);
    }
  };

  const inputStyle = { width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #ccc', fontSize: 14, boxSizing: 'border-box' };

  return (
    <div style={{ padding: 24, maxWidth: 1000, margin: '0 auto' }}>
      <button onClick={() => navigate(`/nna/casos/${id}/resumen`)} style={{ background: 'none', border: 'none', color: '#6C3483', cursor: 'pointer', fontSize: 14, marginBottom: 16 }}>
        ← Volver al resumen
      </button>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2 style={{ margin: 0 }}>Planes de Restitución</h2>
        <button onClick={() => setMostrarFormPlan(!mostrarFormPlan)} style={{ background: '#6C3483', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 18px', cursor: 'pointer' }}>
          {mostrarFormPlan ? 'Cancelar' : '+ Nuevo Plan'}
        </button>
      </div>

      {mostrarFormPlan && (
        <form onSubmit={handleCrearPlan} style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.08)', marginBottom: 24 }}>
          <h3 style={{ marginTop: 0, color: '#6C3483' }}>Nuevo Plan de Restitución</h3>
          <div style={{ marginBottom: 14 }}>
            <label style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 4 }}>Objetivo *</label>
            <textarea required style={{ ...inputStyle, minHeight: 70, resize: 'vertical' }} value={formPlan.objetivo} onChange={e => setFormPlan(f => ({ ...f, objetivo: e.target.value }))} />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 14 }}>
            <div>
              <label style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 4 }}>Fecha inicio</label>
              <input type="date" style={inputStyle} value={formPlan.fecha_inicio} onChange={e => setFormPlan(f => ({ ...f, fecha_inicio: e.target.value }))} />
            </div>
            <div>
              <label style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 4 }}>Fecha término</label>
              <input type="date" style={inputStyle} value={formPlan.fecha_termino} onChange={e => setFormPlan(f => ({ ...f, fecha_termino: e.target.value }))} />
            </div>
          </div>
          <div style={{ marginBottom: 14 }}>
            <label style={{ fontSize: 12, color: '#888', display: 'block', marginBottom: 4 }}>Observaciones</label>
            <textarea style={{ ...inputStyle, minHeight: 50, resize: 'vertical' }} value={formPlan.observaciones} onChange={e => setFormPlan(f => ({ ...f, observaciones: e.target.value }))} />
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
            <strong style={{ fontSize: 14 }}>Medidas ({formPlan.medidas.length})</strong>
            <button type="button" onClick={addMedida} style={{ background: '#EBF5FB', border: 'none', borderRadius: 6, padding: '5px 12px', cursor: 'pointer', fontSize: 13 }}>+ Agregar medida</button>
          </div>
          {formPlan.medidas.map((m, i) => (
            <div key={i} style={{ padding: 12, background: '#F9F9F9', borderRadius: 8, marginBottom: 10 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 10, marginBottom: 8 }}>
                <select style={inputStyle} value={m.tipo} onChange={e => { const arr = [...formPlan.medidas]; arr[i].tipo = e.target.value; setFormPlan(f => ({ ...f, medidas: arr })); }}>
                  {TIPO_MEDIDA.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
                </select>
                <div style={{ display: 'flex', gap: 6 }}>
                  <textarea placeholder="Descripción de la medida *" style={{ ...inputStyle, flex: 1, minHeight: 36, resize: 'none' }} value={m.descripcion} onChange={e => { const arr = [...formPlan.medidas]; arr[i].descripcion = e.target.value; setFormPlan(f => ({ ...f, medidas: arr })); }} />
                  <button type="button" onClick={() => setFormPlan(f => ({ ...f, medidas: f.medidas.filter((_,j) => j!==i) }))} style={{ background: '#FADBD8', border: 'none', borderRadius: 6, padding: '0 8px', cursor: 'pointer' }}>✕</button>
                </div>
              </div>
            </div>
          ))}

          <button type="submit" disabled={saving} style={{ background: '#6C3483', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 24px', cursor: 'pointer', marginTop: 8 }}>
            {saving ? 'Guardando...' : 'Crear Plan'}
          </button>
        </form>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: planSeleccionado ? '1fr 2fr' : '1fr', gap: 20 }}>
        <div>
          {planes.length === 0 ? (
            <p style={{ color: '#999' }}>No hay planes creados.</p>
          ) : (
            planes.map(p => (
              <div
                key={p.id}
                onClick={() => setPlanSeleccionado(p.id === planSeleccionado?.id ? null : p)}
                style={{ background: p.id === planSeleccionado?.id ? '#F5EEF8' : '#fff', borderRadius: 10, padding: 16, boxShadow: '0 1px 6px rgba(0,0,0,0.06)', marginBottom: 12, cursor: 'pointer', border: p.id === planSeleccionado?.id ? '2px solid #6C3483' : '2px solid transparent' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <span style={{ background: ESTADO_COLOR[p.estado] || '#eee', borderRadius: 10, padding: '2px 10px', fontSize: 12 }}>{p.estado}</span>
                  <span style={{ fontSize: 12, color: '#888' }}>{p.fecha_inicio ? `${p.fecha_inicio} → ${p.fecha_termino || '...'}` : ''}</span>
                </div>
                <p style={{ margin: '8px 0 4px', fontSize: 14 }}>{p.objetivo}</p>
                <p style={{ margin: 0, fontSize: 12, color: '#888' }}>{p.medidas?.length || 0} medidas</p>
              </div>
            ))
          )}
        </div>

        {planSeleccionado && (
          <div style={{ background: '#fff', borderRadius: 12, padding: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <h3 style={{ margin: 0, color: '#6C3483' }}>Medidas del Plan</h3>
              <div style={{ display: 'flex', gap: 8 }}>
                {['activo', 'completado', 'cancelado'].map(est => (
                  <button key={est} onClick={() => cambiarEstado(planSeleccionado.id, est)}
                    style={{ fontSize: 11, padding: '4px 10px', borderRadius: 6, border: '1px solid #6C3483', background: planSeleccionado.estado === est ? '#6C3483' : '#fff', color: planSeleccionado.estado === est ? '#fff' : '#6C3483', cursor: 'pointer' }}>
                    {est.charAt(0).toUpperCase() + est.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {planSeleccionado.medidas?.map(m => (
              <div key={m.id} style={{ padding: 14, background: '#F9F9F9', borderRadius: 8, marginBottom: 12 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                  <strong style={{ fontSize: 14 }}>{m.tipo.charAt(0).toUpperCase() + m.tipo.slice(1)}</strong>
                  <span style={{ fontSize: 12, color: '#6C3483' }}>{m.porcentaje_avance}% completado</span>
                </div>
                <p style={{ margin: '0 0 8px', fontSize: 13 }}>{m.descripcion}</p>

                <div style={{ background: '#E8E8E8', borderRadius: 20, height: 6, marginBottom: 10 }}>
                  <div style={{ background: '#6C3483', borderRadius: 20, height: 6, width: `${m.porcentaje_avance}%` }} />
                </div>

                {formSeguimiento.medida_id === m.id ? (
                  <form onSubmit={handleSeguimiento} style={{ background: '#EEF', borderRadius: 8, padding: 12 }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 8 }}>
                      <input required type="date" style={inputStyle} value={formSeguimiento.fecha_seguimiento} onChange={e => setFormSeguimiento(f => ({ ...f, fecha_seguimiento: e.target.value }))} />
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontSize: 12 }}>%</span>
                        <input type="number" min={0} max={100} style={inputStyle} value={formSeguimiento.porcentaje_cumplimiento} onChange={e => setFormSeguimiento(f => ({ ...f, porcentaje_cumplimiento: parseInt(e.target.value) }))} />
                      </div>
                    </div>
                    <textarea required placeholder="Descripción del avance..." style={{ ...inputStyle, minHeight: 50, resize: 'vertical', marginBottom: 8 }} value={formSeguimiento.descripcion_avance} onChange={e => setFormSeguimiento(f => ({ ...f, descripcion_avance: e.target.value }))} />
                    <div style={{ display: 'flex', gap: 8 }}>
                      <button type="submit" disabled={saving} style={{ background: '#6C3483', color: '#fff', border: 'none', borderRadius: 6, padding: '6px 14px', cursor: 'pointer', fontSize: 13 }}>
                        {saving ? 'Guardando...' : 'Guardar'}
                      </button>
                      <button type="button" onClick={() => setFormSeguimiento({ medida_id: null, fecha_seguimiento: '', descripcion_avance: '', porcentaje_cumplimiento: 0 })} style={{ background: '#eee', border: 'none', borderRadius: 6, padding: '6px 12px', cursor: 'pointer', fontSize: 13 }}>
                        Cancelar
                      </button>
                    </div>
                  </form>
                ) : (
                  <button onClick={() => setFormSeguimiento({ medida_id: m.id, fecha_seguimiento: new Date().toISOString().slice(0,10), descripcion_avance: '', porcentaje_cumplimiento: m.porcentaje_avance })}
                    style={{ background: '#EBF5FB', border: 'none', borderRadius: 6, padding: '5px 12px', cursor: 'pointer', fontSize: 12 }}>
                    + Registrar seguimiento
                  </button>
                )}

                {m.seguimientos?.length > 0 && (
                  <div style={{ marginTop: 10, borderTop: '1px solid #eee', paddingTop: 8 }}>
                    {m.seguimientos.slice().reverse().map(s => (
                      <div key={s.id} style={{ fontSize: 12, color: '#555', marginBottom: 4 }}>
                        <strong>{s.fecha_seguimiento}</strong> — {s.descripcion_avance} ({s.porcentaje_cumplimiento}%)
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
