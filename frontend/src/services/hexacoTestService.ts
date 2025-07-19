import axios from 'axios';
import api from './api';  // Importer l'instance axios configurée

// Types basés sur les modèles backend HEXACO
export interface HexacoMetadata {
  versions: Record<string, any>;
  languages: Record<string, any>;
  domains: Record<string, any>;
}

export interface HexacoVersion {
  id: string;
  title: string;
  description: string;
  item_count: number;
  estimated_duration: number;
  language: string;
  active: boolean;
}

export interface HexacoQuestion {
  item_id: number;
  item_text: string;
  response_min: number;
  response_max: number;
  version: string;
  language: string;
  reverse_keyed: boolean;
  facet: string;
}

export interface HexacoAnswerRequest {
  session_id: string;
  item_id: number;
  response_value: number;
  response_time_ms?: number;
}

export interface HexacoScoreResponse {
  domains: Record<string, number>;
  facets: Record<string, number>;
  percentiles: Record<string, number>;
  reliability: Record<string, number>;
  total_responses: number;
  completion_rate: number;
  narrative_description?: string;
}

export interface SessionResponse {
  session_id: string;
  message: string;
}

export interface ProgressResponse {
  total_items: number;
  completed_items: number;
  progress_percentage: number;
  status: string;
  assessment_version: string;
}

// URL de base de l'API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const HEXACO_TEST_API = `${API_BASE_URL}/api/tests/hexaco`;

// Service pour le test HEXACO
const hexacoTestService = {
  // Récupérer les métadonnées générales du test HEXACO
  getMetadata: async (): Promise<HexacoMetadata> => {
    try {
      const response = await api.get<HexacoMetadata>(`/api/tests/hexaco`);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des métadonnées HEXACO:', error);
      throw error;
    }
  },

  // Récupérer les langues disponibles
  getAvailableLanguages: async (): Promise<Record<string, any>> => {
    try {
      const response = await api.get<Record<string, any>>(`/api/tests/hexaco/languages`);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des langues:', error);
      throw error;
    }
  },

  // Récupérer les versions disponibles (optionnellement filtrées par langue)
  getAvailableVersions: async (language?: string): Promise<Record<string, HexacoVersion>> => {
    try {
      const url = language 
        ? `/api/tests/hexaco/versions?language=${language}`
        : `/api/tests/hexaco/versions`;
      const response = await api.get<Record<string, HexacoVersion>>(url);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des versions:', error);
      throw error;
    }
  },

  // Démarrer une nouvelle session de test
  startTest: async (versionId: string): Promise<SessionResponse> => {
    try {
      const response = await api.post<SessionResponse>(`${HEXACO_TEST_API}/start`, {
        version_id: versionId
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors du démarrage du test HEXACO:', error);
      throw error;
    }
  },

  // Récupérer les questions pour une version spécifique
  getQuestions: async (versionId: string): Promise<HexacoQuestion[]> => {
    try {
      const response = await api.get<HexacoQuestion[]>(`${HEXACO_TEST_API}/questions`, {
        params: { version_id: versionId }
      });
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des questions HEXACO:', error);
      throw error;
    }
  },

  // Enregistrer une réponse
  saveAnswer: async (answerData: HexacoAnswerRequest): Promise<{ message: string }> => {
    try {
      const response = await api.post<{ message: string }>(`${HEXACO_TEST_API}/answer`, answerData);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de l\'enregistrement de la réponse HEXACO:', error);
      throw error;
    }
  },

  // Récupérer le progrès d'une session
  getProgress: async (sessionId: string): Promise<ProgressResponse> => {
    try {
      const response = await api.get<ProgressResponse>(`${HEXACO_TEST_API}/progress/${sessionId}`);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération du progrès:', error);
      throw error;
    }
  },

  // Récupérer le score du test
  getScore: async (sessionId: string, includeDescription: boolean = true): Promise<HexacoScoreResponse> => {
    try {
      const response = await api.get<HexacoScoreResponse>(
        `${HEXACO_TEST_API}/score/${sessionId}?include_description=${includeDescription}`
      );
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération du score HEXACO:', error);
      throw error;
    }
  },

  // Récupérer le profil HEXACO de l'utilisateur connecté
  getMyProfile: async (assessmentVersion?: string): Promise<HexacoScoreResponse | null> => {
    try {
      const url = assessmentVersion 
        ? `${HEXACO_TEST_API}/my-profile?assessment_version=${assessmentVersion}`
        : `${HEXACO_TEST_API}/my-profile`;
      const response = await api.get<HexacoScoreResponse | null>(url);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération du profil HEXACO:', error);
      throw error;
    }
  },

  // Récupérer le profil HEXACO d'un utilisateur spécifique
  getUserProfile: async (userId: number, assessmentVersion?: string): Promise<HexacoScoreResponse | null> => {
    try {
      const url = assessmentVersion 
        ? `${HEXACO_TEST_API}/profile/${userId}?assessment_version=${assessmentVersion}`
        : `${HEXACO_TEST_API}/profile/${userId}`;
      const response = await api.get<HexacoScoreResponse | null>(url);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération du profil utilisateur HEXACO:', error);
      throw error;
    }
  },

  // Récupérer l'analyse LLM de l'utilisateur connecté
  getMyAnalysis: async (assessmentVersion?: string, forceRegenerate: boolean = false): Promise<{
    analysis: string;
    assessment_version: string;
    language: string;
    generated_at: string;
  }> => {
    try {
      const params = new URLSearchParams();
      if (assessmentVersion) {
        params.append('assessment_version', assessmentVersion);
      }
      if (forceRegenerate) {
        params.append('force_regenerate', 'true');
      }
      
      const url = `${HEXACO_TEST_API}/my-analysis${params.toString() ? '?' + params.toString() : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'analyse HEXACO:', error);
      throw error;
    }
  },

  // Récupérer l'analyse LLM d'un utilisateur spécifique
  getUserAnalysis: async (userId: number, assessmentVersion?: string, forceRegenerate: boolean = false): Promise<{
    analysis: string;
    assessment_version: string;
    language: string;
    generated_at: string;
  }> => {
    try {
      const params = new URLSearchParams();
      if (assessmentVersion) {
        params.append('assessment_version', assessmentVersion);
      }
      if (forceRegenerate) {
        params.append('force_regenerate', 'true');
      }
      
      const url = `${HEXACO_TEST_API}/analysis/${userId}${params.toString() ? '?' + params.toString() : ''}`;
      const response = await api.get(url);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération de l\'analyse utilisateur HEXACO:', error);
      throw error;
    }
  },

  // Générer un nouvel ID de session (utilisé côté client pour le suivi)
  generateSessionId: (): string => {
    return crypto.randomUUID ? crypto.randomUUID() :
      'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
  }
};

export default hexacoTestService;