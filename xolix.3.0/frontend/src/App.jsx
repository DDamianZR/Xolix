import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Register from './pages/Register';
import UserDetail from './pages/UserDetail';
import UserEdit from './pages/UserEdit';
import Expedientes from './pages/Expedientes';
import Procesos from './pages/Procesos';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/registro" element={<ProtectedRoute><Register /></ProtectedRoute>} />
          <Route path="/usuario/:id" element={<ProtectedRoute><UserDetail /></ProtectedRoute>} />
          <Route path="/editar/:id" element={<ProtectedRoute><UserEdit /></ProtectedRoute>} />
          <Route path="/expedientes" element={<ProtectedRoute><Expedientes /></ProtectedRoute>} />
          <Route path="/procesos" element={<ProtectedRoute><Procesos /></ProtectedRoute>} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
