import React from 'react';
import { motion } from 'framer-motion';
import { Slider } from '@/components/ui/slider';

interface SkillNodeDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  skill: {
    label: string;
    level: number;
    description: string;
  };
}

const SkillNodeDrawer: React.FC<SkillNodeDrawerProps> = ({ isOpen, onClose, skill }) => {
  if (!isOpen) return null;

  return (
    <motion.div
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="fixed right-0 top-0 h-full w-96 bg-white shadow-lg z-50"
    >
      <div className="p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold text-gray-800">{skill.label}</h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            ✕
          </button>
        </div>

        <div className="space-y-6">
          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-2">Description</h3>
            <p className="text-gray-700">{skill.description}</p>
          </div>

          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-2">Self-Assessment</h3>
            <Slider
              defaultValue={[skill.level]}
              max={5}
              step={1}
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-2">
              <span>Beginner</span>
              <span>Expert</span>
            </div>
          </div>

          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-2">Notes</h3>
            <textarea
              className="w-full h-32 p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Add your notes about this skill..."
            />
          </div>

          <div>
            <h3 className="text-sm font-medium text-gray-500 mb-2">Suggested Resources</h3>
            <ul className="space-y-2">
              <li className="text-blue-600 hover:text-blue-800 cursor-pointer">
                • Online Course: Advanced {skill.label}
              </li>
              <li className="text-blue-600 hover:text-blue-800 cursor-pointer">
                • Book: Mastering {skill.label}
              </li>
            </ul>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default SkillNodeDrawer; 