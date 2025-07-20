'use client';

import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import Link from 'next/link';
import UserCard from '@/components/ui/UserCard';
import DailyQuestionCard from '@/components/ui/DailyQuestionCard';
import ColorfulDailyQuestionCard from '@/components/ui/ColorfulDailyQuestionCard';
import ColorfulCareerGoalCard from '@/components/ui/ColorfulCareerGoalCard';
import EnhancedClassesCard from '@/components/classes/EnhancedClassesCard';
import Calendar from '@/components/ui/Calendar';
import EventsNotes from '@/components/ui/EventsNotes';
import JobRecommendationVerticalList from '@/components/jobs/JobRecommendationVerticalList';
import PersonalityCard from '@/components/ui/PersonalityCard';
import SkillShowcase from '@/components/ui/SkillShowcase';
import StarConstellation from '@/components/ui/StarConstellation';
import VectorSearchCard from '@/components/search/VectorSearchCard';
import CareerGoalCard from '@/components/ui/CareerGoalCard';
import hollandTestService, { ScoreResponse } from '@/services/hollandTestService';
import { getJobRecommendations } from '@/services/api';
import { Job } from '@/components/jobs/JobCard';
import { fetchAllUserNotes, Note } from '@/services/spaceService';
import axios from 'axios';
import SaveJobButton from '@/components/common/SaveJobButton';

interface JobRecommendationsResponse {
  recommendations: Job[];
  user_id: number;
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

export default function Dashboard() {
  const router = useRouter();
  
  // Protect this route - redirect unauthenticated users to landing page
  const { isAuthenticated, isLoading: authLoading } = useAuth({ 
    redirectTo: '/', 
    redirectIfFound: false 
  });
  
  // Define API URL with fallback and trim any trailing spaces
  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const cleanApiUrl = API_URL ? API_URL.trim() : '';
  
  // State
  const [hollandResults, setHollandResults] = useState<ScoreResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [jobRecommendations, setJobRecommendations] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [jobsError, setJobsError] = useState<string | null>(null);
  const [currentUserId, setCurrentUserId] = useState<number | undefined>(undefined);
  const [peers, setPeers] = useState<EnhancedPeerProfile[]>([]);
  const [peersLoading, setPeersLoading] = useState(true);
  const [peersError, setPeersError] = useState<string | null>(null);
  const [userNotes, setUserNotes] = useState<Note[]>([]);
  const [notesLoading, setNotesLoading] = useState(true);
  const [notesError, setNotesError] = useState<string | null>(null);

  // Sample user data
  const userData = {
    name: 'Philippe B.',
    role: 'Étudiant Msc. in Data Science',
    level: 3,
    avatarUrl: '/Avatar.PNG',
    skills: ['UI Design', 'JavaScript', 'React', 'Node.js'],
    totalXP: 250,
  };

  // Personality navigation items
  const personalityItems = [
    { name: 'Holland Test', icon: 'Personality', path: '/holland-test' },
    { name: 'HEXACO Test', icon: 'Brain', path: '/hexaco-test/select' },
    { name: 'Self-Reflection', icon: 'Reflection', path: '/self-reflection' },
    { name: 'Holland Results', icon: 'Personality', path: '/profile/holland-results' },
    { name: 'HEXACO Results', icon: 'Brain', path: '/profile/hexaco-results' },
  ];

  // Fetch user data and Holland results
  useEffect(() => {
    const fetchHollandResults = async () => {
      try {
        const results = await hollandTestService.getUserLatestResults();
        setHollandResults(results);
      } catch (err) {
        console.error('Error fetching Holland results:', err);
        setError('Unable to fetch Holland results');
      } finally {
        setLoading(false);
      }
    };

    fetchHollandResults();
  }, []);

  // Fetch job recommendations
  useEffect(() => {
    const fetchJobRecommendations = async () => {
      try {
        setJobsLoading(true);
        setJobsError(null);
        const response = await getJobRecommendations() as JobRecommendationsResponse;
        
        if (response && response.recommendations) {
          const limitedRecommendations = response.recommendations.slice(0, 3);
          
          // Debug: Log the actual job structure
          console.log('🔍 Homepage job recommendations:', {
            count: limitedRecommendations.length,
            firstJob: limitedRecommendations[0] ? {
              id: limitedRecommendations[0].id,
              score: limitedRecommendations[0].score,
              metadata: limitedRecommendations[0].metadata,
              metadataKeys: Object.keys(limitedRecommendations[0].metadata || {}),
              title: limitedRecommendations[0].metadata?.title,
              preferred_label: limitedRecommendations[0].metadata?.preferred_label,
              label: limitedRecommendations[0].metadata?.label,
              description: limitedRecommendations[0].metadata?.description
            } : null
          });
          
          setJobRecommendations(limitedRecommendations);
          
          if (limitedRecommendations.length > 0) {
            setSelectedJob(limitedRecommendations[0]);
          }
        }
      } catch (err) {
        console.error('Error fetching job recommendations:', err);
        setJobsError('Unable to fetch job recommendations');
      } finally {
        setJobsLoading(false);
      }
    };
    
    fetchJobRecommendations();
  }, []);

  // Fetch top peers
  useEffect(() => {
    const fetchPeers = async () => {
      try {
        setPeersLoading(true);
        setPeersError(null);
        
        const token = localStorage.getItem('access_token');
        if (!token) {
          console.log('No auth token found for peer fetching');
          setPeersError('Authentication required');
          return;
        }
        
        const response = await axios.get<EnhancedPeerProfile[]>(`${cleanApiUrl}/peers/compatible`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        
        // Get top 3 peers for homepage
        const topPeers = response.data.slice(0, 3);
        setPeers(topPeers);
      } catch (err: any) {
        console.error('Error fetching peers:', err);
        setPeersError('Unable to fetch peer recommendations');
      } finally {
        setPeersLoading(false);
      }
    };

    fetchPeers();
  }, [cleanApiUrl]);

  // Fetch user notes
  useEffect(() => {
    const fetchNotes = async () => {
      try {
        setNotesLoading(true);
        setNotesError(null);
        
        const notes = await fetchAllUserNotes();
        // Get top 3 most recent notes for home page
        const recentNotes = notes.slice(0, 3);
        setUserNotes(recentNotes);
      } catch (err: any) {
        console.error('Error fetching user notes:', err);
        setNotesError('Unable to fetch notes');
      } finally {
        setNotesLoading(false);
      }
    };

    fetchNotes();
  }, []);

  const handleSelectJob = (job: Job) => {
    setSelectedJob(job);
  };

  // Show loading while checking authentication
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <p className="ml-3 text-gray-600">Loading dashboard...</p>
      </div>
    );
  }

  // Don't render dashboard if not authenticated (will be redirected)
  if (!isAuthenticated) {
    return null;
  }

  return (
    <MainLayout>
      <div className="relative flex w-full min-h-screen flex-col pb-20 overflow-x-hidden" style={{ backgroundColor: '#ffffff' }}>
        
        <div className="relative z-10 w-full">
          <div className="flex-1 w-full px-4 sm:px-6 md:px-12 lg:px-16 xl:px-24 max-w-none">
            {/* Mobile-First Layout Stack - Progress and Focus in one row */}
            <div className="flex flex-col gap-6 mb-8">
              
              {/* Single Row: All cards with same dimensions */}
              <div className="w-full">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                  
                  {/* My Progress Section */}
                  <div className="w-full">
                    <h2 className="text-lg sm:text-xl font-semibold mb-4 px-2" style={{ color: '#000000' }}>My Progress</h2>
                    <div className="w-full">
                      <UserCard
                        name={userData.name}
                        role={userData.role}
                        skills={userData.skills}
                        hollandResults={hollandResults}
                        loading={loading}
                        error={error}
                        className="w-full"
                        style={{
                          width: '100%',
                          height: '220px',
                          borderRadius: '24px',
                          background: '#e0e0e0',
                          boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff'
                        }}
                      />
                    </div>
                  </div>

                  {/* Daily Question Card */}
                  <div className="w-full">
                    <h2 className="text-lg sm:text-xl font-semibold mb-4 px-2" style={{ color: '#000000' }}>Today's Focus</h2>
                    <ColorfulDailyQuestionCard 
                      userId={currentUserId}
                      style={{ height: '220px' }}
                    />
                  </div>

                  {/* Career Goal Card */}
                  <div className="w-full">
                    <h2 className="text-lg sm:text-xl font-semibold mb-4 px-2 opacity-0" style={{ color: '#000000' }}>Hidden</h2>
                    <ColorfulCareerGoalCard
                      style={{ height: '220px' }}
                    />
                  </div>

                  {/* Classes Card */}
                  <div className="w-full">
                    <h2 className="text-lg sm:text-xl font-semibold mb-4 px-2 opacity-0" style={{ color: '#000000' }}>Hidden</h2>
                    <EnhancedClassesCard
                      userId={currentUserId}
                      style={{ height: '220px' }}
                    />
                  </div>
                  
                </div>
              </div>

              {/* Mobile: Calendar moved to bottom, full width on mobile */}
              <div className="w-full lg:hidden">
                <h2 className="text-lg font-semibold mb-4 px-2" style={{ color: '#000000' }}>Schedule</h2>
                <Calendar 
                  events={[
                    { id: '1', date: new Date(2025, 0, 20), title: 'Holland Test Review', type: 'test' },
                    { id: '2', date: new Date(2025, 0, 25), title: 'Career Challenge', type: 'challenge' },
                    { id: '3', date: new Date(2025, 0, 28), title: 'Peer Meetup', type: 'event' }
                  ]}
                  onDateClick={(date) => console.log('Date clicked:', date)}
                />
              </div>
            </div>

            {/* Mobile-First Content Sections */}
            <div className="flex flex-col lg:grid lg:grid-cols-12 gap-6 mb-8">
              {/* Activity Section - Full width on mobile */}
              <div className="w-full lg:col-span-4 xl:col-span-3">
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-lg font-semibold" style={{ color: '#000000' }}>Activity</h2>
                  <Link
                    href="/peers"
                    className="text-sm text-gray-500 hover:text-gray-700 flex items-center gap-1"
                  >
                    <span>3</span>
                    <svg width="16" height="16" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M3 18h6v-2H3v2zM3 6v2h18V6H3zm0 7h12v-2H3v2z"/>
                    </svg>
                  </Link>
                </div>
                
                {/* Search bar */}
                <div className="mb-4">
                  <div className="relative">
                    <svg className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
                    </svg>
                    <input
                      type="text"
                      placeholder="Find update"
                      className="w-full pl-10 pr-4 py-2 text-sm bg-gray-50 border-0 rounded-lg focus:outline-none focus:ring-1 focus:ring-gray-200"
                    />
                  </div>
                </div>
                
                {peersLoading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                    <p className="text-sm text-gray-600 mt-2">Loading peers...</p>
                  </div>
                ) : peersError ? (
                  <div className="text-center py-8">
                    <p className="text-sm text-red-600">{peersError}</p>
                  </div>
                ) : peers.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-sm text-gray-600">No peer recommendations available</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {peers.map((peer) => (
                      <div
                        key={peer.user_id}
                        className="flex items-center gap-3 p-3 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
                        onClick={() => router.push(`/peers/${peer.user_id}`)}
                      >
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
                          {peer.name && peer.name.charAt(0) ? peer.name.charAt(0).toUpperCase() : '?'}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex justify-between items-start">
                            <div className="flex-1 min-w-0">
                              <h3 className="font-medium text-sm text-gray-900 truncate">
                                {peer.name || `User ${peer.user_id}`}
                              </h3>
                              <p className="text-xs text-gray-500 mt-1">
                                {peer.major}{peer.year ? `, Year ${peer.year}` : ''}
                              </p>
                            </div>
                            <div className="flex flex-col items-end ml-2">
                              <span className="text-xs text-gray-400">Jan 2, 12:30</span>
                              <span className="text-xs text-blue-600 font-medium mt-1">
                                {Math.round((peer.compatibility_score || 0) * 100)}% match
                              </span>
                            </div>
                          </div>
                        </div>
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 256 256" className="text-gray-300">
                          <path d="M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z"></path>
                        </svg>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Job Recommendations - Full width on mobile, larger on desktop */}
              <div className="w-full lg:col-span-5 xl:col-span-6">
                <div className="mb-6">
                  <h2 className="text-lg font-semibold" style={{ color: '#000000' }}>Recommended Jobs</h2>
                </div>
                
                {/* Original Recommendations */}
                <div className="mb-6">
                  <div className="flex justify-between items-center mb-3">
                    <h3 className="text-sm font-medium text-gray-700">Your Personalized Recommendations</h3>
                    <Link
                      href="/career/recommendations"
                      className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1 font-medium px-3 py-1.5 rounded-lg hover:bg-blue-50 transition-colors"
                    >
                      <span>See all</span>
                      <svg width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
                        <path d="M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z"></path>
                      </svg>
                    </Link>
                  </div>
                  {jobsLoading ? (
                    <div className="text-center py-6">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
                      <p className="text-xs text-gray-600 mt-2">Loading recommendations...</p>
                    </div>
                  ) : jobsError ? (
                    <div className="text-center py-6">
                      <p className="text-xs text-red-600">{jobsError}</p>
                    </div>
                  ) : jobRecommendations.length === 0 ? (
                    <div className="text-center py-6">
                      <p className="text-xs text-gray-600">No job recommendations available</p>
                    </div>
                  ) : (
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {jobRecommendations.map((job) => (
                        <div
                          key={job.id}
                          className="p-3 hover:bg-gray-50 rounded-lg cursor-pointer transition-colors"
                          onClick={() => handleSelectJob(job)}
                        >
                          <h4 className="font-medium text-sm mb-1">
                            {(() => {
                              // Try different possible title fields
                              const possibleTitles = [
                                job.metadata?.preferred_label,
                                job.metadata?.title,
                                job.metadata?.label,
                                job.metadata?.occupation_label,
                                job.metadata?.job_title,
                                job.metadata?.name,
                                (job as any)?.label, // Direct property (like in JobRecommendationVerticalList)
                                (job as any)?.title,
                                (job as any)?.job_title,
                                (job as any)?.occupation_label
                              ];
                              
                              const title = possibleTitles.find(t => t && t.trim() !== '');
                              return title || `Career Opportunity ${job.id}`;
                            })()}
                          </h4>
                          <p className="text-xs text-gray-600 line-clamp-2 mb-2">
                            {job.metadata.description || 'No description available'}
                          </p>
                          <div className="flex justify-between items-center">
                            <div className="text-xs text-blue-600 font-medium">
                              {Math.round(job.score * 100)}% match
                            </div>
                            <div className="flex items-center gap-2">
                              {job.metadata.skills && job.metadata.skills.length > 0 && (
                                <div className="flex gap-1 flex-wrap">
                                  {job.metadata.skills.slice(0, 2).map((skill, index) => (
                                    <span
                                      key={index}
                                      className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded-full"
                                    >
                                      {skill}
                                    </span>
                                  ))}
                                </div>
                              )}
                              <SaveJobButton job={job} size="sm" />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Vector Search Integration - Moved below recommendations */}
                <div className="mb-4">
                  <VectorSearchCard />
                </div>
              </div>

              {/* Events & Notes + Desktop Calendar */}
              <div className="w-full lg:col-span-3">
                {/* Desktop Calendar - Hidden on mobile */}
                <div className="hidden lg:block mb-6">
                  <h2 className="text-lg font-semibold mb-4" style={{ color: '#000000' }}>Schedule</h2>
                  <Calendar 
                    events={[
                      { id: '1', date: new Date(2025, 0, 20), title: 'Holland Test Review', type: 'test' },
                      { id: '2', date: new Date(2025, 0, 25), title: 'Career Challenge', type: 'challenge' },
                      { id: '3', date: new Date(2025, 0, 28), title: 'Peer Meetup', type: 'event' }
                    ]}
                    onDateClick={(date) => console.log('Date clicked:', date)}
                  />
                </div>
                <EventsNotes
                  events={[
                    {
                      id: '1',
                      title: 'Holland Test Review',
                      date: new Date(2025, 0, 20),
                      type: 'test',
                      description: 'Review your personality test results'
                    },
                    {
                      id: '2',
                      title: 'Career Challenge',
                      date: new Date(2025, 0, 25),
                      type: 'challenge',
                      description: 'Complete the data analysis challenge'
                    }
                  ]}
                  notes={notesLoading ? [] : notesError ? [] : userNotes.map(note => ({
                    id: note.id,
                    title: note.content && note.content.length > 50 ? `${note.content.substring(0, 50)}...` : (note.content || 'Untitled'),
                    content: note.content && note.content.length > 100 ? `${note.content.substring(0, 100)}...` : (note.content || ''),
                    createdAt: new Date(note.created_at),
                    recommendationId: note.saved_recommendation_id
                  }))}
                  onEventClick={(event) => console.log('Event clicked:', event)}
                  onNoteClick={(note) => router.push('/notes')}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}