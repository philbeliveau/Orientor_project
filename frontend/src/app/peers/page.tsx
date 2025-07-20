'use client';
import { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import axios from 'axios';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

// Define API URL with fallback and trim any trailing spaces
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const cleanApiUrl = API_URL ? API_URL.trim() : '';

interface PeerProfile {
  user_id: number;
  name: string | null;
  major: string | null;
  year: number | null;
  similarity: number;
  hobbies: string | null;
  interests: string | null;
}

interface EnhancedPeerProfile {
  user_id: number;
  name: string;
  major: string;
  year?: number;
  job_title?: string;
  industry?: string;
  compatibility_score: number;
  explanation: string;
  score_details: {
    overall_compatibility: number;
    timestamp: string;
  };
}

export default function SuggestedPeersPage() {
  const router = useRouter();
  const [peers, setPeers] = useState<EnhancedPeerProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'compatible' | 'similar'>('compatible');

  useEffect(() => {
    fetchPeers();
  }, [router, viewMode]);

  const fetchPeers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('access_token');
      if (!token) {
        router.push('/login');
        return;
      }
      
      const endpoint = viewMode === 'compatible' ? '/peers/compatible' : '/peers/suggested';
      const response = await axios.get<EnhancedPeerProfile[]>(`${cleanApiUrl}${endpoint}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      setPeers(response.data);
    } catch (err: any) {
      console.error('Error fetching peers:', err);
      setError(err.response?.data?.detail || 'Failed to load suggested peers');
    } finally {
      setLoading(false);
    }
  };

  const refreshSuggestions = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) return;

      await axios.post(`${cleanApiUrl}/peers/refresh`, {}, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      // Refresh the peer list
      await fetchPeers();
    } catch (err: any) {
      console.error('Error refreshing suggestions:', err);
      setError('Failed to refresh suggestions');
    }
  };
  
  // Function to format similarity score as percentage
  const formatSimilarity = (value: number) => {
    return `${Math.round(value * 100)}%`;
  };

  const getCompatibilityColor = (score: number): string => {
    if (score >= 0.8) return 'bg-green-100 text-green-800';
    if (score >= 0.6) return 'bg-blue-100 text-blue-800';
    if (score >= 0.4) return 'bg-yellow-100 text-yellow-800';
    return 'bg-orange-100 text-orange-800';
  };

  return (
    <MainLayout>
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-neutral-darkest">Peer Connections</h2>
            <p className="text-neutral-gray mt-1">
              {viewMode === 'compatible' 
                ? 'AI-powered compatibility analysis for meaningful connections'
                : 'Students with similar interests and backgrounds'
              }
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            {/* View Mode Toggle */}
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('compatible')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'compatible'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-blue-600'
                }`}
              >
                Compatible
              </button>
              <button
                onClick={() => setViewMode('similar')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  viewMode === 'similar'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-blue-600'
                }`}
              >
                Similar
              </button>
            </div>
            
            {/* Refresh Button */}
            <button
              onClick={refreshSuggestions}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
            >
              Refresh
            </button>
          </div>
        </div>
        
        {loading ? (
          <div className="flex justify-center py-10">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-secondary-purple"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        ) : peers.length === 0 ? (
          <div className="text-center py-10">
            <p className="text-neutral-gray">No suggested peers found.</p>
            <p className="mt-2 text-sm text-neutral-gray">
              Complete your profile to get matched with similar students.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {peers.map((peer) => (
              <div key={peer.user_id} className="bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-300 border border-gray-200 overflow-hidden">
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                        {peer.name && peer.name.charAt(0) ? peer.name.charAt(0).toUpperCase() : '?'}
                      </div>
                      <div>
                        <h3 className="text-xl font-semibold text-gray-800">
                          {peer.name || `User ${peer.user_id}`}
                        </h3>
                        <p className="text-gray-600">
                          {peer.major}{peer.year ? `, Year ${peer.year}` : ''}
                        </p>
                        {peer.job_title && (
                          <p className="text-sm text-gray-500">
                            {peer.job_title}{peer.industry ? ` • ${peer.industry}` : ''}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                      viewMode === 'compatible' 
                        ? getCompatibilityColor(peer.compatibility_score || 0)
                        : 'bg-secondary-teal bg-opacity-10 text-secondary-teal'
                    }`}>
                      {formatSimilarity(peer.compatibility_score || 0)} Match
                    </div>
                  </div>
                  
                  {/* Enhanced explanation for compatible view */}
                  {viewMode === 'compatible' && peer.explanation && (
                    <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-700 leading-relaxed">
                        {peer.explanation}
                      </p>
                    </div>
                  )}
                  
                  <div className="flex gap-3">
                    <Link 
                      href={`/chat/${peer.user_id}`}
                      className="flex-1 inline-flex items-center justify-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
                    >
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                      Start Chat
                    </Link>
                    
                    {viewMode === 'compatible' && (
                      <Link
                        href={`/peers/${peer.user_id}`}
                        className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
                      >
                        View Details
                      </Link>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </MainLayout>
  );
} 