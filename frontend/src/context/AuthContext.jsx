// frontend/src/context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { logoutUser } from '../api.js'; // Critical: Must have .js
import axios from 'axios';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (token && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (e) {
        console.error("Failed to parse stored user data:", e);
        clientSideLogout();
      }
    }
    setLoading(false);
  }, []);

  const clientSideLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
    navigate('/login');
  };

  const login = async (credentials) => {
    try {
      const response = await axios.post('https://phase4proj-fleemrkt.onrender.com/api/login', credentials);
      const { access_token, user_id, username, role } = response.data;

      localStorage.setItem('token', access_token);
      const userData = { id: user_id, username, role };
      localStorage.setItem('user', JSON.stringify(userData));
      
      setUser(userData);
      setIsAuthenticated(true);
      return true;
    } catch (error) {
      console.error('Login failed:', error.response?.data?.msg || error.message);
      return false;
    }
  };

  const logout = async () => {
    try {
      await logoutUser();
      console.log("Backend logout successful.");
    } catch (error) {
      console.error("Error blacklisting token on backend:", error.response?.data?.msg || error.message);
    } finally {
      clientSideLogout();
    }
  };

  const authContextValue = {
    user,
    isAuthenticated,
    loading,
    login,
    logout,
  };

  return (
    <AuthContext.Provider value={authContextValue}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
export default AuthContext;