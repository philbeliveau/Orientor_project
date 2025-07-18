'use client';

import React from 'react';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

const TypingIndicator: React.FC = () => {
  return (
    <div className="typing-indicator flex items-center justify-center p-2" data-testid="typing-indicator">
      <LoadingSpinner size="sm" color="#6366f1" />
    </div>
  );
};

export default TypingIndicator;