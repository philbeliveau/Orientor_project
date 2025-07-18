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
      <div className="flex min-h-screen font-inter" style={{
        backgroundColor: 'var(--background)',
        color: 'var(--text)'
      }}>
        {/* Sidebar */}
        <aside className="w-64 shrink-0 border-r" style={{
          borderColor: 'var(--border)',
          backgroundColor: 'var(--background-secondary)'
        }}>
          {/* Tab Navigation */}
          <div className="p-4 border-b" style={{ borderColor: 'var(--border)' }}>
            <div className="flex rounded-lg p-1" style={{ backgroundColor: 'var(--card)' }}>
              <button
                onClick={() => setActiveTab('recommendations')}
                className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === 'recommendations' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                💾 Saved
              </button>
              <button
                onClick={() => setActiveTab('jobs')}
                className={`flex-1 px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === 'jobs' 
                    ? 'bg-blue-600 text-white' 
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                🌳 From Tree
              </button>
            </div>
          </div>

          {/* Tab Content */}
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
        </aside>

        {/* Main Content */}
        <main className="flex-1 px-10 py-6 overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-xl font-semibold tracking-tight" style={{ color: 'var(--text)' }}>
              {activeTab === 'recommendations' ? 'Saved Recommendations' : 'Jobs from Tree Exploration'}
            </h1>
            
            {/* Badge with count and refresh button */}
            <div className="flex gap-3 items-center">
              {activeTab === 'recommendations' && (
                <>
                  <span className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                    {recommendations.length} saved
                  </span>
                  <button
                    onClick={() => {
                      setLoading(true);
                      loadRecommendations();
                    }}
                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm hover:bg-blue-200 transition-colors"
                  >
                    Refresh
                  </button>
                </>
              )}
              {activeTab === 'jobs' && (
                <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                  {savedJobs.length} jobs discovered
                </span>
              )}
            </div>
          </div>

          {/* Detail View */}
          {activeTab === 'recommendations' ? (
            selected ? (
              <RecommendationDetail
                recommendation={selected}
                onGenerate={handleGenerate}
                generating={generating}
              />
            ) : (
              <div className="text-base text-center mt-20" style={{ color: 'var(--text-secondary)' }}>
                <div className="mb-4">💾</div>
                <div>Select a saved recommendation to view details.</div>
              </div>
            )
          ) : (
            selectedJob ? (
              <SavedJobDetail
                job={selectedJob}
              />
            ) : (
              <div className="text-base text-center mt-20" style={{ color: 'var(--text-secondary)' }}>
                <div className="mb-4">🌳</div>
                <div>Select a job from your tree exploration to view details.</div>
                <div className="text-sm mt-2">
                  Visit the <strong>Competence Tree</strong> to discover career opportunities!
                </div>
              </div>
            )
          )}
        </main>
      </div>
    </MainLayout>
  );
}
