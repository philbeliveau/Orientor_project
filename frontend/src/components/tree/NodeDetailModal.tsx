import React, { useState } from 'react';
import LoadingSpinner from '../ui/LoadingSpinner';
import { saveJobFromTree, SaveJobRequest } from '../../services/competenceTreeService';

interface CompetenceNode {
  id: string;
  skill_id?: string;
  skill_label?: string;
  label?: string;
  type?: string;
  challenge?: string;
  xp_reward?: number;
  visible?: boolean;
  revealed?: boolean;
  state?: 'locked' | 'available' | 'completed' | 'hidden';
  notes?: string;
  is_anchor?: boolean;
  depth?: number;
  metadata?: any;
}

interface NodeDetailModalProps {
  node: CompetenceNode;
  graphId?: string;
  onClose: () => void;
  onCompleteChallenge: (nodeId: string) => void;
  onSaveJob?: (node: CompetenceNode) => void;
}

const NodeDetailModal: React.FC<NodeDetailModalProps> = ({
  node,
  graphId,
  onClose,
  onCompleteChallenge,
  onSaveJob
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState<string | null>(null);

  const displayLabel = node.label || node.skill_label || "Unknown Skill";
  const isOccupation = node.type === "occupation";

  const handleSaveJob = async () => {
    if (!isOccupation) return;

    setIsLoading(true);
    setSaveMessage(null);

    try {
      const jobData: SaveJobRequest = {
        esco_id: node.id,
        job_title: displayLabel,
        skills_required: [], // Could be enhanced to extract from metadata
        discovery_source: "tree",
        tree_graph_id: graphId,
        relevance_score: 0.8, // Default relevance
        metadata: {
          node_type: node.type,
          is_anchor: node.is_anchor,
          depth: node.depth,
          xp_reward: node.xp_reward
        }
      };

      const result = await saveJobFromTree(jobData);
      
      if (result.already_saved) {
        setSaveMessage("✅ Job already saved to your space!");
      } else {
        setSaveMessage("✅ Job saved successfully to your space!");
        if (onSaveJob) {
          onSaveJob(node);
        }
      }
    } catch (error: any) {
      setSaveMessage(`❌ Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const getNodeIcon = () => {
    if (node.type === "occupation") return "💼";
    if (node.type === "skillgroup") return "📋";
    if (node.is_anchor) return "⭐";
    return "🔧";
  };

  const getNodeTypeLabel = () => {
    if (node.type === "occupation") return "Job/Occupation";
    if (node.type === "skillgroup") return "Skill Group";
    if (node.is_anchor) return "Anchor Skill";
    return "Skill";
  };

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">{getNodeIcon()}</span>
              <div>
                <h2 className="text-xl font-bold text-gray-900">
                  {displayLabel}
                </h2>
                <p className="text-sm text-gray-600">{getNodeTypeLabel()}</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-xl font-bold"
            >
              ×
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 space-y-4">
          {/* Status badges */}
          <div className="flex flex-wrap gap-2">
            {node.is_anchor && (
              <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
                ⭐ Anchor Skill
              </span>
            )}
            {node.state === 'completed' && (
              <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
                ✅ Completed
              </span>
            )}
            {node.xp_reward && (
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                {node.xp_reward} XP
              </span>
            )}
          </div>

          {/* Challenge section */}
          {node.challenge && (
            <div className="bg-gray-50 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">🎯 Challenge</h3>
              <p className="text-gray-700 text-sm leading-relaxed">
                {node.challenge}
              </p>
              {node.state !== 'completed' && (
                <button
                  onClick={() => onCompleteChallenge(node.id)}
                  className="mt-3 w-full bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-md transition-colors"
                >
                  Complete Challenge (+{node.xp_reward || 25} XP)
                </button>
              )}
            </div>
          )}

          {/* Job saving section for occupations */}
          {isOccupation && (
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="font-semibold text-blue-900 mb-2">💼 Career Opportunity</h3>
              <p className="text-blue-700 text-sm mb-3">
                This is a career opportunity you discovered through your competence tree exploration.
              </p>
              
              {saveMessage && (
                <div className={`mb-3 p-2 rounded text-sm ${
                  saveMessage.includes('Error') 
                    ? 'bg-red-100 text-red-700' 
                    : 'bg-green-100 text-green-700'
                }`}>
                  {saveMessage}
                </div>
              )}
              
              <button
                onClick={handleSaveJob}
                disabled={isLoading}
                className={`w-full font-medium py-2 px-4 rounded-md transition-colors ${
                  isLoading 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-blue-600 hover:bg-blue-700'
                } text-white flex items-center justify-center`}
              >
                {isLoading ? (
                  <>
                    <LoadingSpinner size="sm" color="white" />
                    <span className="ml-2">Saving...</span>
                  </>
                ) : (
                  '💾 Save to My Space'
                )}
              </button>
            </div>
          )}

          {/* Node details */}
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Type:</span>
              <span className="font-medium">{getNodeTypeLabel()}</span>
            </div>
            {node.depth !== undefined && (
              <div className="flex justify-between">
                <span className="text-gray-600">Tree Level:</span>
                <span className="font-medium">{node.depth}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-gray-600">Node ID:</span>
              <span className="font-mono text-xs text-gray-500">{node.id}</span>
            </div>
          </div>

          {/* Notes section */}
          {node.notes && (
            <div className="bg-yellow-50 rounded-lg p-4">
              <h3 className="font-semibold text-yellow-900 mb-2">📝 Notes</h3>
              <p className="text-yellow-700 text-sm">
                {node.notes}
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-gray-200">
          <button
            onClick={onClose}
            className="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-md transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default NodeDetailModal;