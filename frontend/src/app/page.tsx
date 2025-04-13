'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ChatInterface from '@/components/chat/ChatInterface';
import MainLayout from '@/components/layout/MainLayout';
import LandingPage from '@/components/landing/LandingPage';

export default function Home() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('access_token');
    setIsLoggedIn(!!token);
    setLoading(false);
  }, []);

  if (loading) {
    return null; // Show nothing while checking auth status
  }

  return (
    <MainLayout showNav={isLoggedIn}>
      <div className="space-y-6">
        {isLoggedIn ? (
          <ChatInterface />
        ) : (
          <LandingPage />
        )}
      </div>
    </MainLayout>
  );
}