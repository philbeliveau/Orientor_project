import React, { useState } from 'react';
import { toast } from 'react-hot-toast';
import axios from 'axios';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface SaveJobButtonProps {
  job: {
    id: string;
    metadata: {
      title?: string;
      preferred_label?: string;
      description?: string;
      skills?: string[];
      [key: string]: any;
    };
    score?: number;
  };
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const SaveJobButton: React.FC<SaveJobButtonProps> = ({ job, className = '', size = 'md' }) => {
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent parent onClick
    
    if (saved) {
      toast('Job already saved');
      return;
    }

    setSaving(true);
    
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        toast.error('Please login to save jobs');
        return;
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // Prepare the job data for saving - extract skill values
      const skillPattern = /\b(creativity|leadership|digital[\s_]literacy|critical[\s_]thinking|problem[\s_]solving):\s*(\d+(?:\.\d+)?)/gi;
      const skillValues: any = {};
      
      // Try to extract skills from description or metadata
      const textToSearch = `${job.metadata.description || ''} ${JSON.stringify(job.metadata)}`;
      let match;
      while ((match = skillPattern.exec(textToSearch)) !== null) {
        const skillName = match[1].toLowerCase().replace(/\s+/g, '_');
        skillValues[`role_${skillName}`] = parseFloat(match[2]);
      }

      // Convert all arrays in metadata to strings (backend expects Dict[str, str])
      const processedMetadata = { ...job.metadata };
      Object.keys(processedMetadata).forEach(key => {
        if (Array.isArray(processedMetadata[key])) {
          processedMetadata[key] = processedMetadata[key].join(', ');
        } else if (typeof processedMetadata[key] === 'object' && processedMetadata[key] !== null) {
          processedMetadata[key] = JSON.stringify(processedMetadata[key]);
        } else if (typeof processedMetadata[key] !== 'string') {
          processedMetadata[key] = String(processedMetadata[key]);
        }
      });

      const jobData = {
        oasis_code: job.id, // ESCO jobs from home page use their ID as oasis_code
        label: job.metadata.preferred_label || job.metadata.title || 'Untitled Job',
        description: job.metadata.description || '',
        main_duties: job.metadata.main_duties || '',
        // Include skill values if found
        role_creativity: skillValues.role_creativity || 3.0,
        role_leadership: skillValues.role_leadership || 3.0,
        role_digital_literacy: skillValues.role_digital_literacy || 3.0,
        role_critical_thinking: skillValues.role_critical_thinking || 3.0,
        role_problem_solving: skillValues.role_problem_solving || 3.0,
        // Default cognitive traits
        analytical_thinking: 3.5,
        attention_to_detail: 3.5,
        collaboration: 3.5,
        adaptability: 3.5,
        independence: 3.5,
        evaluation: 3.5,
        decision_making: 3.5,
        stress_tolerance: 3.5,
        all_fields: processedMetadata
      };

      const response = await axios.post(
        `${apiUrl}/space/recommendations`,
        jobData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.status === 200 || response.status === 201) {
        setSaved(true);
        toast.success('Job saved to My Space!');
      }
    } catch (error: any) {
      console.error('Error saving job:', error);
      if (error.response?.status === 409) {
        setSaved(true);
        toast('Job already saved');
      } else {
        toast.error('Failed to save job');
      }
    } finally {
      setSaving(false);
    }
  };

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base'
  };

  return (
    <button
      onClick={handleSave}
      disabled={saving || saved}
      className={`
        ${sizeClasses[size]}
        ${saved 
          ? 'bg-green-100 text-green-700 hover:bg-green-200' 
          : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
        }
        ${(saving || saved) ? 'cursor-not-allowed opacity-75' : 'cursor-pointer'}
        rounded-full font-medium transition-colors flex items-center gap-1
        ${className}
      `}
    >
      {saving ? (
        <>
          <LoadingSpinner size="sm" />
          Saving...
        </>
      ) : saved ? (
        <>
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
          Saved
        </>
      ) : (
        <>
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
          </svg>
          Save
        </>
      )}
    </button>
  );
};

export default SaveJobButton;