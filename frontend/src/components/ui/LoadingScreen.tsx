import React from 'react';
import LoadingSpinner from './LoadingSpinner';

interface LoadingScreenProps {
  message?: string;
  className?: string;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
  message = 'Loading...',
  className = ''
}) => {
  return (
    <div className={`min-h-screen flex flex-col items-center justify-center ${className}`}>
      <LoadingSpinner size="lg" />
      {message && (
        <p className="mt-8 text-lg text-gray-600 dark:text-gray-400">{message}</p>
      )}
    </div>
  );
};

export default LoadingScreen; 