export default function DiaComunForm({ data, onChange }) {
  const safeData = data || {
    quien_despierta: '',
    rutina_matutina: '',
    cuidador_dia: '',
    relaciones_externas: '',
    nna_es_central: '',
    adulto_dificultad: '',
    personas_mencionadas: []
  };

  function updateField(field, value) {
    onChange({ ...safeData, [field]: value });
  }

  function addPersona(e) {
    if (e.key === 'Enter' && e.target.value.trim() !== '') {
      e.preventDefault();
      const current = safeData.personas_mencionadas || [];
      updateField('personas_mencionadas', [...current, e.target.value.trim()]);
      e.target.value = '';
    }
  }

  function removePersona(idx) {
    const current = [...(safeData.personas_mencionadas || [])];
    current.splice(idx, 1);
    updateField('personas_mencionadas', current);
  }

  return (
    <div className="form-group" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <h3>Técnica del Día Común</h3>
      <p style={{ color: 'var(--text-secondary)' }}>Relato guiado para entender la dinámica familiar cotidiana.</p>
      
      <div>
        <label>¿Quién se despierta primero en casa?</label>
        <input type="text" value={safeData.quien_despierta || ''} onChange={e => updateField('quien_despierta', e.target.value)} />
      </div>
      <div>
        <label>¿Cómo es la rutina matutina? (Desayuno, preparación para escuela/trabajo)</label>
        <textarea rows="3" value={safeData.rutina_matutina || ''} onChange={e => updateField('rutina_matutina', e.target.value)}></textarea>
      </div>
      <div>
        <label>¿Quién cuida a la NNA durante el día?</label>
        <input type="text" value={safeData.cuidador_dia || ''} onChange={e => updateField('cuidador_dia', e.target.value)} />
      </div>
      <div>
        <label>¿Con quién se relaciona la NNA fuera del hogar?</label>
        <textarea rows="2" value={safeData.relaciones_externas || ''} onChange={e => updateField('relaciones_externas', e.target.value)}></textarea>
      </div>

      <div style={{ padding: '16px', background: 'var(--bg)', borderRadius: '8px', border: '1px solid var(--border)' }}>
        <h4 style={{ marginBottom: '12px' }}>Análisis Automático (Indicadores)</h4>
        
        <div style={{ marginBottom: '16px' }}>
          <label style={{ display: 'block', marginBottom: '8px' }}>¿La NNA es central en la dinámica?</label>
          <div style={{ display: 'flex', gap: '16px' }}>
            {['si', 'no', 'indeterminado'].map(opt => (
              <label key={opt} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'normal' }}>
                <input 
                  type="radio" 
                  name="nna_es_central" 
                  checked={safeData.nna_es_central === opt}
                  onChange={() => updateField('nna_es_central', opt)} 
                />
                {opt.charAt(0).toUpperCase() + opt.slice(1)}
              </label>
            ))}
          </div>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '8px' }}>¿El adulto muestra dificultad emocional o física?</label>
          <div style={{ display: 'flex', gap: '16px' }}>
            {['si', 'no', 'indeterminado'].map(opt => (
              <label key={opt} style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: 'normal' }}>
                <input 
                  type="radio" 
                  name="adulto_dificultad" 
                  checked={safeData.adulto_dificultad === opt}
                  onChange={() => updateField('adulto_dificultad', opt)} 
                />
                {opt.charAt(0).toUpperCase() + opt.slice(1)}
              </label>
            ))}
          </div>
        </div>
      </div>

      <div style={{ borderTop: '1px solid var(--border)', paddingTop: '16px' }}>
        <label>Personas Mencionadas (Presione Enter para añadir)</label>
        <input type="text" placeholder="Ej. Tío Juan" onKeyDown={addPersona} />
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginTop: '12px' }}>
          {(safeData.personas_mencionadas || []).map((p, i) => (
            <span key={i} className="badge badge-rol" style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 12px' }}>
              {p}
              <button type="button" onClick={() => removePersona(i)} style={{ background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}>&times;</button>
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
