import { useState, useCallback, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import api from '../../api/client';
import { ReactFlow, addEdge, Background, Controls, MiniMap, applyNodeChanges, applyEdgeChanges, Panel } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { toPng } from 'html-to-image';

// Custom node rendering logic could be added here. For now, using standard nodes with labels.
const initialNodes = [];
const initialEdges = [];

export default function FamiliogramaEditor() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);
  const [loading, setLoading] = useState(true);
  const reactFlowWrapper = useRef(null);

  useEffect(() => {
    loadFamiliograma();
  }, [id]);

  async function loadFamiliograma() {
    try {
      const res = await api.getNnaFamiliograma(id);
      if (res && res.grafo_json) {
        setNodes(res.grafo_json.nodes || []);
        setEdges(res.grafo_json.edges || []);
      } else {
        // Option to import persons from interview
        const persons = await api.getNnaPersonas(id);
        if (persons && persons.length > 0) {
          const importedNodes = persons.map((p, idx) => ({
            id: `person-${p.id}`,
            position: { x: 100 + (idx * 150), y: 100 },
            data: { label: `${p.nombre}\n(${p.rol_en_familia || 'Sin rol'})` },
            type: p.genero === 'femenino' ? 'output' : 'default', // basic visual diff
            style: { 
              borderRadius: p.genero === 'femenino' ? '50%' : '8px',
              width: 80, height: 80, display: 'flex', alignItems: 'center', justifyContent: 'center',
              border: p.tipo_simbolo === 'clave' ? '4px solid #000' : '2px solid #333',
              background: '#fff'
            }
          }));
          setNodes(importedNodes);
        }
      }
    } catch (err) {
      console.error('Error loading familiograma:', err);
    } finally {
      setLoading(false);
    }
  }

  const onNodesChange = useCallback((changes) => setNodes((nds) => applyNodeChanges(changes, nds)), []);
  const onEdgesChange = useCallback((changes) => setEdges((eds) => applyEdgeChanges(changes, eds)), []);
  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  const addNode = (genero) => {
    const newNode = {
      id: `node-${Date.now()}`,
      position: { x: Math.random() * 200 + 50, y: Math.random() * 200 + 50 },
      data: { label: 'Nueva Persona' },
      style: {
        borderRadius: genero === 'femenino' ? '50%' : '8px',
        width: 80, height: 80, display: 'flex', alignItems: 'center', justifyContent: 'center',
        border: '2px solid #333', background: '#fff'
      }
    };
    setNodes((nds) => nds.concat(newNode));
  };

  async function handleSave() {
    try {
      await api.saveNnaFamiliograma(id, {
        grafo_json: { nodes, edges },
        imagen_url: '' // We could generate base64 here if needed
      });
      alert('Familiograma guardado');
    } catch (err) {
      alert('Error al guardar');
    }
  }

  const exportImage = useCallback(() => {
    if (reactFlowWrapper.current === null) return;
    toPng(reactFlowWrapper.current, { filter: (node) => !(node?.classList?.contains('react-flow__panel')) })
      .then((dataUrl) => {
        const link = document.createElement('a');
        link.download = `familiograma-nna-${id}.png`;
        link.href = dataUrl;
        link.click();
      });
  }, [id]);

  if (loading) return <div className="page-dashboard"><Topbar /><div className="container">Cargando...</div></div>;

  return (
    <div className="page-dashboard" style={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      <Topbar />
      <div style={{ padding: '16px', background: 'var(--bg-card)', borderBottom: '1px solid var(--border)', display: 'flex', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <button className="btn-sm btn-secondary" onClick={() => navigate(`/nna/casos/${id}`)}>← Volver</button>
          <h3 style={{ margin: 0 }}>Editor de Familiograma</h3>
        </div>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button className="btn-sm btn-secondary" onClick={exportImage}>Exportar PNG</button>
          <button className="btn-sm btn-primary" onClick={handleSave}>Guardar</button>
        </div>
      </div>
      
      <div style={{ flex: 1, display: 'flex' }}>
        <div style={{ width: '250px', borderRight: '1px solid var(--border)', background: 'var(--bg)', padding: '16px' }}>
          <h4 style={{ margin: '0 0 16px 0' }}>Símbolos</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <button className="btn-sm" style={{ border: '2px solid #333', background: '#fff', color: '#333' }} onClick={() => addNode('masculino')}>
              ■ Hombre
            </button>
            <button className="btn-sm" style={{ border: '2px solid #333', background: '#fff', color: '#333', borderRadius: '20px' }} onClick={() => addNode('femenino')}>
              ● Mujer
            </button>
            <button className="btn-sm" style={{ border: '4px solid #333', background: '#fff', color: '#333' }} onClick={() => addNode('masculino')}>
              [■] NNA Clave
            </button>
            <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '8px 0' }} />
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Use los controles del canvas para conectar los nodos. Haga clic en un nodo para seleccionarlo y presione Backspace para borrarlo.
            </p>
          </div>
        </div>
        
        <div style={{ flex: 1 }} ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>
      </div>
    </div>
  );
}
