'use client';

import React from 'react';
import { motion } from 'framer-motion';
import Image from 'next/image';
import styles from './JobCard.module.css';
import SetCareerGoalButton from '@/components/common/SetCareerGoalButton';

// Interface pour les données d'un emploi
export interface Job {
  id: string;
  score: number;
  metadata: {
    title: string;
    description?: string;
    skills?: string[];
    match_percentage?: number;
    isco_group?: string;
    preferred_label?: string;
    alt_labels?: string[];
    [key: string]: any; // Pour les autres propriétés potentielles
  };
}

interface JobCardProps {
  job: Job;
  isSelected: boolean;
  onClick: () => void;
  className?: string;
}

// Fonction pour sélectionner un avatar en fonction de l'ID et du titre de l'emploi
const getAvatarForJob = (jobId: string, title: string): string => {
  // Liste des avatars disponibles
  const avatars = [
    'academic.png',
    'artist.png',
    'businessman.png',
    'chef.png',
    'constructor.png',
    'controller.png',
    'health.png',
    'nurse.png',
    'police.png',
    'programmer.png',
    'women.png'
  ];
  
  // Mots-clés pour associer des avatars spécifiques
  const keywordMap: Record<string, string> = {
    'professor': 'academic.png',
    'teacher': 'academic.png',
    'researcher': 'academic.png',
    'artist': 'artist.png',
    'designer': 'artist.png',
    'creative': 'artist.png',
    'business': 'businessman.png',
    'manager': 'businessman.png',
    'executive': 'businessman.png',
    'chef': 'chef.png',
    'cook': 'chef.png',
    'food': 'chef.png',
    'construction': 'constructor.png',
    'builder': 'constructor.png',
    'engineer': 'constructor.png',
    'controller': 'controller.png',
    'accountant': 'controller.png',
    'finance': 'controller.png',
    'health': 'health.png',
    'doctor': 'health.png',
    'medical': 'health.png',
    'nurse': 'nurse.png',
    'caregiver': 'nurse.png',
    'police': 'police.png',
    'security': 'police.png',
    'law': 'police.png',
    'programmer': 'programmer.png',
    'developer': 'programmer.png',
    'software': 'programmer.png',
    'woman': 'women.png',
    'women': 'women.png'
  };
  
  // Vérifier si le titre contient un mot-clé
  const lowerTitle = title.toLowerCase();
  for (const [keyword, avatar] of Object.entries(keywordMap)) {
    if (lowerTitle.includes(keyword.toLowerCase())) {
      return avatar;
    }
  }
  
  // Si aucun mot-clé ne correspond, utiliser l'ID pour sélectionner un avatar
  // Convertir l'ID en nombre pour sélectionner un avatar
  let sum = 0;
  for (let i = 0; i < jobId.length; i++) {
    sum += jobId.charCodeAt(i);
  }
  
  // Utiliser le modulo pour obtenir un index dans la plage des avatars disponibles
  const index = sum % avatars.length;
  return avatars[index];
};

const JobCard: React.FC<JobCardProps> = ({ job, isSelected, onClick, className = '' }) => {
  // Use real job data from ESCO/Pinecone, with better fallback handling
  const rawTitle = job.metadata.preferred_label || job.metadata.title || 
    (job.id.startsWith('occupation::key_') ? `Position ${job.id.replace('occupation::key_', '')}` : job.id) || 'Unknown Position';
  const title = rawTitle && rawTitle.length > 40 ? `${rawTitle.substring(0, 40)}...` : rawTitle;
  const description = job.metadata.description || 'Aucune description disponible';
  const matchPercentage = job.metadata.match_percentage || Math.round(job.score * 100);
  const skills = job.metadata.skills || [];
  const displayedSkills = skills.slice(0, 3);

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`${styles.container} ${isSelected ? styles.selected : ''} ${className}`}
      style={{
        '--r': isSelected ? '0' : '-15',
      } as React.CSSProperties}
    >
      <div 
        className={styles.glass}
        data-text={title}
      >
        <div className="flex flex-col h-full pt-16 pb-4 px-4">
          {/* Match percentage - positioned below the header */}
          <div className="absolute top-12 right-2 bg-green-500 text-white text-xs font-bold px-3 py-1 rounded-full z-10">
            {matchPercentage}% match
          </div>

          {/* Avatar */}
          <div className="flex justify-center mb-4 mt-2">
            <div className="w-20 h-20 rounded-full overflow-hidden border-4 border-white shadow-lg">
              <Image
                src={`/avatar/${getAvatarForJob(job.id, title)}`}
                alt={title}
                width={80}
                height={80}
                className="w-full h-full object-cover object-center"
              />
            </div>
          </div>

          {/* Description */}
          <div className="flex-1 mb-4">
            <p className="text-sm text-gray-700 text-center leading-relaxed line-clamp-3">
              {description && description.length > 120 ? `${description.substring(0, 120)}...` : description}
            </p>
          </div>

          {/* Skills */}
          {displayedSkills.length > 0 && (
            <div className="mb-4">
              <h4 className="text-xs font-semibold text-gray-600 mb-2 text-center">Key Skills</h4>
              <div className="flex flex-wrap gap-1 justify-center">
                {displayedSkills.map((skill, index) => (
                  <span 
                    key={index}
                    className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-md font-medium"
                  >
                    {skill && skill.length > 15 ? `${skill.substring(0, 15)}...` : skill}
                  </span>
                ))}
                {skills.length > 3 && (
                  <span className="bg-gray-100 text-gray-600 text-xs px-2 py-1 rounded-md">
                    +{skills.length - 3} more
                  </span>
                )}
              </div>
            </div>
          )}
          
          {/* Career Goal Button */}
          <div className="mt-auto">
            <SetCareerGoalButton 
              job={job} 
              size="sm" 
              variant="primary"
              source="oasis"
              className="w-full text-xs py-2"
            />
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default JobCard;