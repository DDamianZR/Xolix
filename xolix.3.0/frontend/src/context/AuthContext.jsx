import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [rol, setRol] = useState(localStorage.getItem('rol'));

  const isAuthenticated = !!token;
  const isAdmin = rol === 'director' || rol === 'coordinador';

  function login(accessToken, userRol) {
    localStorage.setItem('token', accessToken);
    localStorage.setItem('rol', userRol);
    setToken(accessToken);
    setRol(userRol);
  }

  function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('rol');
    setToken(null);
    setRol(null);
  }

  return (
    <AuthContext.Provider value={{ token, rol, isAuthenticated, isAdmin, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
