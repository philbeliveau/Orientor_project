/**
 * Orientator AI API Client Service
 * Handles all interactions with the Orientator AI backend
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import { getAuthToken } from './authService';

// Types and interfaces
export enum MessageComponentType {
  TEXT = 'text',
  SKILL_TREE = 'skill_tree',
  CAREER_PATH = 'career_path',
  JOB_CARD = 'job_card',
  PEER_CARD = 'peer_card',
  TEST_RESULT = 'test_result',
  CHALLENGE_CARD = 'challenge_card',
  SAVE_CONFIRMATION = 'save_confirmation'
}

export enum ComponentActionType {
  SAVE = 'save',
  EXPAND = 'expand',
  EXPLORE = 'explore',
  SHARE = 'share',
  START = 'start'
}

export interface ComponentAction {
  type: ComponentActionType;
  label: string;
  endpoint?: string;
  params?: Record<string, any>;
}

export interface MessageComponent {
  id: string;
  type: MessageComponentType;
  data: Record<string, any>;
  actions: ComponentAction[];
  saved: boolean;
  metadata: Record<string, any>;
}

export interface OrientatorMessage {
  message_id: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  components: MessageComponent[];
  metadata: Record<string, any>;
  created_at: string;
}

export interface SendMessageRequest {
  message: string;
  conversation_id: number;
}

export interface SaveComponentRequest {
  component_id: string;
  component_type: MessageComponentType;
  component_data: Record<string, any>;
  source_tool: string;
  conversation_id: number;
  note?: string;
}

export interface SaveComponentResponse {
  success: boolean;
  saved_item_id: number;
  message: string;
}

export interface UserJourney {
  user_id: number;
  journey_stages: Array<{
    type: string;
    data: Record<string, any>;
    achieved_at: string;
    conversation_id?: number;
  }>;
  saved_items_count: number;
  tools_used: string[];
  career_goals: string[];
  skill_progression: Record<string, any>;
  personality_insights?: Record<string, any>;
  peer_connections: Array<{
    peer_id: number;
    name: string;
    match_score: number;
    saved_at?: string;
  }>;
  challenges_completed: Array<{
    challenge_id: number;
    title: string;
    xp_earned: number;
    completed_at: string;
  }>;
}

export interface ConversationSummary {
  id: number;
  title: string;
  created_at: string;
  last_message_at?: string;
  message_count: number;
  tools_used: string[];
  is_favorite: boolean;
  is_archived: boolean;
}

export interface ToolAnalytics {
  total_invocations: number;
  tool_usage: Record<string, {
    count: number;
    success: number;
    success_rate: number;
    avg_execution_time: number;
  }>;
  success_rate: number;
  most_used_tools: Array<{
    tool: string;
    count: number;
  }>;
}

export interface FeedbackRequest {
  message_id: number;
  feedback: string;
  rating?: number;
}

// API Client Class
class OrientatorService {
  private api: AxiosInstance;
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    
    this.api = axios.create({
      baseURL: `${this.baseURL}/api/orientator`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = getAuthToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle unauthorized - redirect to login
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * Send a message to Orientator AI
   */
  async sendMessage(request: SendMessageRequest): Promise<OrientatorMessage> {
    try {
      const response = await this.api.post<OrientatorMessage>('/api/v1/message', request);
      return response.data;
    } catch (error) {
      console.error('Error sending message to Orientator:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Save a component to user's space
   */
  async saveComponent(request: SaveComponentRequest): Promise<SaveComponentResponse> {
    try {
      const response = await this.api.post<SaveComponentResponse>('/api/v1/save-component', request);
      return response.data;
    } catch (error) {
      console.error('Error saving component:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Get user's career journey
   */
  async getUserJourney(userId: number): Promise<UserJourney> {
    try {
      const response = await this.api.get<UserJourney>(`/journey/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching user journey:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Get Orientator conversations
   */
  async getConversations(limit: number = 20, offset: number = 0): Promise<ConversationSummary[]> {
    try {
      const response = await this.api.get<ConversationSummary[]>('/api/v1/conversations', {
        params: { limit, offset }
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching conversations:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Get tool usage analytics
   */
  async getToolAnalytics(): Promise<ToolAnalytics> {
    try {
      const response = await this.api.get<ToolAnalytics>('/api/v1/tool-analytics');
      return response.data;
    } catch (error) {
      console.error('Error fetching tool analytics:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Submit feedback for an AI response
   */
  async submitFeedback(request: FeedbackRequest): Promise<{ success: boolean; message: string }> {
    try {
      const response = await this.api.post('/api/v1/feedback', request, {
        params: {
          message_id: request.message_id,
          rating: request.rating
        }
      });
      return response.data;
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Check service health
   */
  async checkHealth(): Promise<{ status: string; service: string; version: string }> {
    try {
      const response = await this.api.get('/api/v1/health');
      return response.data;
    } catch (error) {
      console.error('Error checking service health:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Execute a component action
   */
  async executeAction(action: ComponentAction, componentData?: any): Promise<any> {
    try {
      if (!action.endpoint) {
        throw new Error('Action endpoint not defined');
      }

      // Determine HTTP method based on action type
      const method = action.type === ComponentActionType.SAVE ? 'post' : 'get';
      
      const response = await this.api.request({
        method,
        url: action.endpoint,
        data: method === 'post' ? { ...action.params, ...componentData } : undefined,
        params: method === 'get' ? action.params : undefined
      });

      return response.data;
    } catch (error) {
      console.error('Error executing action:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Handle API errors
   */
  private handleError(error: any): Error {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        // Server responded with error
        const message = (axiosError.response.data as any)?.detail || 
                       'An error occurred while processing your request';
        return new Error(message);
      } else if (axiosError.request) {
        // Request made but no response
        return new Error('Unable to connect to the server. Please check your connection.');
      }
    }
    // Something else happened
    return new Error('An unexpected error occurred');
  }

  /**
   * Process streaming responses (for future real-time features)
   */
  async *streamMessage(request: SendMessageRequest): AsyncGenerator<Partial<OrientatorMessage>> {
    try {
      const response = await fetch(`${this.baseURL}/api/v1/orientator/message/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const decoder = new TextDecoder();
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              return;
            }
            try {
              yield JSON.parse(data);
            } catch (e) {
              console.error('Error parsing stream data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error streaming message:', error);
      throw this.handleError(error);
    }
  }
}

// Create singleton instance
const orientatorService = new OrientatorService();

// Export service instance and types
export default orientatorService;

// Helper functions for component type checking
export const isSkillTreeComponent = (component: MessageComponent): boolean => {
  return component.type === MessageComponentType.SKILL_TREE;
};

export const isCareerPathComponent = (component: MessageComponent): boolean => {
  return component.type === MessageComponentType.CAREER_PATH;
};

export const isJobCardComponent = (component: MessageComponent): boolean => {
  return component.type === MessageComponentType.JOB_CARD;
};

export const isPeerCardComponent = (component: MessageComponent): boolean => {
  return component.type === MessageComponentType.PEER_CARD;
};

export const isTestResultComponent = (component: MessageComponent): boolean => {
  return component.type === MessageComponentType.TEST_RESULT;
};

export const isChallengeCardComponent = (component: MessageComponent): boolean => {
  return component.type === MessageComponentType.CHALLENGE_CARD;
};

// Helper to format tool names for display
export const formatToolName = (toolName: string): string => {
  const toolDisplayNames: Record<string, string> = {
    'esco_skills': 'ESCO Skills Tree',
    'career_tree': 'Career Path Explorer',
    'oasis_explorer': 'OaSIS Job Explorer',
    'peer_matching': 'Peer Finder',
    'hexaco_test': 'HEXACO Personality Test',
    'holland_test': 'Holland Interest Test',
    'xp_challenges': 'XP Challenges'
  };
  
  return toolDisplayNames[toolName] || toolName;
};