import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Type definitions
export interface Recommendation {
  id: number;
  oasis_code: string;
  label: string;
  description?: string;
  main_duties?: string;
  role_creativity?: number;
  role_leadership?: number;
  role_digital_literacy?: number;
  role_critical_thinking?: number;
  role_problem_solving?: number;
  saved_at: string;
  skill_comparison?: SkillComparison;
  notes?: Note[];
}

export interface SkillComparison {
  user_skills: UserSkills;
  job_skills: UserSkills;
}

export interface Note {
  id: number;
  content: string;
  saved_recommendation_id?: number;
  created_at: string;
  updated_at: string;
}

export interface NoteCreate {
  content: string;
  saved_recommendation_id?: number;
}

export interface NoteUpdate {
  content: string;
}

export interface UserSkills {
  creativity?: number;
  leadership?: number;
  digital_literacy?: number;
  critical_thinking?: number;
  problem_solving?: number;
}

// Configure axios with the token
const getAuthHeader = () => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  return {
    headers: {
      Authorization: `Bearer ${token}`
    }
  };
};

// Fetch saved recommendations
export const fetchSavedRecommendations = async (): Promise<Recommendation[]> => {
  try {
    const response = await axios.get<Recommendation[]>(`${API_URL}/space/recommendations`, getAuthHeader());
    console.log('API response:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching saved recommendations:', error);
    throw error;
  }
};

// Save a recommendation
export const saveRecommendation = async (recommendation: Recommendation): Promise<Recommendation> => {
  try {
    const response = await axios.post<Recommendation>(
      `${API_URL}/space/recommendations`, 
      recommendation, 
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Error saving recommendation:', error);
    throw error;
  }
};

// Delete a saved recommendation
export const deleteRecommendation = async (recommendationId: number): Promise<void> => {
  try {
    await axios.delete(
      `${API_URL}/space/recommendations/${recommendationId}`, 
      getAuthHeader()
    );
  } catch (error) {
    console.error('Error deleting recommendation:', error);
    throw error;
  }
};

// Fetch notes for a recommendation
export const fetchNotes = async (recommendationId: number): Promise<Note[]> => {
  try {
    const response = await axios.get<Note[]>(
      `${API_URL}/space/notes?saved_recommendation_id=${recommendationId}`, 
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching notes:', error);
    throw error;
  }
};

// Create a new note
export const createNote = async (note: NoteCreate): Promise<Note> => {
  try {
    const response = await axios.post<Note>(
      `${API_URL}/space/notes`, 
      note, 
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Error creating note:', error);
    throw error;
  }
};

// Update a note
export const updateNote = async (noteId: number, updates: NoteUpdate): Promise<Note> => {
  try {
    const response = await axios.put<Note>(
      `${API_URL}/space/notes/${noteId}`, 
      updates, 
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Error updating note:', error);
    throw error;
  }
};

// Delete a note
export const deleteNote = async (noteId: number): Promise<void> => {
  try {
    await axios.delete(
      `${API_URL}/space/notes/${noteId}`, 
      getAuthHeader()
    );
  } catch (error) {
    console.error('Error deleting note:', error);
    throw error;
  }
};

// Update user skills
export const updateUserSkills = async (skills: UserSkills): Promise<UserSkills> => {
  try {
    const response = await axios.put<UserSkills>(
      `${API_URL}/space/skills`, 
      skills, 
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Error updating skills:', error);
    throw error;
  }
};

// Get skill comparison data
export const getSkillComparison = async (oasisCode: string): Promise<any> => {
  try {
    const response = await axios.get(
      `${API_URL}/space/recommendations/${oasisCode}/skill-comparison`, 
      getAuthHeader()
    );
    return response.data;
  } catch (error) {
    console.error('Error fetching skill comparison:', error);
    throw error;
  }
}; 