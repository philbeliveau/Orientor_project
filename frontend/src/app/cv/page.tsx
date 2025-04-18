'use client';

import React, { useEffect, useState } from 'react';
import { Typography, Container, Paper, Box, CircularProgress } from '@mui/material';
import { useRouter } from 'next/navigation';
import dynamic from 'next/dynamic';
import axios from 'axios';
import MainLayout from '@/components/layout/MainLayout';

// Dynamically import the ResumeFrame component
const ResumeFrame = dynamic(() => import('@/components/ResumeFrame'), {
  loading: () => (
    <Box display="flex" justifyContent="center" alignItems="center" height="500px">
      <CircularProgress />
    </Box>
  ),
  ssr: false // Disable server-side rendering for this component
});

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function ResumePage() {
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchToken = async () => {
      try {
        // First try to get the token from localStorage
        const authToken = localStorage.getItem('access_token');
        console.log('Token from localStorage:', authToken ? 'Found' : 'Not found');
        
        if (!authToken) {
          // If no token is found, redirect to login
          console.log('No token found, redirecting to login');
          router.push('/login?redirect=/cv');
          return;
        }
        
        setToken(authToken);
        setLoading(false);
      } catch (err: any) {
        console.error('Error fetching auth token:', err);
        setError('Failed to authenticate. Please try logging in again.');
        setLoading(false);
      }
    };

    fetchToken();
  }, [router]);

  if (loading) {
    return (
      <MainLayout>
        <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
          <CircularProgress />
        </Box>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <Container maxWidth="lg" sx={{ py: 4 }}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h5" color="error" gutterBottom>
              {error}
            </Typography>
            <Typography>
              Please <a href="/login" style={{ color: 'blue', textDecoration: 'underline' }}>log in</a> to continue.
            </Typography>
          </Paper>
        </Container>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <Container maxWidth="xl" sx={{ py: 2, mt: 8 }}>
        <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Professional Resume Builder
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Build, customize, and export your professional resume. Your profile information has been prefilled to get you started.
          </Typography>
        </Paper>
        
        <Paper elevation={1} sx={{ height: 'calc(100vh - 300px)', minHeight: '500px', overflow: 'hidden' }}>
          {token && <ResumeFrame token={token} />}
        </Paper>
      </Container>
    </MainLayout>
  );
} 