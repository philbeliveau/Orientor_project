'use client';

import React, { useState, useEffect } from 'react';
import { 
  Chart as ChartJS, 
  RadialLinearScale, 
  PointElement, 
  LineElement, 
  Filler, 
  Tooltip, 
  Legend 
} from 'chart.js';
import { Radar } from 'react-chartjs-2';
import { ScoreResponse } from '@/services/hollandTestService';
import hollandTestService from '@/services/hollandTestService';
import { motion } from 'framer-motion';

// Enregistrer les composants nécessaires pour le graphique radar
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

// Définir les couleurs pour chaque dimension RIASEC
const riasecColors = {
  r: 'rgba(255, 99, 132, 0.7)',   // Rouge
  i: 'rgba(54, 162, 235, 0.7)',    // Bleu
  a: 'rgba(255, 206, 86, 0.7)',    // Jaune
  s: 'rgba(75, 192, 192, 0.7)',    // Vert
  e: 'rgba(153, 102, 255, 0.7)',   // Violet
  c: 'rgba(255, 159, 64, 0.7)',    // Orange
};

// Définir les descriptions détaillées pour chaque dimension RIASEC
const riasecDescriptions = {
  R: {
    title: 'Réaliste',
    description: 'Les personnes de type Réaliste préfèrent travailler avec des objets, des machines, des outils, des plantes ou des animaux. Elles aiment les activités pratiques et concrètes qui demandent de la coordination, de la force physique ou des compétences manuelles. Elles valorisent les résultats pratiques et tangibles.'
  },
  I: {
    title: 'Investigateur',
    description: 'Les personnes de type Investigateur aiment observer, apprendre, analyser et résoudre des problèmes. Elles sont curieuses, méthodiques et précises. Elles préfèrent travailler de façon autonome et valorisent les connaissances scientifiques et intellectuelles.'
  },
  A: {
    title: 'Artistique',
    description: 'Les personnes de type Artistique aiment les activités créatives qui permettent de s\'exprimer librement. Elles sont imaginatives, intuitives et originales. Elles valorisent l\'esthétique, l\'innovation et l\'expression personnelle.'
  },
  S: {
    title: 'Social',
    description: 'Les personnes de type Social aiment travailler avec les autres pour les informer, les aider, les soigner ou les divertir. Elles sont empathiques, patientes et communicatives. Elles valorisent le service aux autres et le travail en équipe.'
  },
  E: {
    title: 'Entreprenant',
    description: 'Les personnes de type Entreprenant aiment influencer, persuader et diriger les autres. Elles sont énergiques, ambitieuses et sociables. Elles valorisent le statut, le pouvoir et la réussite matérielle.'
  },
  C: {
    title: 'Conventionnel',
    description: 'Les personnes de type Conventionnel aiment suivre des procédures établies et respecter des règles. Elles sont organisées, précises et efficaces. Elles valorisent la fiabilité, la stabilité et la sécurité.'
  }
};

interface HollandResultsViewProps {
  userId?: string;
}

const HollandResultsView: React.FC<HollandResultsViewProps> = ({ userId }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [score, setScore] = useState<ScoreResponse | null>(null);
  const [personalizedDescription, setPersonalizedDescription] = useState<string | null>(null);
  const [loadingDescription, setLoadingDescription] = useState(false);
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    const fetchLatestResults = async () => {
      try {
        setLoading(true);
        // Récupérer le dernier résultat de test Holland de l'utilisateur
        const latestResults = await hollandTestService.getUserLatestResults();
        setScore(latestResults);
        setLoading(false);
      } catch (err) {
        console.error('Erreur lors de la récupération des résultats:', err);
        setError('Impossible de récupérer vos résultats RIASEC. Veuillez réessayer plus tard.');
        setLoading(false);
      }
    };

    fetchLatestResults();
  }, []);

  useEffect(() => {
    // Récupérer la description personnalisée si nous avons les scores
    if (score && !personalizedDescription && !loadingDescription) {
      const fetchPersonalizedDescription = async (regenerate: boolean = false) => {
        try {
          setLoadingDescription(true);
          const description = await hollandTestService.getProfileDescription(regenerate);
          setPersonalizedDescription(description);
          setLoadingDescription(false);
        } catch (err) {
          console.error('Erreur lors de la récupération de la description personnalisée:', err);
          setLoadingDescription(false);
        }
      };

      fetchPersonalizedDescription();
    }
  }, [score, personalizedDescription, loadingDescription]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 text-red-700 dark:text-red-400">
        <p>{error}</p>
        <button 
          onClick={() => window.location.href = '/holland-test'}
          className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          Passer le test Holland
        </button>
      </div>
    );
  }

  if (!score) {
    return (
      <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6 text-center">
        <h3 className="text-xl font-semibold mb-3 text-yellow-700 dark:text-yellow-400">
          Aucun résultat disponible
        </h3>
        <p className="text-gray-700 dark:text-gray-300 mb-4">
          Vous n'avez pas encore passé le test Holland Code (RIASEC) ou vos résultats ne sont pas disponibles.
        </p>
        <button 
          onClick={() => window.location.href = '/holland-test'}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          Passer le test Holland
        </button>
      </div>
    );
  }

  // Préparer les données pour le graphique radar
  const chartData = {
    labels: ['Réaliste (R)', 'Investigateur (I)', 'Artistique (A)', 'Social (S)', 'Entreprenant (E)', 'Conventionnel (C)'],
    datasets: [
      {
        label: 'Scores RIASEC',
        data: [score.r_score, score.i_score, score.a_score, score.s_score, score.e_score, score.c_score],
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
        pointBackgroundColor: Object.values(riasecColors),
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
      },
    ],
  };

  // Options pour le graphique radar
  const chartOptions = {
    scales: {
      r: {
        beginAtZero: true,
        ticks: {
          display: false,
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
    },
    maintainAspectRatio: false,
  };

  // Extraire les lettres individuelles du code Holland
  const codeLetters = score.top_3_code ? score.top_3_code.split('') : [];

  return (
    <div className="space-y-8">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 className="text-2xl font-bold mb-6 text-gray-800 dark:text-white">
          Vos résultats du test Holland Code (RIASEC)
        </h2>
        
        {/* Code Holland à 3 lettres */}
        <div className="flex justify-center mb-8">
          {codeLetters.map((letter, index) => (
            <motion.div
              key={index}
              className="flex items-center justify-center w-16 h-16 mx-2 rounded-full text-white text-2xl font-bold"
              style={{ backgroundColor: riasecColors[letter.toLowerCase() as keyof typeof riasecColors] }}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: index * 0.2, type: 'spring', stiffness: 200 }}
            >
              {letter}
            </motion.div>
          ))}
        </div>
        
        {/* Explication du code */}
        <div className="text-center mb-8">
          <p className="text-lg text-gray-700 dark:text-gray-300">
            Votre profil Holland Code est <strong>{score.top_3_code}</strong>
          </p>
        </div>
        
        {/* Graphique radar */}
        <div className="w-full h-80 mb-8">
          <Radar data={chartData} options={chartOptions} />
        </div>
      </div>

      {/* Description personnalisée */}
      {loadingDescription ? (
        <div className="flex items-center justify-center h-32">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
          <span className="ml-3 text-gray-600 dark:text-gray-400">
            {regenerating ? "Régénération de votre profil personnalisé..." : "Génération de votre profil personnalisé..."}
          </span>
        </div>
      ) : personalizedDescription ? (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-xl font-semibold text-gray-800 dark:text-white">
              Votre profil personnalisé
            </h3>
            <button
              onClick={async () => {
                setRegenerating(true);
                try {
                  setLoadingDescription(true);
                  const description = await hollandTestService.getProfileDescription(true);
                  setPersonalizedDescription(description);
                } catch (err) {
                  console.error('Erreur lors de la régénération de la description:', err);
                } finally {
                  setLoadingDescription(false);
                  setRegenerating(false);
                }
              }}
              className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded transition-colors"
              disabled={loadingDescription}
            >
              Régénérer la description
            </button>
          </div>
          <div className="prose dark:prose-invert max-w-none">
            <p className="whitespace-pre-line">{personalizedDescription}</p>
          </div>
        </div>
      ) : null}

      {/* Détails sur chaque dimension RIASEC */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
          Comprendre les dimensions RIASEC
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Object.entries(riasecDescriptions).map(([key, { title, description }]) => {
            const letterScore = score[`${key.toLowerCase()}_score` as keyof ScoreResponse];
            const isInTop3 = score.top_3_code.includes(key);
            
            return (
              <div 
                key={key}
                className={`p-4 rounded-lg border ${
                  isInTop3 
                    ? 'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/20' 
                    : 'border-gray-200 dark:border-gray-700'
                }`}
              >
                <div className="flex items-center mb-2">
                  <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold mr-3"
                    style={{ backgroundColor: riasecColors[key.toLowerCase() as keyof typeof riasecColors] }}
                  >
                    {key}
                  </div>
                  <h4 className="text-lg font-medium text-gray-800 dark:text-white">
                    {title} <span className="text-sm font-normal text-gray-500 dark:text-gray-400">
                      ({typeof letterScore === 'number' ? letterScore.toFixed(1) : letterScore})
                    </span>
                  </h4>
                </div>
                <p className="text-gray-700 dark:text-gray-300 text-sm">
                  {description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bouton pour refaire le test */}
      <div className="flex justify-center mt-6">
        <button
          onClick={() => window.location.href = '/holland-test'}
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
        >
          Refaire le test
        </button>
      </div>
    </div>
  );
};

export default HollandResultsView;