import { useState } from 'react';
import api from '../../api/client';

export default function ObservacionForm({ casoId, personas, onSaved }) {
  const [saving, setSaving] = useState(false);
  const [data, setData] = useState({
    persona_familiar_id: '',
    postura: '',
    tono_voz: '',
    expresion_emocional: [],
    estado_fisico: [],
    nivel_resistencia: '',
    interpretacion_sugerida: ''
  });

  const emociones = ['Entusiasmo', 'Tristeza', 'Enojo', 'Miedo', 'Plana (sin variaciones)', 'Ansiedad', 'Otra'];
  const estados = ['Ojeras', 'Signos de agotamiento', 'Llanto', 'Signos de lesiones visibles', 'Ninguno'];
  const resistencias = ['Colaborativo', 'Inhibido', 'Resistente', 'Hostil'];

  function handleCheck(field, value) {
    setData(prev => {
      const arr = prev[field] || [];
      if (arr.includes(value)) return { ...prev, [field]: arr.filter(v => v !== value) };
      return { ...prev, [field]: [...arr, value] };
    });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!data.persona_familiar_id) return alert('Seleccione una persona');
    
    setSaving(true);
    try {
      await api.createNnaObservacion(casoId, {
        ...data,
        persona_familiar_id: parseInt(data.persona_familiar_id)
      });
      alert('Observación registrada');
      setData({ ...data, postura: '', tono_voz: '', expresion_emocional: [], estado_fisico: [], interpretacion_sugerida: '' });
      if (onSaved) onSaved();
    } catch (err) {
      alert('Error al registrar observación');
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="form-group" style={{ padding: '24px', background: 'var(--bg)', borderRadius: '8px', border: '1px solid var(--border)' }}>
      <h3 style={{ marginBottom: '16px' }}>Nueva Observación</h3>
      
      <div style={{ padding: '12px', background: 'rgba(59, 130, 246, 0.1)', borderLeft: '4px solid var(--primary)', marginBottom: '24px', fontSize: '0.9rem' }}>
        <strong>Importante:</strong> La información obtenida por observación directa tiene el mismo peso que cualquier otra información ofrecida por la familia.
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div>
          <label>Persona Observada *</label>
          <select 
            value={data.persona_familiar_id} 
            onChange={e => setData({ ...data, persona_familiar_id: e.target.value })}
            required
          >
            <option value="">-- Seleccione --</option>
            {personas?.map(p => <option key={p.id} value={p.id}>{p.nombre} ({p.rol_en_familia || 'Sin rol'})</option>)}
          </select>
        </div>
        
        <div>
          <label>Nivel de Resistencia</label>
          <select value={data.nivel_resistencia} onChange={e => setData({ ...data, nivel_resistencia: e.target.value })}>
            <option value="">-- Seleccione --</option>
            {resistencias.map(r => <option key={r} value={r}>{r}</option>)}
          </select>
        </div>

        <div>
          <label>Postura Corporal</label>
          <select value={data.postura} onChange={e => setData({ ...data, postura: e.target.value })}>
            <option value="">-- Seleccione --</option>
            <option value="Erecta">Erecta</option>
            <option value="Encorvada hacia adelante">Encorvada hacia adelante</option>
            <option value="Encorvada hacia atrás">Encorvada hacia atrás</option>
            <option value="Tensa">Tensa</option>
            <option value="Relajada">Relajada</option>
          </select>
        </div>

        <div>
          <label>Tono de Voz</label>
          <select value={data.tono_voz} onChange={e => setData({ ...data, tono_voz: e.target.value })}>
            <option value="">-- Seleccione --</option>
            <option value="Firme">Firme</option>
            <option value="Débil">Débil</option>
            <option value="Tembloroso">Tembloroso</option>
            <option value="Agresivo">Agresivo</option>
            <option value="Plano">Plano</option>
          </select>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '16px' }}>
        <div>
          <label>Expresión Emocional</label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {emociones.map(emo => (
              <label key={emo} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'normal' }}>
                <input type="checkbox" checked={data.expresion_emocional.includes(emo)} onChange={() => handleCheck('expresion_emocional', emo)} />
                {emo}
              </label>
            ))}
          </div>
        </div>
        
        <div>
          <label>Estado Físico Visible</label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {estados.map(est => (
              <label key={est} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'normal' }}>
                <input type="checkbox" checked={data.estado_fisico.includes(est)} onChange={() => handleCheck('estado_fisico', est)} />
                {est}
              </label>
            ))}
          </div>
        </div>
      </div>

      <div style={{ marginTop: '16px' }}>
        <label>Interpretación Sugerida (No diagnóstico)</label>
        <textarea 
          rows="3" 
          value={data.interpretacion_sugerida} 
          onChange={e => setData({ ...data, interpretacion_sugerida: e.target.value })}
          placeholder="Ej: posible estado depresivo, requiere valoración especializada"
        ></textarea>
      </div>

      <button type="submit" className="btn btn-primary" style={{ marginTop: '16px' }} disabled={saving}>
        {saving ? 'Guardando...' : 'Registrar Observación'}
      </button>
    </form>
  );
}
