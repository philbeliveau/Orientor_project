'use client';

import { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import SavedRecommendationsList from '@/components/space/SavedRecommendationsList';
import SkillRadarChart from '@/components/space/SkillRadarChart';
import NotesSection from '@/components/space/NotesSection';
import NoSavedRecommendations from '@/components/space/NoSavedRecommendations';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { fetchSavedRecommendations } from '@/services/spaceService';
import type { Recommendation } from '@/services/spaceService';

export default function SpacePage() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadRecommendations = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await fetchSavedRecommendations();
        console.log('Recommendations from API:', data);
        
        // Check if we got valid data
        if (!Array.isArray(data)) {
          console.error('Expected array of recommendations, got:', typeof data, data);
          setError('Invalid data format received from server.');
          return;
        }
        
        // Validate each recommendation
        const validRecommendations = data.filter(rec => {
          if (!rec.id || !rec.oasis_code || !rec.label) {
            console.warn('Invalid recommendation data:', rec);
            return false;
          }
          return true;
        });
        
        setRecommendations(validRecommendations);
        
        // If recommendations exist, select the first one by default
        if (validRecommendations.length > 0) {
          console.log('First recommendation:', validRecommendations[0]);
          console.log('Skill comparison:', validRecommendations[0].skill_comparison);
          setSelectedRecommendation(validRecommendations[0]);
        }
      } catch (err) {
        console.error('Error loading saved recommendations:', err);
        setError('Failed to load your saved recommendations. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };

    loadRecommendations();
  }, []);

  const handleSelectRecommendation = (recommendation: Recommendation) => {
    console.log('Selected recommendation:', recommendation);
    setSelectedRecommendation(recommendation);
  };

  return (
    <MainLayout>
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-6 gradient-text">My Space</h1>
        
        {isLoading ? (
          <div className="flex justify-center items-center h-64">
            <LoadingSpinner />
          </div>
        ) : error ? (
          <div className="card mb-8 text-red-400">
            <p>{error}</p>
          </div>
        ) : recommendations.length === 0 ? (
          <NoSavedRecommendations />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left column: Saved recommendations list */}
            <div className="lg:col-span-1">
              <SavedRecommendationsList 
                recommendations={recommendations}
                selectedRecommendation={selectedRecommendation}
                onSelectRecommendation={handleSelectRecommendation}
              />
            </div>
            
            {/* Right column: Skill radar and notes */}
            <div className="lg:col-span-2 space-y-8">
              {selectedRecommendation && (
                <>
                  <div className="card">
                    <h2 className="text-2xl font-bold mb-4">{selectedRecommendation.label}</h2>
                    <div className="mb-4">
                      {selectedRecommendation.description && (
                        <p className="mb-2">{selectedRecommendation.description}</p>
                      )}
                      {selectedRecommendation.main_duties && (
                        <div className="mt-4">
                          <h3 className="text-lg font-semibold mb-2">Main Duties</h3>
                          <p>{selectedRecommendation.main_duties}</p>
                        </div>
                      )}
                    </div>
                    
                    {selectedRecommendation.skill_comparison && (
                      <div className="mt-6">
                        <h3 className="text-lg font-semibold mb-4">Skill Comparison</h3>
                        <SkillRadarChart skillComparison={selectedRecommendation.skill_comparison} />
                      </div>
                    )}
                  </div>
                  
                  <NotesSection 
                    recommendation={selectedRecommendation}
                    notes={selectedRecommendation.notes || []}
                  />
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </MainLayout>
  );
}