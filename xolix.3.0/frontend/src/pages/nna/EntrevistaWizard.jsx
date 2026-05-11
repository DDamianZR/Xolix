import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import api from '../../api/client';
import FraseChecklist from '../../components/nna/FraseChecklist';
import DiaComunForm from '../../components/nna/DiaComunForm';
import GradoNegacionSelector from '../../components/nna/GradoNegacionSelector';

export default function EntrevistaWizard() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  
  const [data, setData] = useState({
    frases_comunicadas: [],
    dia_comun: null,
    grado_negacion: 1,
    observaciones_negacion: '',
    completada: false
  });

  useEffect(() => {
    loadEntrevista();
  }, [id]);

  async function loadEntrevista() {
    try {
      const res = await api.getNnaEntrevista(id);
      if (res) {
        setData(res);
      } else {
        // Try to load from localStorage if new
        const saved = localStorage.getItem(`entrevista_draft_${id}`);
        if (saved) setData(JSON.parse(saved));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  // Auto-save to localStorage when data changes
  useEffect(() => {
    if (!loading && !data.completada) {
      localStorage.setItem(`entrevista_draft_${id}`, JSON.stringify(data));
    }
  }, [data, loading, id]);

  async function handleSave(completar = false) {
    setSaving(true);
    try {
      const payload = { ...data, completada: completar || data.completada };
      await api.saveNnaEntrevista(id, payload);
      
      // Also register persons mentioned in dia_comun
      if (payload.dia_comun?.personas_mencionadas?.length > 0) {
        // Simple fire-and-forget for new persons
        for (const nombre of payload.dia_comun.personas_mencionadas) {
           try {
             await api.createNnaPersona(id, { nombre, tipo_simbolo: 'normal' });
           } catch(e) { /* ignore if already exists or error */ }
        }
      }

      setData(payload);
      if (completar) {
        localStorage.removeItem(`entrevista_draft_${id}`);
        // Optionally generate plan automatically or show the button in step 4
      }
      alert('Entrevista guardada correctamente');
    } catch (err) {
      alert('Error al guardar entrevista');
    } finally {
      setSaving(false);
    }
  }

  async function generatePlan() {
    try {
      await handleSave(true); // Ensure it's saved and marked as complete first
      await api.generateNnaPlanAccion(id);
      navigate(`/nna/casos/${id}/plan`);
    } catch (err) {
      alert('Error al generar plan de acción: ' + err.message);
    }
  }

  if (loading) return <div className="page-dashboard"><Topbar /><div className="container">Cargando...</div></div>;

  return (
    <div className="page-dashboard">
      <Topbar />
      <div className="container" style={{ maxWidth: '800px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <button className="btn btn-secondary" onClick={() => navigate(`/nna/casos/${id}`)}>← Volver al Caso</button>
          <h2>Entrevista Guiada</h2>
        </div>

        {/* Wizard Progress */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '32px', position: 'relative' }}>
          <div style={{ position: 'absolute', top: '16px', left: '0', right: '0', height: '4px', background: 'var(--border)', zIndex: 0 }}>
            <div style={{ height: '100%', background: 'var(--primary)', width: `${((step - 1) / 3) * 100}%`, transition: 'width 0.3s' }}></div>
          </div>
          {[1, 2, 3, 4].map(num => (
            <div 
              key={num}
              onClick={() => setStep(num)}
              style={{
                width: '36px', height: '36px', borderRadius: '50%',
                background: step >= num ? 'var(--primary)' : 'var(--bg-card)',
                border: `2px solid ${step >= num ? 'var(--primary)' : 'var(--border)'}`,
                color: step >= num ? '#fff' : 'var(--text-secondary)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 'bold', zIndex: 1, cursor: 'pointer',
                boxShadow: step === num ? '0 0 0 4px rgba(59, 130, 246, 0.2)' : 'none'
              }}
            >
              {num}
            </div>
          ))}
        </div>

        <div className="table-card" style={{ padding: '32px', minHeight: '400px' }}>
          {step === 1 && (
            <FraseChecklist 
              frases={data.frases_comunicadas} 
              onChange={val => setData({ ...data, frases_comunicadas: val })} 
            />
          )}
          
          {step === 2 && (
            <DiaComunForm 
              data={data.dia_comun} 
              onChange={val => setData({ ...data, dia_comun: val })} 
            />
          )}

          {step === 3 && (
            <GradoNegacionSelector 
              value={data.grado_negacion} 
              observaciones={data.observaciones_negacion}
              onChangeValue={val => setData({ ...data, grado_negacion: val })}
              onChangeObservaciones={val => setData({ ...data, observaciones_negacion: val })}
            />
          )}

          {step === 4 && (
            <div>
              <h3 style={{ marginBottom: '16px' }}>Resumen y Cierre</h3>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
                Revise que todos los pasos estén completos. Puede guardar el progreso o finalizar la entrevista para generar el Plan de Acción.
              </p>
              
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '32px' }}>
                <div style={{ padding: '16px', background: 'var(--bg)', borderRadius: '8px' }}>
                  <h4>Frases Comunicadas</h4>
                  <p>{data.frases_comunicadas?.filter(f => f.comunicada).length || 0} de 4 comunicadas.</p>
                </div>
                <div style={{ padding: '16px', background: 'var(--bg)', borderRadius: '8px' }}>
                  <h4>Grado de Negación</h4>
                  <p>Nivel {data.grado_negacion || 1}</p>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
                <button className="btn btn-secondary" onClick={() => handleSave(false)} disabled={saving}>
                  {saving ? 'Guardando...' : 'Guardar Borrador'}
                </button>
                <button className="btn btn-primary" onClick={generatePlan} disabled={saving || data.completada}>
                  Finalizar y Generar Plan de Acción
                </button>
              </div>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '24px' }}>
          <button className="btn btn-secondary" disabled={step === 1} onClick={() => setStep(step - 1)}>
            Anterior
          </button>
          <button className="btn btn-primary" disabled={step === 4} onClick={() => setStep(step + 1)}>
            Siguiente
          </button>
        </div>
      </div>
    </div>
  );
}
