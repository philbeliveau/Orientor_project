import React, { useState, useEffect, useCallback, useMemo, useRef, Suspense } from 'react';
import { useCompetenceTree } from '../useCompetenceTree';
import { PositionedNode } from '../types';
import { getWorkerManager } from './WorkerManager';
import { getExtremeCache } from './ExtremeCache';
import { SpatialIndex, PerformanceTracker, ThrottledEventHandler } from './SpatialIndex';
import LoadingSpinner from '../../ui/LoadingSpinner';
import NodeDetailModal from '../NodeDetailModal';

// Lazy load heavy components
const WebGLTreeRenderer = React.lazy(() => import('./WebGLTreeRenderer'));
const UltraLightFallback = React.lazy(() => import('./UltraLightFallback'));

interface ExtremeCompetenceTreeViewProps {
  graphId: string;
}

type RenderMode = 'webgl' | 'ultra-light' | 'minimal';

const ExtremeCompetenceTreeView: React.FC<ExtremeCompetenceTreeViewProps> = ({ graphId }) => {
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
    getProgress
  } = useCompetenceTree(graphId);

  // Performance tracking
  const performanceTracker = useRef(new PerformanceTracker());
  const spatialIndex = useRef(new SpatialIndex(300)); // Smaller grid for better performance
  const workerManager = useRef(getWorkerManager());
  const extremeCache = useRef(getExtremeCache());
  const mountedRef = useRef(true);

  // UI State
  const [selectedNode, setSelectedNode] = useState<PositionedNode | null>(null);
  const [showNodeModal, setShowNodeModal] = useState(false);
  const [hoveredNode, setHoveredNode] = useState<PositionedNode | null>(null);
  const [renderMode, setRenderMode] = useState<RenderMode>('webgl');

  // Viewport State
  const [zoom, setZoom] = useState(1);
  const [panX, setPanX] = useState(0);
  const [panY, setPanY] = useState(0);

  // Performance State
  const [fps, setFps] = useState(60);
  const [visibleNodeCount, setVisibleNodeCount] = useState(0);
  const [showPerformanceWarning, setShowPerformanceWarning] = useState(false);

  // Extreme optimization state
  const [positionedNodes, setPositionedNodes] = useState<PositionedNode[]>([]);
  const [isLoadingFromCache, setIsLoadingFromCache] = useState(false);
  const [cacheHitRate, setCacheHitRate] = useState(0);

  // Auto-detect optimal render mode based on performance
  useEffect(() => {
    const checkPerformance = () => {
      if (!mountedRef.current) return;
      
      const avgFPS = performanceTracker.current.getAverageFPS();
      setFps(avgFPS);
      
      if (avgFPS < 20) {
        setRenderMode('minimal');
        setShowPerformanceWarning(true);
      } else if (avgFPS < 35) {
        setRenderMode('ultra-light');
        setShowPerformanceWarning(true);
      } else {
        setRenderMode('webgl');
        setShowPerformanceWarning(false);
      }
    };

    const interval = setInterval(checkPerformance, 1000);
    return () => clearInterval(interval);
  }, []);

  // Extreme caching and loading optimization
  useEffect(() => {
    if (!treeData || !nodes.length) return;

    const loadWithExtremeOptimization = async () => {
      setIsLoadingFromCache(true);
      
      try {
        // Check cache first
        const cachedPositions = await extremeCache.current.getCachedNodePositions(graphId);
        
        if (cachedPositions && cachedPositions.length === nodes.length) {
          console.log('🚀 Using cached positions - instant load!');
          setPositionedNodes(cachedPositions);
          spatialIndex.current.updateIndex(cachedPositions);
          setIsLoadingFromCache(false);
          return;
        }

        // Use Web Worker for heavy calculations
        const centerX = typeof window !== 'undefined' ? window.innerWidth / 2 : 800;
        const centerY = typeof window !== 'undefined' ? window.innerHeight / 2 : 600;
        
        const result = await workerManager.current.calculateLayout(
          nodes,
          edges,
          centerX,
          centerY
        );

        if (mountedRef.current) {
          setPositionedNodes(result.nodes);
          spatialIndex.current.updateIndex(result.nodes);
          
          // Cache the results
          await extremeCache.current.cacheNodePositions(graphId, result.nodes);
          await extremeCache.current.cacheTreeData(graphId, treeData);
          
          console.log(`⚡ Layout calculated in ${result.calculateTime}ms (cached: ${result.cached})`);
        }
        
      } catch (error) {
        console.error('Layout calculation failed:', error);
        // Fallback to simple positioning
        const fallbackPositions = nodes.map((node, index) => ({
          ...node,
          x: 400 + (index % 10) * 200,
          y: 300 + Math.floor(index / 10) * 150
        }));
        setPositionedNodes(fallbackPositions);
      } finally {
        setIsLoadingFromCache(false);
      }
    };

    loadWithExtremeOptimization();
  }, [treeData, nodes, edges, graphId]);

  // Ultra-fast viewport culling with spatial indexing
  const visibleNodes = useMemo(() => {
    if (!positionedNodes.length) return [];
    
    performanceTracker.current.startFrame();
    
    const bounds = {
      left: (-panX / zoom) - 200,
      right: (-panX + (window.innerWidth || 1200)) / zoom + 200,
      top: (-panY / zoom) - 200,
      bottom: (-panY + (window.innerHeight || 800)) / zoom + 200
    };

    const visible = spatialIndex.current.getNodesInBounds(bounds);
    
    // Ultra-aggressive culling based on render mode
    const maxNodes = renderMode === 'minimal' ? 10 : 
                     renderMode === 'ultra-light' ? 15 : 25;
    
    const culled = visible.slice(0, maxNodes);
    setVisibleNodeCount(culled.length);
    
    performanceTracker.current.endFrame();
    
    return culled;
  }, [positionedNodes, panX, panY, zoom, renderMode]);

  // Throttled event handlers for maximum performance
  const throttledNodeHover = useRef(new ThrottledEventHandler((node: PositionedNode | null) => {
    if (mountedRef.current) {
      setHoveredNode(node);
    }
  }, 50));

  const handleNodeClick = useCallback((node: PositionedNode) => {
    setSelectedNode(node);
    setShowNodeModal(true);
  }, []);

  const handleNodeHover = useCallback((node: PositionedNode | null) => {
    throttledNodeHover.current.handle(node);
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

  // Smooth and robust zoom system with mouse wheel support
  const handleZoom = useCallback((delta: number, mouseX?: number, mouseY?: number) => {
    setZoom(prev => {
      // Much gentler zoom increments with better limits
      const zoomFactor = delta > 0 ? 1.08 : 0.92; // Even more gentle
      let newZoom = prev * zoomFactor;
      
      // Better zoom limits with smoother boundaries
      const minZoom = 0.1;
      const maxZoom = 5;
      
      // Smooth resistance near boundaries
      if (newZoom < minZoom) {
        newZoom = minZoom + (newZoom - minZoom) * 0.1;
      } else if (newZoom > maxZoom) {
        newZoom = maxZoom + (newZoom - maxZoom) * 0.1;
      }
      
      newZoom = Math.max(minZoom, Math.min(maxZoom, newZoom));
      
      // Zoom towards mouse position for better UX
      if (mouseX !== undefined && mouseY !== undefined && Math.abs(newZoom - prev) > 0.001) {
        const zoomRatio = newZoom / prev;
        const deltaX = (mouseX - panX) * (1 - zoomRatio);
        const deltaY = (mouseY - panY) * (1 - zoomRatio);
        
        setPanX(prevPanX => prevPanX + deltaX);
        setPanY(prevPanY => prevPanY + deltaY);
      }
      
      return newZoom;
    });
  }, [panX, panY]);

  const handlePan = useCallback((deltaX: number, deltaY: number) => {
    setPanX(prev => prev + deltaX);
    setPanY(prev => prev + deltaY);
  }, []);

  // Throttled wheel handler for smooth zooming
  const wheelHandler = useRef(new ThrottledEventHandler((e: WheelEvent) => {
    e.preventDefault();
    
    // Get mouse position relative to canvas
    const rect = (e.target as HTMLElement).getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    // Determine zoom direction with much gentler increments
    const delta = e.deltaY < 0 ? 1 : -1;
    handleZoom(delta, mouseX, mouseY);
  }, 16)); // 60fps throttling

  // Mouse drag panning
  const [isDragging, setIsDragging] = useState(false);
  const [lastMousePos, setLastMousePos] = useState({ x: 0, y: 0 });
  
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setIsDragging(true);
    setLastMousePos({ x: e.clientX, y: e.clientY });
  }, []);
  
  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging) return;
    
    const deltaX = e.clientX - lastMousePos.x;
    const deltaY = e.clientY - lastMousePos.y;
    
    handlePan(deltaX, deltaY);
    setLastMousePos({ x: e.clientX, y: e.clientY });
  }, [isDragging, lastMousePos, handlePan]);
  
  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleResetView = useCallback(() => {
    // Smooth transition to reset view
    const startZoom = zoom;
    const startPanX = panX;
    const startPanY = panY;
    const targetZoom = 1;
    const targetPanX = 0;
    const targetPanY = 0;
    
    let animationId: number;
    let startTime: number;
    const duration = 500; // 500ms animation
    
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      // Smooth easing function
      const easeOut = 1 - Math.pow(1 - progress, 3);
      
      setZoom(startZoom + (targetZoom - startZoom) * easeOut);
      setPanX(startPanX + (targetPanX - startPanX) * easeOut);
      setPanY(startPanY + (targetPanY - startPanY) * easeOut);
      
      if (progress < 1) {
        animationId = requestAnimationFrame(animate);
      }
    };
    
    animationId = requestAnimationFrame(animate);
    
    // Cleanup function
    return () => {
      if (animationId) {
        cancelAnimationFrame(animationId);
      }
    };
  }, [zoom, panX, panY]);

  // Update cache statistics
  useEffect(() => {
    const updateCacheStats = async () => {
      if (!mountedRef.current) return;
      
      const stats = extremeCache.current.getStats();
      setCacheHitRate(stats.cacheHitRate);
    };

    const interval = setInterval(updateCacheStats, 2000);
    return () => clearInterval(interval);
  }, []);

  // Keyboard shortcuts for navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Prevent default if we handle the key
      let handled = false;
      
      switch (e.key) {
        case '+':
        case '=':
          handleZoom(1);
          handled = true;
          break;
        case '-':
        case '_':
          handleZoom(-1);
          handled = true;
          break;
        case '0':
          if (e.ctrlKey || e.metaKey) {
            handleResetView();
            handled = true;
          }
          break;
        case 'ArrowUp':
          handlePan(0, 50);
          handled = true;
          break;
        case 'ArrowDown':
          handlePan(0, -50);
          handled = true;
          break;
        case 'ArrowLeft':
          handlePan(50, 0);
          handled = true;
          break;
        case 'ArrowRight':
          handlePan(-50, 0);
          handled = true;
          break;
      }
      
      if (handled) {
        e.preventDefault();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [handleZoom, handlePan, handleResetView]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      mountedRef.current = false;
    };
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
        flexDirection: 'column',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)'
      }}>
        <LoadingSpinner size="lg" />
        <div style={{ marginTop: '16px', fontSize: '18px', color: '#4b5563' }}>
          ⚡ Loading with extreme optimization...
        </div>
        {isLoadingFromCache && (
          <div style={{ marginTop: '8px', fontSize: '14px', color: '#6b7280' }}>
            🚀 Checking cache for instant load...
          </div>
        )}
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
          🔄 Retry with Extreme Optimization
        </button>
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
      {/* Ultra-minimal header */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        padding: '8px 16px',
        background: 'rgba(255, 255, 255, 0.95)',
        borderBottom: '1px solid #e2e8f0',
        zIndex: 1001
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <button
            onClick={() => window.history.back()}
            style={{
              background: '#6b7280',
              color: 'white',
              border: 'none',
              padding: '6px 10px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
          >
            ← Back
          </button>
          <h1 style={{ margin: 0, fontSize: '16px', color: '#1f2937' }}>
            🚀 Extreme Performance Tree
          </h1>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {/* Performance indicator */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            background: fps >= 45 ? '#10b981' : fps >= 30 ? '#f59e0b' : '#ef4444',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '12px'
          }}>
            <span>{fps} FPS</span>
            <span>•</span>
            <span>{visibleNodeCount} nodes</span>
          </div>

          {/* Cache indicator */}
          <div style={{
            background: cacheHitRate > 50 ? '#10b981' : '#6b7280',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '12px'
          }}>
            📦 {Math.round(cacheHitRate)}% cache
          </div>

          {/* Render mode indicator */}
          <div style={{
            background: renderMode === 'webgl' ? '#3b82f6' : 
                       renderMode === 'ultra-light' ? '#f59e0b' : '#ef4444',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '12px'
          }}>
            {renderMode === 'webgl' ? '🚀 WebGL' : 
             renderMode === 'ultra-light' ? '⚡ Ultra' : '🔥 Minimal'}
          </div>

          {/* Controls with better zoom increments */}
          <button 
            onClick={() => handleZoom(1)} 
            style={{ 
              padding: '6px 12px', 
              fontSize: '14px', 
              background: '#3b82f6', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer',
              marginLeft: '4px'
            }}
          >
            +
          </button>
          <button 
            onClick={() => handleZoom(-1)} 
            style={{ 
              padding: '6px 12px', 
              fontSize: '14px', 
              background: '#3b82f6', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer',
              marginLeft: '4px'
            }}
          >
            -
          </button>
          <button 
            onClick={handleResetView} 
            style={{ 
              padding: '6px 12px', 
              fontSize: '12px', 
              background: '#6b7280', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer',
              marginLeft: '4px'
            }}
          >
            Reset
          </button>
          
          {/* Zoom level indicator */}
          <div style={{
            background: '#f3f4f6',
            color: '#374151',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '12px',
            marginLeft: '8px'
          }}>
            {Math.round(zoom * 100)}%
          </div>
          
          {/* Help indicator */}
          <div style={{
            background: '#374151',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '11px',
            marginLeft: '8px',
            opacity: 0.8
          }}>
            Wheel: Zoom • Drag: Pan • +/-: Zoom • Arrows: Navigate • Ctrl+0: Reset
          </div>
        </div>
      </div>

      {/* Performance warning */}
      {showPerformanceWarning && (
        <div style={{
          position: 'absolute',
          top: '60px',
          left: '50%',
          transform: 'translateX(-50%)',
          background: 'rgba(239, 68, 68, 0.9)',
          color: 'white',
          padding: '8px 16px',
          borderRadius: '6px',
          fontSize: '14px',
          zIndex: 1002
        }}>
          ⚠️ Performance mode: {renderMode} (FPS: {fps})
        </div>
      )}

      {/* Ultra-optimized tree visualization with improved controls */}
      <div 
        style={{ 
          flex: 1, 
          position: 'relative', 
          overflow: 'hidden',
          cursor: isDragging ? 'grabbing' : 'grab'
        }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={(e) => wheelHandler.current.handle(e.nativeEvent)}
      >
        <Suspense fallback={
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            height: '100%',
            background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)'
          }}>
            <LoadingSpinner size="lg" />
          </div>
        }>
          {renderMode === 'webgl' ? (
            <WebGLTreeRenderer
              nodes={visibleNodes}
              edges={edges}
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
            <UltraLightFallback
              nodes={visibleNodes}
              edges={edges}
              onNodeClick={handleNodeClick}
              onNodeHover={handleNodeHover}
              selectedNodeId={selectedNode?.id}
              savedJobs={savedJobsSet}
              zoom={zoom}
              panX={panX}
              panY={panY}
              onZoom={handleZoom}
              onPan={handlePan}
            />
          )}
        </Suspense>
      </div>

      {/* Node detail modal */}
      {showNodeModal && selectedNode && (
        <NodeDetailModal
          node={selectedNode}
          graphId={treeData?.graph_id || ''}
          onClose={handleCloseModal}
          onCompleteChallenge={handleCompleteChallenge}
          onSaveJob={() => handleJobSaved(selectedNode.id)}
        />
      )}
    </div>
  );
};

export default ExtremeCompetenceTreeView;