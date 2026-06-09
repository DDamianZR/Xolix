import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../api/client';

const TIPOS = ['gobierno', 'civil', 'empresa', 'persona_fisica'];
const TIPO_LABELS = { gobierno: 'Institución Gubernamental', civil: 'Organización Civil', empresa: 'Empresa Privada', persona_fisica: 'Persona Física' };
const DIAS = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'];

const initialForm = {
  nombre: '', tipo: 'gobierno', descripcion: '', direccion: '', municipio: '',
  estado: '', pais: 'México', telefono: '', correo: '', sitio_web: '',
  responsables: [], horarios: [], servicios: [],
};

export default function ActorForm() {
  const navigate = useNavigate();
  const { id } = useParams();
  const editMode = !!id;
  const [form, setForm] = useState(initialForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (editMode) {
      api.get(`/actores/${id}`).then(r => {
        const a = r.data;
        setForm({ ...a, responsables: a.responsables || [], horarios: a.horarios || [], servicios: a.servicios || [] });
      });
    }
  }, [id]);

  const addResponsable = () => setForm(f => ({ ...f, responsables: [...f.responsables, { nombre: '', cargo: '', telefono: '', correo: '' }] }));
  const addHorario = () => setForm(f => ({ ...f, horarios: [...f.horarios, { dia_semana: 'lunes', hora_inicio: '09:00', hora_fin: '17:00' }] }));
  const addServicio = () => setForm(f => ({ ...f, servicios: [...f.servicios, { nombre: '', descripcion: '', tipo: 'servicio', es_gratuito: true, costo: '', disponibilidad: '', requisitos: [] }] }));

  const handleSubmit = async e => {
    e.preventDefault();
    setSaving(true); setError('');
    try {
      const payload = { ...form };
      if (editMode) {
        await api.put(`/actores/${id}`, payload);
      } else {
        await api.post('/actores/', payload);
      }
      navigate('/actores');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al guardar');
    } finally {
      setSaving(false);
    }
  };

  const inputStyle = { width: '100%', padding: '8px 10px', borderRadius: 6, border: '1px solid #ccc', fontSize: 14, boxSizing: 'border-box' };
  const labelStyle = { fontSize: 12, color: '#666', marginBottom: 4, display: 'block' };

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: '0 auto' }}>
      <button onClick={() => navigate('/actores')} style={{ background: 'none', border: 'none', color: '#1A5276', cursor: 'pointer', fontSize: 14, marginBottom: 16 }}>
        ← Volver
      </button>
      <h2 style={{ marginBottom: 24 }}>{editMode ? 'Editar Actor' : 'Nuevo Actor'}</h2>

      <form onSubmit={handleSubmit}>
        <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.07)', marginBottom: 20 }}>
          <h3 style={{ marginTop: 0, color: '#1A5276' }}>Información General</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={labelStyle}>Nombre *</label>
              <input required style={inputStyle} value={form.nombre} onChange={e => setForm(f => ({ ...f, nombre: e.target.value }))} />
            </div>
            <div>
              <label style={labelStyle}>Tipo *</label>
              <select required style={inputStyle} value={form.tipo} onChange={e => setForm(f => ({ ...f, tipo: e.target.value }))}>
                {TIPOS.map(t => <option key={t} value={t}>{TIPO_LABELS[t]}</option>)}
              </select>
            </div>
            <div>
              <label style={labelStyle}>Teléfono</label>
              <input style={inputStyle} value={form.telefono} onChange={e => setForm(f => ({ ...f, telefono: e.target.value }))} />
            </div>
            <div style={{ gridColumn: '1 / -1' }}>
              <label style={labelStyle}>Descripción</label>
              <textarea style={{ ...inputStyle, minHeight: 70, resize: 'vertical' }} value={form.descripcion} onChange={e => setForm(f => ({ ...f, descripcion: e.target.value }))} />
            </div>
          </div>
        </div>

        <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.07)', marginBottom: 20 }}>
          <h3 style={{ marginTop: 0, color: '#1A5276' }}>Datos de Contacto</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
            {[['direccion','Dirección','1/-1'],['municipio','Municipio'],['estado','Estado'],['pais','País'],['correo','Correo'],['sitio_web','Sitio web']].map(([k,l,col]) => (
              <div key={k} style={{ gridColumn: col }}>
                <label style={labelStyle}>{l}</label>
                <input style={inputStyle} value={form[k] || ''} onChange={e => setForm(f => ({ ...f, [k]: e.target.value }))} />
              </div>
            ))}
          </div>
        </div>

        <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.07)', marginBottom: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h3 style={{ margin: 0, color: '#1A5276' }}>Responsables</h3>
            <button type="button" onClick={addResponsable} style={{ background: '#EBF5FB', border: 'none', borderRadius: 6, padding: '6px 12px', cursor: 'pointer', fontSize: 13 }}>+ Agregar</button>
          </div>
          {form.responsables.map((r, i) => (
            <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: 10, marginBottom: 10, padding: 12, background: '#F9F9F9', borderRadius: 8 }}>
              <input placeholder="Nombre *" style={inputStyle} value={r.nombre} onChange={e => { const arr = [...form.responsables]; arr[i].nombre = e.target.value; setForm(f => ({ ...f, responsables: arr })); }} />
              <input placeholder="Cargo" style={inputStyle} value={r.cargo || ''} onChange={e => { const arr = [...form.responsables]; arr[i].cargo = e.target.value; setForm(f => ({ ...f, responsables: arr })); }} />
              <input placeholder="Teléfono" style={inputStyle} value={r.telefono || ''} onChange={e => { const arr = [...form.responsables]; arr[i].telefono = e.target.value; setForm(f => ({ ...f, responsables: arr })); }} />
              <div style={{ display: 'flex', gap: 6 }}>
                <input placeholder="Correo" style={{ ...inputStyle, flex: 1 }} value={r.correo || ''} onChange={e => { const arr = [...form.responsables]; arr[i].correo = e.target.value; setForm(f => ({ ...f, responsables: arr })); }} />
                <button type="button" onClick={() => setForm(f => ({ ...f, responsables: f.responsables.filter((_,j) => j!==i) }))} style={{ background: '#FADBD8', border: 'none', borderRadius: 6, padding: '0 8px', cursor: 'pointer' }}>✕</button>
              </div>
            </div>
          ))}
        </div>

        <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.07)', marginBottom: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h3 style={{ margin: 0, color: '#1A5276' }}>Horarios</h3>
            <button type="button" onClick={addHorario} style={{ background: '#EBF5FB', border: 'none', borderRadius: 6, padding: '6px 12px', cursor: 'pointer', fontSize: 13 }}>+ Agregar</button>
          </div>
          {form.horarios.map((h, i) => (
            <div key={i} style={{ display: 'flex', gap: 10, marginBottom: 8, alignItems: 'center' }}>
              <select style={{ ...inputStyle, flex: 1 }} value={h.dia_semana} onChange={e => { const arr = [...form.horarios]; arr[i].dia_semana = e.target.value; setForm(f => ({ ...f, horarios: arr })); }}>
                {DIAS.map(d => <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>)}
              </select>
              <input type="time" style={{ ...inputStyle, flex: 1 }} value={h.hora_inicio || ''} onChange={e => { const arr = [...form.horarios]; arr[i].hora_inicio = e.target.value; setForm(f => ({ ...f, horarios: arr })); }} />
              <span>–</span>
              <input type="time" style={{ ...inputStyle, flex: 1 }} value={h.hora_fin || ''} onChange={e => { const arr = [...form.horarios]; arr[i].hora_fin = e.target.value; setForm(f => ({ ...f, horarios: arr })); }} />
              <button type="button" onClick={() => setForm(f => ({ ...f, horarios: f.horarios.filter((_,j) => j!==i) }))} style={{ background: '#FADBD8', border: 'none', borderRadius: 6, padding: '6px 10px', cursor: 'pointer' }}>✕</button>
            </div>
          ))}
        </div>

        <div style={{ background: '#fff', borderRadius: 12, padding: 24, boxShadow: '0 2px 8px rgba(0,0,0,0.07)', marginBottom: 20 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
            <h3 style={{ margin: 0, color: '#1A5276' }}>Servicios</h3>
            <button type="button" onClick={addServicio} style={{ background: '#EBF5FB', border: 'none', borderRadius: 6, padding: '6px 12px', cursor: 'pointer', fontSize: 13 }}>+ Agregar</button>
          </div>
          {form.servicios.map((s, i) => (
            <div key={i} style={{ padding: 14, background: '#F9F9F9', borderRadius: 8, marginBottom: 12 }}>
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr 1fr', gap: 10, marginBottom: 8 }}>
                <input placeholder="Nombre del servicio *" style={inputStyle} value={s.nombre} onChange={e => { const arr = [...form.servicios]; arr[i].nombre = e.target.value; setForm(f => ({ ...f, servicios: arr })); }} />
                <select style={inputStyle} value={s.tipo} onChange={e => { const arr = [...form.servicios]; arr[i].tipo = e.target.value; setForm(f => ({ ...f, servicios: arr })); }}>
                  <option value="servicio">Servicio</option>
                  <option value="producto">Producto</option>
                </select>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <label style={{ fontSize: 13 }}><input type="checkbox" checked={s.es_gratuito} onChange={e => { const arr = [...form.servicios]; arr[i].es_gratuito = e.target.checked; setForm(f => ({ ...f, servicios: arr })); }} /> Gratuito</label>
                  {!s.es_gratuito && <input placeholder="Costo $" style={{ ...inputStyle, width: 80 }} type="number" value={s.costo} onChange={e => { const arr = [...form.servicios]; arr[i].costo = e.target.value; setForm(f => ({ ...f, servicios: arr })); }} />}
                </div>
              </div>
              <textarea placeholder="Descripción..." style={{ ...inputStyle, minHeight: 50, resize: 'vertical', marginBottom: 6 }} value={s.descripcion} onChange={e => { const arr = [...form.servicios]; arr[i].descripcion = e.target.value; setForm(f => ({ ...f, servicios: arr })); }} />
              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <button type="button" onClick={() => setForm(f => ({ ...f, servicios: f.servicios.filter((_,j) => j!==i) }))} style={{ background: '#FADBD8', border: 'none', borderRadius: 6, padding: '4px 10px', cursor: 'pointer', fontSize: 12 }}>Eliminar servicio</button>
              </div>
            </div>
          ))}
        </div>

        {error && <p style={{ color: '#c0392b', background: '#FADBD8', padding: 10, borderRadius: 6 }}>{error}</p>}

        <button
          type="submit"
          disabled={saving}
          style={{ background: '#1A5276', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 28px', cursor: 'pointer', fontSize: 15, width: '100%' }}
        >
          {saving ? 'Guardando...' : 'Guardar Actor'}
        </button>
      </form>
    </div>
  );
}
