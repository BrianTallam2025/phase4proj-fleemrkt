import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Home() {
  const { isAuthenticated, user } = useAuth();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-blue-500 to-purple-600 text-white p-4">
      <div className="card text-center text-gray-800">
        <h1 className="text-4xl font-bold mb-4">Welcome to Hyperlocal Share!</h1>
        <p className="text-xl mb-8">Your community marketplace for sharing used goods.</p>
        
        {isAuthenticated ? (
          <div className="space-y-4">
            <p className="text-lg">You are logged in as <span className="font-semibold text-blue-600">{user?.username}</span>.</p>
            <Link to="/dashboard" className="btn btn-primary block w-full">
              Go to Dashboard
            </Link>
            {user?.role === 'admin' && (
              <Link to="/admin" className="btn btn-secondary block w-full mt-2">
                Go to Admin Panel
              </Link>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            <Link to="/login" className="btn btn-primary block w-full">
              Login
            </Link>
            <Link to="/register" className="btn btn-secondary block w-full mt-2">
              Register
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}

export default Home;