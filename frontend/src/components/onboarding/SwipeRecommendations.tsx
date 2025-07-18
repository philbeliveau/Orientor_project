'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, useMotionValue, useTransform, PanInfo, animate } from 'framer-motion';
import { Heart, X, ArrowLeft, CheckCircle, RefreshCw } from 'lucide-react';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { PsychProfile, CareerRecommendation } from '../../types/onboarding';
import { getAllJobRecommendations } from '../../services/api';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import SetCareerGoalButton from '@/components/common/SetCareerGoalButton';

interface SwipeRecommendationsProps {
  onComplete: () => void;
  psychProfile?: PsychProfile;
}

const SwipeRecommendations: React.FC<SwipeRecommendationsProps> = ({ 
  onComplete, 
  psychProfile 
}) => {
  const router = useRouter();
  const [currentIndex, setCurrentIndex] = useState(0);
  const [savedCareers, setSavedCareers] = useState<CareerRecommendation[]>([]);
  const [isComplete, setIsComplete] = useState(false);
  const [recommendations, setRecommendations] = useState<CareerRecommendation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Framer Motion values for swipe animation (same as FindYourWay)
  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-10, 10]);
  const cardOpacity = useTransform(x, [-200, 0, 200], [0.5, 1, 0.5]);
  const dragConstraints = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await getAllJobRecommendations(10); // Get 10 recommendations for onboarding
      
      if (response.recommendations && response.recommendations.length > 0) {
        const formattedRecommendations: CareerRecommendation[] = response.recommendations.map((rec: any, index: number) => ({
          id: rec.id || `rec-${index}`,
          title: rec.metadata?.title || rec.metadata?.preferred_label || 'Career Opportunity',
          description: rec.metadata?.description || 'Explore this exciting career opportunity based on your personality profile.',
          match_percentage: Math.round((1 - rec.score) * 100), // Convert distance to percentage
          skills_required: rec.metadata?.skills || ['Professional Skills', 'Communication', 'Problem Solving'],
          education_level: rec.metadata?.education_level || 'Bachelor\'s degree or equivalent experience'
        }));
        
        setRecommendations(formattedRecommendations);
      } else {
        setError('No recommendations available at the moment');
      }
    } catch (error) {
      console.error('Failed to load recommendations:', error);
      setError('Failed to load recommendations. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Same drag handling logic as FindYourWay component
  const handleDragEnd = async (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    const swipeThreshold = 100;
    const career = recommendations[currentIndex];
    
    if (!career) return;

    if (info.offset.x > swipeThreshold) {
      await handleSwipeRight(career);
    } else if (info.offset.x < -swipeThreshold) {
      handleSwipeLeft();
    } else {
      // Reset position with spring animation
      animate(x, 0, {
        type: "spring",
        stiffness: 300,
        damping: 30,
        onComplete: () => {
          x.set(0);
        }
      });
    }
  };

  const handleSwipeRight = async (career: CareerRecommendation) => {
    try {
      // Use the same save mechanism as SaveJobButton to ensure consistency with /space tab
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('Authentication required');
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const jobData = {
        oasis_code: career.id,
        label: career.title || 'Untitled Job',
        description: career.description || '',
        main_duties: '',
        // Default skill values
        role_creativity: 3.0,
        role_leadership: 3.0,
        role_digital_literacy: 3.0,
        role_critical_thinking: 3.0,
        role_problem_solving: 3.0,
        // Default cognitive traits
        analytical_thinking: 3.5,
        attention_to_detail: 3.5,
        collaboration: 3.5,
        adaptability: 3.5,
        independence: 3.5,
        evaluation: 3.5,
        decision_making: 3.5,
        stress_tolerance: 3.5,
        all_fields: {
          title: career.title,
          description: career.description,
          skills_required: career.skills_required,
          education_level: career.education_level,
          match_percentage: career.match_percentage
        }
      };

      console.log('Saving job data:', jobData);
      console.log('API URL:', apiUrl);
      console.log('Token present:', !!token);

      const response = await axios.post(
        `${apiUrl}/space/recommendations`,
        jobData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      console.log('Save response:', response.status, response.data);
      console.log('✅ Successfully saved career:', career.title);
      setSavedCareers(prev => [...prev, career]);
      
      // Reset position and move to next card
      animate(x, 0, {
        type: "spring",
        stiffness: 300,
        damping: 30,
        onComplete: () => {
          x.set(0);
          if (currentIndex >= recommendations.length - 1) {
            setIsComplete(true);
          } else {
            setCurrentIndex(prev => prev + 1);
          }
        }
      });
    } catch (err: any) {
      console.error('Failed to save career:', err);
      console.error('Error details:', {
        message: err.message,
        response: err.response,
        status: err.response?.status,
        data: err.response?.data
      });
      
      // Handle duplicate entries like SaveJobButton does
      if (err.response?.status === 409 && err.response?.data?.detail?.includes('already saved')) {
        console.log('Job already saved, treating as success');
        setSavedCareers(prev => [...prev, career]);
      }
      
      // Still move to next card even if save fails
      animate(x, 0, {
        type: "spring",
        stiffness: 300,
        damping: 30,
        onComplete: () => {
          x.set(0);
          if (currentIndex >= recommendations.length - 1) {
            setIsComplete(true);
          } else {
            setCurrentIndex(prev => prev + 1);
          }
        }
      });
    }
  };

  const handleSwipeLeft = () => {
    // Reset position and move to next card
    animate(x, 0, {
      type: "spring",
      stiffness: 300,
      damping: 30,
      onComplete: () => {
        x.set(0);
        if (currentIndex >= recommendations.length - 1) {
          setIsComplete(true);
        } else {
          setCurrentIndex(prev => prev + 1);
        }
      }
    });
  };

  const handleButtonSwipe = (direction: 'left' | 'right') => {
    const currentCard = recommendations[currentIndex];
    if (!currentCard) return;

    if (direction === 'right') {
      handleSwipeRight(currentCard);
    } else {
      handleSwipeLeft();
    }
  };

  const currentCard = recommendations[currentIndex];
  const progress = recommendations.length > 0 ? ((currentIndex + 1) / recommendations.length) * 100 : 0;
  const hasMoreCards = currentIndex < recommendations.length;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="text-center">
          <LoadingSpinner size="lg" />
          <p className="text-gray-600">Loading career recommendations...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="text-center max-w-md">
          <div className="text-red-500 mb-4">
            <X className="w-16 h-16 mx-auto mb-2" />
            <h2 className="text-xl font-semibold mb-2">Something went wrong</h2>
            <p className="text-gray-600 mb-4">{error}</p>
          </div>
          <button
            onClick={loadRecommendations}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center mx-auto space-x-2"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Try Again</span>
          </button>
        </div>
      </div>
    );
  }

  if (isComplete) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="bg-white rounded-3xl p-8 shadow-lg max-w-md w-full text-center"
        >
          <div className="mb-6">
            <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Great choices!
            </h2>
            <p className="text-gray-600">
              You've saved {savedCareers.length} career{savedCareers.length !== 1 ? 's' : ''} to explore further.
            </p>
          </div>

          {savedCareers.length > 0 && (
            <div className="mb-6">
              <h3 className="font-semibold text-gray-800 mb-3">Your Saved Careers:</h3>
              <div className="space-y-2">
                {savedCareers.map((career) => (
                  <div key={career.id} className="bg-gray-50 rounded-xl p-3 text-left">
                    <div className="flex items-center justify-between">
                      <span className="font-medium text-sm">{career.title}</span>
                      <span className="text-xs text-blue-600 font-semibold">
                        {career.match_percentage}% match
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="space-y-3">
            <button
              onClick={() => {
                console.log('Completing onboarding and redirecting to dashboard...');
                onComplete(); // Call the parent callback
                // Direct redirect to dashboard
                setTimeout(() => {
                  console.log('SwipeRecommendations: Redirecting to dashboard');
                  router.push('/dashboard');
                }, 500);
              }}
              className="w-full bg-blue-500 text-white py-3 px-6 rounded-xl hover:bg-blue-600 transition-colors font-medium"
            >
              Continue to Dashboard
            </button>
            <button
              onClick={() => {
                setCurrentIndex(0);
                setSavedCareers([]);
                setIsComplete(false);
                loadRecommendations();
              }}
              className="w-full bg-gray-100 text-gray-700 py-3 px-6 rounded-xl hover:bg-gray-200 transition-colors font-medium"
            >
              Explore More Careers
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  if (!hasMoreCards || !currentCard) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="text-center">
          <h2 className="text-xl font-semibold mb-4">No more recommendations</h2>
          <button
            onClick={() => setIsComplete(true)}
            className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors"
          >
            View Results
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-white border-b border-gray-200">
        <button 
          onClick={onComplete}
          className="p-2 hover:bg-gray-100 rounded-full transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <div className="flex-1 mx-4">
          <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
            <motion.div 
              className="h-full bg-blue-500"
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <p className="text-sm text-gray-600 mt-1 text-center">
            {currentIndex + 1} of {recommendations.length}
          </p>
        </div>
        <div className="w-9" /> {/* Spacer for balance */}
      </div>

      {/* Card Container */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div 
          ref={dragConstraints} 
          className="w-full max-w-sm h-96 relative"
        >
          <motion.div
            drag="x"
            dragConstraints={dragConstraints}
            dragElastic={0.7}
            onDragEnd={handleDragEnd}
            style={{
              x,
              rotate,
              opacity: cardOpacity,
            }}
            className="w-full h-full absolute cursor-grab active:cursor-grabbing"
            initial={{ x: 0, rotate: 0 }}
            animate={{ x: 0, rotate: 0 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
          >
            <div className="bg-white rounded-2xl shadow-lg h-full p-6 flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                  {currentCard.match_percentage}% match
                </span>
              </div>
              
              <h3 className="text-xl font-bold text-gray-800 mb-3">
                {currentCard.title}
              </h3>
              
              <p className="text-gray-600 text-sm mb-4 flex-1">
                {currentCard.description}
              </p>
              
              <div className="mb-4">
                <h4 className="font-semibold text-gray-800 mb-2">Key Skills:</h4>
                <div className="flex flex-wrap gap-2">
                  {currentCard.skills_required?.slice(0, 3).map((skill, index) => (
                    <span 
                      key={index}
                      className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
              
              <div className="text-xs text-gray-500 mb-4">
                {currentCard.education_level}
              </div>
              
              {/* Career Goal Button */}
              <div className="mt-auto">
                <SetCareerGoalButton 
                  job={{
                    id: currentCard.id,
                    title: currentCard.title,
                    description: currentCard.description
                  }}
                  variant="primary"
                  size="md"
                  source="swipe"
                  className="w-full"
                />
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="p-6 bg-white border-t border-gray-200">
        <div className="flex justify-center space-x-4">
          <button
            onClick={() => handleButtonSwipe('left')}
            className="w-14 h-14 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center transition-colors"
          >
            <X className="w-6 h-6 text-gray-600" />
          </button>
          <button
            onClick={() => handleButtonSwipe('right')}
            className="w-14 h-14 bg-red-500 hover:bg-red-600 rounded-full flex items-center justify-center transition-colors"
          >
            <Heart className="w-6 h-6 text-white" />
          </button>
        </div>
        <p className="text-center text-gray-500 text-sm mt-4">
          Swipe or tap to explore careers
        </p>
      </div>
    </div>
  );
};

export default SwipeRecommendations;