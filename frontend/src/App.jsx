// frontend/src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from "./context/AuthContext.jsx";
import Home from './pages/Home.jsx';
import Login from './pages/Login.jsx';
import Register from './pages/Register.jsx';
import Dashboard from './pages/Dashboard.jsx';
import Admin from './pages/Admin.jsx';
import './index.css';

// PrivateRoute component to protect routes
// This component also uses useAuth, so it needs to be inside AuthProvider,
// which in turn needs to be inside Router.
const PrivateRoute = ({ children, allowedRoles }) => {
  const { isAuthenticated, loading, user } = useAuth();

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center text-xl font-semibold">Loading authentication...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user?.role)) {
    alert('Access Denied: You do not have the required role.');
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

function App() {
  return (
    // CRITICAL CHANGE: AuthProvider must be inside Router
    <Router>
      <AuthProvider> {/* <-- MOVED AuthProvider INSIDE Router */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          <Route 
            path="/dashboard" 
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            } 
          />
          <Route 
            path="/admin" 
            element={
              <PrivateRoute allowedRoles={['admin']}>
                <Admin />
              </PrivateRoute>
            } 
          />

          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </AuthProvider> {/* <-- CLOSING TAG MOVED */}
    </Router>
  );
}

export default App;
