import { SkillNode, TimelineTier } from '@/components/career/TimelineVisualization';

// API endpoints
const API_BASE = process.env.NODE_ENV === 'production' 
  ? process.env.NEXT_PUBLIC_API_URL || 'https://your-backend-api.com'
  : 'http://localhost:8000';

// Types for API responses
export interface CareerGoal {
  id: number;
  user_id: number;
  esco_occupation_id?: string;
  oasis_code?: string;
  title: string;
  description?: string;
  target_date: string;
  is_active: boolean;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
  achieved_at?: string;
  source?: string;
  milestones_count?: number;
  completed_milestones?: number;
}

interface GraphSageScore {
  skill_id: string;
  confidence_score: number;
  tier_level: number;
  relationships: string[];
  metadata: {
    last_updated: string;
    model_version: string;
    training_accuracy: number;
  };
}

interface CareerProgressionResponse {
  user_id: string;
  tiers: TimelineTier[];
  goals: CareerGoal[];
  graphsage_scores: GraphSageScore[];
  last_updated: string;
}

// Utility function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
};

// Career Goals Service
export class CareerGoalsService {
  /**
   * Set a career goal from any job card
   */
  static async setCareerGoalFromJob(job: {
    esco_id?: string;
    oasis_code?: string;
    title: string;
    description?: string;
    source?: string;
  }): Promise<{ goal: CareerGoal; timeline: any }> {
    try {
      const response = await fetch(`${API_BASE}/api/v1/career-goals`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          esco_occupation_id: job.esco_id,
          oasis_code: job.oasis_code,
          title: job.title,
          description: job.description,
          source: job.source,
          target_date: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error setting career goal:', error);
      throw error;
    }
  }

  /**
   * Get active career goal with progression
   */
  static async getActiveCareerGoal(): Promise<{
    goal: CareerGoal | null;
    progression: any;
    milestones: any[];
  }> {
    try {
      const response = await fetch(`${API_BASE}/api/v1/career-goals/active`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching active career goal:', error);
      // Return empty state instead of throwing
      return { goal: null, progression: null, milestones: [] };
    }
  }

  /**
   * Fetch user's career progression with GraphSage scores
   */
  static async getCareerProgression(): Promise<CareerProgressionResponse> {
    try {
      // First try to get active goal's progression
      const { goal, progression } = await this.getActiveCareerGoal();
      
      if (goal && progression) {
        return progression;
      }
      
      // Fallback to generic progression endpoint if available
      const response = await fetch(`${API_BASE}/api/v1/career/progression`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching career progression:', error);
      
      // Return mock data for development
      return this.getMockCareerProgression();
    }
  }

  /**
   * Update GraphSage confidence scores for skills
   */
  static async updateGraphSageScores(skillIds: string[]): Promise<GraphSageScore[]> {
    try {
      const response = await fetch(`${API_BASE}/api/v1/career/graphsage/update`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ skill_ids: skillIds }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.scores;
    } catch (error) {
      console.error('Error updating GraphSage scores:', error);
      throw error;
    }
  }

  /**
   * Update career goal
   */
  static async updateCareerGoal(goalId: number, updates: {
    title?: string;
    description?: string;
    target_date?: string;
    is_active?: boolean;
  }): Promise<CareerGoal> {
    try {
      const response = await fetch(`${API_BASE}/api/v1/career-goals/${goalId}`, {
        method: 'PUT',
        headers: getAuthHeaders(),
        body: JSON.stringify(updates),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error updating career goal:', error);
      throw error;
    }
  }

  /**
   * Complete a milestone
   */
  static async completeMilestone(goalId: number, milestoneId: number): Promise<{
    message: string;
    xp_awarded: number;
    goal_progress: number;
    goal_achieved: boolean;
  }> {
    try {
      const response = await fetch(
        `${API_BASE}/api/v1/career-goals/${goalId}/milestones/${milestoneId}/complete`,
        {
          method: 'POST',
          headers: getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error completing milestone:', error);
      throw error;
    }
  }

  /**
   * Get all career goals
   */
  static async getAllCareerGoals(includeInactive = false): Promise<CareerGoal[]> {
    try {
      const response = await fetch(
        `${API_BASE}/api/v1/career-goals?include_inactive=${includeInactive}`,
        {
          method: 'GET',
          headers: getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching career goals:', error);
      return [];
    }
  }

  /**
   * Get skill recommendations based on GraphSage analysis
   */
  static async getSkillRecommendations(currentSkillIds: string[]): Promise<SkillNode[]> {
    try {
      const response = await fetch(`${API_BASE}/api/v1/career/recommendations/skills`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ current_skills: currentSkillIds }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.recommendations;
    } catch (error) {
      console.error('Error getting skill recommendations:', error);
      throw error;
    }
  }

  /**
   * Analyze skill relationships using GraphSage
   */
  static async analyzeSkillRelationships(skillIds: string[]): Promise<{
    relationships: Array<{
      source: string;
      target: string;
      strength: number;
      confidence: number;
    }>;
    clusters: Array<{
      id: string;
      skills: string[];
      theme: string;
    }>;
  }> {
    try {
      const response = await fetch(`${API_BASE}/api/v1/career/graphsage/relationships`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ skill_ids: skillIds }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error analyzing skill relationships:', error);
      throw error;
    }
  }

  /**
   * Get career path optimization suggestions
   */
  static async getCareerPathOptimization(currentTier: number): Promise<{
    recommendations: Array<{
      skill_id: string;
      priority_score: number;
      expected_impact: number;
      estimated_months: number;
      reasoning: string;
    }>;
    timeline_adjustments: Array<{
      tier_id: string;
      suggested_duration: number;
      current_duration: number;
      reasoning: string;
    }>;
  }> {
    try {
      const response = await fetch(`${API_BASE}/api/v1/career/optimization/${currentTier}`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting career path optimization:', error);
      throw error;
    }
  }

  /**
   * Mock data for development
   */
  private static getMockCareerProgression(): CareerProgressionResponse {
    return {
      user_id: 'mock-user-123',
      tiers: [
        {
          id: 'tier-1',
          title: 'Foundation & Exploration',
          level: 1,
          timeline_months: 6,
          confidence_threshold: 0.8,
          skills: [
            {
              id: 'skill-1-1',
              label: 'Programming Fundamentals',
              confidence_score: 0.92,
              type: 'skill',
              level: 1,
              relationships: ['skill-1-2', 'skill-2-1'],
              metadata: {
                description: 'Learn core programming concepts and syntax',
                estimated_months: 3,
                prerequisites: [],
                learning_resources: ['Online courses', 'Practice projects']
              }
            },
            {
              id: 'skill-1-2',
              label: 'Problem Solving',
              confidence_score: 0.85,
              type: 'skill',
              level: 1,
              relationships: ['skill-1-1', 'skill-2-3'],
              metadata: {
                description: 'Develop analytical thinking and debugging skills',
                estimated_months: 2,
                prerequisites: [],
                learning_resources: ['Algorithm challenges', 'Code reviews']
              }
            }
          ]
        }
      ],
      goals: [
        {
          id: 1,
          user_id: 1,
          title: 'Master Frontend Development',
          description: 'Become proficient in React and modern frontend technologies',
          target_date: '2024-12-31',
          is_active: true,
          progress_percentage: 65,
          created_at: '2024-01-15T00:00:00Z',
          updated_at: '2024-06-20T00:00:00Z'
        }
      ],
      graphsage_scores: [
        {
          skill_id: 'skill-1-1',
          confidence_score: 0.92,
          tier_level: 1,
          relationships: ['skill-1-2', 'skill-2-1'],
          metadata: {
            last_updated: '2024-06-20T10:30:00Z',
            model_version: 'graphsage-v2.1',
            training_accuracy: 0.94
          }
        }
      ],
      last_updated: '2024-06-20T10:30:00Z'
    };
  }
}

// Export types for use in components
export type { GraphSageScore, CareerProgressionResponse };