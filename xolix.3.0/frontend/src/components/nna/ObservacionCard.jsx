export default function ObservacionCard({ obs }) {
  return (
    <div style={{ padding: '16px', background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: '8px', marginBottom: '16px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
        <h4 style={{ margin: 0 }}>{obs.persona_nombre}</h4>
        <span className="badge" style={{ background: 'var(--bg)', color: 'var(--text-secondary)' }}>
          {new Date(obs.fecha_creacion).toLocaleDateString()}
        </span>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', fontSize: '0.9rem', marginBottom: '12px' }}>
        <div>
          <strong>Resistencia:</strong> {obs.nivel_resistencia || 'No registrado'}
        </div>
        <div>
          <strong>Postura:</strong> {obs.postura || 'No registrado'}
        </div>
        <div>
          <strong>Tono de Voz:</strong> {obs.tono_voz || 'No registrado'}
        </div>
        <div>
          <strong>Emociones:</strong> {obs.expresion_emocional?.length > 0 ? obs.expresion_emocional.join(', ') : 'No registrado'}
        </div>
        <div style={{ gridColumn: '1 / -1' }}>
          <strong>Estado Físico:</strong> {obs.estado_fisico?.length > 0 ? obs.estado_fisico.join(', ') : 'No registrado'}
        </div>
      </div>
      
      {obs.interpretacion_sugerida && (
        <div style={{ padding: '12px', background: 'var(--bg)', borderRadius: '4px', borderLeft: '3px solid var(--primary)', fontSize: '0.9rem' }}>
          <strong>Interpretación Sugerida:</strong> {obs.interpretacion_sugerida}
        </div>
      )}
    </div>
  );
}
