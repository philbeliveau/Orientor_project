import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
// const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
});

// Add request interceptor to include the token
api.interceptors.request.use((config) => {
  // Check if we're in a browser environment before accessing localStorage
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) {
      // @ts-ignore
      config.headers = config.headers || {};
      // @ts-ignore
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// Function to get career recommendations for the Find Your Way tab
export const getCareerRecommendations = async (limit = 30) => {
  try {
    console.log('Fetching career recommendations from:', `${API_URL}/careers/recommendations?limit=${limit}`);
    const response = await api.get(`/api/v1/careers/recommendations?limit=${limit}`);
    return response.data;
  } catch (error: any) {
    console.error('Error fetching career recommendations:', error);
    if (error?.response) {
      console.error('API Error Details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        config: {
          baseURL: error.config?.baseURL,
          url: error.config?.url,
          headers: error.config?.headers
        }
      });
    }
    throw error;
  }
};

// Function to save a career when user swipes right
export const saveCareer = async (careerId: number) => {
  try {
    const response = await api.post(`/api/v1/careers/save/${careerId}`);
    return response.data;
  } catch (error) {
    console.error('Error saving career:', error);
    throw error;
  }
};

// Function to get saved careers (for the My Space section)
export const getSavedCareers = async () => {
  try {
    const response = await api.get('/api/v1/careers/saved');
    return response.data;
  } catch (error) {
    console.error('Error fetching saved careers:', error);
    throw error;
  }
};

// Function to get job recommendations for the homepage
export const getJobRecommendations = async (userId?: number, top_k: number = 3) => {
  try {
    // Si userId n'est pas fourni, utilise l'utilisateur courant
    const endpoint = userId
      ? `/api/v1/jobs/recommendations/${userId}?top_k=${top_k}`
      : `/api/v1/jobs/recommendations/me?top_k=${top_k}`;
    
    console.log('Calling job recommendations API:', `${API_URL}${endpoint}`);
    const response = await api.get(endpoint);
    console.log('Job recommendations API response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching job recommendations:', error);
    console.error('API Error Details:', {
      status: (error as any)?.response?.status,
      statusText: (error as any)?.response?.statusText,
      data: (error as any)?.response?.data,
      config: {
        baseURL: (error as any)?.config?.baseURL,
        url: (error as any)?.config?.url,
        headers: (error as any)?.config?.headers
      }
    });
    throw error;
  }
};

// Function to get the skills tree for a specific job
export const getJobSkillsTree = async (jobId: string, depth: number = 1, maxNodes: number = 5) => {
  try {
    const endpoint = `/api/v1/jobs/skill-tree/${jobId}?depth=${depth}&max_nodes=${maxNodes}`;
    console.log('Calling job skills tree API:', `${API_URL}${endpoint}`);
    const response = await api.get(endpoint);
    console.log('Job skills tree API response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching job skills tree:', error);
    console.error('API Error Details:', {
      status: (error as any)?.response?.status,
      statusText: (error as any)?.response?.statusText,
      data: (error as any)?.response?.data,
      config: {
        baseURL: (error as any)?.config?.baseURL,
        url: (error as any)?.config?.url,
        headers: (error as any)?.config?.headers
      }
    });
    throw error;
  }
};

// Function to get all job recommendations for the career recommendations page
export const getAllJobRecommendations = async (limit: number = 30) => {
  try {
    // Use the /recommendations/me endpoint with a higher limit
    const endpoint = `/api/v1/jobs/recommendations/me?top_k=${limit}&embedding_type=esco_embedding`;
    console.log('🔍 Fetching recommendations with limit:', limit);
    const response = await api.get(endpoint);
    
    // Filter out base64 data from the response
    const cleanResponse = {
      ...response.data,
      recommendations: response.data?.recommendations?.map((rec: any) => ({
        id: rec.id,
        score: rec.score,
        metadata: {
          ...rec.metadata,
          // Remove any base64 data from metadata
          visualizations: undefined,
          plotly: undefined,
          matplotlib: undefined,
          streamlit: undefined
        }
      }))
    };
    
    // Log only relevant information
    if (cleanResponse.recommendations) {
      console.log('📊 Recommendations summary:', {
        count: cleanResponse.recommendations.length,
        titles: cleanResponse.recommendations.map((r: any) => r.metadata?.title || r.metadata?.preferred_label),
        userId: cleanResponse.user_id
      });
    }
    
    return cleanResponse;
  } catch (error) {
    console.error('❌ Error fetching recommendations:', {
      status: (error as any)?.response?.status,
      message: (error as any)?.response?.data?.detail || 'Unknown error'
    });
    throw error;
  }
};

export default api;