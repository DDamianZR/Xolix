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
import ActoresList from './pages/ActoresList';
import ActorDetalle from './pages/ActorDetalle';
import ActorForm from './pages/ActorForm';
import ReportesPage from './pages/ReportesPage';

// NNA Pages — módulo original
import NnaDashboard from './pages/nna/NnaDashboard';
import NuevoCasoNNA from './pages/nna/NuevoCasoNNA';
import CasoNNADetalle from './pages/nna/CasoNNADetalle';
import EntrevistaWizard from './pages/nna/EntrevistaWizard';
import FamiliogramaEditor from './pages/nna/FamiliogramaEditor';
import ObservacionesPage from './pages/nna/ObservacionesPage';
import PlanAccionPage from './pages/nna/PlanAccionPage';

// NNA Pages — módulos nuevos
import DiagnosticoPage from './pages/nna/DiagnosticoPage';
import PlanesPage from './pages/nna/PlanesPage';
import EquipoCasoPage from './pages/nna/EquipoCasoPage';

// Colaboradores
import ColaboradoresPage from './pages/ColaboradoresPage';

// NNA Pages — iteración 2 (5 pantallas nuevas)
import PersonasFamiliaresPage from './pages/nna/PersonasFamiliaresPage';
import RelacionesFamiliaresPage from './pages/nna/RelacionesFamiliaresPage';
import HistorialFamiliogramaPage from './pages/nna/HistorialFamiliogramaPage';
import FamiliogramaReportPage from './pages/nna/FamiliogramaReportPage';
import ResumenCasoNNAPage from './pages/nna/ResumenCasoNNAPage';

const PR = ({ children }) => <ProtectedRoute>{children}</ProtectedRoute>;

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Auth */}
          <Route path="/" element={<Login />} />
          <Route path="/verificar" element={<Verificar />} />
          <Route path="/registro" element={<Register />} />

          {/* Personal */}
          <Route path="/dashboard" element={<PR><Dashboard /></PR>} />
          <Route path="/usuario/:id" element={<PR><UserDetail /></PR>} />
          <Route path="/editar/:id" element={<PR><UserEdit /></PR>} />

          {/* Expedientes y Procesos */}
          <Route path="/expedientes" element={<PR><Expedientes /></PR>} />
          <Route path="/procesos" element={<PR><Procesos /></PR>} />
          <Route path="/casos/:id" element={<PR><CasoDetalle /></PR>} />

          {/* Actores */}
          <Route path="/actores" element={<PR><ActoresList /></PR>} />
          <Route path="/actores/nuevo" element={<PR><ActorForm /></PR>} />
          <Route path="/actores/:id" element={<PR><ActorDetalle /></PR>} />
          <Route path="/actores/:id/editar" element={<PR><ActorForm /></PR>} />

          {/* Reportes */}
          <Route path="/reportes" element={<PR><ReportesPage /></PR>} />

          {/* ── Protección NNA ────────────────────── */}
          <Route path="/nna" element={<PR><NnaDashboard /></PR>} />
          <Route path="/nna/casos/nuevo" element={<PR><NuevoCasoNNA /></PR>} />

          {/* Resumen — ruta principal del caso (nueva) */}
          <Route path="/nna/casos/:id/resumen" element={<PR><ResumenCasoNNAPage /></PR>} />

          {/* Módulo original */}
          <Route path="/nna/casos/:id" element={<PR><CasoNNADetalle /></PR>} />
          <Route path="/nna/casos/:id/entrevista" element={<PR><EntrevistaWizard /></PR>} />
          <Route path="/nna/casos/:id/familiograma" element={<PR><FamiliogramaEditor /></PR>} />
          <Route path="/nna/casos/:id/observaciones" element={<PR><ObservacionesPage /></PR>} />
          <Route path="/nna/casos/:id/plan" element={<PR><PlanAccionPage /></PR>} />
          <Route path="/nna/casos/:id/diagnostico" element={<PR><DiagnosticoPage /></PR>} />
          <Route path="/nna/casos/:id/planes" element={<PR><PlanesPage /></PR>} />

          {/* Iteración 2 — 5 pantallas nuevas */}
          <Route path="/nna/casos/:id/personas" element={<PR><PersonasFamiliaresPage /></PR>} />
          <Route path="/nna/casos/:id/relaciones" element={<PR><RelacionesFamiliaresPage /></PR>} />
          <Route path="/nna/casos/:id/historial-familiograma" element={<PR><HistorialFamiliogramaPage /></PR>} />
          <Route path="/nna/casos/:id/reporte" element={<PR><FamiliogramaReportPage /></PR>} />

          {/* Equipo multidisciplinario */}
          <Route path="/nna/casos/:id/equipo" element={<PR><EquipoCasoPage /></PR>} />

          {/* Colaboradores */}
          <Route path="/colaboradores" element={<PR><ColaboradoresPage /></PR>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
