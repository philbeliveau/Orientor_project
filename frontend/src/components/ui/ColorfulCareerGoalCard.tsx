'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Target, TrendingUp, Calendar, CheckCircle, Circle, Plus } from 'lucide-react';
import { CareerGoalsService, CareerGoal } from '@/services/careerGoalsService';

interface ColorfulCareerGoalCardProps {
  style?: React.CSSProperties;
  className?: string;
}

interface Milestone {
  task: string;
  completed: boolean;
}

export default function ColorfulCareerGoalCard({ style, className = '' }: ColorfulCareerGoalCardProps) {
  const [careerGoal, setCareerGoal] = useState<{
    title: string;
    description: string;
    targetDate: string;
    progress: number;
    milestones: Milestone[];
    hasActiveGoal: boolean;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchActiveCareerGoal = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await CareerGoalsService.getActiveCareerGoal();
        
        if (response.goal) {
          // Format the target date
          const targetDate = response.goal.target_date 
            ? new Date(response.goal.target_date).toLocaleDateString('en-US', { 
                month: 'short', 
                year: 'numeric' 
              })
            : 'No deadline';

          // Convert milestones to the expected format
          const milestones: Milestone[] = response.milestones?.slice(0, 4).map(m => ({
            task: m.skill_name,
            completed: m.is_completed
          })) || [];

          // Add placeholder milestones if we have fewer than 4
          while (milestones.length < 4) {
            milestones.push({
              task: "Complete skill assessment",
              completed: false
            });
          }

          setCareerGoal({
            title: response.goal.title,
            description: response.goal.description || "Work towards your dream career",
            targetDate,
            progress: Math.round(response.goal.progress_percentage || 0),
            milestones,
            hasActiveGoal: true
          });
        } else {
          // No active goal set
          setCareerGoal({
            title: "Set Your Career Goal",
            description: "Choose a career path to start your journey",
            targetDate: "Not set",
            progress: 0,
            milestones: [
              { task: "Take personality assessments", completed: false },
              { task: "Explore career recommendations", completed: false },
              { task: "Set your first career goal", completed: false },
              { task: "Create learning timeline", completed: false }
            ],
            hasActiveGoal: false
          });
        }
      } catch (err) {
        console.error('Error fetching active career goal:', err);
        setError('Unable to load career goal');
        // Fallback to default state
        setCareerGoal({
          title: "Set Your Career Goal",
          description: "Choose a career path to start your journey",
          targetDate: "Not set",
          progress: 0,
          milestones: [
            { task: "Take personality assessments", completed: false },
            { task: "Explore career recommendations", completed: false },
            { task: "Set your first career goal", completed: false },
            { task: "Create learning timeline", completed: false }
          ],
          hasActiveGoal: false
        });
      } finally {
        setLoading(false);
      }
    };

    fetchActiveCareerGoal();
  }, []);

  // Show loading state
  if (loading) {
    return (
      <div 
        className={`bg-gradient-to-br from-gray-400 to-gray-500 rounded-3xl p-4 sm:p-6 shadow-lg relative overflow-hidden touch-none select-none ${className}`}
        style={{
          minHeight: '200px',
          WebkitTapHighlightColor: 'transparent',
          touchAction: 'manipulation',
          ...style
        }}
      >
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
          <p className="ml-3 text-white text-sm">Loading career goal...</p>
        </div>
      </div>
    );
  }

  // Show error state
  if (error || !careerGoal) {
    return (
      <div 
        className={`bg-gradient-to-br from-red-400 to-red-500 rounded-3xl p-4 sm:p-6 shadow-lg relative overflow-hidden touch-none select-none ${className}`}
        style={{
          minHeight: '200px',
          WebkitTapHighlightColor: 'transparent',
          touchAction: 'manipulation',
          ...style
        }}
      >
        <div className="flex items-center justify-center h-full text-center">
          <div>
            <p className="text-white text-sm mb-2">Unable to load career goal</p>
            <Link
              href="/goals"
              className="text-white/80 hover:text-white text-xs underline"
            >
              Go to Career Goals →
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const completedMilestones = careerGoal.milestones.filter(m => m.completed).length;
  const totalMilestones = careerGoal.milestones.length;

  // Dynamic styling based on whether user has an active goal
  const cardColors = careerGoal.hasActiveGoal 
    ? 'from-teal-500 to-teal-600' 
    : 'from-blue-500 to-purple-600';

  return (
    <div 
      className={`bg-gradient-to-br ${cardColors} rounded-3xl p-4 sm:p-6 shadow-lg hover:shadow-xl active:scale-95 transition-all duration-300 relative overflow-hidden touch-none select-none ${className}`}
      style={{
        minHeight: '200px',
        WebkitTapHighlightColor: 'transparent',
        touchAction: 'manipulation',
        ...style
      }}
    >
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
      <div className="absolute bottom-0 left-0 w-20 h-20 bg-white/5 rounded-full translate-y-10 -translate-x-10"></div>
      
      {/* Header */}
      <div className="flex items-center justify-between mb-3 sm:mb-4 relative z-10">
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="w-8 h-8 sm:w-10 sm:h-10 bg-white/20 rounded-xl sm:rounded-2xl flex items-center justify-center backdrop-blur-sm">
            {careerGoal.hasActiveGoal ? (
              <Target className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            ) : (
              <Plus className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
            )}
          </div>
          <div>
            <h3 className="text-base sm:text-lg font-semibold text-white">
              {careerGoal.hasActiveGoal ? 'Career Goal' : 'Get Started'}
            </h3>
            <div className="flex items-center gap-1 sm:gap-2">
              <Calendar className="w-3 h-3 text-white/70" />
              <span className="text-white/70 text-xs sm:text-sm">{careerGoal.targetDate}</span>
            </div>
          </div>
        </div>
        <Link
          href={careerGoal.hasActiveGoal ? "/goals" : "/career/recommendations"}
          className="text-white/60 hover:text-white active:text-white transition-colors p-2 -m-2 rounded-lg"
          style={{ minWidth: '44px', minHeight: '44px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
        >
          {careerGoal.hasActiveGoal ? (
            <TrendingUp className="w-4 h-4 sm:w-5 sm:h-5" />
          ) : (
            <Plus className="w-4 h-4 sm:w-5 sm:h-5" />
          )}
        </Link>
      </div>

      {/* Goal Title */}
      <div className="mb-3 sm:mb-4 relative z-10">
        <h4 className="text-white text-lg sm:text-xl font-semibold mb-1 sm:mb-2">
          {careerGoal.title}
        </h4>
        <p className="text-white/80 text-xs sm:text-sm leading-relaxed line-clamp-2">
          {careerGoal.description}
        </p>
      </div>

      {/* Progress */}
      <div className="mb-4 sm:mb-6 relative z-10">
        <div className="flex items-center justify-between mb-2">
          <span className="text-white text-xs sm:text-sm font-medium">
            {careerGoal.hasActiveGoal ? 'Progress' : 'Getting Started'}
          </span>
          <span className="text-white text-xs sm:text-sm font-semibold">{careerGoal.progress}%</span>
        </div>
        <div className="w-full bg-white/20 rounded-full h-2">
          <div 
            className="bg-white h-2 rounded-full transition-all duration-500 shadow-sm"
            style={{ width: `${careerGoal.progress}%` }}
          ></div>
        </div>
      </div>

      {/* Milestones */}
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-3">
          <span className="text-white text-sm font-medium">
            {careerGoal.hasActiveGoal ? 'Key Milestones' : 'Next Steps'}
          </span>
          <span className="text-white/70 text-xs">{completedMilestones}/{totalMilestones} completed</span>
        </div>
        
        <div className="space-y-2">
          {careerGoal.milestones.slice(0, 3).map((milestone, index) => (
            <div key={index} className="flex items-center gap-3">
              {milestone.completed ? (
                <CheckCircle className="w-4 h-4 text-white flex-shrink-0" />
              ) : (
                <Circle className="w-4 h-4 text-white/60 flex-shrink-0" />
              )}
              <span 
                className={`text-xs flex-1 ${
                  milestone.completed ? 'text-white' : 'text-white/70'
                }`}
              >
                {milestone.task}
              </span>
            </div>
          ))}
        </div>

        {/* Action Button */}
        <div className="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-white/20">
          <Link
            href={careerGoal.hasActiveGoal ? "/goals" : "/career/recommendations"}
            className="inline-flex items-center gap-2 text-white text-xs sm:text-sm font-medium hover:text-white/80 active:text-white/80 transition-colors p-2 -m-2 rounded-lg"
            style={{ minHeight: '44px' }}
          >
            <span>
              {careerGoal.hasActiveGoal ? 'View Details' : 'Explore Careers'}
            </span>
            <svg className="w-3 h-3 sm:w-4 sm:h-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6-1.41-1.41z"/>
            </svg>
          </Link>
        </div>
      </div>
    </div>
  );
}