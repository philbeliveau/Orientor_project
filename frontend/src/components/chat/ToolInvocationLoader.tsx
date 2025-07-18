import React from 'react';
import { Sparkles, Brain, Users, TreePine, Briefcase, Target } from 'lucide-react';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

interface ToolInvocationLoaderProps {
  toolName: string;
  message?: string;
  className?: string;
}

const toolIcons: Record<string, React.ReactNode> = {
  esco_skills: <TreePine className="w-5 h-5" />,
  career_tree: <Target className="w-5 h-5" />,
  oasis_explorer: <Briefcase className="w-5 h-5" />,
  peer_matching: <Users className="w-5 h-5" />,
  hexaco_test: <Brain className="w-5 h-5" />,
  holland_test: <Sparkles className="w-5 h-5" />,
  xp_challenges: <Target className="w-5 h-5" />
};

const toolDisplayNames: Record<string, string> = {
  esco_skills: "Skill Analysis",
  career_tree: "Career Path",
  oasis_explorer: "Job Explorer",
  peer_matching: "Peer Finder",
  hexaco_test: "HEXACO Test",
  holland_test: "Holland Test",
  xp_challenges: "XP Challenges"
};

export const ToolInvocationLoader: React.FC<ToolInvocationLoaderProps> = ({
  toolName,
  message,
  className = ""
}) => {
  const icon = toolIcons[toolName] || <Sparkles className="w-5 h-5" />;
  const displayName = toolDisplayNames[toolName] || "Tool";
  const displayMessage = message || `Invoking ${displayName}...`;

  return (
    <div className={`flex items-center space-x-3 p-4 bg-blue-50 rounded-lg border border-blue-200 ${className}`}>
      <div className="flex items-center justify-center w-10 h-10 bg-blue-100 rounded-full">
        <LoadingSpinner size="sm" color="#2563eb" />
      </div>
      <div className="flex-1">
        <div className="flex items-center space-x-2">
          <span className="text-blue-900">{icon}</span>
          <span className="text-sm font-medium text-blue-900">{displayMessage}</span>
        </div>
        <div className="mt-1">
          <LoadingSpinner size="sm" color="#60a5fa" />
        </div>
      </div>
    </div>
  );
};