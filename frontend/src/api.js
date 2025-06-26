import axios from 'axios';
import { handleAPIError } from './utils/errorHandler';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://phase4proj-fleemrkt.onrender.com/api',
  withCredentials: true,
  timeout: 20000, // 20 seconds timeout for Render's free tier
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
});

// Request interceptor
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => Promise.reject(error));

// Response interceptor
api.interceptors.response.use(
  response => {
    // Store new tokens if present in response
    if (response.data?.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    return response;
  },
  async error => {
    const originalRequest = error.config;
    
    // Handle token expiration/validation errors
    if ((error.response?.status === 401 || error.response?.status === 422) && 
        !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const { data } = await api.post('/refresh-token');
        localStorage.setItem('token', data.access_token);
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('token');
        window.location.href = '/login?session=expired';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(handleAPIError(error));
  }
);

export const authAPI = {
  login: credentials => api.post('/login', credentials),
  logout: () => api.post('/logout'),
  register: userData => api.post('/register', userData),
  refreshToken: () => api.post('/refresh-token'),
  getCurrentUser: () => api.get('/users/me')
};

export const itemsAPI = {
  getAllItems: params => api.get('/items', { params }),
  createItem: itemData => api.post('/items', itemData),
  updateItem: (id, itemData) => api.patch(`/items/${id}`, itemData),
  deleteItem: id => api.delete(`/items/${id}`)
};

export default api;