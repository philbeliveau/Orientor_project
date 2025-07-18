import React, { useState } from 'react';
import { Bookmark, BookmarkCheck } from 'lucide-react';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface SaveActionButtonProps {
  onSave: () => Promise<void>;
  saved?: boolean;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'primary' | 'ghost' | 'outline';
  label?: string;
}

export const SaveActionButton: React.FC<SaveActionButtonProps> = ({
  onSave,
  saved = false,
  className = "",
  size = 'md',
  variant = 'primary',
  label = "Save"
}) => {
  const [isSaving, setIsSaving] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const handleSave = async () => {
    if (saved || isSaving) return;
    
    setIsSaving(true);
    try {
      await onSave();
    } catch (error) {
      console.error('Failed to save:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base'
  };

  const variantClasses = {
    primary: saved 
      ? 'bg-green-100 text-green-700 border-green-300' 
      : 'bg-blue-500 text-white hover:bg-blue-600 border-blue-500',
    ghost: saved
      ? 'text-green-700 hover:bg-green-50'
      : 'text-blue-600 hover:bg-blue-50',
    outline: saved
      ? 'border-green-300 text-green-700 hover:bg-green-50'
      : 'border-blue-300 text-blue-600 hover:bg-blue-50 hover:border-blue-400'
  };

  const iconSize = {
    sm: 'w-3 h-3',
    md: 'w-4 h-4',
    lg: 'w-5 h-5'
  };

  return (
    <button
      onClick={handleSave}
      disabled={saved || isSaving}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`
        inline-flex items-center justify-center gap-2 rounded-lg
        font-medium transition-all duration-200 border
        disabled:opacity-60 disabled:cursor-not-allowed
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${className}
      `}
    >
      {isSaving ? (
        <LoadingSpinner size="sm" />
      ) : saved ? (
        <BookmarkCheck className={iconSize[size]} />
      ) : (
        <Bookmark className={`${iconSize[size]} ${isHovered ? 'fill-current' : ''}`} />
      )}
      <span>{saved ? 'Saved' : label}</span>
    </button>
  );
};