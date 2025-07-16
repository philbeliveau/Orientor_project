'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import LandingPage from '@/components/landing/LandingPage';

function HomePageContent() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const checkAuth = () => {
      try {
        const token = localStorage.getItem('access_token');
        console.log('🔍 Root route auth check - Token exists:', !!token);
        
        // If user is authenticated, redirect to dashboard
        if (token) {
          console.log('🔄 User authenticated, redirecting to dashboard');
          router.push('/dashboard');
          return;
        }
        
        // If not authenticated, show landing page
        setIsAuthenticated(false);
      } catch (error) {
        console.error('Error checking authentication:', error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [router, searchParams]);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="ml-3 text-gray-600">Loading...</p>
      </div>
    );
  }

  // Always show landing page for unauthenticated users at root
  console.log('🏠 Showing landing page for unauthenticated user');
  return <LandingPage />;
}

export default function HomePage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="ml-3 text-gray-600">Loading...</p>
      </div>
    }>
      <HomePageContent />
    </Suspense>
  );
}