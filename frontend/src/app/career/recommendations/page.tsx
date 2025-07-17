'use client';

import React, { useEffect, useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { getAllJobRecommendations } from '@/services/api';
import JobSkillsTree from '@/components/jobs/JobSkillsTree';
import JobCard, { Job } from '@/components/jobs/JobCard';
import LoadingScreen from '@/components/ui/LoadingScreen';
import SetCareerGoalButton from '@/components/common/SetCareerGoalButton';
import SaveJobButton from '@/components/common/SaveJobButton';

export default function CareerRecommendationsPage() {
  const [recommendations, setRecommendations] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        setLoading(true);
        const response = await getAllJobRecommendations(30);
        console.log('Fetched recommendations:', response);
        if (response && response.recommendations) {
          setRecommendations(response.recommendations);
          // Set the first job as selected by default
          if (response.recommendations.length > 0) {
            setSelectedJob(response.recommendations[0]);
          }
        }
      } catch (err) {
        console.error('Error fetching recommendations:', err);
        setError('Failed to load career recommendations');
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, []);

  if (loading) {
    return (
      <MainLayout>
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
          <LoadingScreen message="Loading career recommendations..." />
        </div>
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 flex items-center justify-center">
          <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md mx-4">
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Unable to Load Recommendations</h3>
              <p className="text-red-600 mb-4">{error}</p>
              <button 
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-4 lg:px-6 py-6 lg:py-8">
          {/* Header */}
          <div className="mb-6 lg:mb-8">
            <h1 className="text-2xl lg:text-4xl font-bold text-gray-900 mb-2 lg:mb-3">Career Recommendations</h1>
            <p className="text-gray-600 text-base lg:text-lg">
              Discover personalized career recommendations based on your profile
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8">
            {/* Left side: Job Cards */}
            <div className="lg:col-span-5">
              <div className="bg-white rounded-2xl shadow-lg p-4 lg:p-6 h-[700px] lg:h-[800px] overflow-hidden">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg lg:text-xl font-semibold text-gray-900">Recommended Careers</h2>
                  <div className="text-xs lg:text-sm text-gray-500">
                    {recommendations.length} careers found
                  </div>
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-2 gap-3 lg:gap-4 h-[calc(100%-3rem)] overflow-y-auto pr-2">
                  {recommendations.map((job) => (
                    <div key={job.id} className="h-72 lg:h-80">
                      <JobCard
                        job={job}
                        isSelected={selectedJob?.id === job.id}
                        onClick={() => setSelectedJob(job)}
                        className="h-full transition-all duration-200 hover:shadow-md"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right side: Skills Tree */}
            <div className="lg:col-span-7">
              <div className="bg-white rounded-2xl shadow-lg p-4 lg:p-6">
                {selectedJob ? (
                  <div>
                    <div className="flex flex-col lg:flex-row lg:justify-between lg:items-start mb-4 pb-3 border-b border-gray-200 gap-4">
                      <div className="flex-1">
                        <h2 className="text-lg lg:text-xl font-semibold text-gray-900 leading-tight">
                          {selectedJob.metadata.preferred_label || selectedJob.metadata.title || 
                           (selectedJob.id.startsWith('occupation::key_') ? `Position ${selectedJob.id.replace('occupation::key_', '')}` : selectedJob.id)}
                        </h2>
                        <p className="text-xs lg:text-sm text-gray-500 mt-1">Skills & Requirements Analysis</p>
                      </div>
                      <div className="flex flex-col sm:flex-row gap-2 lg:flex-shrink-0">
                        <SaveJobButton job={selectedJob} size="lg" />
                        <SetCareerGoalButton 
                          job={selectedJob} 
                          size="lg" 
                          variant="primary"
                          source="recommendations"
                          className="font-semibold"
                        />
                      </div>
                    </div>
                    <div className="w-full">
                      <JobSkillsTree jobId={selectedJob.id} height="800px" />
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center text-center h-[700px] lg:h-[800px]">
                    <div className="w-20 h-20 lg:w-24 lg:h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                      <svg className="w-10 h-10 lg:w-12 lg:h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                    <h3 className="text-lg lg:text-xl font-semibold text-gray-900 mb-2">Select a Career</h3>
                    <p className="text-gray-500 max-w-md text-sm lg:text-base px-4">
                      Choose a career recommendation from the {recommendations.length > 0 ? 'left' : 'above'} to view its detailed skills tree and requirements analysis.
                    </p>
                    {recommendations.length === 0 && (
                      <div className="mt-6">
                        <button 
                          onClick={() => window.location.reload()}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                        >
                          Refresh Recommendations
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
} 