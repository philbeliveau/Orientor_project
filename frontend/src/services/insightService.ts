import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Type definitions
export interface InsightData {
  preview: string;
  full_text: string;
  if_you_accept: string;
}

// Configure axios with the token
const getAuthHeader = () => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  return token ? {
    headers: {
      Authorization: `Bearer ${token}`
    }
  } : { headers: {} };
};

/**
 * Génère un insight philosophique pour l'utilisateur connecté
 * @returns Les données d'insight générées
 */
export const generateInsight = async (): Promise<InsightData> => {
  try {
    const response = await axios.post<InsightData>(
      `${API_URL}/api/v1/insight/generate`,
      {},
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la génération de l\'insight philosophique:', error);
    throw error;
  }
};

/**
 * Sauvegarde un insight philosophique pour l'utilisateur connecté
 * @param philosophicalText - Le texte philosophique à sauvegarder
 * @returns Le statut de succès
 */
export const saveInsight = async (philosophicalText: string): Promise<{ success: boolean }> => {
  try {
    const response = await axios.patch<{ success: boolean }>(
      `${API_URL}/api/v1/insight/save`,
      {
        philosophical_text: philosophicalText
      },
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la sauvegarde de l\'insight philosophique:', error);
    throw error;
  }
};

/**
 * Réécrit un insight philosophique basé sur le feedback de l'utilisateur connecté
 * @param feedback - Le feedback de l'utilisateur pour la réécriture
 * @returns Les nouvelles données d'insight générées
 */
export const rewriteInsight = async (feedback: string): Promise<InsightData> => {
  try {
    const response = await axios.post<InsightData>(
      `${API_URL}/api/v1/insight/rewrite`,
      {
        feedback: feedback
      },
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la réécriture de l\'insight philosophique:', error);
    throw error;
  }
};

/**
 * Récupère l'insight philosophique existant pour l'utilisateur connecté
 * @returns Les données d'insight existantes
 */
export const getInsight = async (): Promise<InsightData> => {
  try {
    const response = await axios.get<InsightData>(
      `${API_URL}/api/v1/insight/get`,
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la récupération de l\'insight philosophique:', error);
    throw error;
  }
};

/**
 * Régénère un insight philosophique pour l'utilisateur connecté
 * @returns Les nouvelles données d'insight générées
 */
export const regenerateInsight = async (): Promise<InsightData> => {
  try {
    const response = await axios.post<InsightData>(
      `${API_URL}/api/v1/insight/regenerate`,
      {},
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Erreur lors de la régénération de l\'insight philosophique:', error);
    throw error;
  }
};

// Données simulées pour le développement et les tests
export const mockInsightData: InsightData = {
  preview: "Your life seems structured but contains hidden creative impulses...",
  full_text: "You present yourself as methodical and organized, but there's a part of you that craves creative expression and spontaneity. Your career choices reflect a tension between security and passion. The skills you've developed suggest someone preparing for stability, yet your interests hint at unfulfilled creative ambitions...",
  if_you_accept: "If you accept this truth, you might find that integrating your analytical skills with your creative instincts leads to innovations others cannot conceive."
};