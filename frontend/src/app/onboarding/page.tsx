'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ChatOnboard from '../../components/onboarding/ChatOnboard';
import { onboardingService } from '../../services/onboardingService';
import { useAuth } from '@/hooks/useAuth';

const OnboardingPage: React.FC = () => {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [needsOnboarding, setNeedsOnboarding] = useState(true);
  
  // Protect this route - redirect unauthenticated users to landing page
  const { isAuthenticated, isLoading: authLoading } = useAuth({ 
    redirectTo: '/', 
    redirectIfFound: false 
  });

  useEffect(() => {
    checkOnboardingStatus();
  }, []);

  const checkOnboardingStatus = async () => {
    try {
      const status = await onboardingService.getStatus();
      if (status.isComplete) {
        // User has already completed onboarding, redirect to dashboard
        console.log('Onboarding already complete, redirecting to dashboard');
        router.push('/dashboard');
        return;
      }
      setNeedsOnboarding(true);
    } catch (error) {
      console.error('Error checking onboarding status:', error);
      // If we can't check, assume they need onboarding
      setNeedsOnboarding(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOnboardingComplete = async (responses: any[]) => {
    try {
      console.log('Onboarding completed with responses:', responses);
      
      // CRITICAL: Mark onboarding as complete in the database
      console.log('Calling backend to mark onboarding complete...');
      await onboardingService.markOnboardingComplete();
      console.log('✅ Onboarding marked complete in database');
      
      // Update state to show completion message
      setNeedsOnboarding(false);
      
      // Show a success message briefly, then redirect to dashboard
      setTimeout(() => {
        console.log('Redirecting to dashboard after onboarding completion');
        router.push('/dashboard');
      }, 2000);
    } catch (error) {
      console.error('Error handling onboarding completion:', error);
      // Still redirect to dashboard even if there's an error
      console.log('Error occurred, but still redirecting to dashboard');
      router.push('/dashboard');
    }
  };

  // Show loading while checking authentication or onboarding status
  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-text-secondary">Loading onboarding...</p>
        </div>
      </div>
    );
  }

  // Don't render if not authenticated (will be redirected)
  if (!isAuthenticated) {
    return null;
  }

  if (!needsOnboarding) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Welcome to Navigo!</h2>
          <p className="text-text-secondary">Onboarding complete. Taking you to your dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <ChatOnboard onComplete={handleOnboardingComplete} />
    </div>
  );
};

export default OnboardingPage;