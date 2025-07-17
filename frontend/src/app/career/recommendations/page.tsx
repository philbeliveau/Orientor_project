'use client';

import React, { useEffect, useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { getAllJobRecommendations } from '@/services/api';
import JobSkillsTree from '@/components/jobs/JobSkillsTree';
import JobCard, { Job } from '@/components/jobs/JobCard';
import LoadingScreen from '@/components/ui/LoadingScreen';
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
        <LoadingScreen message="Loading career recommendations..." />
      </MainLayout>
    );
  }

  if (error) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-red-500">{error}</div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
        <div className="max-w-7xl mx-auto px-6 py-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-3">Career Recommendations</h1>
            <p className="text-gray-600 text-lg">
              Discover personalized career recommendations based on your profile
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Left side: Job Cards */}
            <div className="lg:col-span-5">
              <div className="bg-white rounded-2xl shadow-lg p-6 h-[800px] overflow-hidden">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Recommended Careers</h2>
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-4 h-[calc(100%-3rem)] overflow-y-auto pr-2">
                  {recommendations.map((job) => (
                    <div key={job.id} className="h-80">
                      <JobCard
                        job={job}
                        isSelected={selectedJob?.id === job.id}
                        onClick={() => setSelectedJob(job)}
                        className="h-full"
                      />
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right side: Skills Tree */}
            <div className="lg:col-span-7">
              <div className="bg-white rounded-2xl shadow-lg p-4">
                {selectedJob ? (
                  <div>
                    <div className="flex justify-between items-start mb-4 pb-3 border-b border-gray-200">
                      <div>
                        <h2 className="text-xl font-semibold text-gray-900">
                          {selectedJob.metadata.preferred_label || selectedJob.metadata.title || 
                           (selectedJob.id.startsWith('occupation::key_') ? `Position ${selectedJob.id.replace('occupation::key_', '')}` : selectedJob.id)}
                        </h2>
                        <p className="text-xs text-gray-500 mt-1">Skills & Requirements Analysis</p>
                      </div>
                      <SaveJobButton job={selectedJob} size="md" />
                    </div>
                    <div className="w-full">
                      <JobSkillsTree jobId={selectedJob.id} height="900px" />
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center text-center" style={{height: "900px"}}>
                    <div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                      <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">Select a Career</h3>
                    <p className="text-gray-500 max-w-md">
                      Choose a career recommendation from the left to view its detailed skills tree and requirements analysis.
                    </p>
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