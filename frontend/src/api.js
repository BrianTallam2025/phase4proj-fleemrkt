import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://phase4proj-fleemrkt.onrender.com/api',
  withCredentials: true,
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
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
  response => response,
  async error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login?session=expired';
    }
    return Promise.reject(error);
  }
);

// Explicit exports (CRITICAL FIX)
export const loginUser = (credentials) => api.post('/login', credentials);
export const logoutUser = () => api.post('/logout');
export const registerUser = (userData) => api.post('/register', userData);
export const refreshToken = () => api.post('/refresh-token');
export const getCurrentUser = () => api.get('/users/me'); // THIS WAS MISSING

// Grouped exports
export const authAPI = {
  login: loginUser,
  logout: logoutUser,
  register: registerUser,
  refreshToken,
  getCurrentUser
};

export default api;