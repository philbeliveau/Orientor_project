'use client';

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Legend } from 'recharts';
import { fetchSavedRecommendations, Recommendation as SpaceServiceRecommendation, Note, deleteRecommendation } from '@/services/spaceService';
import MainLayout from '@/components/layout/MainLayout';
import NotesSection from '@/components/space/NotesSection';
import { extractChartData } from '@/utils/chartUtils';
import { toast } from 'react-hot-toast';

// Define a stricter type for our components that requires certain fields
interface Recommendation extends Omit<SpaceServiceRecommendation, 'id'> {
  id: number;
  saved_at: string;
  skill_comparison?: {
    creativity: { user_skill: number; role_skill: number };
    leadership: { user_skill: number; role_skill: number };
    digital_literacy: { user_skill: number; role_skill: number };
    critical_thinking: { user_skill: number; role_skill: number };
    problem_solving: { user_skill: number; role_skill: number };
  };
  notes?: Note[];
  all_fields?: Record<string, string>;
}

const extractSkillData = (comparison: any) => {
  if (!comparison) return [];
  
  return [
    { subject: 'Creativity', A: comparison.creativity?.role_skill || 0, B: comparison.creativity?.user_skill || 0 },
    { subject: 'Leadership', A: comparison.leadership?.role_skill || 0, B: comparison.leadership?.user_skill || 0 },
    { subject: 'Digital Literacy', A: comparison.digital_literacy?.role_skill || 0, B: comparison.digital_literacy?.user_skill || 0 },
    { subject: 'Critical Thinking', A: comparison.critical_thinking?.role_skill || 0, B: comparison.critical_thinking?.user_skill || 0 },
    { subject: 'Problem Solving', A: comparison.problem_solving?.role_skill || 0, B: comparison.problem_solving?.user_skill || 0 }
  ];
};

export default function SpacePage() {
  const [recommendations, setRecommendations] = useState<SpaceServiceRecommendation[]>([]);
  const [selectedRecommendation, setSelectedRecommendation] = useState<SpaceServiceRecommendation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadRecommendations = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await fetchSavedRecommendations();
        console.log('Recommendations from API:', data);
        setRecommendations(data);
      } catch (err) {
        console.error('Error loading recommendations:', err);
        setError('Failed to load recommendations. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    loadRecommendations();
  }, []);

  const handleRecommendationSelect = (recommendation: SpaceServiceRecommendation) => {
    setSelectedRecommendation(recommendation);
  };

  const handleDeleteRecommendation = async (recommendationId: number) => {
    try {
      await deleteRecommendation(recommendationId);
      setRecommendations(prev => prev.filter(rec => rec.id !== recommendationId));
      if (selectedRecommendation?.id === recommendationId) {
        setSelectedRecommendation(null);
      }
      toast.success('Recommendation deleted successfully');
    } catch (err) {
      console.error('Error deleting recommendation:', err);
      toast.error('Failed to delete recommendation');
    }
  };

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">My Space</h1>
        
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : error ? (
          <div className="text-red-500 text-center">{error}</div>
        ) : recommendations.length === 0 ? (
          <div className="text-center text-gray-500">No saved recommendations yet.</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="md:col-span-1">
              <h2 className="text-xl font-semibold mb-4">Saved Recommendations</h2>
              <div className="space-y-4">
                {recommendations.map((rec) => (
                  <div
                    key={rec.id}
                    className={`p-4 rounded-lg cursor-pointer ${
                      selectedRecommendation?.id === rec.id
                        ? 'bg-blue-100 border-2 border-blue-500'
                        : 'bg-white border border-gray-200 hover:border-blue-300'
                    }`}
                  >
                    <div onClick={() => handleRecommendationSelect(rec)}>
                      <h3 className="font-medium">{rec.label}</h3>
                      <p className="text-sm text-gray-500">{rec.oasis_code}</p>
                    </div>
                    <button
                      onClick={() => rec.id && handleDeleteRecommendation(rec.id)}
                      className="mt-2 text-gray-200 hover:text-gray-700 text-sm font-medium"
                    >
                      Delete
                    </button>
                  </div>
                ))}
              </div>
            </div>

            <div className="md:col-span-2">
              {selectedRecommendation && (
                <>
                  <div className="bg-white p-6 rounded-lg shadow">
                    <h2 className="text-2xl font-bold mb-4">{selectedRecommendation.label}</h2>
                    <p className="text-gray-600 mb-4">{selectedRecommendation.description}</p>
                    
                    {selectedRecommendation.main_duties && (
                      <div className="mb-6">
                        <h3 className="text-lg font-semibold mb-2">Main Duties</h3>
                        <p className="text-gray-700">{selectedRecommendation.main_duties}</p>
                      </div>
                    )}

                    {selectedRecommendation.skill_comparison && (
                      <div className="mt-8">
                        <h3 className="text-lg font-semibold mb-2">Skill Comparison</h3>
                        <ResponsiveContainer width="100%" height={300}>
                          <RadarChart data={extractSkillData(selectedRecommendation.skill_comparison)}>
                            <PolarGrid />
                            <PolarAngleAxis dataKey="subject" />
                            <PolarRadiusAxis angle={30} domain={[0, 5]} />
                            <Radar name="Job Skills" dataKey="A" stroke="#8884d8" fill="#8884d8" fillOpacity={0.6} />
                            <Radar name="My Skills" dataKey="B" stroke="#82ca9d" fill="#82ca9d" fillOpacity={0.6} />
                            <Tooltip />
                            <Legend />
                          </RadarChart>
                        </ResponsiveContainer>
                      </div>
                    )}

                    <div className="mt-8">
                      <h3 className="text-lg font-semibold mb-2">Cognitive Traits & Work Characteristics</h3>
                      <ResponsiveContainer width="100%" height={250}>
                        <BarChart
                          data={extractChartData(selectedRecommendation)}
                          margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" tick={{ fontSize: 10 }} />
                          <YAxis domain={[0, 5]} />
                          <Tooltip />
                          <Bar dataKey="value" fill="#8884d8" />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>

                    {selectedRecommendation.all_fields && (
                      <div className="mt-6">
                        <h3 className="text-lg font-semibold mb-2">Additional Details</h3>
                        <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-sm text-neutral-500">
                          {Object.entries(selectedRecommendation.all_fields).map(([key, value]) => (
                            <div key={key} className="flex gap-1">
                              <span className="font-medium">{key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}:</span>
                              <span>{value}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    <NotesSection
                      recommendation={selectedRecommendation}
                    />
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}