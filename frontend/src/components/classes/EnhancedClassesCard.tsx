'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { BookOpen, Clock, Users, Brain, TrendingUp, MessageCircle } from 'lucide-react';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { courseAnalysisService } from '@/services/courseAnalysisService';

interface Course {
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
  // Analysis status
  insights_count?: number;
  last_analysis?: string;
  career_readiness_score?: number;
}

interface EnhancedClassesCardProps {
  style?: React.CSSProperties;
  className?: string;
  userId?: number;
}

const EnhancedClassesCard: React.FC<EnhancedClassesCardProps> = ({ 
  style, 
  className = '', 
  userId 
}) => {
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAnalysisPrompt, setShowAnalysisPrompt] = useState(false);

  // Fetch user's courses
  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true);
        const coursesData = await courseAnalysisService.getCourses();
        setCourses(coursesData.slice(0, 3)); // Show top 3 most recent courses

        // Check if any courses need analysis
        const needsAnalysis = coursesData.some((course: Course) => 
          !course.insights_count || course.insights_count === 0
        );
        setShowAnalysisPrompt(needsAnalysis);

      } catch (err) {
        console.error('Error fetching courses:', err);
        setError('Unable to load courses');
        // Fallback to mock data for development
        setCourses(getMockCourses());
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, [userId]);

  const getMockCourses = (): Course[] => [
    {
      id: 1,
      course_name: 'Data Science Fundamentals',
      course_code: 'DS 101',
      semester: 'Fall',
      year: 2024,
      professor: 'Dr. Sarah Chen',
      subject_category: 'STEM',
      grade: 'A-',
      credits: 3,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      insights_count: 5,
      last_analysis: '2024-01-15',
      career_readiness_score: 0.85
    },
    {
      id: 2,
      course_name: 'Business Strategy',
      course_code: 'BUS 301',
      semester: 'Fall',
      year: 2024,
      professor: 'Prof. Alex Kumar',
      subject_category: 'business',
      grade: 'B+',
      credits: 3,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      insights_count: 0,
      career_readiness_score: 0.72
    },
    {
      id: 3,
      course_name: 'Psychology of Learning',
      course_code: 'PSY 205',
      semester: 'Fall',
      year: 2024,
      professor: 'Dr. Maria Rodriguez',
      subject_category: 'humanities',
      grade: 'A',
      credits: 3,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      insights_count: 3,
      last_analysis: '2024-01-10',
      career_readiness_score: 0.78
    }
  ];

  const getSubjectColor = (category?: string) => {
    const colors = {
      'STEM': 'bg-gradient-to-br from-blue-500 to-blue-600',
      'business': 'bg-gradient-to-br from-green-500 to-green-600',
      'humanities': 'bg-gradient-to-br from-purple-500 to-purple-600',
      'arts': 'bg-gradient-to-br from-pink-500 to-pink-600',
      'social_sciences': 'bg-gradient-to-br from-teal-500 to-teal-600'
    };
    return colors[category as keyof typeof colors] || 'bg-gradient-to-br from-gray-500 to-gray-600';
  };

  const getCareerReadinessColor = (score?: number) => {
    if (!score) return 'text-gray-400';
    if (score >= 0.8) return 'text-green-500';
    if (score >= 0.6) return 'text-yellow-500';
    return 'text-orange-500';
  };

  const handleStartAnalysis = (courseId: number) => {
    // Navigate to course analysis page
    window.location.href = `/classes/${courseId}/analysis`;
  };

  if (loading) {
    return (
      <div 
        className={`bg-gradient-to-br from-orange-500 to-orange-600 rounded-3xl p-6 shadow-lg flex items-center justify-center ${className}`} 
        style={style}
      >
        <div className="text-white text-center">
          <LoadingSpinner size="md" color="white" />
          <p className="text-sm mt-2">Loading courses...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div 
        className={`bg-gradient-to-br from-red-500 to-red-600 rounded-3xl p-6 shadow-lg ${className}`} 
        style={style}
      >
        <div className="text-white text-center">
          <p className="text-sm mb-4">{error}</p>
          <Link 
            href="/classes/add"
            className="inline-block bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg text-sm transition-colors"
          >
            Add Course
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`bg-gradient-to-br from-orange-500 to-orange-600 rounded-3xl p-4 shadow-lg hover:shadow-xl transition-all duration-300 relative overflow-hidden ${className}`} 
      style={style}
    >
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
      <div className="absolute bottom-0 left-0 w-20 h-20 bg-white/5 rounded-full translate-y-10 -translate-x-10"></div>
      
      {/* Header */}
      <div className="flex items-center justify-between mb-4 relative z-10">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
            <BookOpen className="w-4 h-4 text-white" />
          </div>
          <div>
            <h3 className="text-base font-semibold text-white">My Classes</h3>
            <p className="text-xs text-orange-100">Career Insights</p>
          </div>
        </div>
        
        {/* Career readiness indicator */}
        {courses.length > 0 && (
          <div className="flex items-center gap-1">
            <Brain className="w-4 h-4 text-white/70" />
            <span className="text-xs text-white/70">
              {Math.round((courses.reduce((sum, course) => sum + (course.career_readiness_score || 0), 0) / courses.length) * 100)}%
            </span>
          </div>
        )}
      </div>

      {/* Analysis prompt banner */}
      {showAnalysisPrompt && (
        <div className="mb-3 p-2 bg-white/20 rounded-lg border border-white/30 relative z-10">
          <div className="flex items-center gap-2">
            <MessageCircle className="w-4 h-4 text-white" />
            <p className="text-xs text-white font-medium">Discover Your Career Preferences</p>
          </div>
          <p className="text-xs text-orange-100 mt-1">
            Complete career analysis for your courses to unlock personalized insights
          </p>
        </div>
      )}

      {/* Courses List */}
      <div className="space-y-2 relative z-10">
        {courses.length === 0 ? (
          <div className="text-center py-6">
            <BookOpen className="w-8 h-8 text-white/50 mx-auto mb-2" />
            <p className="text-sm text-white/70 mb-3">No courses added yet</p>
            <Link 
              href="/classes/add"
              className="inline-block bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg text-sm text-white transition-colors"
            >
              Add Your First Course
            </Link>
          </div>
        ) : (
          courses.map((course) => (
            <div 
              key={course.id} 
              className="group hover:bg-white/10 rounded-xl p-2 transition-all duration-200 cursor-pointer backdrop-blur-sm"
              onClick={() => window.location.href = `/classes/${course.id}`}
            >
              <div className="flex items-center gap-2">
                {/* Course Icon */}
                <div className={`w-8 h-8 ${getSubjectColor(course.subject_category)} rounded-lg flex items-center justify-center text-white shadow-sm flex-shrink-0`}>
                  <span className="text-sm font-semibold">
                    {course.course_code?.charAt(0) || (course.course_name && course.course_name.charAt(0)) || '?'}
                  </span>
                </div>
                
                {/* Course Info */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-sm text-white truncate">
                      {course.course_name}
                    </h4>
                    {course.grade && (
                      <span className="text-xs text-orange-200 font-medium ml-2">
                        {course.grade}
                      </span>
                    )}
                  </div>
                  
                  <div className="flex items-center justify-between mt-1">
                    <div className="flex items-center gap-2">
                      <Clock className="w-3 h-3 text-orange-200" />
                      <span className="text-xs text-orange-200">
                        {course.semester} {course.year}
                      </span>
                    </div>
                    
                    {/* Analysis Status */}
                    <div className="flex items-center gap-2">
                      {course.insights_count && course.insights_count > 0 ? (
                        <div className="flex items-center gap-1">
                          <Brain className="w-3 h-3 text-green-300" />
                          <span className="text-xs text-green-300">
                            {course.insights_count} insights
                          </span>
                        </div>
                      ) : (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleStartAnalysis(course.id);
                          }}
                          className="text-xs bg-white/20 hover:bg-white/30 px-2 py-1 rounded text-white transition-colors"
                        >
                          Analyze
                        </button>
                      )}
                      
                      {course.career_readiness_score && (
                        <div className="flex items-center gap-1">
                          <TrendingUp className={`w-3 h-3 ${getCareerReadinessColor(course.career_readiness_score)}`} />
                          <span className={`text-xs ${getCareerReadinessColor(course.career_readiness_score)}`}>
                            {Math.round(course.career_readiness_score * 100)}%
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="mt-4 pt-3 border-t border-white/20 relative z-10">
        <div className="flex items-center justify-between">
          <Link 
            href="/classes"
            className="text-center text-xs text-white hover:text-orange-100 font-medium transition-colors flex items-center gap-1"
          >
            <span>View All Classes</span>
            <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </Link>
          
          <Link
            href="/classes/insights"
            className="text-xs bg-white/20 hover:bg-white/30 px-3 py-1 rounded-lg text-white transition-colors flex items-center gap-1"
          >
            <Brain className="w-3 h-3" />
            <span>Career Insights</span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default EnhancedClassesCard;
