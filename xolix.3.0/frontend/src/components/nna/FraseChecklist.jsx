export default function FraseChecklist({ frases, onChange }) {
  const defaultFrases = [
    { id: '1', texto: 'No estamos aquí para regañar, sino para buscar soluciones juntos.', comunicada: false, notas: '' },
    { id: '2', texto: 'Lo mejor para la NNA es estar con su familia, siempre que sea seguro.', comunicada: false, notas: '' },
    { id: '3', texto: 'Nuestra prioridad es el bienestar y los derechos de la NNA.', comunicada: false, notas: '' },
    { id: '4', texto: 'La información compartida aquí es confidencial pero actuaremos si hay riesgo.', comunicada: false, notas: '' },
  ];

  const currentFrases = frases && frases.length > 0 ? frases : defaultFrases;

  function toggleComunicada(id) {
    const updated = currentFrases.map(f => f.id === id ? { ...f, comunicada: !f.comunicada } : f);
    onChange(updated);
  }

  function updateNotas(id, notas) {
    const updated = currentFrases.map(f => f.id === id ? { ...f, notas } : f);
    onChange(updated);
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <h3 style={{ marginBottom: '8px' }}>Encuadre Inicial</h3>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '16px' }}>
        Asegúrese de comunicar estas premisas a la familia antes de iniciar la entrevista.
      </p>
      {currentFrases.map((f, i) => (
        <div key={f.id} style={{ padding: '16px', border: '1px solid var(--border)', borderRadius: '8px', background: 'var(--bg-card)' }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '12px', marginBottom: '12px' }}>
            <input 
              type="checkbox" 
              checked={f.comunicada} 
              onChange={() => toggleComunicada(f.id)} 
              style={{ width: '20px', height: '20px', marginTop: '2px' }}
            />
            <strong style={{ fontSize: '1.05rem', color: f.comunicada ? 'var(--text)' : 'var(--text-secondary)' }}>
              {i + 1}. {f.texto}
            </strong>
          </div>
          {f.comunicada && (
            <div style={{ marginLeft: '32px' }}>
              <input 
                type="text" 
                placeholder="Notas u observaciones (opcional)" 
                value={f.notas || ''}
                onChange={e => updateNotas(f.id, e.target.value)}
                style={{ width: '100%', padding: '8px', border: '1px solid var(--border)', borderRadius: '4px' }}
              />
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
