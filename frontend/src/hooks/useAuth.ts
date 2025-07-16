'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface UseAuthOptions {
  redirectTo?: string;
  redirectIfFound?: boolean;
}

export function useAuth({ redirectTo = '/', redirectIfFound = false }: UseAuthOptions = {}) {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const checkAuth = () => {
      try {
        const token = localStorage.getItem('access_token');
        const isAuth = !!token;
        
        console.log('🔐 Auth check:', { 
          isAuth, 
          redirectTo, 
          redirectIfFound,
          hasToken: !!token 
        });

        setIsAuthenticated(isAuth);

        // Redirect logic
        if (redirectIfFound && isAuth) {
          // Redirect authenticated users away (e.g., from login page)
          console.log('🔄 Redirecting authenticated user to:', redirectTo);
          router.push(redirectTo);
        } else if (!redirectIfFound && !isAuth) {
          // Redirect unauthenticated users (e.g., from protected pages)
          console.log('🔄 Redirecting unauthenticated user to:', redirectTo);
          router.push(redirectTo);
        }
      } catch (error) {
        console.error('Error checking authentication:', error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router, redirectTo, redirectIfFound]);

  const login = (token: string, userId?: string) => {
    localStorage.setItem('access_token', token);
    if (userId) {
      localStorage.setItem('user_id', userId);
    }
    setIsAuthenticated(true);
    console.log('✅ User logged in successfully');
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_id');
    setIsAuthenticated(false);
    console.log('👋 User logged out');
    router.push('/');
  };

  return {
    isAuthenticated,
    isLoading,
    login,
    logout
  };
}