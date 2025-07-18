import React, { useState, useCallback, useMemo } from 'react';
import { PositionedNode } from '../types';

interface UltraLightFallbackProps {
  nodes: PositionedNode[];
  edges: { source: string; target: string }[];
  onNodeClick: (node: PositionedNode) => void;
  onNodeHover: (node: PositionedNode | null) => void;
  selectedNodeId?: string;
  savedJobs: Set<string>;
  zoom: number;
  panX: number;
  panY: number;
  onZoom: (delta: number) => void;
  onPan: (deltaX: number, deltaY: number) => void;
}

/**
 * Ultra-lightweight fallback renderer for extreme performance
 * Uses minimal DOM elements and simple CSS transforms
 */
const UltraLightFallback: React.FC<UltraLightFallbackProps> = ({
  nodes,
  edges,
  onNodeClick,
  onNodeHover,
  selectedNodeId,
  savedJobs,
  zoom,
  panX,
  panY,
  onZoom,
  onPan
}) => {
  // Ultra-minimal node rendering with absolute positioning
  const renderNode = useCallback((node: PositionedNode, index: number) => {
    const isSelected = selectedNodeId === node.id;
    const isSaved = savedJobs.has(node.id);
    
    // Extreme simplification - just colored circles
    const size = node.is_anchor ? 20 : 12;
    const color = node.is_anchor ? '#8b5cf6' : 
                  node.type === 'occupation' ? (isSaved ? '#f59e0b' : '#3b82f6') :
                  node.type === 'skillgroup' ? '#10b981' : '#6b7280';
    
    return (
      <div
        key={node.id}
        style={{
          position: 'absolute',
          left: node.x - size/2,
          top: node.y - size/2,
          width: size,
          height: size,
          borderRadius: '50%',
          backgroundColor: color,
          border: isSelected ? '2px solid #3b82f6' : 'none',
          cursor: 'pointer',
          boxShadow: isSelected ? '0 0 10px rgba(59, 130, 246, 0.5)' : 'none',
          transition: 'none', // Remove transitions for performance
          zIndex: isSelected ? 10 : 1
        }}
        onClick={() => onNodeClick(node)}
        onMouseEnter={() => onNodeHover(node)}
        onMouseLeave={() => onNodeHover(null)}
        title={node.label || node.skill_label || 'Unknown'}
      />
    );
  }, [selectedNodeId, savedJobs, onNodeClick, onNodeHover]);

  // Ultra-minimal edge rendering
  const renderEdge = useCallback((edge: { source: string; target: string }, index: number) => {
    const sourceNode = nodes.find(n => n.id === edge.source);
    const targetNode = nodes.find(n => n.id === edge.target);
    
    if (!sourceNode || !targetNode) return null;
    
    const dx = targetNode.x - sourceNode.x;
    const dy = targetNode.y - sourceNode.y;
    const length = Math.sqrt(dx * dx + dy * dy);
    const angle = Math.atan2(dy, dx) * 180 / Math.PI;
    
    return (
      <div
        key={`${edge.source}-${edge.target}`}
        style={{
          position: 'absolute',
          left: sourceNode.x,
          top: sourceNode.y,
          width: length,
          height: '1px',
          backgroundColor: '#9ca3af',
          transformOrigin: '0 0',
          transform: `rotate(${angle}deg)`,
          opacity: 0.3,
          zIndex: 0
        }}
      />
    );
  }, [nodes]);

  // Note: Mouse events are now handled by parent component for consistency

  // Memoize rendered elements
  const renderedNodes = useMemo(() => {
    return nodes.map(renderNode);
  }, [nodes, renderNode]);

  const renderedEdges = useMemo(() => {
    return edges.slice(0, 20).map(renderEdge); // Limit edges for performance
  }, [edges, renderEdge]);

  return (
    <div
      style={{
        width: '100%',
        height: '100%',
        position: 'relative',
        overflow: 'hidden',
        background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)'
      }}
    >
      {/* Ultra-minimal rendering container */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          transform: `translate(${panX}px, ${panY}px) scale(${zoom})`,
          transformOrigin: '0 0',
          width: '100%',
          height: '100%'
        }}
      >
        {/* Render edges first */}
        {renderedEdges}
        
        {/* Render nodes */}
        {renderedNodes}
      </div>

      {/* Performance info */}
      <div style={{
        position: 'absolute',
        bottom: '10px',
        left: '10px',
        background: 'rgba(0, 0, 0, 0.8)',
        color: 'white',
        padding: '4px 8px',
        borderRadius: '4px',
        fontSize: '12px',
        pointerEvents: 'none'
      }}>
        🔥 Ultra-Light Mode: {nodes.length} nodes, {Math.min(edges.length, 20)} edges
      </div>
    </div>
  );
};

export default React.memo(UltraLightFallback);