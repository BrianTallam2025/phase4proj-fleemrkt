// frontend/src/api.js
// This file sets up an Axios instance for making API requests.
// It dynamically determines the backend URL based on environment variables,
// and automatically attaches the JWT token for authenticated requests.

import axios from 'axios';

// Dynamically set the base URL for API requests.
// During local development, it will fall back to 'http://localhost:5000/api'.
// In production (e.g., on Vercel), `import.meta.env.VITE_API_BASE_URL` will be
// read from the environment variable configured on Vercel (e.g.,
// https://your-backend-name.onrender.com/api).
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

// Create an Axios instance with the determined base URL.
const api = axios.create({
    baseURL: API_BASE_URL,
});

// Add a request interceptor to include the JWT token in every outgoing request.
// This ensures that authenticated routes on the backend receive the necessary token.
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token'); // Retrieve token from local storage
        if (token) {
            // If a token exists, add it to the Authorization header as a Bearer token.
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config; // Return the modified configuration
    },
    (error) => {
        // Handle any errors that occur before the request is sent.
        return Promise.reject(error);
    }
);

// --- Exported API functions for various endpoints ---
// These functions use the 'api' Axios instance, so they automatically
// use the correct base URL and include the JWT token.

// User Authentication Endpoints (from auth blueprint)
export const registerUser = (userData) => api.post('/register', userData);
export const loginUser = (credentials) => api.post('/login', credentials);
export const getProtectedData = () => api.get('/protected');
export const logoutUser = () => api.post('/logout'); // Note: This calls the backend logout endpoint

// Item Endpoints (from item blueprint)
export const createItem = (itemData) => api.post('/items', itemData);
export const getItems = () => api.get('/items');
export const getItemById = (id) => api.get(`/items/${id}`); // Example: If you have a get by ID route

// Request Endpoints (from request blueprint)
export const createRequest = (item_id) => api.post('/requests', { item_id });
export const getSentRequests = () => api.get('/requests/sent');
export const getReceivedRequests = () => api.get('/requests/received');
export const updateRequestStatus = (request_id, status) => api.put(`/requests/${request_id}/status`, { status });

// Admin Endpoints (from admin blueprint)
export const getAllUsers = () => api.get('/admin/users');
export const createAdminUser = (userData) => api.post('/admin/create_admin_user', userData);
export const adminGetAllRequests = () => api.get('/admin/requests');
export const adminDeleteRequest = (request_id) => api.delete(`/admin/requests/${request_id}`);

// Export the configured Axios instance as default for direct use if needed.
export default api;
