import api from './api';

export interface ReflectionQuestion {
  id: number;
  question: string;
  category: string;
}

export interface ReflectionResponse {
  id: number;
  user_id: number;
  question_id: number;
  prompt_text: string;
  response: string | null;
  response_time_ms: number | null;
  created_at: string;
  updated_at: string;
}

export interface ReflectionResponseCreate {
  question_id: number;
  response: string | null;
}

export interface ReflectionResponseUpdate {
  response: string | null;
}

export interface ReflectionResponseBatch {
  responses: ReflectionResponseCreate[];
}

class ReflectionService {
  private baseUrl = '/api/v1/reflection';

  /**
   * Récupère toutes les questions de réflexion
   */
  async getQuestions(): Promise<ReflectionQuestion[]> {
    try {
      const response = await api.get<ReflectionQuestion[]>(`${this.baseUrl}/questions`);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des questions:', error);
      throw error;
    }
  }

  /**
   * Récupère les réponses de l'utilisateur actuel
   */
  async getCurrentUserResponses(): Promise<ReflectionResponse[]> {
    try {
      const response = await api.get<ReflectionResponse[]>(`${this.baseUrl}/responses`);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des réponses:', error);
      throw error;
    }
  }

  /**
   * Récupère les réponses d'un utilisateur spécifique
   */
  async getUserResponses(userId: number): Promise<ReflectionResponse[]> {
    try {
      const response = await api.get<ReflectionResponse[]>(`${this.baseUrl}/responses/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la récupération des réponses utilisateur:', error);
      throw error;
    }
  }

  /**
   * Sauvegarde ou met à jour une réponse
   */
  async saveResponse(responseData: ReflectionResponseCreate): Promise<ReflectionResponse> {
    try {
      const response = await api.post<ReflectionResponse>(`${this.baseUrl}/responses`, responseData);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la sauvegarde de la réponse:', error);
      throw error;
    }
  }

  /**
   * Met à jour une réponse existante
   */
  async updateResponse(responseId: number, responseData: ReflectionResponseUpdate): Promise<ReflectionResponse> {
    try {
      const response = await api.put<ReflectionResponse>(`${this.baseUrl}/responses/${responseId}`, responseData);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la mise à jour de la réponse:', error);
      throw error;
    }
  }

  /**
   * Sauvegarde plusieurs réponses en lot
   */
  async saveResponsesBatch(batchData: ReflectionResponseBatch): Promise<ReflectionResponse[]> {
    try {
      const response = await api.post<ReflectionResponse[]>(`${this.baseUrl}/responses/batch`, batchData);
      return response.data;
    } catch (error) {
      console.error('Erreur lors de la sauvegarde en lot:', error);
      throw error;
    }
  }

  /**
   * Supprime une réponse
   */
  async deleteResponse(responseId: number): Promise<void> {
    try {
      await api.delete(`${this.baseUrl}/responses/${responseId}`);
    } catch (error) {
      console.error('Erreur lors de la suppression de la réponse:', error);
      throw error;
    }
  }

  /**
   * Combine les questions avec les réponses existantes
   */
  async getQuestionsWithResponses(): Promise<(ReflectionQuestion & { response?: ReflectionResponse })[]> {
    try {
      const [questions, responses] = await Promise.all([
        this.getQuestions(),
        this.getCurrentUserResponses()
      ]);

      // Créer un map des réponses par question_id
      const responsesMap = new Map<number, ReflectionResponse>();
      responses.forEach(response => {
        responsesMap.set(response.question_id, response);
      });

      // Combiner les questions avec leurs réponses
      return questions.map(question => ({
        ...question,
        response: responsesMap.get(question.id)
      }));
    } catch (error) {
      console.error('Erreur lors de la récupération des questions avec réponses:', error);
      throw error;
    }
  }
}

const reflectionService = new ReflectionService();
export default reflectionService;