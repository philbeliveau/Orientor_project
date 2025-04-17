import React from 'react';

interface Recommendation {
  id: number;
  oasis_code: string;
  label: string;
  description?: string;
  main_duties?: string;
  saved_at: string;
  skill_comparison?: any;
}

interface SavedRecommendationsListProps {
  recommendations: Recommendation[];
  selectedRecommendation: Recommendation | null;
  onSelectRecommendation: (recommendation: Recommendation) => void;
}

const SavedRecommendationsList: React.FC<SavedRecommendationsListProps> = ({
  recommendations,
  selectedRecommendation,
  onSelectRecommendation
}) => {
  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Saved Career Paths</h2>
      <div className="space-y-3">
        {recommendations.map((recommendation) => (
          <div
            key={recommendation.id}
            className={`p-4 rounded-lg transition-all duration-300 cursor-pointer hover:bg-neutral-100/30 ${
              selectedRecommendation?.id === recommendation.id 
                ? 'bg-gradient-subtle border border-primary-teal/30' 
                : 'bg-neutral-100/60 border border-neutral-100/30'
            }`}
            onClick={() => onSelectRecommendation(recommendation)}
          >
            <h3 className="text-lg font-medium">{recommendation.label}</h3>
            <p className="text-sm text-neutral-100 mt-1">
              {recommendation.oasis_code}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SavedRecommendationsList; 