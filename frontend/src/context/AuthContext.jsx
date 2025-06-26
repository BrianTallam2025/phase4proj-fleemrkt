import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  loginUser,
  logoutUser,
  getCurrentUser,
  refreshToken
} from '../api'; // Now properly imported

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          const userData = await getCurrentUser(); // Now works
          setUser(userData.data);
          setIsAuthenticated(true);
        }
      } catch (error) {
        console.error('Auth init error:', error);
        localStorage.removeItem('token');
      } finally {
        setLoading(false);
      }
    };
    initializeAuth();
  }, []);

  const login = async (credentials) => {
    try {
      const response = await loginUser(credentials);
      localStorage.setItem('token', response.data.access_token);
      setUser(response.data.user);
      setIsAuthenticated(true);
      navigate(location.state?.from?.pathname || '/dashboard');
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = async () => {
    await logoutUser();
    localStorage.removeItem('token');
    setUser(null);
    setIsAuthenticated(false);
    navigate('/login');
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);