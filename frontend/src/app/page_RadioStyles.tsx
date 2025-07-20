'use client';

import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import UserCard from '@/components/ui/UserCard';
import hollandTestService, { ScoreResponse } from '@/services/hollandTestService';
import { getJobRecommendations } from '@/services/api';
import JobRecommendationList from '@/components/jobs/JobRecommendationList';
import JobSkillsTree from '@/components/jobs/JobSkillsTree';
import { Job } from '@/components/jobs/JobCard';
import styles from '@/styles/patterns.module.css';
import radioStyles from '@/styles/radioNav.module.css';

// Interface pour la réponse de l'API de recommandations d'emploi
interface JobRecommendationsResponse {
  recommendations: Job[];
  user_id: number;
}

export default function Home() {
  const router = useRouter();
  const [userData] = useState({
    name: 'Philippe B.',
    role: 'Étudiant Msc. in Data Science',
    level: 3,
    avatarUrl: '/greg.png',
    skills: ['UI Design', 'JavaScript', 'React', 'Node.js'],
    careerTreesExplored: 3,
    skillsInProgress: 12,
    totalXP: 250,
    careerTreeCompletion: 60,
    skillTreeCompletion: 40,
    badgesEarned: 5,
    challengesCompleted: 8,
    notesSaved: 15,
    recentActivities: [
      {
        type: 'challenge',
        title: 'Challenge Complété',
        description: "Complété challenge: 'Data Analysis Basics'",
        icon: 'CheckCircle'
      },
      {
        type: 'xp',
        title: 'XP Gagné',
        description: 'Gagné 250 XP',
        icon: 'Star'
      }
    ]
  });

  // État pour stocker les résultats du test Holland (RIASEC)
  const [hollandResults, setHollandResults] = useState<ScoreResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // États pour les recommandations d'emploi
  const [jobRecommendations, setJobRecommendations] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [jobsError, setJobsError] = useState<string | null>(null);

  // Récupérer les résultats du test Holland au chargement de la page
  useEffect(() => {
    const fetchHollandResults = async () => {
      try {
        const results = await hollandTestService.getUserLatestResults();
        setHollandResults(results);
      } catch (err) {
        console.error('Erreur lors de la récupération des résultats RIASEC:', err);
        setError('Impossible de récupérer les résultats RIASEC');
      } finally {
        setLoading(false);
      }
    };

    fetchHollandResults();
    
    // Récupérer les recommandations d'emploi
    const fetchJobRecommendations = async () => {
      try {
        setJobsLoading(true);
        setJobsError(null);
        
        // Utiliser l'ID de l'utilisateur actuel (à adapter selon votre système d'authentification)
        const response = await getJobRecommendations() as JobRecommendationsResponse;
        
        if (response && response.recommendations) {
          setJobRecommendations(response.recommendations);
          
          // Sélectionner automatiquement le premier emploi
          if (response.recommendations.length > 0) {
            setSelectedJob(response.recommendations[0]);
          }
        }
      } catch (err) {
        console.error('Erreur lors de la récupération des recommandations d\'emploi:', err);
        setJobsError('Impossible de récupérer les recommandations d\'emploi');
      } finally {
        setJobsLoading(false);
      }
    };
    
    fetchJobRecommendations();
  }, []);
  
  // Fonction pour gérer la sélection d'un emploi
  const handleSelectJob = (job: Job) => {
    setSelectedJob(job);
  };

  // Définir les couleurs pour chaque dimension RIASEC
  const riasecColors = {
    R: 'rgba(255, 99, 132, 0.7)',   // Rouge
    I: 'rgba(54, 162, 235, 0.7)',    // Bleu
    A: 'rgba(255, 206, 86, 0.7)',    // Jaune
    S: 'rgba(75, 192, 192, 0.7)',    // Vert
    E: 'rgba(153, 102, 255, 0.7)',   // Violet
    C: 'rgba(255, 159, 64, 0.7)',    // Orange
  };

  // Définir les descriptions courtes pour chaque dimension RIASEC
  const riasecLabels = {
    R: 'Réaliste',
    I: 'Investigateur',
    A: 'Artistique',
    S: 'Social',
    E: 'Entreprenant',
    C: 'Conventionnel',
  };

  // Navigation items pour la sidebar
  const navItems = [
    { name: 'Chat', icon: 'Chat', path: '/chat' },
    { name: 'Peers', icon: 'Peers', path: '/peers' },
    { name: 'Swipe', icon: 'Swipe', path: '/find-your-way' },
    { name: 'Saved', icon: 'Bookmark', path: '/space' },
    { name: 'Challenges', icon: 'Trophy', path: '/challenges' },
    { name: 'Notes', icon: 'Note', path: '/notes' },
    { name: 'Case Study', icon: 'Case Study', path: '/case-study-journey' },
  ];

  // Career navigation items
  const careerItems = [
    { name: 'Career Search', icon: 'List', path: '/vector-search' },
    { name: 'Skills Tree', icon: 'Tree', path: '/enhanced-skills' },
    { name: 'Career Tree', icon: 'Tree', path: '/career' },
    { name: 'Saved Tree', icon: 'Tree', path: '/tree-path' },
  ];

  // Personality navigation items
  const personalityItems = [
    { name: 'Holland Test', icon: 'Personality', path: '/holland-test' },
    { name: 'Personality', icon: 'Personality', path: '/profile/holland-results' },
  ];

  const navigateTo = (path: string) => {
    router.push(path);
  };

  return (
    <MainLayout showNav={false}>
      <div className={`relative flex w-full min-h-screen flex-col pb-12 overflow-x-hidden ${styles.container}`}>
        <div className="relative z-10 w-full flex h-full grow">
          {/* Sidebar - étroite sur mobile, plus large sur desktop, mais optimisée pour grands écrans */}
          <div className="w-10 md:w-36 lg:w-32 xl:w-40 border-r border-stitch-border transition-all duration-300 flex-shrink-0 -ml-1 md:-ml-2">
            <div className={`flex flex-col gap-5 items-center md:items-start pt-8 px-1 md:px-2 sticky top-0 ${radioStyles['radio-container']}`}>
              {/* Navigation Items */}
              {navItems.map((item, index) => (
                <React.Fragment key={index}>
                  <input
                    type="radio"
                    name="nav"
                    id={`nav-${index}`}
                    defaultChecked={index === 0}
                    onChange={() => navigateTo(item.path)}
                  />
                  <label htmlFor={`nav-${index}`}>
                    {/* Icon */}
                    {item.icon === 'Chat' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="18px" height="18px" fill="currentColor" viewBox="0 0 256 256" className="shrink-0">
                        <path d="M216,48H40A16,16,0,0,0,24,64V224a15.84,15.84,0,0,0,9.25,14.5A16.05,16.05,0,0,0,40,240a15.89,15.89,0,0,0,10.25-3.78.69.69,0,0,0,.13-.11L82.5,208H216a16,16,0,0,0,16-16V64A16,16,0,0,0,216,48ZM40,224V64H216V192H82.5a16,16,0,0,0-10.25,3.78L40,224Z"></path>
                      </svg>
                    )}
                    {item.icon === 'List' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="18px" height="18px" fill="currentColor" viewBox="0 0 256 256" className="shrink-0">
                        <path d="M80,64a8,8,0,0,1,8-8H216a8,8,0,0,1,0,16H88A8,8,0,0,1,80,64Zm136,56H88a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16Zm0,64H88a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16ZM44,52A12,12,0,1,0,56,64,12,12,0,0,0,44,52Zm0,64a12,12,0,1,0,12,12A12,12,0,0,0,44,116Zm0,64a12,12,0,1,0,12,12A12,12,0,0,0,44,180Z"></path>
                      </svg>
                    )}
                    {item.icon === 'Bookmark' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="18px" height="18px" fill="currentColor" viewBox="0 0 256 256" className="shrink-0">
                        <path d="M184,32H72A16,16,0,0,0,56,48V224a8,8,0,0,0,12.24,6.78L128,193.43l59.77,37.35A8,8,0,0,0,200,224V48A16,16,0,0,0,184,32Zm0,177.57-51.77-32.35a8,8,0,0,0-8.48,0L72,209.57V48H184Z"></path>
                      </svg>
                    )}
                    {item.icon === 'Swipe' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="18px" height="18px" fill="currentColor" viewBox="0 0 24 24" className="shrink-0">
                        <path fillRule="evenodd" d="M7.5 5.25a3 3 0 0 1 3-3h3a3 3 0 0 1 3 3v.205c.933.085 1.857.197 2.774.334 1.454.218 2.476 1.483 2.476 2.917v3.033c0 1.211-.734 2.352-1.936 2.752A24.726 24.726 0 0 1 12 15.75c-2.73 0-5.357-.442-7.814-1.259-1.202-.4-1.936-1.541-1.936-2.752V8.706c0-1.434 1.022-2.7 2.476-2.917A48.814 48.814 0 0 1 7.5 5.455V5.25Zm7.5 0v.09a49.488 49.488 0 0 0-6 0v-.09a1.5 1.5 0 0 1 1.5-1.5h3a1.5 1.5 0 0 1 1.5 1.5Zm-3 8.25a.75.75 0 1 0 0-1.5.75.75 0 0 0 0 1.5Z" clipRule="evenodd" />
                        <path d="M3 18.4v-2.796a4.3 4.3 0 0 0 .713.31A26.226 26.226 0 0 0 12 17.25c2.892 0 5.68-.468 8.287-1.335.252-.084.49-.189.713-.311V18.4c0 1.452-1.047 2.728-2.523 2.923-2.12.282-4.282.427-6.477.427a49.19 49.19 0 0 1-6.477-.427C4.047 21.128 3 19.852 3 18.4Z" />
                      </svg>
                    )}
                    {item.icon === 'Trophy' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="18px" height="18px" fill="currentColor" viewBox="0 0 256 256" className="shrink-0">
                        <path d="M232,64H208V56a16,16,0,0,0-16-16H64A16,16,0,0,0,48,56v8H24A16,16,0,0,0,8,80V96a40,40,0,0,0,40,40h3.65A80.13,80.13,0,0,0,120,191.61V216H96a8,8,0,0,0,0,16h64a8,8,0,0,0,0-16H136V191.58c31.94-3.23,58.44-25.64,68.08-55.58H208a40,40,0,0,0,40-40V80A16,16,0,0,0,232,64ZM48,120A24,24,0,0,1,24,96V80H48v32q0,4,.39,8Zm144-8.9c0,35.52-28.49,64.64-63.51,64.9H128a64,64,0,0,1-64-64V56H192ZM232,96a24,24,0,0,1-24,24h-.5a81.81,81.81,0,0,0,.5-8.9V80h24Z"></path>
                      </svg>
                    )}
                    {item.icon === 'Note' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="18px" height="18px" fill="currentColor" viewBox="0 0 256 256" className="shrink-0">
                        <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40ZM40,56H216v96H176a16,16,0,0,0-16,16v48H40Zm152,144V168h24v32Z"></path>
                      </svg>
                    )}
                    {item.icon === 'Peers' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="18px" height="18px" fill="currentColor" viewBox="0 0 256 256" className="shrink-0">
                        <path d="M128,120a48,48,0,1,0-48-48A48,48,0,0,0,128,120Zm0,16c-33.08,0-96,16.54-96,49.38V200a8,8,0,0,0,8,8H216a8,8,0,0,0,8-8v-14.62C224,152.54,161.08,136,128,136Z"></path>
                      </svg>
                    )}
                    {item.icon === 'Case Study' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="18px" height="18px" fill="currentColor" viewBox="0 0 256 256" className="shrink-0">
                        <path d="M128,16A112,112,0,1,0,240,128,112.13,112.13,0,0,0,128,16Zm0,208a96,96,0,1,1,96-96A96.11,96.11,0,0,1,128,224Z"></path>
                      </svg>
                    )}
                    {item.icon === 'Search' && (
                      <svg xmlns="http://www.w3.org/2000/svg" width="18px" height="18px" fill="currentColor" viewBox="0 0 256 256" className="shrink-0">
                        <path d="M112,16A96,96,0,1,0,208,112a95.83,95.83,0,0,0-16.5-54.5l-36.5,36.5A48,48,0,1,1,112,16Zm0,176a80,80,0,1,1,80-80A80.09,80.09,0,0,1,112,192Z"></path>
                      </svg>
                    )}
                    {item.icon === 'Personality' && (
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="18px"
                        height="18px"
                        fill="currentColor"
                        viewBox="0 0 256 256"
                        className="shrink-0"
                      >
                        <path d="M232,128a104,104,0,1,0-193.55,58.25C41.62,187.2,40,191.43,40,196v20a12,12,0,0,0,12,12H88a12,12,0,0,0,12-12V204h8a8,8,0,0,0,8-8V168a40.05,40.05,0,0,0,40-40v-8a8,8,0,0,0-8-8H139.75a40,40,0,0,0-75.5,0H56a8,8,0,0,0,0,16h80a24,24,0,0,1,24,24v8a8,8,0,0,0,8,8h8a12,12,0,0,0,12-12V196c0-4.57-1.62-8.8-4.45-12.25ZM128,24A88,88,0,1,1,40,112,88.1,88.1,0,0,1,128,24Z"></path>
                      </svg>
                    )}
                    
                    {/* Label - visible uniquement sur desktop */}
                    <span className="hidden md:block text-sm font-medium">{item.name}</span>
                  </label>
                </React.Fragment>
              ))}
              <div className={`${radioStyles['glider-container']}`}>
                <div className={`${radioStyles.glider}`}></div>
              </div>
            </div>
          </div>

          {/* Main Content - adapté pour desktop avec largeur complète et optimisé pour grands écrans */}
          <div className="flex flex-col flex-1 w-full">
            {/* Header */}
            <div className="flex flex-wrap justify-between gap-3 p-4 md:p-6 lg:p-8 mb-2">
              <p className="tracking-light text-[32px] md:text-4xl font-bold leading-tight min-w-72" style={{
                color: 'var(--accent-color)',
                fontFamily: 'var(--heading-font)'
              }}>Accueil</p>
            </div>

            {/* Main Content Container */}
            <div className="flex-1 w-full px-4 md:px-8 lg:px-12 xl:px-16">
              {/* User Profile Section - Avatar et RIASEC */}
              <div className="mb-10">
                {/* Unified flex container for the entire profile section */}
                <div className="flex flex-col gap-8">
                  {/* Avatar Section - Centered and Larger */}
                  <div className="w-full max-w-[400px] mx-auto">
                    <UserCard
                      name={userData.name}
                      role={userData.role}
                      skills={userData.skills}
                      className="p-6 bg-black/30 rounded-lg border w-full shadow-md"
                    />
                  </div>
              {/* RIASEC Section */}
              <div className="w-full">
                <div className="bg-black/30 rounded-lg border px-6 py-4 md:px-8 md:py-6"
                     style={{ borderColor: 'var(--border-color)' }}>
                  <h2 className="text-[22px] md:text-[28px] font-bold leading-tight tracking-[-0.02em] mb-6" style={{
                    color: 'var(--accent-color)',
                    fontFamily: 'var(--heading-font)'
                  }}>
                    Profil RIASEC
                  </h2>

                  {loading ? (
                    <p style={{ color: 'var(--text-color)' }}>Chargement du profil RIASEC...</p>
                  ) : error ? (
                    <p className="text-red-500">{error}</p>
                  ) : !hollandResults ? (
                    <div className="p-4 rounded-lg border" style={{
                      backgroundColor: 'var(--primary-color)',
                      borderColor: 'var(--border-color)'
                    }}>
                      <p className="mb-2" style={{ color: 'var(--text-color)' }}>
                        Vous n'avez pas encore passé le test Holland Code (RIASEC).
                      </p>
                      <Link href="/holland-test" className="text-blue-600 hover:underline">
                        Passer le test maintenant
                      </Link>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
                      {/* Left: Code + Trait */}
                      <div className="col-span-1">
                        <p className="font-medium text-sm mb-2" style={{ color: 'var(--accent-color)' }}>
                          Votre code Holland:
                        </p>
                        <div className="flex gap-3 mb-4">
                          {hollandResults.top_3_code && hollandResults.top_3_code.split('').map((letter, index) => (
                            <div
                              key={index}
                              className="flex items-center justify-center w-10 h-10 rounded-full text-white text-base font-bold"
                              style={{
                                backgroundColor:
                                  riasecColors[letter as keyof typeof riasecColors],
                              }}
                            >
                              {letter}
                            </div>
                          ))}
                        </div>

                        <p className="text-xs italic mb-1" style={{ color: 'var(--text-color)' }}>Votre trait dominant</p>
                        <h3
                          className="text-[24px] md:text-[28px] font-bold leading-tight tracking-tight mb-3"
                          style={{
                            color:
                              riasecColors[
                                hollandResults.top_3_code[0] as keyof typeof riasecColors
                              ],
                          }}
                        >
                          {riasecLabels[
                            hollandResults.top_3_code[0] as keyof typeof riasecLabels
                          ]}
                        </h3>

                        <Link
                          href="/profile/holland-results"
                          className="text-blue-600 hover:underline text-sm"
                        >
                          Voir le profil complet
                        </Link>
                      </div>

                      {/* Right: Personality Description */}
                      {hollandResults.personality_description && (
                        <div className="lg:col-span-2 lg:border-l border-stitch-border lg:pl-8">
                          <p className="font-medium text-sm mb-2" style={{ color: 'var(--accent-color)' }}>
                            Description du profil:
                          </p>
                          <p className="text-sm leading-relaxed" style={{ color: 'var(--text-color)' }}>
                            {hollandResults.personality_description}
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>

                </div>
              </div>

                              {/* Section des recommandations d'emploi - occupe toute la largeur */}
                              <div className="md:col-span-12 mt-8">
                  <h2 className="text-[22px] md:text-2xl font-bold leading-tight tracking-[-0.015em] pb-3 pt-5" style={{
                    color: 'var(--accent-color)',
                    fontFamily: 'var(--heading-font)'
                  }}>Recommandations d'emploi</h2>
                  <div className="w-full">
                    <JobRecommendationList
                      recommendations={jobRecommendations}
                      isLoading={jobsLoading}
                      error={jobsError}
                      onSelectJob={handleSelectJob}
                      className="mb-8"
                    />
                    
                    {/* Arbre de compétences pour l'emploi sélectionné */}
                    {selectedJob && (
                      <JobSkillsTree
                        jobId={selectedJob.id}
                        className="mt-8"
                      />
                    )}
                  </div>
                </div>

              {/* Dashboard Grid - responsive avec largeur complète et optimisé pour grands écrans */}
              <div className="grid grid-cols-1 md:grid-cols-12 gap-6 md:gap-8">
                {/* Student Summary - occupe toute la largeur sur mobile, 8 colonnes sur desktop */}
                <div className="md:col-span-8">
                  <h2 className="text-[22px] md:text-2xl font-bold leading-tight tracking-[-0.015em] pb-3 pt-5" style={{
                    color: 'var(--accent-color)',
                    fontFamily: 'var(--heading-font)'
                  }}>Résumé de l'étudiant</h2>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 md:gap-6">
                    <div className="flex flex-col gap-2 rounded-lg border p-4 md:p-5 items-start min-h-[100px] shadow-md bg-black/30"
                         style={{ borderColor: 'var(--border-color)' }}>
                      <p className="tracking-light text-2xl md:text-3xl font-bold leading-tight" style={{
                        color: 'var(--accent-color)',
                        fontFamily: 'var(--heading-font)'
                      }}>{userData.careerTreesExplored}</p>
                      <div className="flex items-center gap-2"><p className="text-sm md:text-base font-normal leading-normal" style={{
                        color: 'var(--text-color)',
                        fontFamily: 'var(--body-font)'
                      }}>Career Trees Explorés</p></div>
                    </div>
                    <div className="flex flex-col gap-2 rounded-lg border p-4 md:p-5 items-start min-h-[100px] shadow-md bg-black/30"
                         style={{ borderColor: 'var(--border-color)' }}>
                      <p className="tracking-light text-2xl md:text-3xl font-bold leading-tight" style={{
                        color: 'var(--accent-color)',
                        fontFamily: 'var(--heading-font)'
                      }}>{userData.skillsInProgress}</p>
                      <div className="flex items-center gap-2"><p className="text-sm md:text-base font-normal leading-normal" style={{
                        color: 'var(--text-color)',
                        fontFamily: 'var(--body-font)'
                      }}>Compétences en cours</p></div>
                    </div>
                    <div className="flex flex-col gap-2 rounded-lg border p-4 md:p-5 items-start min-h-[100px] shadow-md bg-black/30"
                         style={{ borderColor: 'var(--border-color)' }}>
                      <p className="tracking-light text-2xl md:text-3xl font-bold leading-tight" style={{
                        color: 'var(--accent-color)',
                        fontFamily: 'var(--heading-font)'
                      }}>{userData.totalXP}</p>
                      <div className="flex items-center gap-2"><p className="text-sm md:text-base font-normal leading-normal" style={{
                        color: 'var(--text-color)',
                        fontFamily: 'var(--body-font)'
                      }}>XP Total</p></div>
                    </div>
                  </div>
                </div>

                {/* Stats supplémentaires - visible uniquement sur desktop, 4 colonnes */}
                <div className="hidden md:block md:col-span-4">
                  <h2 className="text-2xl font-bold leading-tight tracking-[-0.015em] pb-3 pt-5" style={{
                    color: 'var(--accent-color)',
                    fontFamily: 'var(--heading-font)'
                  }}>Statistiques</h2>
                  <div className="grid grid-cols-2 gap-6">
                    <div className="flex flex-col gap-2 rounded-lg border p-4 md:p-5 items-start min-h-[100px] shadow-md bg-black/30"
                         style={{ borderColor: 'var(--border-color)' }}>
                      <p className="tracking-light text-3xl font-bold leading-tight" style={{
                        color: 'var(--accent-color)',
                        fontFamily: 'var(--heading-font)'
                      }}>{userData.challengesCompleted}</p>
                      <div className="flex items-center gap-2"><p className="text-base font-normal leading-normal" style={{
                        color: 'var(--text-color)',
                        fontFamily: 'var(--body-font)'
                      }}>Défis complétés</p></div>
                    </div>
                    <div className="flex flex-col gap-2 rounded-lg border p-4 md:p-5 items-start min-h-[100px] shadow-md bg-black/30"
                         style={{ borderColor: 'var(--border-color)' }}>
                      <p className="tracking-light text-3xl font-bold leading-tight" style={{
                        color: 'var(--accent-color)',
                        fontFamily: 'var(--heading-font)'
                      }}>{userData.notesSaved}</p>
                      <div className="flex items-center gap-2"><p className="text-base font-normal leading-normal" style={{
                        color: 'var(--text-color)',
                        fontFamily: 'var(--body-font)'
                      }}>Notes sauvegardées</p></div>
                    </div>
                  </div>
                </div>

                {/* How to get there? Section */}
                <div className="md:col-span-12 mt-4">
                  <h2 className="text-[22px] md:text-2xl font-bold leading-tight tracking-[-0.015em] pb-4 pt-5" style={{
                    color: 'var(--accent-color)',
                    fontFamily: 'var(--heading-font)'
                  }}>Tree</h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mb-6">
                    {careerItems.map((item, index) => (
                      <Link
                        key={index}
                        href={item.path}
                        className="flex items-center gap-4 bg-black/30 p-5 rounded-lg border transition-colors shadow-md min-h-[90px]"
                        style={{
                          borderColor: 'var(--border-color)'
                        }}
                      >
                        <div className="flex items-center justify-center rounded-lg shrink-0 size-12"
                             style={{
                               color: 'var(--text-color)',
                               backgroundColor: 'var(--primary-color)'
                             }}>
                          {item.icon === 'Tree' && (
                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                              <path d="M198.1,62.6a76,76,0,0,0-140.2,0A72.27,72.27,0,0,0,16,127.8C15.89,166.62,47.36,199,86.14,200A71.68,71.68,0,0,0,120,192.49V232a8,8,0,0,0,16,0V192.49A71.45,71.45,0,0,0,168,200l1.86,0c38.78-1,70.25-33.36,70.14-72.18A72.26,72.26,0,0,0,198.1,62.6ZM169.45,184a55.61,55.61,0,0,1-32.52-9.4q-.47-.3-.93-.57V132.94l43.58-21.78a8,8,0,1,0-7.16-14.32L136,115.06V88a8,8,0,0,0-16,0v51.06L83.58,120.84a8,8,0,1,0-7.16,14.32L120,156.94V174q-.47.27-.93.57A55.7,55.7,0,0,1,86.55,184a56,56,0,0,1-22-106.86,15.9,15.9,0,0,0,8.05-8.33,60,60,0,0,1,110.7,0,15.9,15.9,0,0,0,8.05,8.33,56,56,0,0,1-22,106.86Z"></path>
                            </svg>
                          )}
                          {item.icon === 'List' && (
                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                              <path d="M80,64a8,8,0,0,1,8-8H216a8,8,0,0,1,0,16H88A8,8,0,0,1,80,64Zm136,56H88a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16Zm0,64H88a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16ZM44,52A12,12,0,1,0,56,64,12,12,0,0,0,44,52Zm0,64a12,12,0,1,0,12,12A12,12,0,0,0,44,116Zm0,64a12,12,0,1,0,12,12A12,12,0,0,0,44,180Z"></path>
                            </svg>
                          )}
                        </div>
                        <div className="flex flex-col">
                          <p className="text-lg font-medium" style={{
                            color: 'var(--accent-color)',
                            fontFamily: 'var(--heading-font)'
                          }}>{item.name}</p>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>

                {/* Personality Section */}
                <div className="md:col-span-12 mt-4">
                  <h2 className="text-[22px] md:text-2xl font-bold leading-tight tracking-[-0.015em] pb-4 pt-5" style={{
                    color: 'var(--accent-color)',
                    fontFamily: 'var(--heading-font)'
                  }}>Personality</h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 mb-6">
                    {personalityItems.map((item, index) => (
                      <Link
                        key={index}
                        href={item.path}
                        className="flex items-center gap-4 bg-black/30 p-5 rounded-lg border transition-colors shadow-md min-h-[90px]"
                        style={{ borderColor: 'var(--border-color)' }}
                      >
                        <div className="flex items-center justify-center rounded-lg shrink-0 size-12"
                             style={{
                               color: 'var(--text-color)',
                               backgroundColor: 'var(--primary-color)'
                             }}>
                          <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                            <path d="M80,64a8,8,0,0,1,8-8H216a8,8,0,0,1,0,16H88A8,8,0,0,1,80,64Zm136,56H88a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16Zm0,64H88a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16ZM44,52A12,12,0,1,0,56,64,12,12,0,0,0,44,52Zm0,64a12,12,0,1,0,12,12A12,12,0,0,0,44,116Zm0,64a12,12,0,1,0,12,12A12,12,0,0,0,44,180Z"></path>
                          </svg>
                        </div>
                        <div className="flex flex-col">
                          <p className="text-lg font-medium" style={{
                            color: 'var(--accent-color)',
                            fontFamily: 'var(--heading-font)'
                          }}>{item.name}</p>
                        </div>
                      </Link>
                    ))}
                  </div>
                </div>

                {/* Recent Activity - occupe toute la largeur */}
                <div className="md:col-span-12 mt-4">
                  <h2 className="text-[22px] md:text-2xl font-bold leading-tight tracking-[-0.015em] pb-4 pt-5" style={{
                    color: 'var(--accent-color)',
                    fontFamily: 'var(--heading-font)'
                  }}>Activité récente</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6 mb-8">
                    {userData.recentActivities.map((activity, index) => (
                      <div key={index} className="flex items-center gap-4 bg-black/30 p-5 md:p-6 rounded-lg border shadow-md min-h-[100px]"
                           style={{ borderColor: 'var(--border-color)' }}>
                        <div className="flex items-center justify-center rounded-lg shrink-0 size-12 md:size-14"
                             style={{
                               color: 'var(--text-color)',
                               backgroundColor: 'var(--primary-color)'
                             }}>
                          {activity.icon === 'CheckCircle' ? (
                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                              <path d="M173.66,98.34a8,8,0,0,1,0,11.32l-56,56a8,8,0,0,1-11.32,0l-24-24a8,8,0,0,1,11.32-11.32L112,148.69l50.34-50.35A8,8,0,0,1,173.66,98.34ZM232,128A104,104,0,1,1,128,24,104.11,104.11,0,0,1,232,128Zm-16,0a88,88,0,1,0-88,88A88.1,88.1,0,0,0,216,128Z"></path>
                            </svg>
                          ) : (
                            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="24px" fill="currentColor" viewBox="0 0 256 256">
                              <path d="M239.2,97.29a16,16,0,0,0-13.81-11L166,81.17,142.72,25.81h0a15.95,15.95,0,0,0-29.44,0L90.07,81.17,30.61,86.32a16,16,0,0,0-9.11,28.06L66.61,153.8,53.09,212.34a16,16,0,0,0,23.84,17.34l51-31,51.11,31a16,16,0,0,0,23.84-17.34l-13.51-58.6,45.1-39.36A16,16,0,0,0,239.2,97.29Zm-15.22,5-45.1,39.36a16,16,0,0,0-5.08,15.71L187.35,216v0l-51.07-31a15.9,15.9,0,0,0-16.54,0l-51,31h0L82.2,157.4a16,16,0,0,0-5.08-15.71L32,102.35a.37.37,0,0,1,0-.09l59.44-5.14a16,16,0,0,0,13.35-9.75L128,32.08l23.2,55.29a16,16,0,0,0,13.35,9.75L224,102.26S224,102.32,224,102.33Z"></path>
                            </svg>
                          )}
                        </div>
                        <div className="flex flex-col justify-center w-full">
                          <p className="text-base md:text-lg font-medium leading-normal line-clamp-1 break-words"
                             style={{ color: 'var(--accent-color)' }}>{activity.title}</p>
                          <p className="text-sm md:text-base font-normal leading-normal line-clamp-2 break-words"
                             style={{ color: 'var(--text-color)' }}>{activity.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}