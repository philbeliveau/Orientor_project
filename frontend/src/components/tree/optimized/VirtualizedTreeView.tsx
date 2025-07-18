import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import { PositionedNode } from '../types';

interface VirtualizedTreeViewProps {
  nodes: PositionedNode[];
  edges: { source: string; target: string }[];
  onNodeClick?: (node: PositionedNode) => void;
  onNodeHover?: (node: PositionedNode | null) => void;
  selectedNodeId?: string;
  savedJobs?: Set<string>;
  searchQuery?: string;
  nodeTypes?: Set<string>;
}

interface ViewportState {
  zoom: number;
  panX: number;
  panY: number;
  width: number;
  height: number;
}

const VirtualizedTreeView: React.FC<VirtualizedTreeViewProps> = ({
  nodes,
  edges,
  onNodeClick,
  onNodeHover,
  selectedNodeId,
  savedJobs = new Set(),
  searchQuery = '',
  nodeTypes = new Set(['occupation', 'skillgroup', 'skill', 'anchor'])
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [viewport, setViewport] = useState<ViewportState>({
    zoom: 1,
    panX: 0,
    panY: 0,
    width: 0,
    height: 0
  });
  const [isDragging, setIsDragging] = useState(false);
  const [lastMousePos, setLastMousePos] = useState({ x: 0, y: 0 });
  const [hoveredNode, setHoveredNode] = useState<PositionedNode | null>(null);

  // Update viewport dimensions
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const { width, height } = containerRef.current.getBoundingClientRect();
        setViewport(prev => ({ ...prev, width, height }));
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Filter nodes based on search and type filters
  const filteredNodes = useMemo(() => {
    let filtered = nodes;

    // Filter by type
    if (nodeTypes.size > 0 && nodeTypes.size < 4) {
      filtered = filtered.filter(node => {
        const nodeType = node.is_anchor ? 'anchor' : (node.type || 'skill');
        return nodeTypes.has(nodeType);
      });
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(node => {
        const label = (node.label || node.skill_label || '').toLowerCase();
        const challenge = (node.challenge || '').toLowerCase();
        return label.includes(query) || challenge.includes(query);
      });
    }

    return filtered;
  }, [nodes, nodeTypes, searchQuery]);

  // Viewport culling - only render visible nodes
  const visibleNodes = useMemo(() => {
    const { zoom, panX, panY, width, height } = viewport;
    
    if (filteredNodes.length === 0 || width === 0 || height === 0) return [];

    const padding = 300; // Large padding for smooth scrolling
    const leftBound = (-panX / zoom) - padding;
    const rightBound = (-panX + width) / zoom + padding;
    const topBound = (-panY / zoom) - padding;
    const bottomBound = (-panY + height) / zoom + padding;

    return filteredNodes.filter(node => {
      const nodeWidth = node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200);
      const nodeHeight = node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100);
      
      return node.x + nodeWidth/2 >= leftBound &&
             node.x - nodeWidth/2 <= rightBound &&
             node.y + nodeHeight/2 >= topBound &&
             node.y - nodeHeight/2 <= bottomBound;
    });
  }, [filteredNodes, viewport]);

  // Visible edges
  const visibleEdges = useMemo(() => {
    const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
    return edges.filter(edge => 
      visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target)
    ).slice(0, 100); // Limit connections for performance
  }, [edges, visibleNodes]);

  // Level-of-detail system
  const lodNodes = useMemo(() => {
    const { zoom } = viewport;
    
    if (zoom > 0.8) {
      return visibleNodes; // Full detail
    } else if (zoom > 0.4) {
      // Medium detail - show important nodes only
      return visibleNodes.filter(node => 
        node.is_anchor || node.type === 'occupation'
      );
    } else {
      // Low detail - anchors only
      return visibleNodes.filter(node => node.is_anchor);
    }
  }, [visibleNodes, viewport.zoom]);

  // Pan and zoom handlers
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault();
    
    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;

    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    setViewport(prev => {
      const zoomStep = 0.1;
      const zoomDirection = e.deltaY > 0 ? -1 : 1;
      const newZoom = Math.max(0.1, Math.min(3, prev.zoom + (zoomStep * zoomDirection)));
      
      if (newZoom !== prev.zoom) {
        const zoomRatio = newZoom / prev.zoom;
        const deltaX = (mouseX - prev.panX) * (1 - zoomRatio);
        const deltaY = (mouseY - prev.panY) * (1 - zoomRatio);
        
        return {
          ...prev,
          zoom: newZoom,
          panX: prev.panX + deltaX,
          panY: prev.panY + deltaY
        };
      }
      return prev;
    });
  }, []);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setIsDragging(true);
    setLastMousePos({ x: e.clientX, y: e.clientY });
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (isDragging) {
      const deltaX = e.clientX - lastMousePos.x;
      const deltaY = e.clientY - lastMousePos.y;
      
      setViewport(prev => ({
        ...prev,
        panX: prev.panX + deltaX,
        panY: prev.panY + deltaY
      }));
      
      setLastMousePos({ x: e.clientX, y: e.clientY });
    } else {
      // Handle hover detection
      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect) return;

      const x = (e.clientX - rect.left - viewport.panX) / viewport.zoom;
      const y = (e.clientY - rect.top - viewport.panY) / viewport.zoom;

      const hoveredNode = lodNodes.find(node => {
        const cardWidth = node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200);
        const cardHeight = node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100);
        
        return x >= node.x - cardWidth/2 &&
               x <= node.x + cardWidth/2 &&
               y >= node.y - cardHeight/2 &&
               y <= node.y + cardHeight/2;
      });

      if (hoveredNode !== hoveredNode) {
        setHoveredNode(hoveredNode || null);
        onNodeHover?.(hoveredNode || null);
      }
    }
  }, [isDragging, lastMousePos, viewport, lodNodes, onNodeHover]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
  }, []);

  const handleClick = useCallback((e: React.MouseEvent) => {
    if (isDragging) return;

    const rect = containerRef.current?.getBoundingClientRect();
    if (!rect) return;

    const x = (e.clientX - rect.left - viewport.panX) / viewport.zoom;
    const y = (e.clientY - rect.top - viewport.panY) / viewport.zoom;

    const clickedNode = lodNodes.find(node => {
      const cardWidth = node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200);
      const cardHeight = node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100);
      
      return x >= node.x - cardWidth/2 &&
             x <= node.x + cardWidth/2 &&
             y >= node.y - cardHeight/2 &&
             y <= node.y + cardHeight/2;
    });

    if (clickedNode) {
      onNodeClick?.(clickedNode);
    }
  }, [isDragging, viewport, lodNodes, onNodeClick]);

  // Reset view function
  const resetView = useCallback(() => {
    setViewport(prev => ({
      ...prev,
      zoom: 1,
      panX: 0,
      panY: 0
    }));
  }, []);

  // Render node as optimized div
  const renderNode = useCallback((node: PositionedNode) => {
    const styles = {
      position: 'absolute' as const,
      left: node.x - (node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100)),
      top: node.y - (node.is_anchor ? 70 : (node.type === "occupation" ? 60 : 50)),
      width: node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200),
      height: node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100),
      borderRadius: '12px',
      cursor: 'pointer',
      transition: 'transform 0.2s ease',
      transform: selectedNodeId === node.id ? 'scale(1.05)' : 'scale(1)',
      zIndex: selectedNodeId === node.id ? 10 : 1
    };

    const cardStyles = {
      width: '100%',
      height: '100%',
      borderRadius: '12px',
      padding: '12px',
      display: 'flex',
      flexDirection: 'column' as const,
      alignItems: 'center',
      justifyContent: 'center',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
      border: '2px solid',
      background: node.type === "occupation" ? 
        (savedJobs.has(node.id) ? '#fef3c7' : '#dbeafe') :
        node.type === "skillgroup" ? '#d1fae5' :
        node.is_anchor ? '#ede9fe' : '#f3f4f6',
      borderColor: node.type === "occupation" ? 
        (savedJobs.has(node.id) ? '#d97706' : '#2563eb') :
        node.type === "skillgroup" ? '#059669' :
        node.is_anchor ? '#7c3aed' : '#4b5563'
    };

    const icon = node.type === "occupation" ? 
      (savedJobs.has(node.id) ? "⭐" : "💼") :
      node.type === "skillgroup" ? "📚" :
      node.is_anchor ? "🎯" : "🔧";

    return (
      <div
        key={node.id}
        style={styles}
        onClick={() => onNodeClick?.(node)}
        onMouseEnter={() => onNodeHover?.(node)}
        onMouseLeave={() => onNodeHover?.(null)}
      >
        <div style={cardStyles}>
          <div style={{ fontSize: '24px', marginBottom: '8px' }}>
            {icon}
          </div>
          <div style={{ 
            fontSize: node.is_anchor ? '16px' : '14px',
            fontWeight: '600',
            textAlign: 'center',
            color: '#1f2937',
            lineHeight: '1.2'
          }}>
            {(node.label || node.skill_label || "Unknown").substring(0, 
              node.is_anchor ? 32 : 28
            )}
          </div>
          {node.is_anchor && (
            <div style={{ 
              fontSize: '12px',
              color: '#8b5cf6',
              fontWeight: '500',
              marginTop: '4px'
            }}>
              ANCHOR SKILL
            </div>
          )}
          {node.state === 'completed' && (
            <div style={{
              position: 'absolute',
              top: '8px',
              left: '8px',
              width: '16px',
              height: '16px',
              borderRadius: '50%',
              background: '#10b981',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '10px'
            }}>
              ✓
            </div>
          )}
        </div>
      </div>
    );
  }, [selectedNodeId, savedJobs, onNodeClick, onNodeHover]);

  return (
    <div
      ref={containerRef}
      style={{
        width: '100%',
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
        background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%)',
        cursor: isDragging ? 'grabbing' : 'grab'
      }}
      onWheel={handleWheel}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onClick={handleClick}
    >
      {/* Render connections as SVG overlay */}
      <svg
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
          zIndex: 0
        }}
      >
        <g transform={`translate(${viewport.panX}, ${viewport.panY}) scale(${viewport.zoom})`}>
          {visibleEdges.map((edge, index) => {
            const sourceNode = lodNodes.find(n => n.id === edge.source);
            const targetNode = lodNodes.find(n => n.id === edge.target);
            
            if (!sourceNode || !targetNode) return null;

            const startX = sourceNode.x;
            const startY = sourceNode.y + (sourceNode.is_anchor ? 70 : 60);
            const endX = targetNode.x;
            const endY = targetNode.y - (targetNode.is_anchor ? 70 : 60);
            
            const midX = (startX + endX) / 2;
            const midY = (startY + endY) / 2;
            const distance = Math.sqrt((endX - startX)**2 + (endY - startY)**2);
            const curveOffset = Math.min(distance * 0.15, 80);
            const controlY = midY - curveOffset;

            const strokeColor = sourceNode.is_anchor || targetNode.is_anchor ? 
              '#8b5cf6' : sourceNode.type === "occupation" || targetNode.type === "occupation" ? 
              '#3b82f6' : '#10b981';

            return (
              <path
                key={`${edge.source}-${edge.target}-${index}`}
                d={`M ${startX} ${startY} Q ${midX} ${controlY} ${endX} ${endY}`}
                stroke={strokeColor}
                strokeWidth="2"
                fill="none"
                opacity="0.6"
              />
            );
          })}
        </g>
      </svg>

      {/* Render nodes */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          transform: `translate(${viewport.panX}px, ${viewport.panY}px) scale(${viewport.zoom})`,
          transformOrigin: '0 0',
          width: '100%',
          height: '100%'
        }}
      >
        {lodNodes.map(renderNode)}
      </div>

      {/* Controls */}
      <div style={{
        position: 'absolute',
        bottom: '20px',
        right: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        zIndex: 1000
      }}>
        <button
          onClick={() => setViewport(prev => ({ ...prev, zoom: Math.min(3, prev.zoom + 0.2) }))}
          style={{
            padding: '8px 12px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          +
        </button>
        <button
          onClick={() => setViewport(prev => ({ ...prev, zoom: Math.max(0.1, prev.zoom - 0.2) }))}
          style={{
            padding: '8px 12px',
            background: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          -
        </button>
        <button
          onClick={resetView}
          style={{
            padding: '8px 12px',
            background: '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            fontSize: '12px'
          }}
        >
          Reset
        </button>
      </div>

      {/* Performance stats */}
      <div style={{
        position: 'absolute',
        top: '10px',
        left: '10px',
        background: 'rgba(0, 0, 0, 0.8)',
        color: 'white',
        padding: '8px 12px',
        borderRadius: '6px',
        fontSize: '12px',
        zIndex: 1000
      }}>
        Rendering: {lodNodes.length}/{filteredNodes.length} nodes
        <br />
        Zoom: {Math.round(viewport.zoom * 100)}%
      </div>
    </div>
  );
};

export default React.memo(VirtualizedTreeView);