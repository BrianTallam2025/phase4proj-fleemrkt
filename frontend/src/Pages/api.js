import axios from 'axios';

// Create an Axios instance with a base URL for your Flask API
const api = axios.create({
    baseURL: 'http://localhost:5000/api', // Flask backend runs on port 5000
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

// --- User Authentication Endpoints ---
export const registerUser = (userData) => api.post('/register', userData);
// Login is handled directly in AuthContext to manage token storage
export const getProtectedData = () => api.get('/protected');

// --- Item Endpoints ---
export const createItem = (itemData) => api.post('/items', itemData);
export const getItems = () => api.get('/items');

// --- Request Endpoints ---
export const createRequest = (item_id) => api.post('/requests', { item_id });
export const getSentRequests = () => api.get('/requests/sent');
export const getReceivedRequests = () => api.get('/requests/received');
export const updateRequestStatus = (request_id, status) => api.put(`/requests/${request_id}/status`, { status });

// --- Admin Endpoints ---
export const getAllUsers = () => api.get('/admin/users');
export const createAdminUser = (userData) => api.post('/admin/create_admin_user', userData);
export const adminGetAllRequests = () => api.get('/admin/requests');
export const adminDeleteRequest = (request_id) => api.delete(`/admin/requests/${request_id}`);

export default api;