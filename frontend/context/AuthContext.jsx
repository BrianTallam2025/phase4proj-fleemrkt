    // frontend/src/context/AuthContext.jsx
    import React, { createContext, useContext, useState, useEffect } from 'react';
    import { useNavigate } from 'react-router-dom';
    // Using the named import logoutUser from api.js
    import { logoutUser } from '../api'; // <--- NEW: Import logoutUser from api.js
    import axios from 'axios'; // Still used for direct login call

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
            // In a blacklisting setup, the local token expiration check is less critical
            // as the backend is the source of truth for revocation.
            // However, a simple check can still prevent unnecessary API calls with expired tokens.
            setUser(parsedUser);
            setIsAuthenticated(true);
          } catch (e) {
            console.error("Failed to parse stored user data:", e);
            clientSideLogout(); // Force client-side cleanup if data is corrupt
          }
        }
        setLoading(false);
      }, []);

      // Separate function for client-side cleanup only
      const clientSideLogout = () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
        setIsAuthenticated(false);
        navigate('/login');
      };


      const login = async (credentials) => {
        try {
          const response = await axios.post('http://localhost:5000/api/login', credentials);
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

      // Main logout function that calls backend
      const logout = async () => {
        try {
          await logoutUser(); // Call the backend logout endpoint
          console.log("Backend logout successful.");
        } catch (error) {
          console.error("Error blacklisting token on backend:", error.response?.data?.msg || error.message);
          // Even if backend call fails (e.g., network error, token already expired),
          // proceed with client-side logout for consistent UX.
        } finally {
          clientSideLogout(); // Always clean up client-side storage
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
    