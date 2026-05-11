export default function GradoNegacionSelector({ value, observaciones, onChangeValue, onChangeObservaciones }) {
  const grados = [
    { 
      nivel: 1, 
      titulo: 'Reconoce y Acepta Apoyo', 
      desc: 'Reconoce la situación problemática y está dispuesto/a a recibir ayuda para mejorar la dinámica familiar.' 
    },
    { 
      nivel: 2, 
      titulo: 'Niega pero no es Hostil', 
      desc: 'Minimiza o niega la situación, pero mantiene una actitud dialogante y no se muestra hostil ante la intervención.' 
    },
    { 
      nivel: 3, 
      titulo: 'Niega y/o Representa Riesgo', 
      desc: 'Negación absoluta, actitud hostil o defensiva que representa un riesgo inminente para la NNA.' 
    }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <h3>Grado de Negación Familiar</h3>
      <p style={{ color: 'var(--text-secondary)' }}>Evalúe el nivel de reconocimiento del problema por parte de la familia.</p>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {grados.map(g => {
          const isSelected = value === g.nivel;
          return (
            <div 
              key={g.nivel}
              onClick={() => onChangeValue(g.nivel)}
              style={{
                padding: '16px',
                border: `2px solid ${isSelected ? 'var(--primary)' : 'var(--border)'}`,
                borderRadius: '8px',
                background: isSelected ? 'var(--bg)' : 'var(--bg-card)',
                cursor: 'pointer',
                transition: 'all 0.2s'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                <div style={{ 
                  width: '24px', height: '24px', borderRadius: '50%', 
                  background: isSelected ? 'var(--primary)' : 'transparent',
                  border: `2px solid ${isSelected ? 'var(--primary)' : 'var(--border)'}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: '12px', fontWeight: 'bold'
                }}>
                  {isSelected && '✓'}
                </div>
                <strong style={{ fontSize: '1.1rem' }}>Nivel {g.nivel}: {g.titulo}</strong>
              </div>
              <p style={{ margin: '0 0 0 36px', color: 'var(--text-secondary)' }}>{g.desc}</p>
            </div>
          );
        })}
      </div>

      <div style={{ marginTop: '16px' }} className="form-group">
        <label>Observaciones de Negación</label>
        <textarea 
          rows="4" 
          value={observaciones || ''} 
          onChange={e => onChangeObservaciones(e.target.value)}
          placeholder="Escriba aquí los motivos o conductas que justifican el nivel seleccionado..."
        ></textarea>
      </div>
    </div>
  );
}
