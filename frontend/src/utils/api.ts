/**
 * API utility functions for consistent API URL handling
 */

// Get the API URL from environment variables
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://orientor-backend-production.up.railway.app';

// Clean API URL (remove trailing spaces)
export const apiUrl = API_URL.trim();

// Helper to build full endpoint URLs
export const endpoint = (path: string): string => {
  // Make sure path starts with a slash
  const formattedPath = path.startsWith('/') ? path : `/${path}`;
  
  // If the path already includes /api, don't add it again
  if (formattedPath.startsWith('/api/')) {
    return `${apiUrl}${formattedPath.substring(4)}`; // Remove /api prefix since it's in the rewrite
  }
  
  return `${apiUrl}${formattedPath}`;
};

// Authentication helper
export const getAuthHeader = (): Record<string, string> => {
  // Ensure this works in both browser and server environments
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }
  return {};
};

// Debug/logging helper
export const logApiDetails = () => {
  console.log('API URL:', apiUrl);
  console.log('Environment:', process.env.NODE_ENV);
  console.log('Is production:', process.env.NODE_ENV === 'production');
  console.log('API URL from env:', process.env.NEXT_PUBLIC_API_URL);
}; 