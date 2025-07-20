"use client";

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import axios from 'axios';

// Define API URL with fallback and trim any trailing spaces
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const cleanApiUrl = API_URL ? API_URL.trim() : '';

interface PeerDetails {
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

const PeerDetailPage: React.FC = () => {
  const [peer, setPeer] = useState<PeerDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const params = useParams();
  const peerId = params?.peerId as string;

  useEffect(() => {
    if (peerId) {
      fetchPeerDetails();
    }
  }, [peerId]);

  const fetchPeerDetails = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        router.push('/login');
        return;
      }

      // Fetch from compatible peers endpoint and find the specific peer
      const response = await axios.get<PeerDetails[]>(`${cleanApiUrl}/peers/compatible`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });

      const peerDetail = response.data.find((p: PeerDetails) => p.user_id.toString() === peerId);
      
      if (!peerDetail) {
        setError('Peer not found');
        return;
      }

      setPeer(peerDetail);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching peer details:', err);
      if (err.response?.status === 401) {
        router.push('/login');
        return;
      }
      setError('Failed to load peer details');
    } finally {
      setLoading(false);
    }
  };

  const handleStartChat = () => {
    if (peer) {
      router.push(`/chat/${peer.user_id}`);
    }
  };

  const formatCompatibilityScore = (score: number): string => {
    return `${Math.round(score * 100)}%`;
  };

  const getCompatibilityColor = (score: number): string => {
    if (score >= 0.8) return 'text-green-600 dark:text-green-400';
    if (score >= 0.6) return 'text-blue-600 dark:text-blue-400';
    if (score >= 0.4) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-orange-600 dark:text-orange-400';
  };

  const getCompatibilityBgColor = (score: number): string => {
    if (score >= 0.8) return 'bg-green-100 dark:bg-green-900/30 border-green-200 dark:border-green-800';
    if (score >= 0.6) return 'bg-blue-100 dark:bg-blue-900/30 border-blue-200 dark:border-blue-800';
    if (score >= 0.4) return 'bg-yellow-100 dark:bg-yellow-900/30 border-yellow-200 dark:border-yellow-800';
    return 'bg-orange-100 dark:bg-orange-900/30 border-orange-200 dark:border-orange-800';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg animate-pulse">
            <div className="p-8">
              <div className="h-8 bg-gray-200 dark:bg-gray-700 rounded mb-4"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded mb-2"></div>
              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-2/3 mb-8"></div>
              <div className="h-32 bg-gray-200 dark:bg-gray-700 rounded"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 text-center">
            <h1 className="text-2xl font-bold text-gray-800 dark:text-white mb-4">
              Error Loading Peer
            </h1>
            <p className="text-red-600 dark:text-red-400 mb-6">{error}</p>
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => router.push('/peers')}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Back to Peers
              </button>
              <button
                onClick={fetchPeerDetails}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!peer) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-6">
          <button
            onClick={() => router.push('/peers')}
            className="flex items-center text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 mb-4 transition-colors"
          >
            ← Back to Peers
          </button>
          <h1 className="text-3xl font-bold text-gray-800 dark:text-white">
            Peer Profile
          </h1>
        </div>

        <div className="grid gap-6">
          {/* Main Profile Card */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden">
            <div className="p-8">
              {/* Profile Header */}
              <div className="flex items-start justify-between mb-6">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-2xl">
                    {peer.name && peer.name.charAt(0) ? peer.name.charAt(0).toUpperCase() : '?'}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-800 dark:text-white">
                      {peer.name || 'Anonymous'}
                    </h2>
                    <p className="text-lg text-gray-600 dark:text-gray-400">
                      {peer.major}{peer.year ? `, Year ${peer.year}` : ''}
                    </p>
                    {peer.job_title && (
                      <p className="text-md text-gray-500 dark:text-gray-500">
                        {peer.job_title}{peer.industry ? ` at ${peer.industry}` : ''}
                      </p>
                    )}
                  </div>
                </div>
                
                {/* Compatibility Score */}
                <div className={`${getCompatibilityBgColor(peer.compatibility_score)} border rounded-lg p-4 text-center`}>
                  <div className={`text-2xl font-bold ${getCompatibilityColor(peer.compatibility_score)}`}>
                    {formatCompatibilityScore(peer.compatibility_score)}
                  </div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    Compatibility
                  </div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 mb-8">
                <button
                  onClick={handleStartChat}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors font-medium"
                >
                  Start Conversation
                </button>
                <button
                  onClick={() => {/* TODO: Implement connect functionality */}}
                  className="px-6 py-3 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors font-medium"
                >
                  Connect
                </button>
              </div>

              {/* Compatibility Analysis */}
              <div className="border-t border-gray-200 dark:border-gray-700 pt-6">
                <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">
                  Why You're Compatible
                </h3>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                    {peer.explanation}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Compatibility Breakdown */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-6">
              Compatibility Analysis
            </h3>
            
            <div className="grid md:grid-cols-2 gap-6">
              {/* Overall Score */}
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h4 className="font-semibold text-gray-800 dark:text-white mb-2">
                  Overall Compatibility
                </h4>
                <div className="flex items-center gap-3">
                  <div className="flex-1 bg-gray-200 dark:bg-gray-600 rounded-full h-3">
                    <div 
                      className="bg-blue-600 h-3 rounded-full transition-all duration-1000"
                      style={{ width: `${peer.compatibility_score * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {formatCompatibilityScore(peer.compatibility_score)}
                  </span>
                </div>
              </div>

              {/* Analysis Timestamp */}
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <h4 className="font-semibold text-gray-800 dark:text-white mb-2">
                  Analysis Date
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {(() => {
                    const date = new Date(peer.score_details.timestamp);
                    return isNaN(date.getTime()) ? 'Date invalide' : date.toLocaleDateString();
                  })()}
                </p>
              </div>
            </div>

            {/* Compatibility Factors */}
            <div className="mt-6">
              <h4 className="font-semibold text-gray-800 dark:text-white mb-3">
                Compatibility Factors
              </h4>
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  This compatibility score is based on shared career interests, complementary skills, 
                  aligned goals, personality compatibility, and career stage preferences. 
                  The algorithm analyzes multiple dimensions to suggest meaningful connections.
                </p>
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
            <h3 className="text-xl font-semibold text-gray-800 dark:text-white mb-6">
              Quick Actions
            </h3>
            
            <div className="grid md:grid-cols-3 gap-4">
              <button
                onClick={handleStartChat}
                className="flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded-lg transition-colors"
              >
                💬 Message
              </button>
              
              <button
                onClick={() => {/* TODO: Schedule meeting */}}
                className="flex items-center justify-center gap-2 bg-purple-600 hover:bg-purple-700 text-white px-4 py-3 rounded-lg transition-colors"
              >
                📅 Schedule
              </button>
              
              <button
                onClick={() => {/* TODO: Share contact */}}
                className="flex items-center justify-center gap-2 bg-orange-600 hover:bg-orange-700 text-white px-4 py-3 rounded-lg transition-colors"
              >
                📤 Share
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PeerDetailPage;