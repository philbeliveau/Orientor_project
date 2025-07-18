import React, { useState, useCallback, lazy, Suspense } from 'react';
import LoadingSpinner from '../ui/LoadingSpinner';
import { useCompetenceTree } from './useCompetenceTree';
import { TreeVisualization } from './TreeVisualization';
import { PositionedNode } from './types';
import ChallengeCard from '../ui/ChallengeCard';
import '../tree/treestyles.css';

// Lazy load modal for better performance
const NodeDetailModal = lazy(() => import('./NodeDetailModal'));

interface CompetenceTreeViewProps {
  graphId: string;
}

const CompetenceTreeView: React.FC<CompetenceTreeViewProps> = ({ graphId }) => {
  const {
    nodes,
    edges,
    loading,
    error,
    savedNodes,
    completeNode,
    toggleSaveNode,
    getProgress,
    getVisibleNodes
  } = useCompetenceTree(graphId);

  const [selectedNode, setSelectedNode] = useState<PositionedNode | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [currentChallenge, setCurrentChallenge] = useState<PositionedNode | null>(null);

  // Handle node click
  const handleNodeClick = useCallback((node: PositionedNode) => {
    setSelectedNode(node);
    setShowModal(true);
  }, []);

  // Handle challenge completion
  const handleCompleteChallenge = useCallback(async (nodeId: string) => {
    try {
      await completeNode(nodeId);
      setCurrentChallenge(null);
      // Show success notification
    } catch (error) {
      console.error('Failed to complete challenge:', error);
      // Show error notification
    }
  }, [completeNode]);

  // Start challenge
  const startChallenge = useCallback((node: PositionedNode) => {
    setCurrentChallenge(node);
    setShowModal(false);
  }, []);

  // Get visible nodes for rendering
  const visibleNodes = getVisibleNodes();
  const progress = getProgress();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-red-600 text-center">
          <p className="text-xl font-semibold mb-2">Error Loading Tree</p>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="competence-tree-container h-full flex flex-col">
      {/* Progress Header */}
      <div className="bg-white shadow-sm border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Competence Tree</h2>
            <p className="text-gray-600 mt-1">
              Build your skills by completing challenges
            </p>
          </div>
          <div className="flex items-center gap-6">
            <div className="text-right">
              <p className="text-sm text-gray-600">Progress</p>
              <p className="text-2xl font-bold text-blue-600">
                {progress.percentage}%
              </p>
            </div>
            <div className="w-32 h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-600 transition-all duration-500"
                style={{ width: `${progress.percentage}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Tree Visualization */}
      <div className="flex-1 relative">
        <TreeVisualization
          nodes={visibleNodes}
          edges={edges}
          onNodeClick={handleNodeClick}
          onNodeComplete={handleCompleteChallenge}
          savedNodes={savedNodes}
        />
      </div>

      {/* Current Challenge */}
      {currentChallenge && (
        <div className="absolute bottom-4 left-4 right-4 max-w-md mx-auto">
          <ChallengeCard
            challenge={currentChallenge.challenge || ''}
            xpReward={currentChallenge.xp_reward || 0}
            completed={false}
            onComplete={() => handleCompleteChallenge(currentChallenge.id)}
          />
        </div>
      )}

      {/* Node Detail Modal */}
      {showModal && selectedNode && (
        <Suspense fallback={<div className="modal-loading">Loading...</div>}>
          <NodeDetailModal
            node={selectedNode}
            onClose={() => setShowModal(false)}
            onCompleteChallenge={(nodeId) => handleCompleteChallenge(nodeId)}
            onSaveJob={(node) => toggleSaveNode(node.id)}
          />
        </Suspense>
      )}
    </div>
  );
};

export default CompetenceTreeView;