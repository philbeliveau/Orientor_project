'use client';

import React from 'react';
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

// Définir les descriptions courtes pour chaque dimension RIASEC
const riasecLabels = {
  R: 'Réaliste',
  I: 'Investigateur',
  A: 'Artistique',
  S: 'Social',
  E: 'Entreprenant',
  C: 'Conventionnel',
};

interface ResultScreenProps {
  score: ScoreResponse;
  onRetakeTest: () => void;
}

const ResultScreen: React.FC<ResultScreenProps> = ({ score, onRetakeTest }) => {
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
  
  // Obtenir la description du trait dominant (première lettre du code)
  const dominantTrait = codeLetters[0];
  const dominantTraitLabel = riasecLabels[dominantTrait as keyof typeof riasecLabels];

  return (
    <motion.div 
      className="flex flex-col items-center justify-center w-full max-w-4xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <h2 className="text-3xl font-bold text-center mb-6 text-gray-800 dark:text-white">
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
        <p className="text-md text-gray-600 dark:text-gray-400 mt-2">
          Trait dominant: <strong>{dominantTraitLabel}</strong>
        </p>
      </div>
      
      {/* Graphique radar */}
      <div className="w-full h-80 mb-8">
        <Radar data={chartData} options={chartOptions} />
      </div>
      
      {/* Description du trait dominant */}
      {score.personality_description && (
        <div className="bg-gray-100 dark:bg-gray-700 p-6 rounded-lg mb-8 w-full">
          <h3 className="text-xl font-semibold mb-3 text-gray-800 dark:text-white">
            À propos du type {dominantTraitLabel} ({dominantTrait})
          </h3>
          <p className="text-gray-700 dark:text-gray-300">
            {score.personality_description}
          </p>
        </div>
      )}
      
      {/* Bouton pour refaire le test */}
      <button
        onClick={onRetakeTest}
        className="mt-6 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
      >
        Refaire le test
      </button>
    </motion.div>
  );
};

export default ResultScreen;