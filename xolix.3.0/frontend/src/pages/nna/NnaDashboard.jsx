import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import api from '../../api/client';
import CasoNNACard from '../../components/nna/CasoNNACard';

export default function NnaDashboard() {
  const navigate = useNavigate();
  const [casos, setCasos] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCasos();
  }, []);

  async function loadCasos() {
    try {
      const data = await api.getNnaCasos();
      setCasos(data);
    } catch (err) {
      alert('Error al cargar casos NNA');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container">
        <button className="btn btn-secondary" style={{ marginBottom: '16px' }} onClick={() => navigate('/dashboard')}>
          ← Volver al Dashboard
        </button>
        <div className="table-header">
          <h3>Módulo de Protección NNA</h3>
          <button className="btn btn-add" onClick={() => navigate('/nna/casos/nuevo')}>
            + Nuevo Caso NNA
          </button>
        </div>

        {loading ? (
          <div className="status-msg">Cargando...</div>
        ) : casos.length === 0 ? (
          <div className="status-msg">No hay casos registrados aún.</div>
        ) : (
          casos.map(caso => <CasoNNACard key={caso.id} caso={caso} />)
        )}
      </div>
    </div>
  );
}
