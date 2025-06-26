import axios from 'axios';

// Configure the base API client with enhanced defaults
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://phase4proj-fleemrkt.onrender.com/api',
  withCredentials: true, // Essential for cookie-based auth
  timeout: 15000, // Increased timeout for Render's free tier
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'X-Requested-With': 'XMLHttpRequest'
  }
});

// Enhanced request interceptor
api.interceptors.request.use(
  (config) => {
    // Automatically add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add CSRF protection if using sessions
    const csrfToken = getCookie('csrf_token');
    if (csrfToken) {
      config.headers['X-CSRF-TOKEN'] = csrfToken;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Comprehensive response interceptor
api.interceptors.response.use(
  (response) => {
    // Store new tokens if they're returned
    if (response.data?.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    return response;
  },
  async (error) => {
    const originalRequest = error.config;
    
    // Handle token expiration (401)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Attempt to refresh token
        const refreshResponse = await api.post('/refresh-token');
        const newToken = refreshResponse.data.access_token;
        
        // Store the new token
        localStorage.setItem('token', newToken);
        
        // Retry the original request
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // If refresh fails, clear storage and redirect
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login?session=expired';
        return Promise.reject(refreshError);
      }
    }
    
    // Handle other error cases
    if (error.response) {
      switch (error.response.status) {
        case 403: // Forbidden
          console.error('Access forbidden:', error.response.data);
          break;
          
        case 429: // Rate limited
          console.error('Rate limited:', error.response.data);
          break;
          
        case 500: // Server error
          console.error('Server error:', error.response.data);
          break;
          
        default:
          console.error('API Error:', error.response.data);
      }
      
      // Return a consistent error format
      return Promise.reject({
        status: error.response.status,
        message: error.response.data?.message || 'An error occurred',
        data: error.response.data
      });
    } else if (error.request) {
      // Network errors
      return Promise.reject({
        status: 0,
        message: 'Network error - please check your connection'
      });
    } else {
      // Configuration errors
      return Promise.reject({
        status: -1,
        message: 'Request configuration error'
      });
    }
  }
);

// Helper function for cookies
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// Auth API with enhanced error handling
export const authAPI = {
  login: async (credentials) => {
    try {
      const response = await api.post('/login', credentials);
      return {
        success: true,
        data: response.data,
        headers: response.headers
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: 'Login failed' }
      };
    }
  },
  
  logout: async () => {
    try {
      await api.post('/logout');
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: 'Logout failed' }
      };
    }
  },
  
  register: async (userData) => {
    try {
      const response = await api.post('/register', userData);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: 'Registration failed' }
      };
    }
  },
  
  refreshToken: async () => {
    try {
      const response = await api.post('/refresh-token');
      return {
        success: true,
        token: response.data.access_token
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: 'Token refresh failed' }
      };
    }
  },
  
  getCurrentUser: async () => {
    try {
      const response = await api.get('/users/me');
      return {
        success: true,
        user: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to fetch user' }
      };
    }
  }
};

// Enhanced items API
export const itemsAPI = {
  getAllItems: async (params = {}) => {
    try {
      const response = await api.get('/items', { params });
      return {
        success: true,
        items: response.data
      };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || { message: 'Failed to fetch items' }
      };
    }
  },
  
  // ... other item methods with the same pattern ...
};

// Consistent error handler
export const handleAPIError = (error) => {
  if (error.response) {
    return error.response.data?.message || 
           error.response.statusText || 
           `Request failed with status ${error.response.status}`;
  }
  return error.message || 'An unexpected error occurred';
};

export default api;