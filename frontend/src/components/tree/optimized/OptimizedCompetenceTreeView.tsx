import React, { useState, useEffect, useCallback, useMemo, Suspense } from 'react';
import { useCompetenceTree } from '../useCompetenceTree';
import { PositionedNode } from '../types';
import LoadingSpinner from '../../ui/LoadingSpinner';
import NodeDetailModal from '../NodeDetailModal';
import LazyTreeLoader from './LazyTreeLoader';
import PerformanceMonitor from './PerformanceMonitor';

// Lazy load the heavy rendering components
const CanvasTreeRenderer = React.lazy(() => import('./CanvasTreeRenderer'));
const VirtualizedTreeView = React.lazy(() => import('./VirtualizedTreeView'));

interface OptimizedCompetenceTreeViewProps {
  graphId: string;
}

type RenderMode = 'canvas' | 'virtualized' | 'hybrid';

const OptimizedCompetenceTreeView: React.FC<OptimizedCompetenceTreeViewProps> = ({ graphId }) => {
  const {
    treeData,
    nodes,
    edges,
    loading,
    error,
    completedNodes,
    savedNodes,
    completeNode,
    toggleSaveNode,
    reload,
    getVisibleNodes,
    getProgress
  } = useCompetenceTree(graphId);

  // UI State
  const [selectedNode, setSelectedNode] = useState<PositionedNode | null>(null);
  const [showNodeModal, setShowNodeModal] = useState(false);
  const [hoveredNode, setHoveredNode] = useState<PositionedNode | null>(null);
  const [renderMode, setRenderMode] = useState<RenderMode>('hybrid');
  const [showPerformanceMonitor, setShowPerformanceMonitor] = useState(false);

  // Viewport State
  const [zoom, setZoom] = useState(1);
  const [panX, setPanX] = useState(0);
  const [panY, setPanY] = useState(0);

  // Search and Filter State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNodeTypes, setSelectedNodeTypes] = useState<Set<string>>(
    new Set(['occupation', 'skillgroup', 'skill', 'anchor'])
  );

  // Progressive Loading State
  const [loadedNodes, setLoadedNodes] = useState<PositionedNode[]>([]);
  const [loadedEdges, setLoadedEdges] = useState<{ source: string; target: string }[]>([]);
  const [isFullyLoaded, setIsFullyLoaded] = useState(false);

  // Auto-detect optimal render mode based on node count
  const optimalRenderMode = useMemo<RenderMode>(() => {
    if (nodes.length > 100) return 'canvas';
    if (nodes.length > 50) return 'virtualized';
    return 'hybrid';
  }, [nodes.length]);

  // Apply optimal render mode
  useEffect(() => {
    if (renderMode === 'hybrid') {
      setRenderMode(optimalRenderMode);
    }
  }, [optimalRenderMode, renderMode]);

  // Handle progressive loading completion
  useEffect(() => {
    if (loadedNodes.length === nodes.length && loadedEdges.length === edges.length) {
      setIsFullyLoaded(true);
    }
  }, [loadedNodes.length, loadedEdges.length, nodes.length, edges.length]);

  // Filtered nodes for search and type filtering
  const filteredNodes = useMemo(() => {
    let filtered = isFullyLoaded ? nodes : loadedNodes;

    // Apply type filter
    if (selectedNodeTypes.size > 0 && selectedNodeTypes.size < 4) {
      filtered = filtered.filter(node => {
        const nodeType = node.is_anchor ? 'anchor' : (node.type || 'skill');
        return selectedNodeTypes.has(nodeType);
      });
    }

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(node => {
        const label = (node.label || node.skill_label || '').toLowerCase();
        const challenge = (node.challenge || '').toLowerCase();
        return label.includes(query) || challenge.includes(query);
      });
    }

    return filtered;
  }, [isFullyLoaded ? nodes : loadedNodes, selectedNodeTypes, searchQuery, isFullyLoaded, loadedNodes]);

  // Event Handlers
  const handleNodeClick = useCallback((node: PositionedNode) => {
    setSelectedNode(node);
    setShowNodeModal(true);
  }, []);

  const handleNodeHover = useCallback((node: PositionedNode | null) => {
    setHoveredNode(node);
  }, []);

  const handleCloseModal = useCallback(() => {
    setShowNodeModal(false);
    setSelectedNode(null);
  }, []);

  const handleCompleteChallenge = useCallback(async (nodeId: string) => {
    try {
      await completeNode(nodeId);
    } catch (error) {
      console.error('Failed to complete challenge:', error);
    }
  }, [completeNode]);

  const handleJobSaved = useCallback((nodeId: string) => {
    toggleSaveNode(nodeId);
  }, [toggleSaveNode]);

  // Zoom and Pan Controls
  const handleZoomIn = useCallback(() => {
    setZoom(prev => Math.min(3, prev + 0.2));
  }, []);

  const handleZoomOut = useCallback(() => {
    setZoom(prev => Math.max(0.1, prev - 0.2));
  }, []);

  const handleResetView = useCallback(() => {
    setZoom(1);
    setPanX(0);
    setPanY(0);
  }, []);

  // Progressive loading handlers
  const handleNodesLoaded = useCallback((nodes: PositionedNode[]) => {
    setLoadedNodes(nodes);
  }, []);

  const handleEdgesLoaded = useCallback((edges: { source: string; target: string }[]) => {
    setLoadedEdges(edges);
  }, []);

  const progress = getProgress();
  const savedJobsSet = useMemo(() => new Set(savedNodes), [savedNodes]);

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)'
      }}>
        <LoadingSpinner size="lg" />
        <div style={{ marginLeft: '16px', fontSize: '18px', color: '#4b5563' }}>
          Loading your competence tree...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)'
      }}>
        <div style={{ color: '#ef4444', fontSize: '18px', marginBottom: '16px' }}>
          ⚠️ Error loading competence tree
        </div>
        <div style={{ color: '#6b7280', marginBottom: '24px' }}>
          {error}
        </div>
        <button
          onClick={reload}
          style={{
            padding: '12px 24px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px'
          }}
        >
          Try Again
        </button>
      </div>
    );
  }

  if (!treeData || nodes.length === 0) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)'
      }}>
        <div style={{ color: '#6b7280', fontSize: '18px' }}>
          No competence tree data available
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      width: '100vw',
      height: '100vh',
      position: 'fixed',
      top: 0,
      left: 0,
      zIndex: 1000,
      display: 'flex', 
      flexDirection: 'column',
      background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%)'
    }}>
      {/* Header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        padding: '12px 24px',
        background: 'rgba(255, 255, 255, 0.98)',
        borderBottom: '1px solid #e2e8f0',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        zIndex: 1001
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={() => window.history.back()}
            style={{
              background: '#6b7280',
              color: 'white',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            ← Back
          </button>
          <h1 style={{ margin: 0, fontSize: '20px', color: '#1f2937', fontWeight: '600' }}>
            Optimized Competence Tree
          </h1>
          
          {/* Search */}
          <input
            type="text"
            placeholder="Search nodes..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              padding: '8px 12px',
              borderRadius: '6px',
              border: '1px solid #d1d5db',
              fontSize: '14px',
              width: '200px'
            }}
          />
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {/* Render Mode Switch */}
          <select
            value={renderMode}
            onChange={(e) => setRenderMode(e.target.value as RenderMode)}
            style={{
              padding: '6px 12px',
              borderRadius: '6px',
              border: '1px solid #d1d5db',
              fontSize: '14px'
            }}
          >
            <option value="hybrid">Auto ({optimalRenderMode})</option>
            <option value="canvas">Canvas</option>
            <option value="virtualized">Virtualized</option>
          </select>

          {/* Performance Monitor Toggle */}
          <button
            onClick={() => setShowPerformanceMonitor(!showPerformanceMonitor)}
            style={{
              background: showPerformanceMonitor ? '#10b981' : '#6b7280',
              color: 'white',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px'
            }}
          >
            📊 Stats
          </button>

          {/* Progress */}
          <div style={{ 
            fontSize: '14px', 
            color: '#6b7280',
            background: '#f3f4f6',
            padding: '6px 12px',
            borderRadius: '6px'
          }}>
            {progress.completed}/{progress.total} completed ({progress.percentage}%)
          </div>

          {/* Zoom Controls */}
          <div style={{ display: 'flex', gap: '0' }}>
            <button onClick={handleZoomOut} style={{ 
              background: '#6b7280', color: 'white', border: 'none',
              padding: '8px 12px', borderRadius: '6px 0 0 6px', cursor: 'pointer' 
            }}>-</button>
            <button onClick={handleZoomIn} style={{ 
              background: '#6b7280', color: 'white', border: 'none',
              padding: '8px 12px', borderRadius: '0 6px 6px 0', cursor: 'pointer' 
            }}>+</button>
          </div>
          
          <button onClick={handleResetView} style={{
            background: '#3b82f6', color: 'white', border: 'none',
            padding: '8px 12px', borderRadius: '6px', cursor: 'pointer'
          }}>
            Reset View
          </button>
        </div>
      </div>

      {/* Tree Visualization */}
      <div style={{ flex: 1, position: 'relative', overflow: 'hidden' }}>
        <Suspense fallback={
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100%' 
          }}>
            <LoadingSpinner size="lg" />
          </div>
        }>
          {renderMode === 'canvas' ? (
            <CanvasTreeRenderer
              nodes={filteredNodes}
              edges={isFullyLoaded ? edges : loadedEdges}
              width={window.innerWidth}
              height={window.innerHeight - 60}
              zoom={zoom}
              panX={panX}
              panY={panY}
              onNodeClick={handleNodeClick}
              onNodeHover={handleNodeHover}
              selectedNodeId={selectedNode?.id}
              savedJobs={savedJobsSet}
            />
          ) : (
            <VirtualizedTreeView
              nodes={filteredNodes}
              edges={isFullyLoaded ? edges : loadedEdges}
              onNodeClick={handleNodeClick}
              onNodeHover={handleNodeHover}
              selectedNodeId={selectedNode?.id}
              savedJobs={savedJobsSet}
              searchQuery={searchQuery}
              nodeTypes={selectedNodeTypes}
            />
          )}
        </Suspense>

        {/* Progressive Loading Overlay */}
        {!isFullyLoaded && (
          <LazyTreeLoader
            nodes={nodes}
            edges={edges}
            onNodesLoaded={handleNodesLoaded}
            onEdgesLoaded={handleEdgesLoaded}
            batchSize={15}
            loadDelay={30}
          />
        )}

        {/* Performance Monitor */}
        {showPerformanceMonitor && (
          <PerformanceMonitor
            nodeCount={nodes.length}
            edgeCount={edges.length}
            visibleNodes={filteredNodes.length}
            showStats={true}
          />
        )}
      </div>

      {/* Node Detail Modal */}
      {showNodeModal && selectedNode && (
        <NodeDetailModal
          node={selectedNode}
          graphId={treeData.graph_id}
          onClose={handleCloseModal}
          onCompleteChallenge={handleCompleteChallenge}
          onSaveJob={() => handleJobSaved(selectedNode.id)}
        />
      )}
    </div>
  );
};

export default OptimizedCompetenceTreeView;