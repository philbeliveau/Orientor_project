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

export default function SuggestedPeersPage() {
  const router = useRouter();
  const [peers, setPeers] = useState<PeerProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPeers = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const token = localStorage.getItem('access_token');
        if (!token) {
          router.push('/login');
          return;
        }
        
        const response = await axios.get<PeerProfile[]>(`${cleanApiUrl}/peers/suggested`, {
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
    
    fetchPeers();
  }, [router]);
  
  // Function to format similarity score as percentage
  const formatSimilarity = (value: number) => {
    return `${Math.round(value * 100)}%`;
  };

  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-neutral-darkest">Suggested Peers</h2>
          <div className="text-sm text-neutral-gray">
            Students with similar interests and backgrounds
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
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {peers.map((peer) => (
              <div key={peer.user_id} className="card hover:shadow-md transition-shadow">
                <div className="flex flex-col h-full">
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="text-xl font-semibold text-secondary-purple">
                        {peer.name || `User ${peer.user_id}`}
                      </h3>
                      {peer.major && (
                        <p className="text-neutral-gray">
                          {peer.major}{peer.year ? `, Year ${peer.year}` : ''}
                        </p>
                      )}
                    </div>
                    <div className="bg-secondary-teal bg-opacity-10 text-secondary-teal px-2 py-1 rounded text-sm font-medium">
                      {formatSimilarity(peer.similarity)} Match
                    </div>
                  </div>
                  
                  <div className="mt-4 flex-grow">
                    {peer.interests && (
                      <div className="mb-2">
                        <span className="text-sm font-medium text-neutral-gray">Interests: </span>
                        <span className="text-sm text-neutral-lightgray">{peer.interests}</span>
                      </div>
                    )}
                    {peer.hobbies && (
                      <div>
                        <span className="text-sm font-medium text-neutral-gray">Hobbies: </span>
                        <span className="text-sm text-neutral-lightgray">{peer.hobbies}</span>
                      </div>
                    )}
                  </div>
                  
                  <div className="mt-4 pt-4 border-t border-neutral-lightest">
                    <Link 
                      href={`/chat/${peer.user_id}`}
                      className="inline-flex items-center justify-center w-full px-4 py-2 bg-secondary-purple bg-opacity-10 hover:bg-opacity-20 text-secondary-purple rounded font-medium transition-colors"
                    >
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                      </svg>
                      Start Conversation
                    </Link>
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