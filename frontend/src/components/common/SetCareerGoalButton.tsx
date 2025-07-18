'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'react-hot-toast';
import { CareerGoalsService } from '@/services/careerGoalsService';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface SetCareerGoalButtonProps {
  job: {
    id?: string;
    esco_id?: string;
    oasis_code?: string;
    title?: string;
    preferred_label?: string;
    description?: string;
    metadata?: {
      title?: string;
      description?: string;
      oasis_code?: string;
      [key: string]: any;
    };
    [key: string]: any;
  };
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  onSuccess?: () => void;
  source?: string; // Where the button is placed: 'oasis', 'saved', 'swipe', 'tree'
}

const SetCareerGoalButton: React.FC<SetCareerGoalButtonProps> = ({
  job,
  variant = 'primary',
  size = 'md',
  className = '',
  onSuccess,
  source = 'unknown'
}) => {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleSetGoal = async () => {
    setLoading(true);
    
    try {
      // Extract job details from various formats
      const jobTitle = job.title || job.metadata?.title || job.preferred_label || 'Unknown Position';
      const jobDescription = job.description || job.metadata?.description || '';
      const escoId = job.esco_id || job.id;
      const oasisCode = job.oasis_code || job.metadata?.oasis_code;
      
      // Call the API to set career goal
      const result = await CareerGoalsService.setCareerGoalFromJob({
        esco_id: escoId,
        oasis_code: oasisCode,
        title: jobTitle,
        description: jobDescription,
        source: source
      });
      
      // Show success message with navigation option
      toast.success(
        <div>
          <p className="font-medium">Career goal set!</p>
          <p className="text-sm">{jobTitle}</p>
          <button
            onClick={() => router.push('/goals')}
            className="mt-2 text-xs bg-white/20 px-2 py-1 rounded hover:bg-white/30 transition-colors"
          >
            View Timeline →
          </button>
        </div>,
        {
          duration: 5000,
          position: 'top-center',
          style: {
            background: '#10B981',
            color: 'white',
          }
        }
      );
      
      // Call success callback if provided
      if (onSuccess) {
        onSuccess();
      }
      
      // Optional: Navigate to goals page after a delay
      if (variant === 'primary') {
        setTimeout(() => {
          router.push('/goals');
        }, 2000);
      }
      
    } catch (error: any) {
      console.error('Failed to set career goal:', error);
      toast.error(error.message || 'Failed to set career goal');
    } finally {
      setLoading(false);
    }
  };

  // Button styling based on variant and size
  const baseStyles = "inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed rounded-lg";
  
  const variantStyles = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 active:bg-blue-800 shadow-sm",
    secondary: "bg-gray-100 text-gray-700 hover:bg-gray-200 active:bg-gray-300 border border-gray-200",
    ghost: "text-gray-600 hover:text-gray-900 hover:bg-gray-100"
  };
  
  const sizeStyles = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg"
  };

  return (
    <button
      onClick={handleSetGoal}
      disabled={loading}
      className={`${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
    >
      {loading ? (
        <>
          <LoadingSpinner size="sm" />
          <span>Setting...</span>
        </>
      ) : (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
          </svg>
          <span>Set as Career Goal</span>
        </>
      )}
    </button>
  );
};

export default SetCareerGoalButton;