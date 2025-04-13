/**
 * API utility functions for consistent API URL handling
 */

// Get the API URL from environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Clean API URL (remove trailing spaces)
export const apiUrl = API_URL.trim();

// Helper to build full endpoint URLs
export const endpoint = (path: string): string => {
  // Make sure path starts with a slash
  const formattedPath = path.startsWith('/') ? path : `/${path}`;
  return `${apiUrl}${formattedPath}`;
};

// Authentication helper
export const getAuthHeader = (): Record<string, string> => {
  const token = localStorage.getItem('access_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// Debug/logging helper
export const logApiDetails = () => {
  console.log('API URL:', apiUrl);
  console.log('Environment:', process.env.NODE_ENV);
  console.log('Is production:', process.env.NODE_ENV === 'production');
}; 