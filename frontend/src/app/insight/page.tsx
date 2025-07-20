'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import MainLayout from '@/components/layout/MainLayout';
import { getInsight, generateInsight, regenerateInsight, saveInsight, rewriteInsight, InsightData, mockInsightData } from '@/services/insightService';
import PersonalityCard from '@/components/ui/PersonalityCard';
import SkillShowcase from '@/components/ui/SkillShowcase';
import AvatarPanel from '@/components/avatar/AvatarPanel';
import hollandTestService, { ScoreResponse } from '@/services/hollandTestService';
import Link from 'next/link';
import styles from './insight.module.css';
import LoadingScreen from '@/components/ui/LoadingScreen';

const InsightPage: React.FC = () => {
  const router = useRouter();
  const [userId, setUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [insight, setInsight] = useState<InsightData | null>(null);
  const [feedback, setFeedback] = useState<string>('');
  const [showFullText, setShowFullText] = useState<boolean>(false);
  const [saving, setSaving] = useState<boolean>(false);
  const [rewriting, setRewriting] = useState<boolean>(false);
  const [regenerating, setRegenerating] = useState<boolean>(false);
  
  // Personality-related state
  const [hollandResults, setHollandResults] = useState<ScoreResponse | null>(null);
  const [personalityLoading, setPersonalityLoading] = useState(true);
  const [personalityError, setPersonalityError] = useState<string | null>(null);
  
  // Personality navigation items
  const personalityItems = [
    { name: 'Holland Test', icon: 'Personality', path: '/holland-test' },
    { name: 'HEXACO Test', icon: 'Brain', path: '/hexaco-test/select' },
    { name: 'Self-Reflection', icon: 'Reflection', path: '/self-reflection' },
    { name: 'Holland Results', icon: 'Personality', path: '/profile/holland-results' },
    { name: 'HEXACO Results', icon: 'Brain', path: '/profile/hexaco-results' },
  ];

  useEffect(() => {
    // Récupérer l'ID de l'utilisateur depuis le localStorage
    const fetchUserId = () => {
      try {
        // Récupérer l'ID de l'utilisateur depuis le localStorage
        const userDataStr = localStorage.getItem('user_data');
        if (userDataStr) {
          try {
            const userData = JSON.parse(userDataStr);
            if (userData && userData.id) {
              console.log("ID utilisateur récupéré:", userData.id);
              setUserId(userData.id);
              return userData.id;
            }
          } catch (parseError) {
            console.warn('Failed to parse user_data from localStorage:', parseError);
            localStorage.removeItem('user_data');
          }
        }
        
        // Fallback: utiliser l'ID 19 (celui qui est actuellement connecté selon les logs)
        console.warn("Aucun ID utilisateur trouvé dans localStorage, utilisation de l'ID 19");
        const fallbackId = 19;
        setUserId(fallbackId);
        return fallbackId;
      } catch (error) {
        console.error("Erreur lors de la récupération de l'ID utilisateur:", error);
        // Fallback en cas d'erreur
        const fallbackId = 19;
        setUserId(fallbackId);
        return fallbackId;
      }
    };

    const loadInsight = async () => {
      try {
        setLoading(true);
        const id = fetchUserId();
        
        // D'abord essayer de récupérer un insight existant
        try {
          console.log("Tentative de récupération d'un insight existant...");
          const existingData = await getInsight();
          console.log("Insight existant trouvé:", existingData);
          setInsight(existingData);
        } catch (getError) {
          // Si aucun insight n'existe, ne pas en générer automatiquement
          console.log("Aucun insight existant trouvé");
          setInsight(null);
        }
      } catch (error) {
        console.error('Erreur lors du chargement de l\'insight:', error);
        setInsight(null);
      } finally {
        setLoading(false);
      }
    };

    loadInsight();
  }, []);
  
  // Fetch Holland test results
  useEffect(() => {
    const fetchHollandResults = async () => {
      try {
        const results = await hollandTestService.getUserLatestResults();
        setHollandResults(results);
      } catch (err) {
        console.error('Error fetching Holland results:', err);
        setPersonalityError('Unable to fetch Holland results');
      } finally {
        setPersonalityLoading(false);
      }
    };

    fetchHollandResults();
  }, []);

  const handleSaveInsight = async () => {
    if (!insight) return;
    
    try {
      setSaving(true);
      await saveInsight(insight.full_text);
      alert('Insight sauvegardé avec succès!');
      router.push('/profile'); // Rediriger vers le profil ou une autre page appropriée
    } catch (error) {
      console.error('Erreur lors de la sauvegarde de l\'insight:', error);
      alert('Erreur lors de la sauvegarde. Veuillez réessayer.');
    } finally {
      setSaving(false);
    }
  };

  const handleRewriteInsight = async () => {
    if (!feedback) return;
    
    try {
      setRewriting(true);
      
      // Appeler l'API même en mode développement pour tester les modifications
      console.log("Appel de l'API pour réécrire l'insight avec le feedback:", feedback);
      const newInsight = await rewriteInsight(feedback);
      console.log("Réponse de l'API pour la réécriture:", newInsight);
      setInsight(newInsight);
      setFeedback('');
    } catch (error) {
      console.error('Erreur lors de la réécriture de l\'insight:', error);
      alert('Erreur lors de la réécriture. Veuillez réessayer.');
    } finally {
      setRewriting(false);
    }
  };

  const handleGenerateFirstInsight = async () => {
    try {
      setLoading(true);
      console.log("Génération du premier insight...");
      const newInsight = await generateInsight();
      console.log("Premier insight généré:", newInsight);
      setInsight(newInsight);
    } catch (error) {
      console.error('Erreur lors de la génération du premier insight:', error);
      alert('Erreur lors de la génération. Veuillez réessayer.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateInsight = async () => {
    try {
      setRegenerating(true);
      console.log("Régénération de l'insight...");
      const newInsight = await regenerateInsight();
      console.log("Insight régénéré:", newInsight);
      setInsight(newInsight);
    } catch (error) {
      console.error('Erreur lors de la régénération de l\'insight:', error);
      alert('Erreur lors de la régénération. Veuillez réessayer.');
    } finally {
      setRegenerating(false);
    }
  };

  if (loading) {
    return (
      <MainLayout showNav={true}>
        <div className="premium-container relative flex w-full min-h-screen flex-col pb-12 overflow-x-hidden">
          <div className="relative z-10 w-full flex h-full grow">
            <div className="flex flex-col flex-1 w-full">
              <div className="flex flex-wrap justify-between gap-3 p-4 md:p-6 lg:p-8 mb-2">
                <div className="flex items-center gap-4">
                  <Link
                    href="/"
                    className="premium-button-icon"
                    title="Retour à l'accueil"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                  </Link>
                  <h1 className="premium-title text-[32px] md:text-4xl font-bold leading-tight">
                    Insight Philosophique
                  </h1>
                </div>
              </div>
              <div className="flex-1 w-full px-4 md:px-8 lg:px-12 xl:px-16 max-w-[2000px] mx-auto">
                <LoadingScreen message="Generating your insight philosophique..." />
              </div>
            </div>
          </div>
        </div>
      </MainLayout>
    );
  }

  return (
    <MainLayout showNav={true}>
      <div className="premium-container relative flex w-full min-h-screen flex-col pb-12 overflow-x-hidden">
        <div className="relative z-10 w-full flex h-full grow">
          <div className="flex flex-col flex-1 w-full">
            {/* Header */}
            <div className="flex flex-wrap justify-between gap-3 p-4 md:p-6 lg:p-8 mb-2">
              <div className="flex items-center gap-4">
                <Link
                  href="/"
                  className="premium-button-icon"
                  title="Retour à l'accueil"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </Link>
                <h1 className="premium-title text-[32px] md:text-4xl font-bold leading-tight">
                  🧠 Personalité
                </h1>
              </div>
            </div>

            {/* Main Content Container */}
            <div className="flex-1 w-full px-4 md:px-8 lg:px-12 xl:px-16 max-w-[2000px] mx-auto">
              
              {/* Profile Avatar Section */}
              <div className="premium-card p-6 mb-8">
                <h2 className="premium-section-title mb-6">Profile Avatar</h2>
                <div className="flex items-center gap-6">
                  <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center">
                    <span className="text-gray-500">Avatar</span>
                  </div>
                  <div>
                    <h3 className="text-xl font-bold">Your Profile</h3>
                    <p className="text-gray-600">
                      This avatar represents your unique personality traits and skills
                    </p>
                    <button className="mt-3 premium-button-primary px-4 py-2 text-sm">
                      Customize Avatar
                    </button>
                  </div>
                </div>
              </div>
              
              {/* Personality Content Section */}
              <div className="space-y-8 mb-12">
                
                {/* Skills Section */}
                <div className="premium-card p-6">
                  <h2 className="premium-section-title mb-6">Your Skills</h2>
                  <SkillShowcase userId={userId || undefined} />
                </div>
                
                {/* Avatar Profile Section */}
                <div className="premium-card p-6">
                  <h2 className="premium-section-title mb-6">Your Avatar Profile</h2>
                  <p className="premium-text-secondary mb-6">
                    Generate your personalized avatar based on your psychological profile and personality traits.
                  </p>
                  <AvatarPanel className="w-full" />
                </div>
                
                {/* Personality Tests Section */}
                <div className="premium-card p-6">
                  <h2 className="premium-section-title mb-6">Personality Tests</h2>
                  <PersonalityCard items={personalityItems} />
                  
                  {/* RIASEC Results */}
                  {hollandResults && (
                    <div className="mt-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                      <h3 className="text-lg font-semibold mb-4 text-gray-700 dark:text-gray-300">RIASEC Results</h3>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        <div className="text-center p-3 bg-white dark:bg-gray-700 rounded-lg">
                          <div className="font-bold text-lg text-red-600">R</div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">Réaliste</div>
                          <div className="font-semibold text-gray-800 dark:text-gray-200">{hollandResults.r_score?.toFixed(1)}</div>
                        </div>
                        <div className="text-center p-3 bg-white dark:bg-gray-700 rounded-lg">
                          <div className="font-bold text-lg text-blue-600">I</div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">Investigateur</div>
                          <div className="font-semibold text-gray-800 dark:text-gray-200">{hollandResults.i_score?.toFixed(1)}</div>
                        </div>
                        <div className="text-center p-3 bg-white dark:bg-gray-700 rounded-lg">
                          <div className="font-bold text-lg text-yellow-600">A</div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">Artistique</div>
                          <div className="font-semibold text-gray-800 dark:text-gray-200">{hollandResults.a_score?.toFixed(1)}</div>
                        </div>
                        <div className="text-center p-3 bg-white dark:bg-gray-700 rounded-lg">
                          <div className="font-bold text-lg text-green-600">S</div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">Social</div>
                          <div className="font-semibold text-gray-800 dark:text-gray-200">{hollandResults.s_score?.toFixed(1)}</div>
                        </div>
                        <div className="text-center p-3 bg-white dark:bg-gray-700 rounded-lg">
                          <div className="font-bold text-lg text-purple-600">E</div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">Entreprenant</div>
                          <div className="font-semibold text-gray-800 dark:text-gray-200">{hollandResults.e_score?.toFixed(1)}</div>
                        </div>
                        <div className="text-center p-3 bg-white dark:bg-gray-700 rounded-lg">
                          <div className="font-bold text-lg text-orange-600">C</div>
                          <div className="text-sm text-gray-600 dark:text-gray-400">Conventionnel</div>
                          <div className="font-semibold text-gray-800 dark:text-gray-200">{hollandResults.c_score?.toFixed(1)}</div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  {/* HEXACO Placeholder */}
                  <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <h3 className="text-lg font-semibold mb-3 text-blue-700 dark:text-blue-300">HEXACO Results</h3>
                    <div className="text-sm text-blue-600 dark:text-blue-400">
                      Take the HEXACO test to see your comprehensive personality analysis here.
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Philosophical Insight Section */}
              <div className="space-y-8">
                <div className="premium-card p-6">
                  <h2 className="premium-section-title mb-6">Philosophical Insight</h2>
              {!insight && !loading && (
                <div className="text-center py-12">
                  <div className="max-w-2xl mx-auto">
                    <h2 className="premium-title text-2xl mb-4">Aucune analyse philosophique disponible</h2>
                    <p className="premium-text-secondary text-lg mb-8">
                      Générez votre première analyse personnalisée basée sur votre profil, vos tests de personnalité et vos réflexions.
                    </p>
                    <button
                      className="premium-button-primary px-8 py-3 text-lg"
                      onClick={handleGenerateFirstInsight}
                    >
                      Générer mon analyse philosophique
                    </button>
                  </div>
                </div>
              )}
              
              {insight && (
                <div className="space-y-8">
                  {/* Accept Section */}
                  <div className={styles.acceptSection}>
                    <h2>Si vous acceptez cette vérité</h2>
                    <p className={styles.acceptText}>{insight.if_you_accept}</p>
                  </div>
                  
                  {/* Full Text Section */}
                  <div className={styles.fullTextSection}>
                    <h2>Analyse complète</h2>
                    <div className={styles.fullText}>
                      {insight.full_text}
                    </div>
                  </div>
                  
                  {/* Actions Section */}
                  <div className={styles.actionsSection}>
                    <button
                      className={`${styles.actionButton} ${styles.saveButton}`}
                      onClick={handleSaveInsight}
                      disabled={saving}
                    >
                      {saving ? 'Sauvegarde...' : 'Sauvegarder cette analyse'}
                    </button>
                    
                    <div className={styles.rewriteSection}>
                      <h3>Vous souhaitez une autre perspective ?</h3>
                      <textarea
                        className={styles.feedbackInput}
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        placeholder="Décrivez ce que vous souhaitez explorer différemment..."
                        rows={4}
                      />
                      <button
                        className={`${styles.actionButton} ${styles.rewriteButton}`}
                        onClick={handleRewriteInsight}
                        disabled={rewriting || !feedback}
                      >
                        {rewriting ? 'Réécriture...' : 'Demander une réécriture'}
                      </button>
                    </div>
                  </div>
                </div>
              )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
};

export default InsightPage;
