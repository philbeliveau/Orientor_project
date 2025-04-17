'use client';

import React, { useState } from 'react';
import SkillTreeCanvas from '@/components/space/SkillTreeCanvas';
import SkillNodeDrawer from '@/components/space/SkillNodeDrawer';
import DailyPromptCard from '@/components/space/DailyPromptCard';
import { Node } from 'reactflow';

interface SkillNodeData {
  label: string;
  level: number;
  description: string;
}

interface CustomNode extends Node {
  type: 'skill';
  data: SkillNodeData;
}

export default function SpacePage() {
  const [selectedSkill, setSelectedSkill] = useState<SkillNodeData | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  const handleNodeClick = (node: CustomNode) => {
    setSelectedSkill(node.data);
    setIsDrawerOpen(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-white to-blue-50">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <SkillTreeCanvas onNodeClick={handleNodeClick} />
          </div>
          
          <div className="space-y-8">
            <DailyPromptCard />
            
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Active Skills
              </h3>
              <div className="flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm">
                  Problem Solving
                </span>
                <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                  Data Analysis
                </span>
                <span className="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm">
                  Communication
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {selectedSkill && (
        <SkillNodeDrawer
          isOpen={isDrawerOpen}
          onClose={() => setIsDrawerOpen(false)}
          skill={selectedSkill}
        />
      )}
    </div>
  );
}