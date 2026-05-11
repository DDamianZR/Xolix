import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Register from './pages/Register';
import Verificar from './pages/Verificar';
import UserDetail from './pages/UserDetail';
import UserEdit from './pages/UserEdit';
import Expedientes from './pages/Expedientes';
import Procesos from './pages/Procesos';
import CasoDetalle from './pages/CasoDetalle';

// NNA Pages
import NnaDashboard from './pages/nna/NnaDashboard';
import NuevoCasoNNA from './pages/nna/NuevoCasoNNA';
import CasoNNADetalle from './pages/nna/CasoNNADetalle';
import EntrevistaWizard from './pages/nna/EntrevistaWizard';
import FamiliogramaEditor from './pages/nna/FamiliogramaEditor';
import ObservacionesPage from './pages/nna/ObservacionesPage';
import PlanAccionPage from './pages/nna/PlanAccionPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/verificar" element={<Verificar />} />
          <Route path="/registro" element={<Register />} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/usuario/:id" element={<ProtectedRoute><UserDetail /></ProtectedRoute>} />
          <Route path="/editar/:id" element={<ProtectedRoute><UserEdit /></ProtectedRoute>} />
          <Route path="/expedientes" element={<ProtectedRoute><Expedientes /></ProtectedRoute>} />
          <Route path="/procesos" element={<ProtectedRoute><Procesos /></ProtectedRoute>} />
          <Route path="/casos/:id" element={<ProtectedRoute><CasoDetalle /></ProtectedRoute>} />
          
          {/* Protección NNA */}
          <Route path="/nna" element={<ProtectedRoute><NnaDashboard /></ProtectedRoute>} />
          <Route path="/nna/casos/nuevo" element={<ProtectedRoute><NuevoCasoNNA /></ProtectedRoute>} />
          <Route path="/nna/casos/:id" element={<ProtectedRoute><CasoNNADetalle /></ProtectedRoute>} />
          <Route path="/nna/casos/:id/entrevista" element={<ProtectedRoute><EntrevistaWizard /></ProtectedRoute>} />
          <Route path="/nna/casos/:id/familiograma" element={<ProtectedRoute><FamiliogramaEditor /></ProtectedRoute>} />
          <Route path="/nna/casos/:id/observaciones" element={<ProtectedRoute><ObservacionesPage /></ProtectedRoute>} />
          <Route path="/nna/casos/:id/plan" element={<ProtectedRoute><PlanAccionPage /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
