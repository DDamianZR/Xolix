import { useState, useCallback, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Topbar from '../../components/Topbar';
import api from '../../api/client';
import { ReactFlow, addEdge, Background, Controls, MiniMap, applyNodeChanges, applyEdgeChanges } from '@xyflow/react';
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
  const [selectedNode, setSelectedNode] = useState(null);
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
            data: { 
              label: `${p.nombre}\n(${p.rol_en_familia || 'Sin rol'})`,
              tipo: p.tipo_simbolo === 'clave' 
                ? (p.genero === 'femenino' ? 'femenino_clave' : 'masculino_clave')
                : (p.genero === 'femenino' ? 'femenino' : 'masculino'),
              edad: p.edad || '',
              rol: p.rol_en_familia || '',
              ocupacion: p.ocupacion || '',
              notas: p.observaciones || ''
            },
            type: 'default',
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
  
  const onSelectionChange = useCallback(({ nodes }) => {
    if (nodes.length === 1) {
      setSelectedNode(nodes[0]);
    } else {
      setSelectedNode(null);
    }
  }, []);

  const addNode = (tipo) => {
    const isFemenino = tipo.includes('femenino');
    const isClave = tipo.includes('clave');
    
    const newNode = {
      id: `node-${Date.now()}`,
      position: { x: Math.random() * 200 + 50, y: Math.random() * 200 + 50 },
      data: { label: 'Nueva Persona', tipo: tipo, edad: '', rol: '', ocupacion: '', notas: '' },
      style: {
        borderRadius: isFemenino ? '50%' : '8px',
        width: 80, height: 80, display: 'flex', alignItems: 'center', justifyContent: 'center',
        border: isClave ? '4px solid #000' : '2px solid #333', background: '#fff'
      }
    };
    setNodes((nds) => nds.concat(newNode));
  };

  const updateNodeData = (field, value) => {
    if (!selectedNode) return;
    
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === selectedNode.id) {
          const updatedNode = { ...node };
          if (field === 'label') {
            updatedNode.data = { ...node.data, label: value };
          } else if (field === 'tipo') {
            updatedNode.data = { ...node.data, tipo: value };
            
            const isFemenino = value.includes('femenino');
            const isClave = value.includes('clave');
            
            updatedNode.style = { 
              ...node.style, 
              borderRadius: isFemenino ? '50%' : '8px',
              border: isClave ? '4px solid #000' : '2px solid #333'
            };
          } else {
            updatedNode.data = { ...node.data, [field]: value };
          }
          
          // Update selected node state immediately so the input doesn't lose focus or lag
          setSelectedNode(updatedNode);
          return updatedNode;
        }
        return node;
      })
    );
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
      
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
        <div style={{ width: '250px', borderRight: '1px solid var(--border)', background: 'var(--bg)', padding: '16px', overflowY: 'auto' }}>
          <h4 style={{ margin: '0 0 16px 0' }}>Símbolos</h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <button className="btn-sm" style={{ border: '2px solid #333', background: '#fff', color: '#333' }} onClick={() => addNode('masculino')}>
              ■ Hombre
            </button>
            <button className="btn-sm" style={{ border: '2px solid #333', background: '#fff', color: '#333', borderRadius: '20px' }} onClick={() => addNode('femenino')}>
              ● Mujer
            </button>
            <button className="btn-sm" style={{ border: '4px solid #333', background: '#fff', color: '#333' }} onClick={() => addNode('masculino_clave')}>
              [■] NNA Clave (H)
            </button>
            <button className="btn-sm" style={{ border: '4px solid #333', background: '#fff', color: '#333', borderRadius: '20px' }} onClick={() => addNode('femenino_clave')}>
              [●] NNA Clave (M)
            </button>
            <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '8px 0' }} />
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              Use los controles del canvas para conectar los nodos. Haga clic en un nodo para seleccionarlo y editar sus detalles. Presione Backspace para borrarlo.
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
            onSelectionChange={onSelectionChange}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>
        
        {selectedNode && (
          <div style={{ width: '300px', borderLeft: '1px solid var(--border)', background: 'var(--bg)', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px', overflowY: 'auto' }}>
            <h4 style={{ margin: 0, paddingBottom: '12px', borderBottom: '1px solid var(--border)' }}>Editar Familiar</h4>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Nombre / Etiqueta</label>
              <input 
                className="form-input" 
                value={selectedNode.data.label || ''} 
                onChange={(e) => updateNodeData('label', e.target.value)} 
                placeholder="Nombre del familiar"
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Género / Tipo</label>
              <select 
                className="form-input" 
                value={selectedNode.data.tipo || ''} 
                onChange={(e) => updateNodeData('tipo', e.target.value)}
              >
                <option value="">Seleccione...</option>
                <option value="masculino">Hombre</option>
                <option value="femenino">Mujer</option>
                <option value="masculino_clave">Hombre (Clave)</option>
                <option value="femenino_clave">Mujer (Clave)</option>
              </select>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Edad</label>
              <input 
                type="number" 
                className="form-input" 
                value={selectedNode.data.edad || ''} 
                onChange={(e) => updateNodeData('edad', e.target.value)} 
                placeholder="Ej. 35"
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Rol en la Familia</label>
              <input 
                className="form-input" 
                value={selectedNode.data.rol || ''} 
                onChange={(e) => updateNodeData('rol', e.target.value)} 
                placeholder="Ej. Madre, Padre, Hermano..."
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Ocupación</label>
              <input 
                className="form-input" 
                value={selectedNode.data.ocupacion || ''} 
                onChange={(e) => updateNodeData('ocupacion', e.target.value)} 
                placeholder="Ej. Estudiante, Empleado..."
              />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>Notas Adicionales</label>
              <textarea 
                className="form-input" 
                value={selectedNode.data.notas || ''} 
                onChange={(e) => updateNodeData('notas', e.target.value)} 
                rows={4}
                placeholder="Observaciones médicas, comportamiento, etc."
                style={{ resize: 'vertical' }}
              />
            </div>
            
          </div>
        )}
      </div>
    </div>
  );
}

