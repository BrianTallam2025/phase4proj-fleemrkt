import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api, { authAPI } from '../api';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        const { data } = await authAPI.getCurrentUser();
        setUser(data);
        setIsAuthenticated(true);
        
        // Redirect from login if already authenticated
        if (location.pathname === '/login') {
          navigate(location.state?.from?.pathname || '/dashboard');
        }
      } catch (error) {
        localStorage.removeItem('token');
        if (location.pathname !== '/login') {
          navigate('/login', { state: { from: location } });
        }
      } finally {
        setLoading(false);
      }
    };

    initializeAuth();
  }, [location, navigate]);

  const login = async (credentials) => {
    try {
      const { data } = await authAPI.login(credentials);
      localStorage.setItem('token', data.access_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`;
      
      setUser(data.user);
      setIsAuthenticated(true);
      navigate(location.state?.from?.pathname || '/dashboard');
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const logout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('token');
      delete api.defaults.headers.common['Authorization'];
      setUser(null);
      setIsAuthenticated(false);
      navigate('/login');
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        login,
        logout
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};