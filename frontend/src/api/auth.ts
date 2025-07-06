import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface User {
  id: number;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Token management
export const getToken = (): string | null => {
  return localStorage.getItem('access_token');
};

export const setToken = (token: string): void => {
  localStorage.setItem('access_token', token);
};

export const removeToken = (): void => {
  localStorage.removeItem('access_token');
};

export const isAuthenticated = (): boolean => {
  const token = getToken();
  if (!token) return false;

  try {
    // Check if token is expired
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Date.now() / 1000;
    return payload.exp > currentTime;
  } catch (error) {
    return false;
  }
};

// Setup axios interceptor to add token to requests
axios.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Setup axios interceptor to handle auth errors
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      removeToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication API calls
export async function login(credentials: LoginData): Promise<AuthResponse> {
  const formData = new FormData();
  formData.append('username', credentials.email);  // OAuth2 uses 'username' field
  formData.append('password', credentials.password);

  const response = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
}

export async function register(userData: RegisterData): Promise<User> {
  const response = await axios.post(`${API_BASE_URL}/auth/register`, userData);
  return response.data;
}

export async function getCurrentUser(): Promise<User> {
  const response = await axios.get(`${API_BASE_URL}/auth/me`);
  return response.data;
}

export async function logout(): Promise<void> {
  removeToken();
  // Could also call a logout endpoint if you implement one
}
