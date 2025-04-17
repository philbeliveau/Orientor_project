'use client';
import LandingPage from '@/components/landing/LandingPage';
import MainLayout from '@/components/layout/MainLayout';

export default function Home() {
  return (
    <MainLayout showNav={false}>
      <LandingPage />
    </MainLayout>
  );
}