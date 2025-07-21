/**
 * Custom hook for School Programs API interactions
 */

import { useCallback } from 'react';
import { toast } from 'react-hot-toast';
import { Program, SearchFilters, SearchResults, UserProgramInteraction, SaveProgramRequest } from '../types';

export const useSchoolProgramsAPI = () => {

  const searchPrograms = useCallback(async (filters: SearchFilters, page: number = 1): Promise<SearchResults> => {
    try {
      const response = await fetch('/api/v1/school-programs/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          ...filters,
          pagination: { page, limit: 20 }
        }),
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      return await response.json();
    } catch (error) {
      toast.error("Unable to search programs. Please try again.");
      throw error;
    }
  }, []);

  const getProgramDetails = useCallback(async (programId: string): Promise<Program> => {
    try {
      const response = await fetch(`/api/v1/school-programs/programs/${programId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch program details');
      }

      return await response.json();
    } catch (error) {
      toast.error("Unable to load program details.");
      throw error;
    }
  }, []);

  const saveProgram = useCallback(async (programId: string, notes?: string): Promise<void> => {
    try {
      const response = await fetch('/api/v1/school-programs/users/saved-programs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          program_id: programId,
          notes: notes,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to save program');
      }

      toast.success("Program saved to your list!");
    } catch (error) {
      toast.error("Unable to save program. Please try again.");
    }
  }, []);

  const recordInteraction = useCallback(async (programId: string, type: string, metadata?: any): Promise<void> => {
    try {
      await fetch('/api/v1/school-programs/users/interactions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          program_id: programId,
          interaction_type: type,
          metadata: metadata || {},
        }),
      });
    } catch (error) {
      // Silent fail for analytics
      console.warn('Failed to record interaction:', error);
    }
  }, []);

  const getSavedPrograms = useCallback(async (): Promise<Program[]> => {
    try {
      const response = await fetch('/api/v1/school-programs/users/saved-programs', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch saved programs');
      }

      return await response.json();
    } catch (error) {
      toast.error("Unable to load saved programs.");
      throw error;
    }
  }, []);

  const removeSavedProgram = useCallback(async (programId: string): Promise<void> => {
    try {
      const response = await fetch(`/api/v1/school-programs/users/saved-programs/${programId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to remove saved program');
      }

      toast.success("Program removed from your saved list.");
    } catch (error) {
      toast.error("Unable to remove program. Please try again.");
    }
  }, []);

  const getAvailableFilters = useCallback(async () => {
    try {
      const response = await fetch('/api/v1/school-programs/filters', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch filters');
      }

      return await response.json();
    } catch (error) {
      console.warn('Failed to fetch filters:', error);
      return {
        program_types: [],
        levels: [],
        provinces: [],
        languages: [
          { value: 'en', label: 'English', count: 0 },
          { value: 'fr', label: 'French', count: 0 }
        ]
      };
    }
  }, []);

  return {
    searchPrograms,
    getProgramDetails,
    saveProgram,
    recordInteraction,
    getSavedPrograms,
    removeSavedProgram,
    getAvailableFilters,
  };
};