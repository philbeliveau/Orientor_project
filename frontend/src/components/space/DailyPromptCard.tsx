import React from 'react';
import { motion } from 'framer-motion';

const DailyPromptCard: React.FC = () => {
  const prompts = [
    "What's one skill you'd like to develop further today?",
    "How can you apply your current skills in a new way?",
    "What challenges have helped you grow recently?",
    "Which skill would you like to master next?",
  ];

  const currentPrompt = prompts[Math.floor(Math.random() * prompts.length)];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-sm p-6 max-w-md mx-auto"
    >
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
        <h3 className="text-sm font-medium text-gray-500">Daily Reflection</h3>
      </div>
      
      <p className="text-lg text-gray-800 mb-4">{currentPrompt}</p>
      
      <div className="space-y-3">
        <textarea
          className="w-full h-24 p-3 text-sm border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          placeholder="Share your thoughts..."
        />
        <button
          className="w-full py-2 px-4 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          Save Reflection
        </button>
      </div>
    </motion.div>
  );
};

export default DailyPromptCard; 