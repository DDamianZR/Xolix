import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import api from '../../api/client';
import ObservacionForm from '../../components/nna/ObservacionForm';
import ObservacionCard from '../../components/nna/ObservacionCard';

export default function ObservacionesPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [observaciones, setObservaciones] = useState([]);
  const [personas, setPersonas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [id]);

  async function loadData() {
    try {
      const [obs, pers] = await Promise.all([
        api.getNnaObservaciones(id),
        api.getNnaPersonas(id)
      ]);
      setObservaciones(obs);
      setPersonas(pers);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className="page-dashboard"><Topbar /><div className="container">Cargando...</div></div>;

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
          <button className="btn btn-secondary" onClick={() => navigate(`/nna/casos/${id}`)}>← Volver al Caso</button>
          <h2 style={{ margin: 0 }}>Registro de Observaciones No Verbales</h2>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
          <div>
            <ObservacionForm casoId={id} personas={personas} onSaved={loadData} />
          </div>
          
          <div>
            <h3 style={{ marginBottom: '16px' }}>Historial de Observaciones</h3>
            {observaciones.length === 0 ? (
              <div className="status-msg">No hay observaciones registradas aún.</div>
            ) : (
              observaciones.map(obs => <ObservacionCard key={obs.id} obs={obs} />)
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
