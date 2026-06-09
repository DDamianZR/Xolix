import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

const TIPOS = ['', 'gobierno', 'civil', 'empresa', 'persona_fisica'];

export default function ActoresList() {
  const navigate = useNavigate();
  const [actores, setActores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filtros, setFiltros] = useState({ municipio: '', estado: '', tipo: '', es_gratuito: '' });

  const cargar = async () => {
    setLoading(true);
    const params = new URLSearchParams();
    if (filtros.municipio) params.append('municipio', filtros.municipio);
    if (filtros.estado) params.append('estado', filtros.estado);
    if (filtros.tipo) params.append('tipo', filtros.tipo);
    if (filtros.es_gratuito !== '') params.append('es_gratuito', filtros.es_gratuito);
    const res = await api.get(`/actores/?${params}`);
    setActores(res.data);
    setLoading(false);
  };

  useEffect(() => { cargar(); }, []);

  const tipoLabel = { gobierno: 'Gubernamental', civil: 'Org. Civil', empresa: 'Empresa', persona_fisica: 'Persona Física' };

  return (
    <div style={{ padding: 24, maxWidth: 1100, margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
        <h2 style={{ margin: 0 }}>Actores en Materia de Derechos</h2>
        <button
          onClick={() => navigate('/actores/nuevo')}
          style={{ background: '#1A5276', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 18px', cursor: 'pointer' }}
        >
          + Nuevo Actor
        </button>
      </div>

      {/* Filtros */}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 20, padding: 16, background: '#EBF5FB', borderRadius: 8 }}>
        <input
          placeholder="Municipio..."
          value={filtros.municipio}
          onChange={e => setFiltros(f => ({ ...f, municipio: e.target.value }))}
          style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid #ccc', flex: 1, minWidth: 140 }}
        />
        <input
          placeholder="Estado..."
          value={filtros.estado}
          onChange={e => setFiltros(f => ({ ...f, estado: e.target.value }))}
          style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid #ccc', flex: 1, minWidth: 140 }}
        />
        <select
          value={filtros.tipo}
          onChange={e => setFiltros(f => ({ ...f, tipo: e.target.value }))}
          style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid #ccc' }}
        >
          {TIPOS.map(t => <option key={t} value={t}>{t ? tipoLabel[t] : 'Todos los tipos'}</option>)}
        </select>
        <select
          value={filtros.es_gratuito}
          onChange={e => setFiltros(f => ({ ...f, es_gratuito: e.target.value }))}
          style={{ padding: '6px 10px', borderRadius: 6, border: '1px solid #ccc' }}
        >
          <option value="">Todos (gratuito/costo)</option>
          <option value="true">Solo gratuitos</option>
          <option value="false">Solo con costo</option>
        </select>
        <button onClick={cargar} style={{ background: '#1A5276', color: '#fff', border: 'none', borderRadius: 6, padding: '6px 16px', cursor: 'pointer' }}>
          Buscar
        </button>
      </div>

      {loading ? (
        <p style={{ textAlign: 'center', color: '#999' }}>Cargando...</p>
      ) : actores.length === 0 ? (
        <p style={{ textAlign: 'center', color: '#999' }}>No se encontraron actores con esos filtros.</p>
      ) : (
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr style={{ background: '#1A5276', color: '#fff' }}>
              <th style={{ padding: '10px 12px', textAlign: 'left' }}>Nombre</th>
              <th style={{ padding: '10px 12px', textAlign: 'left' }}>Tipo</th>
              <th style={{ padding: '10px 12px', textAlign: 'left' }}>Municipio</th>
              <th style={{ padding: '10px 12px', textAlign: 'left' }}>Estado</th>
              <th style={{ padding: '10px 12px', textAlign: 'left' }}>Teléfono</th>
              <th style={{ padding: '10px 12px', textAlign: 'left' }}>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {actores.map((a, i) => (
              <tr key={a.id} style={{ background: i % 2 === 0 ? '#fff' : '#EBF5FB' }}>
                <td style={{ padding: '8px 12px', fontWeight: 600 }}>{a.nombre}</td>
                <td style={{ padding: '8px 12px' }}>
                  <span style={{ background: '#D6EAF8', borderRadius: 12, padding: '2px 10px', fontSize: 12 }}>
                    {tipoLabel[a.tipo] || a.tipo}
                  </span>
                </td>
                <td style={{ padding: '8px 12px' }}>{a.municipio || '—'}</td>
                <td style={{ padding: '8px 12px' }}>{a.estado || '—'}</td>
                <td style={{ padding: '8px 12px' }}>{a.telefono || '—'}</td>
                <td style={{ padding: '8px 12px' }}>
                  <button
                    onClick={() => navigate(`/actores/${a.id}`)}
                    style={{ background: 'none', color: '#1A5276', border: '1px solid #1A5276', borderRadius: 6, padding: '4px 10px', cursor: 'pointer', fontSize: 12 }}
                  >
                    Ver
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
