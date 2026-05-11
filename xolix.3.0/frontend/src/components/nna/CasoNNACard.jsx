import { useNavigate } from 'react-router-dom';

export default function CasoNNACard({ caso }) {
  const navigate = useNavigate();

  return (
    <div className="table-card" style={{ padding: '16px', marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <div>
        <h4 style={{ margin: '0 0 8px 0' }}>{caso.nna_nombre}</h4>
        <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          <span>Edad: {caso.nna_edad || 'N/A'}</span> • 
          <span style={{ marginLeft: '8px' }}>Género: {caso.nna_genero || 'N/A'}</span>
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <span className={`badge ${caso.estado === 'activo' ? 'badge-active' : 'badge-inactive'}`}>
          {caso.estado === 'activo' ? 'Activo' : 'Cerrado'}
        </span>
        <button className="btn-sm btn-view" onClick={() => navigate(`/nna/casos/${caso.id}`)}>
          Ver Expediente
        </button>
      </div>
    </div>
  );
}
