import api from './api';

export interface Course {
  id: number;
  course_name: string;
  course_code?: string;
  semester?: string;
  year?: number;
  professor?: string;
  subject_category?: string;
  grade?: string;
  credits?: number;
  description?: string;
  learning_outcomes?: string[];
  created_at: string;
  updated_at: string;
}

export interface CourseCreate {
  course_name: string;
  course_code?: string;
  semester?: string;
  year?: number;
  professor?: string;
  subject_category?: string;
  grade?: string;
  credits?: number;
  description?: string;
  learning_outcomes?: string[];
}

export interface PsychologicalInsight {
  id: number;
  insight_type: string;
  insight_value: any;
  confidence_score: number;
  evidence_source: string;
  extracted_at: string;
  course_id: number;
  user_id: number;
}

export interface CareerSignal {
  id: number;
  signal_type: string;
  strength_score: number;
  evidence_source: string;
  pattern_metadata?: any;
  esco_skill_mapping?: any;
  trend_analysis?: any;
  created_at: string;
  updated_at: string;
  course_id?: number;
  user_id: number;
}

export interface AnalysisSession {
  session_id: string;
  conversation_started: boolean;
  next_questions: Array<{
    id: string;
    question: string;
    intent: string;
    follow_up_triggers: string[];
  }>;
  context_insights?: any;
}

export interface AnalysisResponse {
  next_questions: Array<{
    id: string;
    question: string;
    intent: string;
  }>;
  insights_discovered: PsychologicalInsight[];
  session_complete: boolean;
  career_recommendations: any[];
}

export interface PsychologicalProfile {
  user_id: number;
  profile_summary: {
    cognitive_preferences: any;
    work_style_indicators: any;
    subject_affinities: any;
    career_readiness: any;
    confidence_score: number;
  };
  insights_by_course: Record<number, PsychologicalInsight[]>;
  career_signals: CareerSignal[];
  esco_recommendations: any;
  last_updated: string;
}

export interface CareerSignalsData {
  user_id: number;
  signals: CareerSignal[];
  pattern_analysis: any;
  esco_tree_paths: any[];
  trend_indicators: any;
  recommendations: any[];
}

export interface ConversationSummary {
  session_id: string;
  summary: any;
  total_questions: number;
  insights_count: number;
  key_discoveries: string[];
  career_recommendations: any[];
  next_steps: string[];
}

class CourseAnalysisService {
  // Course Management
  async getCourses(filters?: {
    semester?: string;
    year?: number;
    subject_category?: string;
  }): Promise<Course[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) {
          params.append(key, value.toString());
        }
      });
    }
    
    const url = `/api/v1/courses${params.toString() ? `?${params.toString()}` : ''}`;
    const response = await api.get(url);
    return response.data;
  }

  async getCourse(courseId: number): Promise<Course> {
    const response = await api.get(`/api/v1/courses/${courseId}`);
    return response.data;
  }

  async createCourse(courseData: CourseCreate): Promise<Course> {
    const response = await api.post('/api/v1/courses', courseData);
    return response.data;
  }

  async updateCourse(courseId: number, updateData: Partial<CourseCreate>): Promise<Course> {
    const response = await api.put(`/api/v1/courses/${courseId}`, updateData);
    return response.data;
  }

  async deleteCourse(courseId: number): Promise<void> {
    await api.delete(`/api/v1/courses/${courseId}`);
  }

  // Career Analysis
  async startTargetedAnalysis(
    courseId: number, 
    focusAreas?: string[],
    userContext?: any
  ): Promise<AnalysisSession> {
    const response = await api.post(`/api/v1/courses/${courseId}/targeted-analysis`, {
      focus_areas: focusAreas,
      user_context: userContext
    });
    return response.data;
  }

  async respondToQuestion(
    sessionId: string,
    questionId: string,
    userResponse: string
  ): Promise<AnalysisResponse> {
    const response = await api.post(`/api/v1/conversations/${sessionId}/respond`, {
      question_id: questionId,
      response: userResponse
    });
    return response.data;
  }

  // Psychological Profile
  async getPsychologicalProfile(userId: number): Promise<PsychologicalProfile> {
    const response = await api.get(`/api/v1/psychological-profile/${userId}`);
    return response.data;
  }

  async getCareerSignals(userId: number): Promise<CareerSignalsData> {
    const response = await api.get(`/api/v1/career-signals/${userId}`);
    return response.data;
  }

  // Course Insights
  async getCourseInsights(courseId: number): Promise<PsychologicalInsight[]> {
    const response = await api.get(`/api/v1/courses/${courseId}/insights`);
    return response.data;
  }

  // Session Management
  async getConversationSummary(sessionId: string): Promise<ConversationSummary> {
    const response = await api.get(`/api/v1/conversations/${sessionId}/summary`);
    return response.data;
  }

  // Utility Methods
  getSubjectCategoryOptions(): Array<{ value: string; label: string }> {
    return [
      { value: 'STEM', label: 'STEM' },
      { value: 'business', label: 'Business' },
      { value: 'humanities', label: 'Humanities' },
      { value: 'arts', label: 'Arts' },
      { value: 'social_sciences', label: 'Social Sciences' },
      { value: 'other', label: 'Other' }
    ];
  }

  getInsightTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      'cognitive_preference': 'Cognitive Style',
      'work_style': 'Work Preferences',
      'subject_affinity': 'Subject Interests',
      'learning_preference': 'Learning Style'
    };
    return labels[type] || type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  getSignalTypeLabel(type: string): string {
    const labels: Record<string, string> = {
      'analytical_thinking': 'Analytical Thinking',
      'creative_problem_solving': 'Creative Problem Solving',
      'interpersonal_skills': 'Interpersonal Skills',
      'leadership_potential': 'Leadership Potential',
      'attention_to_detail': 'Attention to Detail',
      'stress_tolerance': 'Stress Tolerance'
    };
    return labels[type] || type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  getSignalStrengthLabel(strength: number): string {
    if (strength >= 0.8) return 'Strong';
    if (strength >= 0.6) return 'Developing';
    if (strength >= 0.4) return 'Emerging';
    return 'Initial';
  }

  getConfidenceLabel(confidence: number): string {
    if (confidence >= 0.8) return 'High Confidence';
    if (confidence >= 0.6) return 'Medium Confidence';
    return 'Low Confidence';
  }

  // Formatting Helpers
  formatInsightValue(type: string, value: any): string {
    if (typeof value === 'object') {
      if (type === 'cognitive_preference') {
        return Object.entries(value)
          .map(([key, val]) => `${key}: ${val}`)
          .join(', ');
      }
      return JSON.stringify(value);
    }
    return String(value);
  }

  // Filter and Search
  filterCoursesByTimeframe(courses: Course[], timeframe: 'all' | 'semester' | 'year'): Course[] {
    if (timeframe === 'all') return courses;
    
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth();
    const currentSemester = currentMonth >= 8 ? 'Fall' : currentMonth >= 5 ? 'Summer' : 'Spring';
    
    return courses.filter(course => {
      if (timeframe === 'year') {
        return course.year === currentYear;
      }
      if (timeframe === 'semester') {
        return course.year === currentYear && course.semester === currentSemester;
      }
      return true;
    });
  }

  groupInsightsByType(insights: PsychologicalInsight[]): Record<string, PsychologicalInsight[]> {
    return insights.reduce((groups, insight) => {
      const type = insight.insight_type;
      if (!groups[type]) {
        groups[type] = [];
      }
      groups[type].push(insight);
      return groups;
    }, {} as Record<string, PsychologicalInsight[]>);
  }

  calculateOverallCareerReadiness(signals: CareerSignal[]): number {
    if (signals.length === 0) return 0;
    
    const totalStrength = signals.reduce((sum, signal) => sum + signal.strength_score, 0);
    return totalStrength / signals.length;
  }

  // Recommendation Helpers
  suggestNextCourseAnalysis(courses: Course[], analyzedCourseIds: number[]): Course | null {
    const unanalyzedCourses = courses.filter(course => !analyzedCourseIds.includes(course.id));
    
    if (unanalyzedCourses.length === 0) return null;
    
    // Prioritize recent courses with grades
    return unanalyzedCourses
      .filter(course => course.grade)
      .sort((a, b) => {
        const dateA = new Date(a.updated_at);
        const dateB = new Date(b.updated_at);
        // Handle invalid dates by treating them as older (epoch time)
        const timeA = isNaN(dateA.getTime()) ? 0 : dateA.getTime();
        const timeB = isNaN(dateB.getTime()) ? 0 : dateB.getTime();
        return timeB - timeA;
      })[0] || 
      unanalyzedCourses[0];
  }

  identifyMissingAnalyses(profile: PsychologicalProfile): string[] {
    const suggestions: string[] = [];
    
    const insightTypes = ['cognitive_preference', 'work_style', 'subject_affinity'];
    const signalTypes = ['analytical_thinking', 'creative_problem_solving', 'interpersonal_skills'];
    
    // Check for missing insight types
    const allInsights = Object.values(profile.insights_by_course).flat();
    const presentInsightTypes = new Set(allInsights.map(i => i.insight_type));
    
    insightTypes.forEach(type => {
      if (!presentInsightTypes.has(type)) {
        suggestions.push(`Complete analysis to discover your ${this.getInsightTypeLabel(type).toLowerCase()}`);
      }
    });
    
    // Check for weak signals
    const weakSignals = profile.career_signals.filter(s => s.strength_score < 0.5);
    if (weakSignals.length > 0) {
      suggestions.push(`Strengthen ${weakSignals.length} developing skill areas through targeted coursework`);
    }
    
    return suggestions;
  }
}

export const courseAnalysisService = new CourseAnalysisService();