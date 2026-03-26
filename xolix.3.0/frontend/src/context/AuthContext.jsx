import { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [rol, setRol] = useState(localStorage.getItem('rol'));
  const [theme, setTheme] = useState(localStorage.getItem('xolix-theme') || 'light');

  const isAuthenticated = !!token;
  const isAdmin = rol === 'director' || rol === 'coordinador';

  // Apply theme class to body
  useEffect(() => {
    document.body.classList.toggle('dark', theme === 'dark');
    localStorage.setItem('xolix-theme', theme);
  }, [theme]);

  function toggleTheme() {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
  }

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
    <AuthContext.Provider value={{ token, rol, isAuthenticated, isAdmin, theme, toggleTheme, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
