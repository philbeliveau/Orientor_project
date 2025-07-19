import axios from 'axios';
import api from './api';  // Importer l'instance axios configurée

// Types basés sur les modèles backend
export interface TestMetadata {
  id: number;
  title: string;
  description: string;
  seo_code: string;
  video_url?: string;
  image_url?: string;
  chapter_count: number;
  question_count: number;
}

export interface Choice {
  id: number;
  title: string;
  question_id: number;
  sort_idx: number;
  r: number;
  i: number;
  a: number;
  s: number;
  e: number;
  c: number;
}

export interface Question {
  id: number;
  title: string;
  chapter_number: number;
  sort_idx: number;
  choices: Choice[];
}

export interface AnswerRequest {
  attempt_id: string;
  question_id: number;
  choice_id: number;
}

export interface ScoreResponse {
  r_score: number;
  i_score: number;
  a_score: number;
  s_score: number;
  e_score: number;
  c_score: number;
  top_3_code: string;
  personality_description?: string;
}

// URL de base de l'API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const HOLLAND_TEST_API = `${API_BASE_URL}/api/tests/holland`;

// Service pour le test Holland
const hollandTestService = {
  // Récupérer les métadonnées du test
  getTestMetadata: async (): Promise<TestMetadata> => {
    try {
      const response = await api.get<TestMetadata>(`/api/tests/holland`);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des métadonnées du test:', error);
      throw error;
    }
  },

  // Récupérer toutes les questions du test
  getQuestions: async (): Promise<Question[]> => {
    try {
      const response = await api.get<Question[]>(`/api/tests/holland/questions`);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des questions:', error);
      throw error;
    }
  },

  // Enregistrer une réponse
  saveAnswer: async (answerData: AnswerRequest): Promise<{ message: string; id: string }> => {
    try {
      const response = await api.post<{ message: string; id: string }>(`${HOLLAND_TEST_API}/answer`, answerData);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de l\'enregistrement de la réponse:', error);
      throw error;
    }
  },

  // Récupérer le score du test
  getScore: async (attemptId: string, includeDescription: boolean = true): Promise<ScoreResponse> => {
    try {
      const response = await api.get<ScoreResponse>(
        `${HOLLAND_TEST_API}/score/${attemptId}?include_description=${includeDescription}`
      );
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération du score:', error);
      throw error;
    }
  },

  // Récupérer les derniers résultats du test Holland pour l'utilisateur connecté
  getUserLatestResults: async (): Promise<ScoreResponse> => {
    try {
      const response = await api.get<ScoreResponse>(`${HOLLAND_TEST_API}/user-results`);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des résultats du test:', error);
      throw error;
    }
  },

  // Récupérer la description personnalisée du profil basée sur les résultats RIASEC
  getProfileDescription: async (regenerate: boolean = false): Promise<string> => {
    try {
      const response = await api.get<{ description: string }>(
        `${HOLLAND_TEST_API}/profile-description?regenerate=${regenerate}`
      );
      return response.data.description;
    } catch (error) {
      console.error('Erreur lors de la récupération de la description du profil:', error);
      throw error;
    }
  },
  
  // Récupérer la description personnalisée pour un utilisateur spécifique
  getUserProfileDescription: async (userId: string, regenerate: boolean = false): Promise<string> => {
    try {
      const response = await api.get<{ description: string }>(
        `${HOLLAND_TEST_API}/profile-description/${userId}?regenerate=${regenerate}`
      );
      return response.data.description;
    } catch (error) {
      console.error('Erreur lors de la récupération de la description du profil:', error);
      throw error;
    }
  },

  // Générer un nouvel ID de tentative
  generateAttemptId: (): string => {
    return crypto.randomUUID ? crypto.randomUUID() :
      'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, (c) => {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
      });
  }
};

export default hollandTestService;