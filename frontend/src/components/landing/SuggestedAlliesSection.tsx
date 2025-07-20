"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

// Define API URL with fallback and trim any trailing spaces
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const cleanApiUrl = API_URL ? API_URL.trim() : '';

interface HomepagePeer {
  user_id: number;
  name: string;
  major: string;
  year?: number;
  compatibility_score: number;
  brief_explanation: string;
  avatar_url?: string;
}

interface SuggestedAlliesSectionProps {
  className?: string;
}

const SuggestedAlliesSection: React.FC<SuggestedAlliesSectionProps> = ({ className = "" }) => {
  const [peers, setPeers] = useState<HomepagePeer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchHomepagePeers();
  }, []);

  const fetchHomepagePeers = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setError('Authentication required');
        router.push('/login');
        return;
      }

      const response = await axios.get<HomepagePeer[]>(`${cleanApiUrl}/peers/homepage`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      setPeers(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching homepage peers:', err);
      if (err.response?.status === 401) {
        router.push('/login');
        return;
      }
      setError('Failed to load peer suggestions');
    } finally {
      setLoading(false);
    }
  };

  const handlePeerClick = (peerId: number) => {
    router.push(`/peers/${peerId}`);
  };

  const handleViewAllClick = () => {
    router.push('/peers');
  };

  const formatCompatibilityScore = (score: number): string => {
    return `${Math.round(score * 100)}%`;
  };

  if (loading) {
    return (
      <section className={`suggested-allies-section ${className}`}>
        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white">
              Suggested Allies
            </h2>
          </div>
          <div className="flex gap-4 overflow-x-auto">
            {[1, 2, 3].map((i) => (
              <div
                key={i}
                className="flex-shrink-0 w-80 h-40 bg-gray-200 dark:bg-gray-700 rounded-lg animate-pulse"
              />
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className={`suggested-allies-section ${className}`}>
        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white">
              Suggested Allies
            </h2>
          </div>
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-center">
            <p className="text-red-600 dark:text-red-400">{error}</p>
            <button
              onClick={fetchHomepagePeers}
              className="mt-2 px-4 py-2 bg-red-100 dark:bg-red-800 text-red-700 dark:text-red-200 rounded hover:bg-red-200 dark:hover:bg-red-700 transition-colors"
            >
              Retry
            </button>
          </div>
        </div>
      </section>
    );
  }

  if (peers.length === 0) {
    return (
      <section className={`suggested-allies-section ${className}`}>
        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-800 dark:text-white">
              Suggested Allies
            </h2>
          </div>
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-8 text-center">
            <p className="text-blue-600 dark:text-blue-400 mb-4">
              No peer suggestions available yet. Complete your profile to get personalized recommendations.
            </p>
            <button
              onClick={() => router.push('/profile')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Complete Profile
            </button>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className={`suggested-allies-section ${className}`}>
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800 dark:text-white">
            Suggested Allies
          </h2>
          <button
            onClick={handleViewAllClick}
            className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 font-medium transition-colors"
          >
            View All →
          </button>
        </div>
        
        <div className="flex gap-4 overflow-x-auto pb-4">
          {peers.map((peer) => (
            <div
              key={peer.user_id}
              onClick={() => handlePeerClick(peer.user_id)}
              className="flex-shrink-0 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-all duration-300 cursor-pointer border border-gray-200 dark:border-gray-700 hover:border-blue-300 dark:hover:border-blue-600"
            >
              <div className="p-6">
                {/* Header with avatar and basic info */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                      {peer.name && peer.name.charAt(0) ? peer.name.charAt(0).toUpperCase() : '?'}
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
                        {peer.name || 'Anonymous'}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {peer.major}{peer.year ? `, Year ${peer.year}` : ''}
                      </p>
                    </div>
                  </div>
                  <div className="flex flex-col items-end">
                    <div className="bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 px-2 py-1 rounded-full text-xs font-medium">
                      {formatCompatibilityScore(peer.compatibility_score)} Match
                    </div>
                  </div>
                </div>

                {/* Compatibility explanation */}
                <div className="mb-4">
                  <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
                    {peer.brief_explanation}
                  </p>
                </div>

                {/* Action button */}
                <div className="flex justify-between items-center">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      router.push(`/chat/${peer.user_id}`);
                    }}
                    className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors font-medium mr-2"
                  >
                    Start Chat
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handlePeerClick(peer.user_id);
                    }}
                    className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    View
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Call-to-action if only few peers */}
        {peers.length < 3 && (
          <div className="mt-6 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 text-center">
            <p className="text-yellow-700 dark:text-yellow-300 mb-2">
              Want more peer suggestions? 
            </p>
            <button
              onClick={() => router.push('/hexaco-test')}
              className="text-yellow-800 dark:text-yellow-200 font-medium hover:underline"
            >
              Complete personality assessment
            </button>
          </div>
        )}
      </div>
    </section>
  );
};

export default SuggestedAlliesSection;