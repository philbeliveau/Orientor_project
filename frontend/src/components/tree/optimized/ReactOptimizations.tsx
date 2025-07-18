import React, { memo, useCallback, useMemo } from 'react';
import { PositionedNode } from '../types';

// Optimized TreeNode component with React.memo
export const OptimizedTreeNode = memo<{
  node: PositionedNode;
  onNodeClick: (node: PositionedNode) => void;
  onNodeHover: (node: PositionedNode | null) => void;
  isSelected: boolean;
  isSaved: boolean;
}>(({ node, onNodeClick, onNodeHover, isSelected, isSaved }) => {
  const handleClick = useCallback(() => {
    onNodeClick(node);
  }, [node, onNodeClick]);

  const handleMouseEnter = useCallback(() => {
    onNodeHover(node);
  }, [node, onNodeHover]);

  const handleMouseLeave = useCallback(() => {
    onNodeHover(null);
  }, [onNodeHover]);

  const nodeStyles = useMemo(() => {
    const baseStyles = {
      position: 'absolute' as const,
      left: node.x - (node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100)),
      top: node.y - (node.is_anchor ? 70 : (node.type === "occupation" ? 60 : 50)),
      width: node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200),
      height: node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100),
      borderRadius: '12px',
      cursor: 'pointer',
      transition: 'transform 0.2s ease',
      transform: isSelected ? 'scale(1.05)' : 'scale(1)',
      zIndex: isSelected ? 10 : 1
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
        (isSaved ? '#fef3c7' : '#dbeafe') :
        node.type === "skillgroup" ? '#d1fae5' :
        node.is_anchor ? '#ede9fe' : '#f3f4f6',
      borderColor: node.type === "occupation" ? 
        (isSaved ? '#d97706' : '#2563eb') :
        node.type === "skillgroup" ? '#059669' :
        node.is_anchor ? '#7c3aed' : '#4b5563'
    };

    return { baseStyles, cardStyles };
  }, [node, isSelected, isSaved]);

  const icon = useMemo(() => {
    if (node.type === "occupation") return isSaved ? "⭐" : "💼";
    if (node.type === "skillgroup") return "📚";
    if (node.is_anchor) return "🎯";
    return "🔧";
  }, [node.type, node.is_anchor, isSaved]);

  const displayLabel = useMemo(() => {
    const label = node.label || node.skill_label || "Unknown";
    const maxLength = node.is_anchor ? 32 : 28;
    return label.length > maxLength ? label.substring(0, maxLength) + '...' : label;
  }, [node.label, node.skill_label, node.is_anchor]);

  return (
    <div
      style={nodeStyles.baseStyles}
      onClick={handleClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <div style={nodeStyles.cardStyles}>
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
          {displayLabel}
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
});

OptimizedTreeNode.displayName = 'OptimizedTreeNode';

// Custom hook for optimized event handlers
export const useOptimizedHandlers = () => {
  const createNodeClickHandler = useCallback((callback: (node: PositionedNode) => void) => {
    return useCallback((node: PositionedNode) => {
      callback(node);
    }, [callback]);
  }, []);

  const createNodeHoverHandler = useCallback((callback: (node: PositionedNode | null) => void) => {
    return useCallback((node: PositionedNode | null) => {
      callback(node);
    }, [callback]);
  }, []);

  return { createNodeClickHandler, createNodeHoverHandler };
};

// Optimized connection renderer
export const OptimizedConnection = memo<{
  sourceNode: PositionedNode;
  targetNode: PositionedNode;
  strokeColor: string;
  strokeWidth: number;
}>(({ sourceNode, targetNode, strokeColor, strokeWidth }) => {
  const pathData = useMemo(() => {
    const startX = sourceNode.x;
    const startY = sourceNode.y + (sourceNode.is_anchor ? 70 : 60);
    const endX = targetNode.x;
    const endY = targetNode.y - (targetNode.is_anchor ? 70 : 60);
    
    const midX = (startX + endX) / 2;
    const midY = (startY + endY) / 2;
    const distance = Math.sqrt((endX - startX)**2 + (endY - startY)**2);
    const curveOffset = Math.min(distance * 0.15, 80);
    const controlY = midY - curveOffset;

    return `M ${startX} ${startY} Q ${midX} ${controlY} ${endX} ${endY}`;
  }, [sourceNode, targetNode]);

  return (
    <path
      d={pathData}
      stroke={strokeColor}
      strokeWidth={strokeWidth}
      fill="none"
      opacity="0.6"
    />
  );
});

OptimizedConnection.displayName = 'OptimizedConnection';

// Performance-optimized list renderer
export const VirtualizedNodeList = memo<{
  nodes: PositionedNode[];
  renderItem: (node: PositionedNode, index: number) => React.ReactNode;
  itemHeight: number;
  containerHeight: number;
  scrollTop: number;
}>(({ nodes, renderItem, itemHeight, containerHeight, scrollTop }) => {
  const visibleItems = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      nodes.length
    );
    
    return nodes.slice(startIndex, endIndex).map((node, index) => ({
      node,
      index: startIndex + index
    }));
  }, [nodes, itemHeight, containerHeight, scrollTop]);

  return (
    <div style={{ position: 'relative', height: nodes.length * itemHeight }}>
      {visibleItems.map(({ node, index }) => (
        <div
          key={node.id}
          style={{
            position: 'absolute',
            top: index * itemHeight,
            left: 0,
            right: 0,
            height: itemHeight
          }}
        >
          {renderItem(node, index)}
        </div>
      ))}
    </div>
  );
});

VirtualizedNodeList.displayName = 'VirtualizedNodeList';

// Debounced search hook
export const useDebouncedSearch = (value: string, delay: number) => {
  const [debouncedValue, setDebouncedValue] = React.useState(value);

  React.useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
};

// Optimized filter hook
export const useOptimizedFilter = (
  nodes: PositionedNode[], 
  searchQuery: string, 
  nodeTypes: Set<string>
) => {
  return useMemo(() => {
    let filtered = nodes;

    // Apply type filter
    if (nodeTypes.size > 0 && nodeTypes.size < 4) {
      filtered = filtered.filter(node => {
        const nodeType = node.is_anchor ? 'anchor' : (node.type || 'skill');
        return nodeTypes.has(nodeType);
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
  }, [nodes, searchQuery, nodeTypes]);
};

export default {
  OptimizedTreeNode,
  OptimizedConnection,
  VirtualizedNodeList,
  useOptimizedHandlers,
  useDebouncedSearch,
  useOptimizedFilter
};