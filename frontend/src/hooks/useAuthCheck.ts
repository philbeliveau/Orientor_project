'use client';
import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { logger } from '@/utils/logger';

export function useAuthCheck(showNav: boolean = true) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  // Public routes that don't require authentication
  const publicRoutes = ['/', '/login', '/register', '/landing', '/test-page'];
  const isPublicRoute = pathname ? publicRoutes.includes(pathname) : false;

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token') || '';
    logger.debug('Auth check - Token:', token ? 'Found' : 'Not found', 'Pathname:', pathname);
    
    // Check authentication properly
    if (!token && !isPublicRoute && showNav) {
      logger.debug('No token found, redirecting to login');
      router.push('/login');
      return;
    }
    
    // Set proper logged in state based on token
    const loggedIn = !!token;
    logger.debug('Setting isLoggedIn to:', loggedIn);
    setIsLoggedIn(loggedIn);
    setIsLoading(false);
  }, [router, isPublicRoute, showNav, pathname]);

  return {
    isLoggedIn,
    isLoading,
    isPublicRoute
  };
}