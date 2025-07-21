'use client';

import React, { useState, useEffect } from 'react';
import SkillCard from './SkillCard';
import BasicSkillCard from './BasicSkillCard';
import LoadingSpinner from './LoadingSpinner';
import { generateCompetenceTree } from '@/services/competenceTreeService';
import { getUserSkills, UserSkills } from '@/services/spaceService';

interface SkillShowcaseProps {
  userId?: number;
  className?: string;
}

interface AnchorSkill {
  id: string;
  esco_label: string;
  esco_description: string;
  category: string;
  confidence: number;
  applications?: string[];
  justification: string;
}

const SkillShowcase: React.FC<SkillShowcaseProps> = ({ userId, className = '' }) => {
  const [skills, setSkills] = useState<AnchorSkill[]>([]);
  const [basicSkills, setBasicSkills] = useState<UserSkills | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [hasGenerated, setHasGenerated] = useState<boolean>(false);
  const [showBasicSkills, setShowBasicSkills] = useState<boolean>(true); // Always show basic skills first
  const [selectedSkill, setSelectedSkill] = useState<string | null>(null);
  const [skillDescriptions, setSkillDescriptions] = useState<{[key: string]: string}>({});

  const generateSkillDescription = async (skillName: string) => {
    if (skillDescriptions[skillName]) {
      setSelectedSkill(skillName);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const token = localStorage.getItem('access_token');
      
      // Generate AI description for the skill
      const response = await fetch(`${API_URL}/api/v1/insight/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          prompt: `Generate a detailed, professional description for the skill "${skillName}". Include:
          - What this skill involves
          - Why it's important in today's workplace
          - How to develop this skill
          - Real-world applications
          Keep it engaging and practical, around 150-200 words.`,
          context: `skill_analysis_${skillName.toLowerCase().replace(' ', '_')}`
        })
      });

      if (response.ok) {
        const data = await response.json();
        setSkillDescriptions(prev => ({
          ...prev,
          [skillName]: data.content || data.insight || 'Description generated successfully.'
        }));
        setSelectedSkill(skillName);
      } else {
        setError('Failed to generate skill description');
      }
    } catch (err) {
      console.error('Error generating skill description:', err);
      setError('An error occurred while generating the description');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSkillClick = (skillName: string) => {
    generateSkillDescription(skillName);
  };

  // Fetch basic skills
  const fetchBasicSkills = async () => {
    try {
      const userSkills = await getUserSkills();
      setBasicSkills(userSkills);
      
      // Check if user has any non-null skill values
      const hasSkillData = Object.values(userSkills).some(value => value !== null && value !== undefined);
      setShowBasicSkills(hasSkillData);
    } catch (err) {
      console.error('Error fetching basic skills:', err);
    }
  };

  // Check if user already has anchor skills
  useEffect(() => {
    const checkExistingSkills = async () => {
      if (!userId) {
        console.log('No userId available for checking existing skills');
        return;
      }

      setIsLoading(true);
      try {
        const token = localStorage.getItem('access_token');
        if (!token) {
          console.log('No auth token available');
          setIsLoading(false);
          return;
        }

        console.log(`Checking existing anchor skills for user ${userId}...`);
        const response = await fetch('/api/v1/competence-tree/anchor-skills', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        console.log(`Anchor skills response status: ${response.status}`);
        
        if (response.ok) {
          const data = await response.json();
          console.log('Anchor skills response:', data);
          
          if (data.anchor_skills && data.anchor_skills.length > 0) {
            setSkills(data.anchor_skills.slice(0, 5));
            setHasGenerated(true);
            console.log(`Found ${data.anchor_skills.length} existing anchor skills`);
          } else {
            console.log('No anchor skills found in response');
            // Fetch basic skills as fallback
            await fetchBasicSkills();
          }
        } else {
          console.log(`Failed to fetch anchor skills: ${response.status} ${response.statusText}`);
          // Fetch basic skills as fallback
          await fetchBasicSkills();
        }
      } catch (err) {
        console.error('Error checking for existing anchor skills:', err);
        // Fetch basic skills as fallback
        await fetchBasicSkills();
      } finally {
        setIsLoading(false);
      }
    };

    checkExistingSkills();
  }, [userId]);

  // For testing purposes, show basic skills even without userId
  if (userId === undefined) {
    console.log('SkillShowcase: No userId, showing basic skills demo...');
    return (
      <div className={`w-full ${className}`}>
        <div 
          className="rounded-lg p-6"
          style={{
            backgroundColor: 'var(--primary-color)',
            borderWidth: '1px',
            borderStyle: 'solid',
            borderColor: 'var(--border-color)'
          }}
        >
          {/* Header */}
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 
                className="text-xl font-bold"
                style={{ color: 'var(--accent-color)' }}
              >
                Your Core Skills
              </h2>
              <p 
                className="text-sm mt-1"
                style={{ color: 'var(--text-color)' }}
              >
                Essential abilities for career success
              </p>
            </div>
          </div>

          {/* Basic Skills Grid - Demo */}
          <div className="mb-4">
            <p 
              className="text-sm"
              style={{ color: 'var(--text-color)' }}
            >
              Explore these fundamental skills
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4 mb-6">
            {[
              { 
                name: 'Creativity', 
                description: 'Generate innovative ideas and original solutions'
              },
              { 
                name: 'Leadership', 
                description: 'Guide teams and inspire others toward goals'
              },
              { 
                name: 'Critical Thinking', 
                description: 'Analyze information and make logical decisions'
              },
              { 
                name: 'Problem Solving', 
                description: 'Identify issues and develop effective solutions'
              },
              { 
                name: 'Digital Literacy', 
                description: 'Use technology effectively and adapt to new tools'
              }
            ].map((skill, index) => (
              <BasicSkillCard
                key={index}
                skill={{
                  name: skill.name,
                  description: skill.description,
                  icon: "🎯"
                }}
                className="h-full"
              />
            ))}
          </div>

          {/* Action bar */}
          <div className="flex items-center justify-between pt-4 border-t" style={{ borderColor: 'var(--border-color)' }}>
            <div className="flex items-center gap-4">
              <p 
                className="text-sm"
                style={{ color: 'var(--text-color)' }}
              >
                Login to get personalized skill insights
              </p>
            </div>
            <button
              onClick={() => window.location.href = '/login'}
              className="px-6 py-2 rounded-lg font-medium text-white transition-all duration-200 hover:opacity-90 hover:transform hover:scale-105"
              style={{ backgroundColor: 'var(--accent-color)' }}
            >
              Login
            </button>
          </div>
        </div>
      </div>
    );
  }
  
  if (!userId) {
    console.log('SkillShowcase: No userId available');
    return null;
  }
  
  console.log(`SkillShowcase: Rendering for userId ${userId}`);

  // Always show basic skills with new card design
  return (
    <div className={`w-full ${className}`}>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6 mb-6">
          {[
            { 
              name: 'Creativity', 
              description: 'Generate innovative ideas and original solutions',
              icon: '◇'
            },
            { 
              name: 'Leadership', 
              description: 'Guide teams and inspire others toward goals',
              icon: '◆'
            },
            { 
              name: 'Critical Thinking', 
              description: 'Analyze information and make logical decisions',
              icon: '○'
            },
            { 
              name: 'Problem Solving', 
              description: 'Identify issues and develop effective solutions',
              icon: '◎'
            },
            { 
              name: 'Digital Literacy', 
              description: 'Use technology effectively and adapt to new tools',
              icon: '□'
            }
          ].map((skill, index) => (
            <BasicSkillCard
              key={index}
              skill={{
                name: skill.name,
                description: skill.description,
                icon: skill.icon
              }}
              className="h-full"
              onClick={handleSkillClick}
            />
          ))}
      </div>

      {/* Modal for displaying AI-generated skill descriptions */}
      {selectedSkill && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div 
            className="bg-white rounded-lg p-6 max-w-md w-full max-h-[80vh] overflow-y-auto"
            style={{
              backgroundColor: 'var(--primary-color)',
              borderColor: 'var(--border-color)',
              borderWidth: '1px',
              borderStyle: 'solid'
            }}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between mb-4">
              <h3 
                className="text-xl font-bold"
                style={{ color: 'var(--accent-color)' }}
              >
                {selectedSkill}
              </h3>
              <button
                onClick={() => setSelectedSkill(null)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
                style={{ color: 'var(--text-color)' }}
              >
                ×
              </button>
            </div>

            {/* Modal Content */}
            <div>
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <LoadingSpinner size="md" />
                  <p 
                    className="ml-3 text-sm"
                    style={{ color: 'var(--text-color)' }}
                  >
                    Generating description...
                  </p>
                </div>
              ) : skillDescriptions[selectedSkill] ? (
                <div>
                  <p 
                    className="text-sm leading-relaxed whitespace-pre-line"
                    style={{ color: 'var(--text-color)' }}
                  >
                    {skillDescriptions[selectedSkill]}
                  </p>
                </div>
              ) : (
                <p 
                  className="text-sm"
                  style={{ color: 'var(--text-color)' }}
                >
                  Click to generate a detailed description for this skill.
                </p>
              )}
            </div>

            {/* Modal Footer */}
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setSelectedSkill(null)}
                className="px-4 py-2 rounded-lg font-medium text-white transition-all duration-200 hover:opacity-90"
                style={{ backgroundColor: 'var(--accent-color)' }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error notification */}
      {error && (
        <div className="fixed bottom-4 right-4 bg-red-500 text-white p-4 rounded-lg shadow-lg z-50">
          <p className="text-sm">{error}</p>
          <button
            onClick={() => setError(null)}
            className="ml-2 text-white hover:text-gray-200"
          >
            ×
          </button>
        </div>
      )}
    </div>
  );
};

export default SkillShowcase;