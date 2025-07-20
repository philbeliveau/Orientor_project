import React, { useState, useEffect, useCallback, useMemo, Suspense } from 'react';
import dynamic from 'next/dynamic';
import { CompetenceTreeData, PositionedNode } from '../types/competence.types';
import { calculateRadialTreeLayout } from '../utils/treeLayout';
import { TreeNode } from './TreeNode';
import { getCompetenceTree, completeChallenge } from '@/services/competenceTreeService';
import LoadingSpinner from '@/components/ui/LoadingSpinner';

// Lazy load heavy components
const NodeDetailModal = dynamic(() => import('@/components/tree/NodeDetailModal'), {
  loading: () => <LoadingSpinner />,
  ssr: false
});

const ChallengeCard = dynamic(() => import('@/components/ui/ChallengeCard'), {
  loading: () => <LoadingSpinner />,
  ssr: false
});

interface CompetenceTreeViewProps {
  graphId: string;
}

export const CompetenceTreeView: React.FC<CompetenceTreeViewProps> = ({ graphId }) => {
  const [treeData, setTreeData] = useState<CompetenceTreeData | null>(null);
  const [positionedNodes, setPositionedNodes] = useState<PositionedNode[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<PositionedNode | null>(null);
  const [completedNodes, setCompletedNodes] = useState<Set<string>>(new Set());
  const [savedOccupations, setSavedOccupations] = useState<Set<string>>(new Set());
  const [showNodeDetail, setShowNodeDetail] = useState(false);
  const [currentChallenge, setCurrentChallenge] = useState<PositionedNode | null>(null);

  // Fetch tree data
  useEffect(() => {
    const fetchTreeData = async () => {
      try {
        setLoading(true);
        const data = await getCompetenceTree(graphId);
        setTreeData(data);
        
        // Load saved data from localStorage
        const saved = localStorage.getItem('savedOccupations');
        if (saved) {
          try {
            setSavedOccupations(new Set(JSON.parse(saved)));
          } catch (e) {
            console.warn('Failed to parse saved occupations from localStorage:', e);
            localStorage.removeItem('savedOccupations');
            setSavedOccupations(new Set());
          }
        }
        
        const completed = localStorage.getItem('completedChallenges');
        if (completed) {
          try {
            setCompletedNodes(new Set(JSON.parse(completed)));
          } catch (e) {
            console.warn('Failed to parse completed challenges from localStorage:', e);
            localStorage.removeItem('completedChallenges');
            setCompletedNodes(new Set());
          }
        }
      } catch (err) {
        setError('Failed to load competence tree');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchTreeData();
  }, [graphId]);

  // Calculate positions when tree data changes
  useEffect(() => {
    if (treeData) {
      const positioned = calculateRadialTreeLayout(treeData.nodes, treeData.edges);
      setPositionedNodes(positioned);
    }
  }, [treeData]);

  // Handle node completion
  const handleNodeComplete = useCallback(async (nodeId: string) => {
    try {
      await completeChallenge(nodeId, 1); // Using default userId 1 for now
      const newCompleted = new Set(Array.from(completedNodes).concat(nodeId));
      setCompletedNodes(newCompleted);
      localStorage.setItem('completedChallenges', JSON.stringify(Array.from(newCompleted)));
      
      // Update tree data to reflect completion
      if (treeData) {
        const updatedNodes = treeData.nodes.map(node =>
          node.id === nodeId ? { ...node, state: 'completed' as const } : node
        );
        setTreeData({ ...treeData, nodes: updatedNodes });
      }
    } catch (err) {
      console.error('Failed to complete challenge:', err);
    }
  }, [completedNodes, treeData]);

  // Handle node click
  const handleNodeClick = useCallback((node: PositionedNode) => {
    setSelectedNode(node);
    if (node.challenge) {
      setCurrentChallenge(node);
    } else {
      setShowNodeDetail(true);
    }
  }, []);

  // SVG viewport dimensions
  const svgDimensions = useMemo(() => ({
    width: typeof window !== 'undefined' ? Math.max(3200, window.innerWidth * 1.5) : 3200,
    height: typeof window !== 'undefined' ? Math.max(2200, window.innerHeight * 1.5) : 2200
  }), []);

  // Render loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  // Render edges
  const renderEdges = () => {
    if (!treeData) return null;
    
    return treeData.edges.map((edge, index) => {
      const source = positionedNodes.find(n => n.id === edge.source);
      const target = positionedNodes.find(n => n.id === edge.target);
      
      if (!source || !target) return null;
      
      return (
        <line
          key={`edge-${index}`}
          x1={source.x}
          y1={source.y}
          x2={target.x}
          y2={target.y}
          stroke="#e5e7eb"
          strokeWidth="2"
          strokeDasharray={edge.type === 'optional' ? '5,5' : 'none'}
          opacity="0.6"
        />
      );
    });
  };

  return (
    <div className="relative w-full h-screen overflow-hidden bg-gray-50">
      <svg
        width={svgDimensions.width}
        height={svgDimensions.height}
        className="competence-tree-svg"
        style={{
          position: 'absolute',
          left: '50%',
          top: '50%',
          transform: 'translate(-50%, -50%)',
        }}
      >
        <g className="edges-layer">
          {renderEdges()}
        </g>
        <g className="nodes-layer">
          {positionedNodes.map(node => (
            <TreeNode
              key={node.id}
              node={node}
              onComplete={handleNodeComplete}
              onNodeClick={handleNodeClick}
              isSaved={savedOccupations.has(node.id)}
            />
          ))}
        </g>
      </svg>

      {/* Lazy loaded modals */}
      <Suspense fallback={<LoadingSpinner />}>
        {showNodeDetail && selectedNode && (
          <NodeDetailModal
            node={selectedNode}
            onClose={() => setShowNodeDetail(false)}
            onCompleteChallenge={handleNodeComplete}
          />
        )}
        
        {currentChallenge && (
          <ChallengeCard
            challenge={currentChallenge.challenge || ''}
            xpReward={currentChallenge.xp_reward || 0}
            completed={completedNodes.has(currentChallenge.id)}
            onComplete={() => handleNodeComplete(currentChallenge.id)}
          />
        )}
      </Suspense>
    </div>
  );
};