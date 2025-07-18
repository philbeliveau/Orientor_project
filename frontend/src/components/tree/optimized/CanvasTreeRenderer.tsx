import React, { useEffect, useRef, useCallback, useMemo } from 'react';
import { PositionedNode } from '../types';

interface CanvasTreeRendererProps {
  nodes: PositionedNode[];
  edges: { source: string; target: string }[];
  width: number;
  height: number;
  zoom: number;
  panX: number;
  panY: number;
  onNodeClick?: (node: PositionedNode) => void;
  onNodeHover?: (node: PositionedNode | null) => void;
  selectedNodeId?: string;
  savedJobs?: Set<string>;
}

interface ViewportBounds {
  left: number;
  right: number;
  top: number;
  bottom: number;
}

const CanvasTreeRenderer: React.FC<CanvasTreeRendererProps> = ({
  nodes,
  edges,
  width,
  height,
  zoom,
  panX,
  panY,
  onNodeClick,
  onNodeHover,
  selectedNodeId,
  savedJobs = new Set()
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const hoveredNodeRef = useRef<PositionedNode | null>(null);
  const animationFrameRef = useRef<number>();

  // Calculate viewport bounds for culling
  const viewportBounds = useMemo<ViewportBounds>(() => {
    const padding = 200; // Extra padding for smoother scrolling
    return {
      left: (-panX / zoom) - padding,
      right: (-panX + width) / zoom + padding,
      top: (-panY / zoom) - padding,
      bottom: (-panY + height) / zoom + padding
    };
  }, [panX, panY, zoom, width, height]);

  // Viewport culling - only render visible nodes
  const visibleNodes = useMemo(() => {
    return nodes.filter(node => {
      const nodeWidth = node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200);
      const nodeHeight = node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100);
      
      return node.x + nodeWidth/2 >= viewportBounds.left &&
             node.x - nodeWidth/2 <= viewportBounds.right &&
             node.y + nodeHeight/2 >= viewportBounds.top &&
             node.y - nodeHeight/2 <= viewportBounds.bottom;
    });
  }, [nodes, viewportBounds]);

  // Visible edges - only render connections between visible nodes
  const visibleEdges = useMemo(() => {
    const visibleNodeIds = new Set(visibleNodes.map(n => n.id));
    return edges.filter(edge => 
      visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target)
    );
  }, [edges, visibleNodes]);

  // Get node style configuration
  const getNodeStyles = useCallback((node: PositionedNode) => {
    const isSaved = savedJobs.has(node.id);
    
    if (node.type === "occupation") {
      return {
        primary: isSaved ? "#f59e0b" : "#3b82f6",
        secondary: isSaved ? "#fef3c7" : "#dbeafe",
        border: isSaved ? "#d97706" : "#2563eb"
      };
    }
    if (node.type === "skillgroup") {
      return {
        primary: "#10b981",
        secondary: "#d1fae5",
        border: "#059669"
      };
    }
    if (node.is_anchor) {
      return {
        primary: "#8b5cf6",
        secondary: "#ede9fe",
        border: "#7c3aed"
      };
    }
    return {
      primary: "#6b7280",
      secondary: "#f3f4f6",
      border: "#4b5563"
    };
  }, [savedJobs]);

  // Draw a rounded rectangle
  const drawRoundedRect = useCallback((
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    width: number,
    height: number,
    radius: number
  ) => {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  }, []);

  // Draw a single node
  const drawNode = useCallback((ctx: CanvasRenderingContext2D, node: PositionedNode) => {
    const styles = getNodeStyles(node);
    const cardWidth = node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200);
    const cardHeight = node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100);
    const x = node.x - cardWidth/2;
    const y = node.y - cardHeight/2;
    
    if (!node.visible) {
      // Draw hidden node
      ctx.strokeStyle = "#e2e8f0";
      ctx.lineWidth = 2;
      ctx.setLineDash([8, 4]);
      drawRoundedRect(ctx, x, y, cardWidth, cardHeight, 12);
      ctx.stroke();
      ctx.setLineDash([]);
      
      // Draw question mark
      ctx.fillStyle = "#94a3b8";
      ctx.font = "24px system-ui";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("?", node.x, node.y);
      return;
    }

    // Draw card shadow
    ctx.fillStyle = styles.primary + "1A"; // 10% opacity
    drawRoundedRect(ctx, x + 2, y + 2, cardWidth, cardHeight, 12);
    ctx.fill();

    // Draw main card
    ctx.fillStyle = styles.secondary;
    drawRoundedRect(ctx, x, y, cardWidth, cardHeight, 12);
    ctx.fill();
    
    ctx.strokeStyle = styles.border;
    ctx.lineWidth = 2;
    ctx.setLineDash([]);
    drawRoundedRect(ctx, x, y, cardWidth, cardHeight, 12);
    ctx.stroke();

    // Draw icon background
    ctx.fillStyle = styles.primary;
    ctx.beginPath();
    ctx.arc(node.x, y + 30, 24, 0, 2 * Math.PI);
    ctx.fill();

    // Draw icon
    const icon = node.type === "occupation" ? (savedJobs.has(node.id) ? "⭐" : "💼") :
                 node.type === "skillgroup" ? "📚" :
                 node.is_anchor ? "🎯" : "🔧";
    
    ctx.fillStyle = "white";
    ctx.font = "24px system-ui";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(icon, node.x, y + 30);

    // Draw title
    const displayLabel = node.label || node.skill_label || "Unknown Skill";
    const maxLength = node.is_anchor ? 32 : 28;
    const truncatedLabel = displayLabel.length > maxLength ? 
      displayLabel.substring(0, maxLength) + '...' : displayLabel;
    
    ctx.fillStyle = "#1f2937";
    ctx.font = `600 ${node.is_anchor ? 16 : 14}px system-ui`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(truncatedLabel, node.x, y + cardHeight - 40);

    // Draw anchor subtitle
    if (node.is_anchor) {
      ctx.fillStyle = styles.primary;
      ctx.font = "500 12px system-ui";
      ctx.fillText("ANCHOR SKILL", node.x, y + cardHeight - 15);
    }

    // Draw XP badge
    if (node.xp_reward) {
      const badgeX = x + cardWidth - 35;
      const badgeY = y + 5;
      
      ctx.fillStyle = "#10b981";
      drawRoundedRect(ctx, badgeX, badgeY, 30, 16, 8);
      ctx.fill();
      
      ctx.fillStyle = "white";
      ctx.font = "600 9px system-ui";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText(node.xp_reward.toString(), badgeX + 15, badgeY + 8);
    }

    // Draw completion indicator
    if (node.state === 'completed') {
      ctx.fillStyle = "#10b981";
      ctx.beginPath();
      ctx.arc(x + 10, y + 10, 8, 0, 2 * Math.PI);
      ctx.fill();
      
      ctx.fillStyle = "white";
      ctx.font = "600 10px system-ui";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("✓", x + 10, y + 10);
    }

    // Draw saved indicator
    if (savedJobs.has(node.id) && node.type === "occupation") {
      ctx.fillStyle = "#f59e0b";
      ctx.beginPath();
      ctx.arc(x + cardWidth - 10, y + cardHeight - 10, 8, 0, 2 * Math.PI);
      ctx.fill();
      
      ctx.fillStyle = "white";
      ctx.font = "600 10px system-ui";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("★", x + cardWidth - 10, y + cardHeight - 10);
    }

    // Highlight selected node
    if (selectedNodeId === node.id) {
      ctx.strokeStyle = "#3b82f6";
      ctx.lineWidth = 4;
      ctx.setLineDash([]);
      drawRoundedRect(ctx, x - 2, y - 2, cardWidth + 4, cardHeight + 4, 14);
      ctx.stroke();
    }
  }, [getNodeStyles, savedJobs, selectedNodeId, drawRoundedRect]);

  // Draw connection lines
  const drawEdges = useCallback((ctx: CanvasRenderingContext2D) => {
    const nodeMap = new Map(visibleNodes.map(n => [n.id, n]));
    
    visibleEdges.forEach(edge => {
      const sourceNode = nodeMap.get(edge.source);
      const targetNode = nodeMap.get(edge.target);
      
      if (!sourceNode || !targetNode) return;

      // Calculate connection points
      const sourceCardHeight = sourceNode.is_anchor ? 140 : (sourceNode.type === "occupation" ? 120 : 100);
      const targetCardHeight = targetNode.is_anchor ? 140 : (targetNode.type === "occupation" ? 120 : 100);
      
      const startX = sourceNode.x;
      const startY = sourceNode.y + sourceCardHeight/2;
      const endX = targetNode.x;
      const endY = targetNode.y - targetCardHeight/2;

      // Create smooth curve
      const midX = (startX + endX) / 2;
      const midY = (startY + endY) / 2;
      const distance = Math.sqrt((endX - startX)**2 + (endY - startY)**2);
      const curveOffset = Math.min(distance * 0.15, 80);
      const controlY = midY - curveOffset;

      // Determine connection style
      let strokeColor = "#10b981";
      let strokeWidth = 2;
      
      if (sourceNode.is_anchor || targetNode.is_anchor) {
        strokeColor = "#8b5cf6";
        strokeWidth = 3;
      } else if (sourceNode.type === "occupation" || targetNode.type === "occupation") {
        strokeColor = "#3b82f6";
        strokeWidth = 2.5;
      }

      // Draw connection glow
      ctx.strokeStyle = strokeColor + "33"; // 20% opacity
      ctx.lineWidth = strokeWidth + 2;
      ctx.beginPath();
      ctx.moveTo(startX, startY);
      ctx.quadraticCurveTo(midX, controlY, endX, endY);
      ctx.stroke();

      // Draw main connection
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = strokeWidth;
      ctx.beginPath();
      ctx.moveTo(startX, startY);
      ctx.quadraticCurveTo(midX, controlY, endX, endY);
      ctx.stroke();

      // Draw direction indicator
      ctx.fillStyle = strokeColor;
      ctx.beginPath();
      ctx.arc(endX, endY - 8, 4, 0, 2 * Math.PI);
      ctx.fill();
    });
  }, [visibleEdges, visibleNodes]);

  // Main render function
  const render = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);

    // Apply transformation
    ctx.save();
    ctx.translate(panX, panY);
    ctx.scale(zoom, zoom);

    // Draw edges first (behind nodes)
    drawEdges(ctx);

    // Draw nodes
    visibleNodes.forEach(node => drawNode(ctx, node));

    ctx.restore();
  }, [width, height, panX, panY, zoom, drawEdges, drawNode, visibleNodes]);

  // Handle mouse events
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left - panX) / zoom;
    const y = (e.clientY - rect.top - panY) / zoom;

    // Find hovered node
    const hoveredNode = visibleNodes.find(node => {
      const cardWidth = node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200);
      const cardHeight = node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100);
      
      return x >= node.x - cardWidth/2 &&
             x <= node.x + cardWidth/2 &&
             y >= node.y - cardHeight/2 &&
             y <= node.y + cardHeight/2;
    });

    if (hoveredNode !== hoveredNodeRef.current) {
      hoveredNodeRef.current = hoveredNode || null;
      onNodeHover?.(hoveredNode || null);
      canvas.style.cursor = hoveredNode ? 'pointer' : 'grab';
    }
  }, [panX, panY, zoom, visibleNodes, onNodeHover]);

  const handleMouseClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left - panX) / zoom;
    const y = (e.clientY - rect.top - panY) / zoom;

    // Find clicked node
    const clickedNode = visibleNodes.find(node => {
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
  }, [panX, panY, zoom, visibleNodes, onNodeClick]);

  // Render using requestAnimationFrame for smooth performance
  useEffect(() => {
    const renderFrame = () => {
      render();
      animationFrameRef.current = requestAnimationFrame(renderFrame);
    };

    animationFrameRef.current = requestAnimationFrame(renderFrame);

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [render]);

  // Set canvas size
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.scale(dpr, dpr);
    }
  }, [width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{ 
        display: 'block', 
        cursor: 'grab',
        background: 'transparent'
      }}
      onMouseMove={handleMouseMove}
      onClick={handleMouseClick}
    />
  );
};

export default React.memo(CanvasTreeRenderer);