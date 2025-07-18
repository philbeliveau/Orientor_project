'use client';

import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size = 'md', 
  color = 'primary-purple',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8'
  };

  const getColorClass = () => {
    if (color !== 'primary-purple') {
      return color;
    }
    return '#6366f1';
  };

  const spinnerColor = getColorClass();

  return (
    <div className={`flex justify-center items-center ${className}`}>
      <div 
        className={`${sizeClasses[size]} animate-spin rounded-full border-2 border-gray-200`}
        style={{
          borderTopColor: spinnerColor,
          borderRightColor: spinnerColor
        }}
      />
    </div>
  );
};

export default LoadingSpinner; 