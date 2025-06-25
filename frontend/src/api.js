// frontend/src/api.js
// This file centralizes all API calls to your Flask backend using Axios.
import axios from 'axios';

// Dynamically set the base URL based on the environment.
// In development, it falls back to 'http://localhost:5000/api'.
// In production (e.g., on Render), you will set VITE_API_BASE_URL as an environment variable.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://phase4proj-fleemrkt.onrender.com/api';

// Create an Axios instance with the dynamic base URL for your Flask API
const api = axios.create({
    baseURL: API_BASE_URL,
});

// Add a request interceptor to include the JWT token in every request
// if it exists in localStorage.
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// --- User Authentication Endpoints (from user_auth_bp) ---
export const registerUser = (userData) => api.post('/register', userData);
export const loginUser = (credentials) => api.post('/login', credentials);
export const getProtectedData = () => api.get('/protected');
export const logoutUser = () => api.post('/logout');

// --- Item Endpoints (from item_bp) ---
export const createItem = (itemData) => api.post('/items', itemData);
export const getItems = () => api.get('/items');

// --- Request Endpoints (from request_bp) ---
export const createRequest = (item_id) => api.post('/requests', { item_id });
export const getSentRequests = () => api.get('/requests/sent');
export const getReceivedRequests = () => api.get('/requests/received');
export const updateRequestStatus = (request_id, status) => api.put(`/requests/${request_id}/status`, { status });


// --- Admin Endpoints (from admin_bp) ---
export const getAllUsers = () => api.get('/admin/users');
export const createAdminUser = (userData) => api.post('/admin/create_admin_user', userData);
export const adminGetAllRequests = () => api.get('/admin/requests');
export const adminDeleteRequest = (request_id) => api.delete(`/admin/requests/${request_id}`);


export default api;
