import api from './api';
import { PsychProfile, OnboardingResponse } from '../types/onboarding';

export interface OnboardingStatus {
  isComplete: boolean;
  hasStarted: boolean;
  currentStep?: string;
  completedAt?: string;
}

export interface OnboardingSessionResponse {
  session_id: string;
  message: string;
}

export interface OnboardingProgressResponse {
  message: string;
  progress: number;
  total: number;
}

export interface OnboardingCompleteResponse {
  message: string;
  assessment_id: number;
  profile_created: boolean;
}

export interface OnboardingProfileResponse {
  profile: PsychProfile;
  description: string;
  created_at: string;
  assessment_version: string;
}

export interface OnboardingResponsesData {
  responses: OnboardingResponse[];
  assessment_status: string;
  completed_items: number;
  total_items: number;
}

class OnboardingService {
  private baseURL = '/onboarding';

  /**
   * Get the current onboarding status for the authenticated user
   */
  async getStatus(): Promise<OnboardingStatus> {
    try {
      console.log('Checking onboarding status...');
      console.log('API URL:', api.defaults.baseURL);
      console.log('Request URL:', `${this.baseURL}/status`);
      console.log('Full URL:', `${api.defaults.baseURL}${this.baseURL}/status`);
      
      // Check if we have a valid token
      const token = localStorage.getItem('access_token');
      console.log('Auth token present:', !!token);
      if (token) {
        console.log('Token starts with:', token.substring(0, 10) + '...');
      }
      
      const response = await api.get(`${this.baseURL}/status`);
      console.log('Onboarding status response:', response.data);
      
      // Validate the response structure
      const status = response.data;
      if (typeof status.isComplete !== 'boolean' || typeof status.hasStarted !== 'boolean') {
        console.warn('Invalid onboarding status response structure:', status);
        // Return default status for new users
        return {
          isComplete: false,
          hasStarted: false,
          currentStep: null,
          completedAt: null
        };
      }
      
      return status;
    } catch (error: any) {
      console.error('Failed to get onboarding status:', error);
      
      // Check if it's an authentication error
      if (error.response?.status === 401 || error.response?.status === 403) {
        console.error('Authentication error while checking onboarding status');
        throw error; // Re-throw auth errors
      }
      
      // For other errors, assume user is new and needs onboarding
      console.warn('Assuming new user needs onboarding due to error:', error.message);
      return {
        isComplete: false,
        hasStarted: false,
        currentStep: null,
        completedAt: null
      };
    }
  }

  /**
   * Start a new onboarding session
   */
  async startOnboarding(): Promise<OnboardingSessionResponse> {
    try {
      const response = await api.post(`${this.baseURL}/start`);
      return response.data;
    } catch (error) {
      console.error('Failed to start onboarding:', error);
      throw error;
    }
  }

  /**
   * Save a single onboarding response
   */
  async saveResponse(responseData: OnboardingResponse): Promise<OnboardingProgressResponse> {
    try {
      const response = await api.post(`${this.baseURL}/response`, responseData);
      return response.data;
    } catch (error) {
      console.error('Failed to save onboarding response:', error);
      throw error;
    }
  }

  /**
   * Complete the onboarding process
   */
  async completeOnboarding(data: {
    responses: OnboardingResponse[];
    psychProfile?: PsychProfile;
  }): Promise<OnboardingCompleteResponse> {
    try {
      console.log('Sending onboarding completion data:', {
        responses: data.responses.length,
        psychProfile: data.psychProfile ? 'Present' : 'Missing',
        data: data
      });
      const response = await api.post(`${this.baseURL}/complete`, data);
      console.log('Onboarding completion response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to complete onboarding:', error);
      throw error;
    }
  }

  /**
   * Get the user's onboarding psychological profile
   */
  async getProfile(): Promise<OnboardingProfileResponse> {
    try {
      const response = await api.get(`${this.baseURL}/profile`);
      return response.data;
    } catch (error) {
      console.error('Failed to get onboarding profile:', error);
      throw error;
    }
  }

  /**
   * Get all onboarding responses for the user
   */
  async getResponses(): Promise<OnboardingResponsesData> {
    try {
      const response = await api.get(`${this.baseURL}/responses`);
      return response.data;
    } catch (error) {
      console.error('Failed to get onboarding responses:', error);
      throw error;
    }
  }

  /**
   * Reset onboarding progress for the user
   */
  async resetOnboarding(): Promise<{ message: string }> {
    try {
      const response = await api.delete(`${this.baseURL}/reset`);
      return response.data;
    } catch (error) {
      console.error('Failed to reset onboarding:', error);
      throw error;
    }
  }

  /**
   * Check if user needs onboarding
   */
  async needsOnboarding(): Promise<boolean> {
    try {
      const status = await this.getStatus();
      console.log('Onboarding status check result:', { isComplete: status.isComplete, hasStarted: status.hasStarted });
      return !status.isComplete;
    } catch (error: any) {
      // If it's an auth error, re-throw it
      if (error.response?.status === 401 || error.response?.status === 403) {
        throw error;
      }
      
      // For other errors, assume they need onboarding
      console.warn('Could not check onboarding status, assuming onboarding needed:', error.message);
      return true;
    }
  }

  /**
   * Get onboarding progress percentage
   */
  async getProgress(): Promise<number> {
    try {
      const responsesData = await this.getResponses();
      if (responsesData.total_items === 0) return 0;
      return Math.round((responsesData.completed_items / responsesData.total_items) * 100);
    } catch (error) {
      console.error('Failed to get onboarding progress:', error);
      return 0;
    }
  }

  /**
   * Skip onboarding for a user by creating a default profile
   */
  async skipOnboarding(): Promise<OnboardingCompleteResponse> {
    try {
      console.log('Skipping onboarding...');
      const response = await api.post(`${this.baseURL}/skip`);
      console.log('Skip onboarding response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Failed to skip onboarding:', error);
      throw error;
    }
  }
}

export const onboardingService = new OnboardingService();
export default onboardingService;