import React from 'react';
import Link from 'next/link';

const NoSavedRecommendations: React.FC = () => {
  return (
    <div className="card text-center py-12">
      <div className="max-w-md mx-auto">
        <h2 className="text-2xl font-bold mb-4">No Saved Careers Yet</h2>
        <p className="text-neutral-300 mb-6">
          You haven't saved any career recommendations yet. Explore career recommendations and save them to track your progress and make notes.
        </p>
        <Link 
          href="/vector-search" 
          className="btn btn-primary"
        >
          Explore Career Recommendations
        </Link>
      </div>
    </div>
  );
};

export default NoSavedRecommendations; 