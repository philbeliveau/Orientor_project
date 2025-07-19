'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import MainLayout from '@/components/layout/MainLayout';
import Sidebar from '@/components/space/Sidebar';
import SavedJobsList from '@/components/space/SavedJobsList';
import RecommendationDetail from '@/components/space/RecommendationDetail';
import SavedJobDetail from '@/components/space/SavedJobDetail';
import { 
  fetchSavedRecommendations, 
  deleteRecommendation, 
  generateLLMAnalysisForRecommendation,
  fetchSavedJobs,
  deleteSavedJob,
  cleanupTestJobs
} from '@/services/spaceService';
import type { Recommendation, SavedJob } from '@/services/spaceService';
import { toast } from 'react-hot-toast';

export default function SpacePage() {
  // Tab state
  const [activeTab, setActiveTab] = useState<'recommendations' | 'jobs'>('recommendations');
  
  // Recommendations state
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [selected, setSelected] = useState<Recommendation | null>(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Jobs state
  const [savedJobs, setSavedJobs] = useState<SavedJob[]>([]);
  const [selectedJob, setSelectedJob] = useState<SavedJob | null>(null);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [jobsError, setJobsError] = useState<string | null>(null);
  
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    console.log('Mounted at:', pathname);
  }, [pathname]);

  // Load recommendations
  const loadRecommendations = async () => {
    try {
      console.log('🔄 Loading saved recommendations...');
      const data = await fetchSavedRecommendations();
      console.log('📊 Fetched recommendations:', data);
      console.log(`📈 Total recommendations found: ${data.length}`);
      
      if (data.length === 0) {
        console.log('⚠️ No saved recommendations found. Make sure you have saved some jobs from SwipeRecommendations.');
      } else {
        console.log('✅ Recommendations loaded successfully');
        data.forEach((rec, index) => {
          console.log(`${index + 1}. ${rec.label} (ID: ${rec.id})`);
        });
      }
      
      // All saved recommendations are ESCO jobs from home page (they have oasis_code)
      setRecommendations(data);
    } catch (err) {
      console.error('❌ Error fetching recommendations:', err);
      setError('Could not fetch recommendations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecommendations();
  }, []);

  // Load saved jobs
  useEffect(() => {
    const loadJobs = async () => {
      try {
        const data = await fetchSavedJobs();
        // OaSIS jobs from tree exploration are in separate table
        setSavedJobs(data);
      } catch (err) {
        setJobsError('Could not fetch saved jobs.');
      } finally {
        setJobsLoading(false);
      }
    };
    loadJobs();
  }, []);

  // Recommendation handlers
  const handleSelect = (rec: Recommendation) => {
    setSelected(rec);
    setSelectedJob(null); // Clear job selection
  };

  const handleDelete = async (recommendation: Recommendation) => {
    try {
      // For fake test jobs with occupation::key_* codes, use oasis_code
      // For real jobs, use the numeric ID
      const identifier = recommendation.oasis_code?.startsWith('occupation::key_') 
        ? recommendation.oasis_code 
        : recommendation.id;
      
      if (!identifier) {
        toast.error('Cannot delete recommendation: missing identifier');
        return;
      }
      
      await deleteRecommendation(identifier);
      setRecommendations(prev => prev.filter(r => r.id !== recommendation.id));
      if (selected?.id === recommendation.id) setSelected(null);
      toast.success('Recommendation deleted');
    } catch {
      toast.error('Failed to delete recommendation');
    }
  };

  // Job handlers
  const handleSelectJob = (job: SavedJob) => {
    setSelectedJob(job);
    setSelected(null); // Clear recommendation selection
  };

  const handleDeleteJob = async (id: number) => {
    try {
      await deleteSavedJob(id);
      setSavedJobs(prev => prev.filter(j => j.id !== id));
      if (selectedJob?.id === id) setSelectedJob(null);
      toast.success('Job removed');
    } catch {
      toast.error('Failed to remove job');
    }
  };


  const handleGenerate = async () => {
    if (!selected || !selected.id) return;
    try {
      setGenerating(true);
      const updatedRecommendation = await generateLLMAnalysisForRecommendation(selected.id);
      setSelected(updatedRecommendation);
      setRecommendations(prev => prev.map(r => (r.id === updatedRecommendation.id ? updatedRecommendation : r)));
      toast.success('LLM analysis generated successfully');
    } catch (err) {
      console.error('Error generating LLM analysis:', err);
      toast.error('Failed to generate analysis');
    } finally {
      setGenerating(false);
    }
  };

  // Cleanup test jobs function
  const handleCleanupTestJobs = async () => {
    try {
      const result = await cleanupTestJobs();
      await loadRecommendations(); // Reload the list
      toast.success(`Removed ${result.deleted_count} test jobs`);
    } catch (err) {
      console.error('Error cleaning up test jobs:', err);
      toast.error('Failed to cleanup test jobs');
    }
  };

  return (
    <MainLayout>
      <div className="relative flex w-full min-h-screen flex-col pb-20 overflow-x-hidden" style={{ backgroundColor: '#ffffff' }}>
        
        <div className="relative z-10 w-full">
          <div className="flex-1 w-full px-4 sm:px-6 md:px-12 lg:px-16 xl:px-24 max-w-none">
            
            {/* Header Section with Dashboard-style design */}
            <div className="flex flex-col gap-6 mb-8">
              <div className="w-full">
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  
                  {/* Header Title Card */}
                  <div className="lg:col-span-2">
                    <h1 className="text-2xl font-semibold mb-4" style={{ color: '#000000' }}>My Workspace</h1>
                    <div 
                      className="w-full p-6"
                      style={{
                        borderRadius: '24px',
                        background: '#e0e0e0',
                        boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff'
                      }}
                    >
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h2 className="text-lg font-medium text-gray-900">
                            {activeTab === 'recommendations' ? 'Saved Recommendations' : 'Jobs from Tree Exploration'}
                          </h2>
                          <p className="text-sm text-gray-600 mt-1">
                            {activeTab === 'recommendations' 
                              ? 'Career recommendations you\'ve saved for later review' 
                              : 'Career opportunities discovered through skill tree exploration'
                            }
                          </p>
                        </div>
                        
                        {/* Tab Toggle with Dashboard-style buttons */}
                        <div className="flex rounded-lg p-1 bg-white shadow-inner">
                          <button
                            onClick={() => setActiveTab('recommendations')}
                            className={`px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                              activeTab === 'recommendations' 
                                ? 'bg-blue-500 text-white shadow-md' 
                                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                            }`}
                          >
                            💾 Saved
                          </button>
                          <button
                            onClick={() => setActiveTab('jobs')}
                            className={`px-4 py-2 text-sm font-medium rounded-md transition-all duration-200 ${
                              activeTab === 'jobs' 
                                ? 'bg-blue-500 text-white shadow-md' 
                                : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                            }`}
                          >
                            🌳 From Tree
                          </button>
                        </div>
                      </div>
                      
                      {/* Stats */}
                      <div className="flex gap-4">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl font-bold text-blue-600">
                            {activeTab === 'recommendations' ? recommendations.length : savedJobs.length}
                          </span>
                          <span className="text-sm text-gray-600">
                            {activeTab === 'recommendations' ? 'saved items' : 'discovered jobs'}
                          </span>
                        </div>
                        {activeTab === 'recommendations' && (
                          <button
                            onClick={() => {
                              setLoading(true);
                              loadRecommendations();
                            }}
                            className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs hover:bg-blue-200 transition-colors"
                          >
                            Refresh
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Quick Actions Card */}
                  <div className="w-full">
                    <h2 className="text-lg font-semibold mb-4 opacity-0">Hidden</h2>
                    <div 
                      className="w-full p-6"
                      style={{
                        height: '200px',
                        borderRadius: '24px',
                        background: '#e0e0e0',
                        boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff'
                      }}
                    >
                      <h3 className="text-md font-medium text-gray-900 mb-3">Quick Actions</h3>
                      <div className="space-y-2">
                        <button 
                          onClick={() => router.push('/find-your-way')}
                          className="w-full text-left p-3 rounded-lg hover:bg-white/50 transition-colors text-sm"
                        >
                          <div className="flex items-center gap-3">
                            <span className="text-lg">🎯</span>
                            <div>
                              <div className="font-medium text-gray-900">Discover More Jobs</div>
                              <div className="text-xs text-gray-600">Explore new career paths</div>
                            </div>
                          </div>
                        </button>
                        <button 
                          onClick={() => router.push('/competence-tree')}
                          className="w-full text-left p-3 rounded-lg hover:bg-white/50 transition-colors text-sm"
                        >
                          <div className="flex items-center gap-3">
                            <span className="text-lg">🌳</span>
                            <div>
                              <div className="font-medium text-gray-900">Skill Tree</div>
                              <div className="text-xs text-gray-600">Navigate career connections</div>
                            </div>
                          </div>
                        </button>
                      </div>
                    </div>
                  </div>
                  
                </div>
              </div>
            </div>

            {/* Content Section with Dashboard-style layout */}
            <div className="flex flex-col lg:grid lg:grid-cols-12 gap-6 mb-8">
              
              {/* Sidebar with Dashboard-style card */}
              <div className="w-full lg:col-span-4">
                <div 
                  className="w-full p-6"
                  style={{
                    borderRadius: '24px',
                    background: '#e0e0e0',
                    boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff',
                    minHeight: '500px'
                  }}
                >
                  {activeTab === 'recommendations' ? (
                    <Sidebar
                      items={recommendations}
                      selectedId={selected?.id}
                      onSelect={handleSelect}
                      onDelete={handleDelete}
                      loading={loading}
                      error={error}
                    />
                  ) : (
                    <SavedJobsList
                      jobs={savedJobs}
                      selectedJobId={selectedJob?.id}
                      onSelect={handleSelectJob}
                      onDelete={handleDeleteJob}
                      loading={jobsLoading}
                      error={jobsError}
                    />
                  )}
                </div>
              </div>

              {/* Main Content with Dashboard-style card */}
              <div className="w-full lg:col-span-8">
                <div 
                  className="w-full p-6"
                  style={{
                    borderRadius: '24px',
                    background: '#e0e0e0',
                    boxShadow: '10px 10px 20px #bebebe, -10px -10px 20px #ffffff',
                    minHeight: '500px'
                  }}
                >
                  {activeTab === 'recommendations' ? (
                    selected ? (
                      <RecommendationDetail
                        recommendation={selected}
                        onGenerate={handleGenerate}
                        generating={generating}
                      />
                    ) : (
                      <div className="text-center mt-20">
                        <div className="mb-4 text-4xl">💾</div>
                        <div className="text-lg font-medium text-gray-900 mb-2">Select a saved recommendation</div>
                        <div className="text-sm text-gray-600">Choose an item from the sidebar to view detailed analysis</div>
                      </div>
                    )
                  ) : (
                    selectedJob ? (
                      <SavedJobDetail
                        job={selectedJob}
                      />
                    ) : (
                      <div className="text-center mt-20">
                        <div className="mb-4 text-4xl">🌳</div>
                        <div className="text-lg font-medium text-gray-900 mb-2">Select a job from your exploration</div>
                        <div className="text-sm text-gray-600 mb-4">Choose a career opportunity you discovered in the skill tree</div>
                        <button 
                          onClick={() => router.push('/competence-tree')}
                          className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm"
                        >
                          Explore Competence Tree
                        </button>
                      </div>
                    )
                  )}
                </div>
              </div>
              
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
