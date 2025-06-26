// frontend/src/context/AuthContext.jsx
// This context manages user authentication state (login, logout, user data).

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
// CRITICAL: Import the 'api' instance and specific logoutUser function from api.js.
// All backend communication for auth should go through 'api' to leverage base URL and interceptors.
import api, { logoutUser } from '../api.js'; 

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Effect to initialize authentication state from local storage on component mount.
  useEffect(() => {
    const token = localStorage.getItem('token');
    const storedUser = localStorage.getItem('user');

    if (token && storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (e) {
        // Log parsing errors and perform a client-side logout to clear corrupted data.
        console.error("Failed to parse stored user data:", e);
        clientSideLogout();
      }
    }
    setLoading(false); // Set loading to false once initial check is done.
  }, []); // Empty dependency array ensures this runs only once on mount.

  // Helper function for client-side logout (clears local storage).
  const clientSideLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
    navigate('/login'); // Redirect to login page after logout.
  };

  // Function to handle user login.
  const login = async (credentials) => {
    try {
      // Use the 'api' instance for the login request. This ensures consistency
      // with base URL configuration and future interceptors (though not needed for login itself).
      const response = await api.post('/login', credentials); 
      const { access_token, user_id, username, role } = response.data;

      // Store token and user data in local storage.
      localStorage.setItem('token', access_token);
      const userData = { id: user_id, username, role };
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Update React state.
      setUser(userData);
      setIsAuthenticated(true);
      return true; // Indicate successful login.
    } catch (error) {
      // Log and return false on login failure.
      console.error('Login failed:', error.response?.data?.msg || error.message);
      return false;
    }
  };

  // Function to handle user logout.
  const logout = async () => {
    try {
      // Call the backend logout endpoint to blacklist the token.
      await logoutUser(); 
      console.log("Backend logout successful.");
    } catch (error) {
      // Log errors during backend token blacklisting, but proceed with client-side logout.
      console.error("Error blacklisting token on backend:", error.response?.data?.msg || error.message);
    } finally {
      // Always perform client-side logout regardless of backend success/failure.
      clientSideLogout();
    }
  };

  // Value provided by the AuthContext to its consumers.
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

// Custom hook to easily consume the AuthContext.
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext; // Export AuthContext itself (useful for testing or advanced scenarios)
