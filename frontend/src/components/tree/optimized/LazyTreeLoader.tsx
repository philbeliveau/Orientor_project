import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { PositionedNode } from '../types';

interface LazyTreeLoaderProps {
  nodes: PositionedNode[];
  edges: { source: string; target: string }[];
  onNodesLoaded: (nodes: PositionedNode[]) => void;
  onEdgesLoaded: (edges: { source: string; target: string }[]) => void;
  batchSize?: number;
  loadDelay?: number;
}

interface LoadingState {
  loadedNodes: number;
  loadedEdges: number;
  isLoading: boolean;
  progress: number;
}

const LazyTreeLoader: React.FC<LazyTreeLoaderProps> = ({
  nodes,
  edges,
  onNodesLoaded,
  onEdgesLoaded,
  batchSize = 10,
  loadDelay = 50
}) => {
  const [loadingState, setLoadingState] = useState<LoadingState>({
    loadedNodes: 0,
    loadedEdges: 0,
    isLoading: false,
    progress: 0
  });

  // Priority-based loading - important nodes first
  const prioritizedNodes = useMemo(() => {
    const anchors = nodes.filter(n => n.is_anchor);
    const occupations = nodes.filter(n => n.type === 'occupation' && !n.is_anchor);
    const skillgroups = nodes.filter(n => n.type === 'skillgroup' && !n.is_anchor);
    const skills = nodes.filter(n => !n.is_anchor && n.type !== 'occupation' && n.type !== 'skillgroup');
    
    // Load in priority order: anchors -> occupations -> skillgroups -> skills
    return [...anchors, ...occupations, ...skillgroups, ...skills];
  }, [nodes]);

  // Progressive loading with batching
  const loadNextBatch = useCallback(async () => {
    if (loadingState.isLoading) return;

    setLoadingState(prev => ({ ...prev, isLoading: true }));

    const { loadedNodes, loadedEdges } = loadingState;
    const totalItems = prioritizedNodes.length + edges.length;

    // Load nodes first
    if (loadedNodes < prioritizedNodes.length) {
      const nextBatch = prioritizedNodes.slice(loadedNodes, loadedNodes + batchSize);
      const allLoadedNodes = prioritizedNodes.slice(0, loadedNodes + nextBatch.length);
      
      // Simulate loading delay for smoother UX
      await new Promise(resolve => setTimeout(resolve, loadDelay));
      
      onNodesLoaded(allLoadedNodes);
      
      const newLoadedNodes = loadedNodes + nextBatch.length;
      const progress = ((newLoadedNodes + loadedEdges) / totalItems) * 100;
      
      setLoadingState(prev => ({
        ...prev,
        loadedNodes: newLoadedNodes,
        progress,
        isLoading: false
      }));
    }
    // Then load edges
    else if (loadedEdges < edges.length) {
      const nextBatch = edges.slice(loadedEdges, loadedEdges + batchSize * 2); // Edges load faster
      const allLoadedEdges = edges.slice(0, loadedEdges + nextBatch.length);
      
      await new Promise(resolve => setTimeout(resolve, loadDelay / 2));
      
      onEdgesLoaded(allLoadedEdges);
      
      const newLoadedEdges = loadedEdges + nextBatch.length;
      const progress = ((loadedNodes + newLoadedEdges) / totalItems) * 100;
      
      setLoadingState(prev => ({
        ...prev,
        loadedEdges: newLoadedEdges,
        progress,
        isLoading: false
      }));
    }
  }, [loadingState, prioritizedNodes, edges, batchSize, loadDelay, onNodesLoaded, onEdgesLoaded]);

  // Auto-load next batch when current batch is complete
  useEffect(() => {
    if (!loadingState.isLoading && loadingState.progress < 100) {
      const timer = setTimeout(loadNextBatch, 10);
      return () => clearTimeout(timer);
    }
  }, [loadingState.isLoading, loadingState.progress, loadNextBatch]);

  // Reset loading when nodes/edges change
  useEffect(() => {
    setLoadingState({
      loadedNodes: 0,
      loadedEdges: 0,
      isLoading: false,
      progress: 0
    });
  }, [nodes.length, edges.length]);

  const isComplete = loadingState.progress >= 100;

  return (
    <div style={{
      position: 'absolute',
      top: '50%',
      left: '50%',
      transform: 'translate(-50%, -50%)',
      background: 'white',
      padding: '24px',
      borderRadius: '12px',
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
      zIndex: 1000,
      minWidth: '300px',
      textAlign: 'center',
      display: isComplete ? 'none' : 'block'
    }}>
      <div style={{
        fontSize: '18px',
        fontWeight: '600',
        marginBottom: '16px',
        color: '#1f2937'
      }}>
        🌳 Loading Competence Tree
      </div>
      
      <div style={{
        fontSize: '14px',
        color: '#6b7280',
        marginBottom: '16px'
      }}>
        Loading {loadingState.loadedNodes}/{nodes.length} nodes, {loadingState.loadedEdges}/{edges.length} connections
      </div>

      {/* Progress bar */}
      <div style={{
        width: '100%',
        height: '8px',
        background: '#e5e7eb',
        borderRadius: '4px',
        overflow: 'hidden',
        marginBottom: '16px'
      }}>
        <div style={{
          width: `${loadingState.progress}%`,
          height: '100%',
          background: 'linear-gradient(90deg, #3b82f6, #10b981)',
          borderRadius: '4px',
          transition: 'width 0.3s ease'
        }} />
      </div>

      <div style={{
        fontSize: '12px',
        color: '#9ca3af'
      }}>
        {Math.round(loadingState.progress)}% complete
      </div>

      {/* Loading animation */}
      <div style={{
        marginTop: '16px',
        display: 'flex',
        justifyContent: 'center',
        gap: '4px'
      }}>
        {[0, 1, 2].map(i => (
          <div
            key={i}
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              background: '#3b82f6',
              animation: `pulse 1.5s ease-in-out ${i * 0.2}s infinite`
            }}
          />
        ))}
      </div>

      <style jsx>{`
        @keyframes pulse {
          0%, 80%, 100% { opacity: 0.3; }
          40% { opacity: 1; }
        }
      `}</style>
    </div>
  );
};

export default React.memo(LazyTreeLoader);