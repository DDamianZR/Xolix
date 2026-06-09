import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api/client';

export default function ActorDetalle() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [actor, setActor] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/actores/${id}`).then(r => { setActor(r.data); setLoading(false); });
  }, [id]);

  if (loading) return <p style={{ padding: 24 }}>Cargando...</p>;
  if (!actor) return <p style={{ padding: 24 }}>Actor no encontrado.</p>;

  const tipoLabel = { gobierno: 'Gubernamental', civil: 'Org. Civil', empresa: 'Empresa', persona_fisica: 'Persona Física' };

  return (
    <div style={{ padding: 24, maxWidth: 900, margin: '0 auto' }}>
      <button onClick={() => navigate('/actores')} style={{ background: 'none', border: 'none', color: '#1A5276', cursor: 'pointer', fontSize: 14, marginBottom: 16 }}>
        ← Volver al catálogo
      </button>

      <div style={{ background: '#fff', borderRadius: 12, boxShadow: '0 2px 12px rgba(0,0,0,0.08)', padding: 28 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <div>
            <h2 style={{ margin: '0 0 6px' }}>{actor.nombre}</h2>
            <span style={{ background: '#D6EAF8', borderRadius: 12, padding: '3px 12px', fontSize: 13 }}>
              {tipoLabel[actor.tipo] || actor.tipo}
            </span>
          </div>
          <button
            onClick={() => navigate(`/actores/${id}/editar`)}
            style={{ background: '#1A5276', color: '#fff', border: 'none', borderRadius: 8, padding: '8px 16px', cursor: 'pointer' }}
          >
            Editar
          </button>
        </div>

        {actor.descripcion && <p style={{ marginTop: 16, color: '#555' }}>{actor.descripcion}</p>}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginTop: 20 }}>
          {[
            ['Dirección', actor.direccion],
            ['Municipio', actor.municipio],
            ['Estado', actor.estado],
            ['País', actor.pais],
            ['Teléfono', actor.telefono],
            ['Correo', actor.correo],
            ['Sitio web', actor.sitio_web],
          ].map(([label, val]) => val ? (
            <div key={label}>
              <span style={{ fontSize: 12, color: '#888' }}>{label}</span>
              <p style={{ margin: '2px 0', fontSize: 14 }}>{val}</p>
            </div>
          ) : null)}
        </div>

        {actor.responsables?.length > 0 && (
          <div style={{ marginTop: 24 }}>
            <h3 style={{ borderBottom: '1px solid #eee', paddingBottom: 8 }}>Responsables</h3>
            {actor.responsables.map(r => (
              <div key={r.id} style={{ padding: '8px 0', borderBottom: '1px solid #f5f5f5' }}>
                <strong>{r.nombre}</strong>{r.cargo ? ` — ${r.cargo}` : ''}
                {r.telefono && <span style={{ color: '#666', marginLeft: 12, fontSize: 13 }}>{r.telefono}</span>}
              </div>
            ))}
          </div>
        )}

        {actor.horarios?.length > 0 && (
          <div style={{ marginTop: 24 }}>
            <h3 style={{ borderBottom: '1px solid #eee', paddingBottom: 8 }}>Horarios</h3>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {actor.horarios.filter(h => h.activo).map(h => (
                <span key={h.id} style={{ background: '#EBF5FB', borderRadius: 8, padding: '4px 12px', fontSize: 13 }}>
                  {h.dia_semana} {h.hora_inicio}–{h.hora_fin}
                </span>
              ))}
            </div>
          </div>
        )}

        {actor.servicios?.length > 0 && (
          <div style={{ marginTop: 24 }}>
            <h3 style={{ borderBottom: '1px solid #eee', paddingBottom: 8 }}>Servicios</h3>
            {actor.servicios.filter(s => s.activo).map(s => (
              <div key={s.id} style={{ padding: 12, background: '#F9F9F9', borderRadius: 8, marginBottom: 10 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <strong>{s.nombre}</strong>
                  <span style={{ background: s.es_gratuito ? '#D5F5E3' : '#FDEBD0', borderRadius: 10, padding: '2px 10px', fontSize: 12 }}>
                    {s.es_gratuito ? 'Gratuito' : `$${s.costo}`}
                  </span>
                </div>
                {s.descripcion && <p style={{ margin: '4px 0', fontSize: 13, color: '#666' }}>{s.descripcion}</p>}
                {s.disponibilidad && <p style={{ margin: 0, fontSize: 12, color: '#888' }}>Disponibilidad: {s.disponibilidad}</p>}
                {s.requisitos?.length > 0 && (
                  <ul style={{ margin: '8px 0 0', paddingLeft: 18 }}>
                    {s.requisitos.map(r => <li key={r.id} style={{ fontSize: 13, color: '#555' }}>{r.descripcion}</li>)}
                  </ul>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
