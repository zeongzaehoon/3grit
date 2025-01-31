import { APIClient } from '../types';

export const api = new APIClient('http://localhost:8000');

// Initialize token from localStorage if exists
const savedToken = localStorage.getItem('token');
if (savedToken) {
  api.setToken(savedToken);
} 