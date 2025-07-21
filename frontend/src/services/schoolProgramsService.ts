/**
 * School Programs Service
 * 
 * API service functions for school programs functionality
 */

import { Program, SearchFilters, SearchResults } from '@/components/school-programs/types';

class SchoolProgramsService {
  private baseUrl = '/api/v1/school-programs';

  private async makeRequest<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': token ? `Bearer ${token}` : '',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async searchPrograms(filters: SearchFilters, page: number = 1): Promise<SearchResults> {
    return this.makeRequest<SearchResults>('/search', {
      method: 'POST',
      body: JSON.stringify({
        ...filters,
        pagination: { page, limit: 20 }
      }),
    });
  }

  async quickSearch(params: {
    q?: string;
    type?: string;
    level?: string;
    province?: string;
    limit?: number;
    page?: number;
  }): Promise<SearchResults> {
    const searchParams = new URLSearchParams();
    
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, value.toString());
      }
    });

    return this.makeRequest<SearchResults>(`/search?${searchParams.toString()}`);
  }

  async getProgramDetails(programId: string): Promise<Program> {
    return this.makeRequest<Program>(`/programs/${programId}`);
  }

  async saveProgram(programId: string, notes?: string): Promise<{ status: string; message: string }> {
    return this.makeRequest(`/users/saved-programs`, {
      method: 'POST',
      body: JSON.stringify({
        program_id: programId,
        notes,
      }),
    });
  }

  async getSavedPrograms(): Promise<Program[]> {
    return this.makeRequest<Program[]>('/users/saved-programs');
  }

  async removeSavedProgram(programId: string): Promise<{ status: string; message: string }> {
    return this.makeRequest(`/users/saved-programs/${programId}`, {
      method: 'DELETE',
    });
  }

  async recordInteraction(programId: string, interactionType: string, metadata?: any): Promise<{ status: string; message: string }> {
    return this.makeRequest('/users/interactions', {
      method: 'POST',
      body: JSON.stringify({
        program_id: programId,
        interaction_type: interactionType,
        metadata: metadata || {},
      }),
    });
  }

  async getAvailableFilters(): Promise<{
    program_types: { value: string; label: string; count: number }[];
    levels: { value: string; label: string; count: number }[];
    provinces: { value: string; label: string; count: number }[];
    languages: { value: string; label: string; count: number }[];
  }> {
    return this.makeRequest('/filters');
  }

  async comparePrograms(programIds: string[]): Promise<{
    programs: Program[];
    comparison_matrix: Record<string, any[]>;
  }> {
    return this.makeRequest('/compare', {
      method: 'POST',
      body: JSON.stringify({
        program_ids: programIds,
      }),
    });
  }

  async getHealthCheck(): Promise<{
    status: string;
    timestamp: string;
    database: string;
    statistics: Record<string, any>;
  }> {
    return this.makeRequest('/health');
  }
}

export const schoolProgramsService = new SchoolProgramsService();