'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import LandingPage from '@/components/landing/LandingPage';
import Dashboard from './dashboard/page';

function HomePageContent() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [forceLanding, setForceLanding] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    const checkAuth = () => {
      try {
        // Check if user wants to force landing page
        const forceLanding = searchParams.get('landing') === 'true';
        if (forceLanding) {
          setForceLanding(true);
          setIsAuthenticated(false);
          setIsLoading(false);
          return;
        }

        const token = localStorage.getItem('access_token');
        console.log('🔍 Auth check - Token exists:', !!token);
        setIsAuthenticated(!!token);
      } catch (error) {
        console.error('Error checking authentication:', error);
        setIsAuthenticated(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAuth();
  }, [searchParams]);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="ml-3 text-gray-600">Checking authentication...</p>
      </div>
    );
  }

  // Show landing page for unauthenticated users or forced landing
  if (!isAuthenticated || forceLanding) {
    return <LandingPage />;
  }

  // Show dashboard for authenticated users
  console.log('🏠 Showing dashboard for authenticated user');
  return <Dashboard />;
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