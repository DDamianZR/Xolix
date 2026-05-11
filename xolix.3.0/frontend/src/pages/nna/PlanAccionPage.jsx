import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import api from '../../api/client';

export default function PlanAccionPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPlan();
  }, [id]);

  async function loadPlan() {
    try {
      const data = await api.getNnaPlanAccion(id);
      setPlan(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function toggleSubtarea(subId) {
    try {
      await api.toggleSubtarea(subId);
      loadPlan();
    } catch (err) {
      alert('Error al actualizar subtarea');
    }
  }

  if (loading) return <div className="page-dashboard"><Topbar /><div className="container">Cargando...</div></div>;

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container" style={{ maxWidth: '800px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
          <button className="btn btn-secondary" onClick={() => navigate(`/nna/casos/${id}`)}>← Volver al Caso</button>
          <h2 style={{ margin: 0 }}>Plan de Acción Post-Entrevista</h2>
        </div>

        {!plan ? (
          <div className="table-card" style={{ padding: '32px', textAlign: 'center' }}>
            <h3 style={{ marginBottom: '16px' }}>No hay plan de acción activo</h3>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
              El plan de acción se genera automáticamente al finalizar la Entrevista Inicial.
            </p>
            <button className="btn btn-primary" onClick={() => navigate(`/nna/casos/${id}/entrevista`)}>
              Ir a la Entrevista
            </button>
          </div>
        ) : (
          <div className="table-card" style={{ padding: '32px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
              <div>
                <h3 style={{ margin: '0 0 8px 0' }}>{plan.titulo}</h3>
                <p style={{ color: 'var(--text-secondary)', margin: 0 }}>{plan.descripcion}</p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span className={`badge badge-rol`}>{plan.estado.replace('_', ' ')}</span>
                <div style={{ marginTop: '8px', fontWeight: 'bold' }}>Progreso: {plan.progreso}%</div>
              </div>
            </div>

            <div style={{ height: '8px', background: 'var(--border)', borderRadius: '4px', marginBottom: '32px', overflow: 'hidden' }}>
              <div style={{ height: '100%', background: 'var(--primary)', width: `${plan.progreso}%`, transition: 'width 0.3s' }}></div>
            </div>

            <h4>Subtareas Predefinidas</h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
              {plan.subtareas.map(sub => (
                <div 
                  key={sub.id} 
                  style={{ 
                    display: 'flex', alignItems: 'center', gap: '16px', 
                    padding: '16px', border: '1px solid var(--border)', borderRadius: '8px',
                    background: sub.completada ? 'rgba(34, 197, 94, 0.1)' : 'var(--bg-card)',
                    opacity: sub.completada ? 0.8 : 1
                  }}
                >
                  <input 
                    type="checkbox" 
                    checked={sub.completada} 
                    onChange={() => toggleSubtarea(sub.id)} 
                    style={{ width: '24px', height: '24px', cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '1.1rem', textDecoration: sub.completada ? 'line-through' : 'none' }}>
                    {sub.titulo}
                  </span>
                </div>
              ))}
            </div>
            
            <div style={{ marginTop: '32px', textAlign: 'center' }}>
              <button className="btn btn-secondary" onClick={() => navigate('/procesos')}>
                Ver en Task Manager General
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
