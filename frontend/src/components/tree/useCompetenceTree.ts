import { useState, useEffect, useCallback } from 'react';
import { CompetenceTreeData, CompetenceNode, PositionedNode } from './types';
import { calculateNodePositions } from './layoutAlgorithm';
import { getCompetenceTree, completeChallenge, generateCompetenceTree } from '../../services/competenceTreeService';

export const useCompetenceTree = (graphId: string) => {
  const [treeData, setTreeData] = useState<CompetenceTreeData | null>(null);
  const [positionedNodes, setPositionedNodes] = useState<PositionedNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [completedNodes, setCompletedNodes] = useState<Set<string>>(new Set());
  const [savedNodes, setSavedNodes] = useState<string[]>([]);
  const [userId, setUserId] = useState<number | null>(null);

  useEffect(() => {
    const storedUserId = localStorage.getItem('user_id');
    if (storedUserId) {
      setUserId(parseInt(storedUserId, 10));
    }
  }, []);

  // Load tree data
  const loadTreeData = useCallback(async () => {
    if (!graphId || !userId) return;

    setLoading(true);
    setError(null);

    try {
      let data;
      try {
        data = await getCompetenceTree(graphId);
      } catch (error: any) {
        if (error.response && error.response.status === 404) {
          console.log("No tree found, generating a new one...");
          const newTree = await generateCompetenceTree(userId);
          data = await getCompetenceTree(newTree.graph_id);
        } else {
          throw error;
        }
      }
      setTreeData(data);

      // Calculate positions for nodes
      const positioned = calculateNodePositions(data.nodes, data.edges);
      setPositionedNodes(positioned);

      // Extract completed nodes
      const completed = new Set(
        data.nodes
          .filter(node => node.state === 'completed')
          .map(node => node.id)
      );
      setCompletedNodes(completed);

      // Load saved nodes from localStorage
      const saved = JSON.parse(localStorage.getItem('savedNodes') || '[]');
      setSavedNodes(saved);
    } catch (err) {
      console.error('Failed to load competence tree:', err);
      setError('Failed to load competence tree. Please try again.');
    } finally {
      setLoading(false);
    }
  }, [graphId]);

  // Complete a challenge/node
  const completeNode = useCallback(async (nodeId: string) => {
    if (!userId) {
      console.error("User ID not found, cannot complete challenge.");
      return;
    }
    try {
      await completeChallenge(nodeId, userId);
      
      // Update local state
      setCompletedNodes(prev => new Set(Array.from(prev).concat(nodeId)));
      
      // Update the node state in positioned nodes
      setPositionedNodes(prev => 
        prev.map(node => 
          node.id === nodeId 
            ? { ...node, state: 'completed' as const }
            : node
        )
      );

      // Reload tree to get updated states
      await loadTreeData();
    } catch (err) {
      console.error('Failed to complete challenge:', err);
      throw err;
    }
  }, [loadTreeData]);

  // Save/unsave a node
  const toggleSaveNode = useCallback((nodeId: string) => {
    setSavedNodes(prev => {
      const newSaved = prev.includes(nodeId)
        ? prev.filter(id => id !== nodeId)
        : [...prev, nodeId];
      
      localStorage.setItem('savedNodes', JSON.stringify(newSaved));
      return newSaved;
    });
  }, []);

  // Filter nodes by visibility
  const getVisibleNodes = useCallback(() => {
    return positionedNodes.filter(node => 
      node.visible !== false && node.state !== 'hidden'
    );
  }, [positionedNodes]);

  // Get node connections
  const getNodeConnections = useCallback((nodeId: string) => {
    if (!treeData) return { incoming: [], outgoing: [] };

    const incoming = treeData.edges
      .filter(edge => edge.target === nodeId)
      .map(edge => edge.source);

    const outgoing = treeData.edges
      .filter(edge => edge.source === nodeId)
      .map(edge => edge.target);

    return { incoming, outgoing };
  }, [treeData]);

  // Get node by ID
  const getNodeById = useCallback((nodeId: string): PositionedNode | undefined => {
    return positionedNodes.find(node => node.id === nodeId);
  }, [positionedNodes]);

  // Get nodes by type
  const getNodesByType = useCallback((type: string) => {
    return positionedNodes.filter(node => node.type === type);
  }, [positionedNodes]);

  // Calculate progress
  const getProgress = useCallback(() => {
    const visibleNodes = getVisibleNodes();
    const completedCount = visibleNodes.filter(node => 
      completedNodes.has(node.id)
    ).length;

    return {
      completed: completedCount,
      total: visibleNodes.length,
      percentage: visibleNodes.length > 0 
        ? Math.round((completedCount / visibleNodes.length) * 100)
        : 0
    };
  }, [getVisibleNodes, completedNodes]);

  // Initial load
  useEffect(() => {
    if (userId) {
      loadTreeData();
    }
  }, [loadTreeData, userId]);

  return {
    // Data
    treeData,
    nodes: positionedNodes,
    edges: treeData?.edges || [],
    
    // State
    loading,
    error,
    completedNodes,
    savedNodes,
    
    // Actions
    completeNode,
    toggleSaveNode,
    reload: loadTreeData,
    
    // Helpers
    getVisibleNodes,
    getNodeConnections,
    getNodeById,
    getNodesByType,
    getProgress
  };
};