import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';

// Importez les styles existants si nécessaire
import '../tree/treestyles.css';

// Composant pour afficher un défi
import ChallengeCard from '../ui/ChallengeCard';
import NodeDetailModal from './NodeDetailModal';
import LoadingSpinner from '../ui/LoadingSpinner';
import { getCompetenceTree, completeChallenge } from '../../services/competenceTreeService';

// Types personnalisés
interface CompetenceNode {
  id: string;
  skill_id?: string;
  skill_label?: string;
  label?: string;
  type?: string;
  challenge?: string;
  xp_reward?: number;
  visible?: boolean;
  revealed?: boolean;
  state?: 'locked' | 'available' | 'completed' | 'hidden';
  notes?: string;
  is_anchor?: boolean;
  depth?: number;
  metadata?: any;
}

interface CompetenceTreeData {
  nodes: CompetenceNode[];
  edges: { source: string; target: string; weight?: number; type?: string }[];
  graph_id: string;
}

interface CompetenceTreeViewProps {
  graphId: string;
}

interface PositionedNode extends CompetenceNode {
  x: number;
  y: number;
}

// Custom Node Component for SVG rendering with modern card design
const TreeNode: React.FC<{
  node: PositionedNode;
  onComplete: (nodeId: string) => void;
  onNodeClick: (node: PositionedNode) => void;
  isSaved?: boolean;
}> = ({ node, onComplete, onNodeClick, isSaved = false }) => {
  const [showTooltip, setShowTooltip] = React.useState(false);
  const displayLabel = node.label || node.skill_label || "Unknown Skill";
  
  // Modern, semantic color scheme
  const getNodeStyles = () => {
    if (node.type === "occupation") {
      return {
        primary: isSaved ? "#f59e0b" : "#3b82f6", // Amber for saved, blue for occupations
        secondary: isSaved ? "#fef3c7" : "#dbeafe", // Light backgrounds
        text: "#1f2937",
        border: isSaved ? "#d97706" : "#2563eb",
        shadow: isSaved ? "0 4px 20px rgba(245, 158, 11, 0.3)" : "0 4px 20px rgba(59, 130, 246, 0.3)"
      };
    }
    if (node.type === "skillgroup") {
      return {
        primary: "#10b981", // Emerald for skill groups
        secondary: "#d1fae5",
        text: "#1f2937", 
        border: "#059669",
        shadow: "0 4px 20px rgba(16, 185, 129, 0.3)"
      };
    }
    if (node.is_anchor) {
      return {
        primary: "#8b5cf6", // Purple for anchors
        secondary: "#ede9fe",
        text: "#1f2937",
        border: "#7c3aed", 
        shadow: "0 6px 25px rgba(139, 92, 246, 0.4)"
      };
    }
    // Default skill nodes
    return {
      primary: "#6b7280", // Gray for regular skills
      secondary: "#f3f4f6",
      text: "#1f2937",
      border: "#4b5563",
      shadow: "0 4px 15px rgba(107, 114, 128, 0.2)"
    };
  };

  const getNodeIcon = () => {
    if (node.type === "occupation") return isSaved ? "⭐" : "💼";
    if (node.type === "skillgroup") return "📚";
    if (node.is_anchor) return "🎯";
    return "🔧";
  };

  const styles = getNodeStyles();
  
  // Much larger, readable cards - significantly increased sizes
  const cardWidth = node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200);
  const cardHeight = node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100);
  
  if (!node.visible) {
    return (
      <g transform={`translate(${node.x - cardWidth/2}, ${node.y - cardHeight/2})`}>
        <rect
          width={cardWidth}
          height={cardHeight}
          fill="#f8fafc"
          stroke="#e2e8f0"
          strokeWidth="2"
          strokeDasharray="8,4"
          rx="12"
          ry="12"
        />
        <text 
          x={cardWidth/2}
          y={cardHeight/2}
          textAnchor="middle" 
          dominantBaseline="middle"
          fontSize="24"
          fill="#94a3b8"
        >
          ?
        </text>
      </g>
    );
  }

  return (
    <g transform={`translate(${node.x - cardWidth/2}, ${node.y - cardHeight/2})`}>
      {/* Card shadow/glow */}
      <rect
        width={cardWidth}
        height={cardHeight}
        fill={styles.primary}
        rx="12"
        ry="12"
        style={{ 
          filter: `drop-shadow(${styles.shadow})`,
          opacity: 0.1
        }}
        transform="translate(2, 2)"
      />
      
      {/* Main card */}
      <rect
        width={cardWidth}
        height={cardHeight}
        fill={styles.secondary}
        stroke={styles.border}
        strokeWidth="2"
        rx="12"
        ry="12"
        style={{ 
          cursor: 'pointer',
          transition: 'all 0.2s ease'
        }}
        onClick={() => onNodeClick(node)}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      />
      
      {/* Icon background circle - larger for bigger cards */}
      <circle
        cx={cardWidth/2}
        cy={30}
        r="24"
        fill={styles.primary}
        style={{ pointerEvents: 'none' }}
      />
      
      {/* Icon - larger */}
      <text 
        x={cardWidth/2}
        y={30}
        textAnchor="middle" 
        dominantBaseline="middle"
        fontSize="24"
        fill="white"
        style={{ pointerEvents: 'none' }}
      >
        {getNodeIcon()}
      </text>
      
      {/* Title - larger and more visible */}
      <text
        x={cardWidth/2}
        y={cardHeight - 40}
        textAnchor="middle"
        fontSize={node.is_anchor ? "16" : "14"}
        fill={styles.text}
        fontWeight="600"
        style={{ pointerEvents: 'none' }}
      >
        {displayLabel.length > (node.is_anchor ? 32 : 28) ? 
          displayLabel.substring(0, node.is_anchor ? 32 : 28) + '...' : 
          displayLabel}
      </text>
      
      {/* Subtitle for anchors - larger */}
      {node.is_anchor && (
        <text
          x={cardWidth/2}
          y={cardHeight - 15}
          textAnchor="middle"
          fontSize="12"
          fill={styles.primary}
          fontWeight="500"
          style={{ pointerEvents: 'none' }}
        >
          ANCHOR SKILL
        </text>
      )}
      
      {/* XP Badge */}
      {node.xp_reward && (
        <g>
          <rect
            x={cardWidth - 35}
            y={5}
            width="30"
            height="16"
            fill="#10b981"
            rx="8"
            ry="8"
          />
          <text
            x={cardWidth - 20}
            y={13}
            textAnchor="middle"
            fontSize="9"
            fill="white"
            fontWeight="600"
            style={{ pointerEvents: 'none' }}
          >
            {node.xp_reward}
          </text>
        </g>
      )}
      
      {/* Completion indicator */}
      {node.state === 'completed' && (
        <g>
          <circle
            cx={10}
            cy={10}
            r="8"
            fill="#10b981"
          />
          <text
            x={10}
            y={10}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize="10"
            fill="white"
            fontWeight="600"
          >
            ✓
          </text>
        </g>
      )}
      
      {/* Saved indicator */}
      {isSaved && node.type === "occupation" && (
        <g>
          <circle
            cx={cardWidth - 10}
            cy={cardHeight - 10}
            r="8"
            fill="#f59e0b"
          />
          <text
            x={cardWidth - 10}
            y={cardHeight - 10}
            textAnchor="middle"
            dominantBaseline="middle"
            fontSize="10"
            fill="white"
            fontWeight="600"
          >
            ★
          </text>
        </g>
      )}
      
      {/* Modern hover tooltip */}
      {showTooltip && node.challenge && (
        <g>
          {/* Tooltip background with modern design */}
          <rect
            x={cardWidth + 15}
            y={-30}
            width="320"
            height="80"
            fill="white"
            stroke="#e5e7eb"
            strokeWidth="1"
            rx="12"
            ry="12"
            style={{ 
              filter: 'drop-shadow(0 10px 25px rgba(0, 0, 0, 0.15))',
              opacity: 0.98
            }}
          />
          
          {/* Tooltip header */}
          <rect
            x={cardWidth + 15}
            y={-30}
            width="320"
            height="25"
            fill={styles.primary}
            rx="12"
            ry="12"
            style={{ clipPath: 'inset(0 0 50% 0)' }}
          />
          
          {/* Challenge label */}
          <text
            x={cardWidth + 25}
            y={-15}
            fill="white"
            fontSize="11"
            fontWeight="700"
          >
            💡 CHALLENGE
          </text>
          
          {/* Challenge text */}
          <text
            x={cardWidth + 25}
            y={0}
            fill="#374151"
            fontSize="11"
            fontWeight="500"
          >
            {node.challenge.length > 55 ? node.challenge.substring(0, 55) + '...' : node.challenge}
          </text>
          
          {/* XP reward badge in tooltip */}
          {node.xp_reward && (
            <g>
              <rect
                x={cardWidth + 25}
                y={15}
                width="60"
                height="20"
                fill="#10b981"
                rx="10"
                ry="10"
              />
              <text
                x={cardWidth + 55}
                y={25}
                textAnchor="middle"
                fill="white"
                fontSize="10"
                fontWeight="600"
              >
                +{node.xp_reward} XP
              </text>
            </g>
          )}
        </g>
      )}
    </g>
  );
};

// Optimized function to calculate clean hierarchical tree layout
const calculateRadialTreeLayout = (nodes: CompetenceNode[], edges: { source: string; target: string }[]): PositionedNode[] => {
  if (!nodes.length) return [];
  
  // Calculate center based on actual viewport size (with SSR safety)
  const centerX = typeof window !== 'undefined' ? Math.max(1600, window.innerWidth * 0.75) : 1600;
  const centerY = typeof window !== 'undefined' ? Math.max(1100, window.innerHeight * 0.75) : 1100;
  const positioned: PositionedNode[] = [];
  
  // Show ALL nodes that have visible !== false (including undefined visible)
  const visibleNodes = nodes.filter(n => n.visible !== false);
  const anchors = visibleNodes.filter(n => n.is_anchor);
  const nonAnchors = visibleNodes.filter(n => !n.is_anchor);
  
  // Build adjacency map for hierarchy
  const adjacencyMap = new Map<string, string[]>();
  const parentMap = new Map<string, string>();
  
  edges.forEach(edge => {
    const sourceVisible = visibleNodes.find(n => n.id === edge.source);
    const targetVisible = visibleNodes.find(n => n.id === edge.target);
    
    if (sourceVisible && targetVisible) {
      if (!adjacencyMap.has(edge.source)) adjacencyMap.set(edge.source, []);
      adjacencyMap.get(edge.source)!.push(edge.target);
      parentMap.set(edge.target, edge.source);
    }
  });
  
  // Build tree hierarchy starting from anchors
  const treeHierarchy = new Map<number, CompetenceNode[]>(); // level -> nodes
  const processedNodes = new Set<string>();
  
  // Level 0: Position ALL anchors
  if (anchors.length > 0) {
    treeHierarchy.set(0, anchors);
    
    if (anchors.length === 1) {
      positioned.push({
        ...anchors[0],
        x: centerX,
        y: centerY
      });
    } else {
      const anchorRadius = typeof window !== 'undefined' ? Math.max(600, window.innerWidth * 0.3) : 600; // Larger radius for bigger cards
      anchors.forEach((anchor, index) => {
        const angle = (2 * Math.PI * index) / anchors.length;
        positioned.push({
          ...anchor,
          x: centerX + anchorRadius * Math.cos(angle),
          y: centerY + anchorRadius * Math.sin(angle)
        });
      });
    }
    
    anchors.forEach(anchor => processedNodes.add(anchor.id));
  }
  
  // Build subsequent levels - increase max levels and remove child limits
  let currentLevel = 0;
  const maxLevels = 5; // Increase to show more levels
  
  while (currentLevel < maxLevels) {
    const currentLevelNodes = treeHierarchy.get(currentLevel) || [];
    const nextLevelNodes: CompetenceNode[] = [];
    
    // Find ALL children of current level nodes (no limits)
    currentLevelNodes.forEach(parent => {
      const children = (adjacencyMap.get(parent.id) || [])
        .map(id => visibleNodes.find(n => n.id === id))
        .filter(node => node && !processedNodes.has(node.id));
      
      console.log(`Level ${currentLevel} parent ${parent.label || parent.id} has ${children.length} children:`, 
        children.map(c => c?.label || c?.id));
      
      nextLevelNodes.push(...children as CompetenceNode[]);
      children.forEach(child => child && processedNodes.add(child.id));
    });
    
    if (nextLevelNodes.length === 0) {
      console.log(`No more children at level ${currentLevel + 1}, stopping`);
      break;
    }
    
    treeHierarchy.set(currentLevel + 1, nextLevelNodes);
    console.log(`Level ${currentLevel + 1} has ${nextLevelNodes.length} nodes`);
    currentLevel++;
  }
  
  // Position nodes level by level with clean spacing
  for (let level = 1; level <= currentLevel; level++) {
    const levelNodes = treeHierarchy.get(level) || [];
    const baseRadius = (typeof window !== 'undefined' ? Math.max(800, window.innerWidth * 0.4) : 800) + (level - 1) * (typeof window !== 'undefined' ? Math.max(600, window.innerHeight * 0.3) : 600);
    
    
    // Group nodes by their parent for proper positioning
    const nodesByParent = new Map<string, CompetenceNode[]>();
    levelNodes.forEach(node => {
      const parent = parentMap.get(node.id);
      if (parent) {
        if (!nodesByParent.has(parent)) nodesByParent.set(parent, []);
        nodesByParent.get(parent)!.push(node);
      }
    });
    
    
    // Position children around their parents
    nodesByParent.forEach((children, parentId) => {
      const parent = positioned.find(p => p.id === parentId);
      if (!parent) {
        return;
      }
      
      // Calculate parent's angle from center
      const parentAngle = Math.atan2(parent.y - centerY, parent.x - centerX);
      
      if (children.length === 1) {
        // Single child: extend directly outward from parent
        const child = children[0];
        positioned.push({
          ...child,
          x: centerX + baseRadius * Math.cos(parentAngle),
          y: centerY + baseRadius * Math.sin(parentAngle)
        });
      } else {
        // Multiple children: spread around parent direction with wider spread
        const spreadAngle = Math.PI / 2; // 90 degrees spread (much wider)
        const angleStep = spreadAngle / Math.max(children.length - 1, 1);
        
        children.forEach((child, index) => {
          const childAngle = parentAngle - spreadAngle / 2 + angleStep * index;
          positioned.push({
            ...child,
            x: centerX + baseRadius * Math.cos(childAngle),
            y: centerY + baseRadius * Math.sin(childAngle)
          });
        });
      }
    });
  }
  
  // Check for any orphaned nodes (visible but not positioned)
  const orphanedNodes = visibleNodes.filter(node => !positioned.find(p => p.id === node.id));
  if (orphanedNodes.length > 0) {
    console.log("WARNING: Orphaned nodes not positioned:", orphanedNodes.map(n => ({
      id: n.id,
      label: n.label || n.skill_label,
      is_anchor: n.is_anchor
    })));
    
    // Position orphaned nodes in outer ring
    orphanedNodes.forEach((node, index) => {
      const angle = (2 * Math.PI * index) / orphanedNodes.length;
      const outerRadius = (typeof window !== 'undefined' ? Math.max(1000, window.innerWidth * 0.45) : 1000) + currentLevel * (typeof window !== 'undefined' ? Math.max(450, window.innerHeight * 0.3) : 450);
      positioned.push({
        ...node,
        x: centerX + outerRadius * Math.cos(angle),
        y: centerY + outerRadius * Math.sin(angle)
      });
    });
  }
  
  console.log("=== FINAL LAYOUT RESULT ===");
  console.log("Positioned nodes:", positioned.length, "of", visibleNodes.length, "visible");
  console.log("Tree levels created:", currentLevel);
  
  return positioned;
};

const CompetenceTreeView: React.FC<CompetenceTreeViewProps> = ({ graphId }) => {
  
  const [treeData, setTreeData] = useState<CompetenceTreeData | null>(null);
  const [positionedNodes, setPositionedNodes] = useState<PositionedNode[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<PositionedNode | null>(null);
  const [showNodeModal, setShowNodeModal] = useState<boolean>(false);
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set());
  const [zoom, setZoom] = useState<number>(1);
  const [panX, setPanX] = useState<number>(0);
  const [panY, setPanY] = useState<number>(0);
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [lastMousePos, setLastMousePos] = useState<{x: number, y: number}>({x: 0, y: 0});
  
  // Advanced features for Priority 6
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [showMinimap, setShowMinimap] = useState<boolean>(false);
  const [selectedNodeTypes, setSelectedNodeTypes] = useState<Set<string>>(new Set(['occupation', 'skillgroup', 'skill']));
  const [nodeClusteringEnabled, setNodeClusteringEnabled] = useState<boolean>(false);
  
  // Calculate dimensions based on viewport (with SSR safety)
  const svgWidth = typeof window !== 'undefined' ? Math.max(3200, window.innerWidth * 1.5) : 3200;
  const svgHeight = typeof window !== 'undefined' ? Math.max(2200, window.innerHeight * 1.5) : 2200;
  
  // Function to save the tree as an image (on demand only)
  const saveTreeAsImage = useCallback(() => {
    try {
      const svgElement = document.querySelector('svg');
      if (!svgElement) return;

      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      canvas.width = svgWidth;
      canvas.height = svgHeight;

      const svgData = new XMLSerializer().serializeToString(svgElement);
      const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
      const svgUrl = URL.createObjectURL(svgBlob);

      const img = new Image();
      img.onload = function() {
        if (ctx) {
          ctx.drawImage(img, 0, 0);
          canvas.toBlob(function(blob) {
            if (blob) {
              const url = URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = `competence-tree-${new Date().getTime()}.png`;
              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
              URL.revokeObjectURL(url);
            }
          }, 'image/png');
        }
        URL.revokeObjectURL(svgUrl);
      };
      img.src = svgUrl;
    } catch (error) {
      console.error('Error saving tree as image:', error);
    }
  }, [svgWidth, svgHeight]);
  
  // Fonction pour charger l'arbre de compétences
  // Optimized loading with caching and memoization
  const loadCompetenceTree = useCallback(async () => {
    if (!graphId) return;
    
    try {
      setLoading(true);
      setError(null);
      
      // Check localStorage first for cached tree data
      const cachedTreeData = localStorage.getItem(`competence-tree-${graphId}`);
      const cachedPositions = localStorage.getItem(`competence-tree-positions-${graphId}`);
      
      if (cachedTreeData && cachedPositions) {
        try {
          const data = JSON.parse(cachedTreeData);
          const positions = JSON.parse(cachedPositions);
          setTreeData(data);
          setPositionedNodes(positions);
          setLoading(false);
          return;
        } catch (e) {
          console.warn('Failed to parse cached tree data:', e);
          localStorage.removeItem(`competence-tree-${graphId}`);
          localStorage.removeItem(`competence-tree-positions-${graphId}`);
          // Continue to fetch fresh data
        }
      }
      
      const data = await getCompetenceTree(graphId);
      
      setTreeData(data);
      
      // Save tree data to localStorage for persistence
      localStorage.setItem(`competence-tree-${graphId}`, JSON.stringify(data));
      
      // Calculate positions using optimized radial layout
      const positioned = calculateRadialTreeLayout(data.nodes, data.edges);
      setPositionedNodes(positioned);
      
      // Cache positioned nodes to avoid recalculation
      localStorage.setItem(`competence-tree-positions-${graphId}`, JSON.stringify(positioned));
      
      setLoading(false);
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue lors du chargement de l\'arbre de compétences');
      setLoading(false);
    }
  }, [graphId]);
  
  // Charger l'arbre au montage du composant
  useEffect(() => {
    if (graphId) {
      loadCompetenceTree();
    }
  }, [graphId, loadCompetenceTree]);
  
  // Fonction pour marquer un défi comme complété
  const handleCompleteChallenge = async (nodeId: string) => {
    try {
      const userId = 1; // À adapter selon votre système d'authentification
      await completeChallenge(nodeId, userId);
      
      // Recharger l'arbre pour obtenir les nouveaux nœuds révélés
      loadCompetenceTree();
    } catch (err: any) {
      setError(err.message || 'Une erreur est survenue lors de la complétion du défi');
    }
  };

  const handleNodeClick = (node: PositionedNode) => {
    setSelectedNode(node);
    setShowNodeModal(true);
  };

  const handleCloseModal = () => {
    setShowNodeModal(false);
    setSelectedNode(null);
  };

  const handleJobSaved = (node: CompetenceNode) => {
    setSavedJobs(prev => new Set([...Array.from(prev), node.id]));
  };

  // Zoom and pan handlers with smooth transitions
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    
    // Get the SVG bounding box to calculate mouse position relative to SVG
    const svgRect = e.currentTarget.getBoundingClientRect();
    const mouseX = e.clientX - svgRect.left;
    const mouseY = e.clientY - svgRect.top;
    
    // Much smaller zoom increments for smoother zooming
    const zoomStep = 0.03; // Even smaller for ultra-smooth zooming
    const zoomDirection = e.deltaY > 0 ? -1 : 1;
    
    setZoom(prev => {
      const newZoom = prev + (zoomStep * zoomDirection);
      const clampedZoom = Math.max(0.2, Math.min(4, newZoom));
      
      // Calculate zoom towards mouse position
      if (clampedZoom !== prev) {
        const zoomRatio = clampedZoom / prev;
        const deltaX = (mouseX - panX) * (1 - zoomRatio);
        const deltaY = (mouseY - panY) * (1 - zoomRatio);
        
        setPanX(currentPanX => currentPanX + deltaX);
        setPanY(currentPanY => currentPanY + deltaY);
      }
      
      return clampedZoom;
    });
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setLastMousePos({ x: e.clientX, y: e.clientY });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging) return;
    
    const deltaX = e.clientX - lastMousePos.x;
    const deltaY = e.clientY - lastMousePos.y;
    
    setPanX(prev => prev + deltaX);
    setPanY(prev => prev + deltaY);
    
    setLastMousePos({ x: e.clientX, y: e.clientY });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const resetView = () => {
    setZoom(1);
    setPanX(0);
    setPanY(0);
  };

  const zoomIn = () => {
    setZoom(prev => Math.min(4, prev + 0.2));
  };

  const zoomOut = () => {
    setZoom(prev => Math.max(0.2, prev - 0.2));
  };

  // Node clustering algorithm for better organization (Priority 6)
  const clusteredNodes = useMemo(() => {
    if (!nodeClusteringEnabled || !positionedNodes.length) return positionedNodes;
    
    // Group nodes by type and domain
    const clusters = new Map<string, PositionedNode[]>();
    
    positionedNodes.forEach(node => {
      const clusterKey = node.is_anchor ? 'anchors' : 
                        node.type === 'occupation' ? 'occupations' :
                        node.type === 'skillgroup' ? 'skillgroups' : 'skills';
      
      if (!clusters.has(clusterKey)) {
        clusters.set(clusterKey, []);
      }
      clusters.get(clusterKey)!.push(node);
    });
    
    // Reorganize clusters in distinct areas
    const clusteredResult: PositionedNode[] = [];
    const centerX = typeof window !== 'undefined' ? Math.max(1600, window.innerWidth * 0.75) : 1600;
    const centerY = typeof window !== 'undefined' ? Math.max(1100, window.innerHeight * 0.75) : 1100;
    
    // Position anchors in center
    const anchors = clusters.get('anchors') || [];
    anchors.forEach((anchor, index) => {
      const angle = (2 * Math.PI * index) / Math.max(anchors.length, 1);
      const radius = 200;
      clusteredResult.push({
        ...anchor,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      });
    });
    
    // Position occupation clusters in outer ring
    const occupations = clusters.get('occupations') || [];
    occupations.forEach((occupation, index) => {
      const angle = (2 * Math.PI * index) / Math.max(occupations.length, 1);
      const radius = 500;
      clusteredResult.push({
        ...occupation,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      });
    });
    
    // Position skill groups in middle ring
    const skillgroups = clusters.get('skillgroups') || [];
    skillgroups.forEach((skillgroup, index) => {
      const angle = (2 * Math.PI * index) / Math.max(skillgroups.length, 1) + Math.PI / 4; // Offset from occupations
      const radius = 350;
      clusteredResult.push({
        ...skillgroup,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      });
    });
    
    // Position individual skills in outermost ring
    const skills = clusters.get('skills') || [];
    skills.forEach((skill, index) => {
      const angle = (2 * Math.PI * index) / Math.max(skills.length, 1) + Math.PI / 8; // Another offset
      const radius = 650;
      clusteredResult.push({
        ...skill,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      });
    });
    
    return clusteredResult;
  }, [positionedNodes, nodeClusteringEnabled]);

  // Performance-optimized filtering and search (Priority 6)
  const filteredNodes = useMemo(() => {
    const nodesToFilter = nodeClusteringEnabled ? clusteredNodes : positionedNodes;
    if (!nodesToFilter.length) return [];
    
    let filtered = nodesToFilter;
    
    // Filter by node type
    if (selectedNodeTypes.size < 3) {
      filtered = filtered.filter(node => {
        const nodeType = node.is_anchor ? 'anchor' : (node.type || 'skill');
        return selectedNodeTypes.has(nodeType) || selectedNodeTypes.has(node.type || 'skill');
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
  }, [clusteredNodes, positionedNodes, nodeClusteringEnabled, selectedNodeTypes, searchQuery]);

  // Aggressive viewport culling for maximum performance
  const visibleNodes = useMemo(() => {
    if (filteredNodes.length < 15) return filteredNodes; // Very aggressive threshold
    
    // Use larger bounds but cull more aggressively
    const viewportWidth = typeof window !== 'undefined' ? window.innerWidth : 1200;
    const viewportHeight = typeof window !== 'undefined' ? window.innerHeight : 800;
    
    const leftBound = -panX / zoom - 600; // Even larger padding
    const rightBound = (-panX + viewportWidth) / zoom + 600;
    const topBound = -panY / zoom - 600;
    const bottomBound = (-panY + viewportHeight) / zoom + 600;
    
    return filteredNodes.filter(node => {
      return node.x >= leftBound && node.x <= rightBound && 
             node.y >= topBound && node.y <= bottomBound;
    });
  }, [filteredNodes, Math.floor(panX / 200), Math.floor(panY / 200), Math.floor(zoom * 5)]); // More aggressive throttling

  // Performance-capped visible nodes (absolute limit for extreme performance)
  const performanceVisibleNodes = useMemo(() => {
    const maxNodes = 50; // Hard cap for maximum performance
    if (visibleNodes.length <= maxNodes) return visibleNodes;
    
    // Prioritize anchors and occupations when capping
    const anchors = visibleNodes.filter(n => n.is_anchor);
    const occupations = visibleNodes.filter(n => n.type === 'occupation' && !n.is_anchor);
    const others = visibleNodes.filter(n => !n.is_anchor && n.type !== 'occupation');
    
    const result = [...anchors];
    const remaining = maxNodes - anchors.length;
    
    if (remaining > 0) {
      result.push(...occupations.slice(0, Math.floor(remaining * 0.7)));
      const stillRemaining = maxNodes - result.length;
      if (stillRemaining > 0) {
        result.push(...others.slice(0, stillRemaining));
      }
    }
    
    return result;
  }, [visibleNodes]);

  // Ultra-optimized connection lines rendering with performance cap
  const connectionLines = useMemo(() => {
    if (!treeData?.edges || performanceVisibleNodes.length === 0) return [];
    
    const visibleNodeIds = new Set(performanceVisibleNodes.map(n => n.id));
    const nodeMap = new Map(performanceVisibleNodes.map(n => [n.id, n]));
    
    // Limit connections for performance
    const maxConnections = 100;
    const relevantEdges = treeData.edges
      .filter(edge => visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target))
      .slice(0, maxConnections);
    
    return relevantEdges.map((edge) => {
        const sourceNode = nodeMap.get(edge.source);
        const targetNode = nodeMap.get(edge.target);
        if (!sourceNode || !targetNode) return null;

        // Smart connection points (edge of cards, not center) - updated for larger cards
        const sourceCardWidth = sourceNode.is_anchor ? 280 : (sourceNode.type === "occupation" ? 240 : 200);
        const sourceCardHeight = sourceNode.is_anchor ? 140 : (sourceNode.type === "occupation" ? 120 : 100);
        const targetCardWidth = targetNode.is_anchor ? 280 : (targetNode.type === "occupation" ? 240 : 200);
        const targetCardHeight = targetNode.is_anchor ? 140 : (targetNode.type === "occupation" ? 120 : 100);
        
        // Calculate connection points on card edges
        const dx = targetNode.x - sourceNode.x;
        const dy = targetNode.y - sourceNode.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        // Start point (bottom edge of source card)
        const startX = sourceNode.x;
        const startY = sourceNode.y + sourceCardHeight/2;
        
        // End point (top edge of target card) 
        const endX = targetNode.x;
        const endY = targetNode.y - targetCardHeight/2;
        
        // Create smooth curve
        const midX = (startX + endX) / 2;
        const midY = (startY + endY) / 2;
        const curveOffset = Math.min(distance * 0.15, 80); // Smooth curve
        const controlY = midY - curveOffset;
        
        // Connection type styling
        const getConnectionStyle = () => {
          if (sourceNode.is_anchor || targetNode.is_anchor) {
            return {
              stroke: "#8b5cf6",
              strokeWidth: "3",
              strokeOpacity: "0.8",
              strokeDasharray: "none"
            };
          }
          if (sourceNode.type === "occupation" || targetNode.type === "occupation") {
            return {
              stroke: "#3b82f6", 
              strokeWidth: "2.5",
              strokeOpacity: "0.7",
              strokeDasharray: "none"
            };
          }
          return {
            stroke: "#10b981",
            strokeWidth: "2",
            strokeOpacity: "0.6", 
            strokeDasharray: "none"
          };
        };
        
        const connectionStyle = getConnectionStyle();
        const pathData = `M ${startX} ${startY} Q ${midX} ${controlY} ${endX} ${endY}`;
        
        return (
          <g key={`${sourceNode.id}-${targetNode.id}`}>
            {/* Connection glow effect */}
            <path
              d={pathData}
              stroke={connectionStyle.stroke}
              strokeWidth={parseFloat(connectionStyle.strokeWidth) + 2}
              strokeOpacity="0.2"
              fill="none"
              style={{
                filter: 'blur(2px)'
              }}
            />
            
            {/* Main connection line */}
            <path
              d={pathData}
              stroke={connectionStyle.stroke}
              strokeWidth={connectionStyle.strokeWidth}
              strokeOpacity={connectionStyle.strokeOpacity}
              fill="none"
              strokeDasharray={connectionStyle.strokeDasharray}
              strokeLinecap="round"
              style={{
                filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1))'
              }}
            />
            
            {/* Connection direction arrow */}
            <circle
              cx={endX}
              cy={endY - 8}
              r="4"
              fill={connectionStyle.stroke}
              opacity={connectionStyle.strokeOpacity}
            />
          </g>
        );
      })
      .filter(Boolean); // Remove null entries
  }, [treeData?.edges, performanceVisibleNodes]);

  // Keyboard navigation support
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target && (e.target as HTMLElement).tagName === 'INPUT') return; // Don't interfere with input fields
      
      const panStep = 50 / zoom; // Adjust pan step based on zoom level
      
      switch (e.key) {
        case 'ArrowUp':
          e.preventDefault();
          setPanY(prev => prev + panStep);
          break;
        case 'ArrowDown':
          e.preventDefault();
          setPanY(prev => prev - panStep);
          break;
        case 'ArrowLeft':
          e.preventDefault();
          setPanX(prev => prev + panStep);
          break;
        case 'ArrowRight':
          e.preventDefault();
          setPanX(prev => prev - panStep);
          break;
        case '+':
        case '=':
          e.preventDefault();
          zoomIn();
          break;
        case '-':
          e.preventDefault();
          zoomOut();
          break;
        case '0':
          e.preventDefault();
          resetView();
          break;
        case 'f':
        case 'F':
          if (e.ctrlKey || e.metaKey) {
            e.preventDefault();
            // Focus search input (will implement in UI)
          }
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [zoom, zoomIn, zoomOut, resetView]);
  
  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <LoadingSpinner size="lg" />
        <div style={{ marginLeft: '16px' }}>Chargement de l'arbre de compétences...</div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <div style={{ color: 'red' }}>Erreur: {error}</div>
      </div>
    );
  }
  
  if (!treeData || positionedNodes.length === 0) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <div>Aucun arbre de compétences trouvé</div>
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
      background: '#f8fafc'
    }}>
      {/* Header bar */}
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
        <div className="flex items-center gap-4">
          <button
            onClick={() => window.history.back()}
            style={{
              background: '#6b7280',
              color: 'white',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500'
            }}
          >
            ← Back
          </button>
          <h1 style={{ margin: 0, fontSize: '20px', color: '#1f2937', fontWeight: '600' }}>
            Competence Tree Explorer
          </h1>
          
          {/* Search Bar (Priority 6) */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <input
              type="text"
              placeholder="Search nodes... (Ctrl+F)"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                padding: '6px 12px',
                borderRadius: '6px',
                border: '1px solid #d1d5db',
                fontSize: '14px',
                width: '200px',
                outline: 'none'
              }}
              onFocus={(e) => e.target.style.borderColor = '#3b82f6'}
              onBlur={(e) => e.target.style.borderColor = '#d1d5db'}
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                style={{
                  background: 'none',
                  border: 'none',
                  color: '#6b7280',
                  cursor: 'pointer',
                  fontSize: '16px'
                }}
              >
                ✕
              </button>
            )}
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {/* Node Type Filters (Priority 6) */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            {[
              { key: 'occupation', label: '💼', color: '#3b82f6' },
              { key: 'skillgroup', label: '📚', color: '#10b981' },
              { key: 'anchor', label: '🎯', color: '#8b5cf6' }
            ].map(filter => (
              <button
                key={filter.key}
                onClick={() => {
                  const newTypes = new Set(selectedNodeTypes);
                  if (newTypes.has(filter.key)) {
                    newTypes.delete(filter.key);
                  } else {
                    newTypes.add(filter.key);
                  }
                  setSelectedNodeTypes(newTypes);
                }}
                style={{
                  background: selectedNodeTypes.has(filter.key) ? filter.color : '#f3f4f6',
                  color: selectedNodeTypes.has(filter.key) ? 'white' : '#6b7280',
                  border: 'none',
                  padding: '4px 8px',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  fontSize: '12px',
                  fontWeight: '500'
                }}
              >
                {filter.label}
              </button>
            ))}
          </div>
          
          <span style={{ 
            fontSize: '14px', 
            color: '#6b7280',
            background: '#f3f4f6',
            padding: '6px 12px',
            borderRadius: '6px'
          }}>
            {performanceVisibleNodes.length}/{positionedNodes.length} nodes • Zoom: {Math.round(zoom * 100)}%
          </span>
          
          {/* Node Clustering Toggle */}
          <button
            onClick={() => setNodeClusteringEnabled(!nodeClusteringEnabled)}
            style={{
              background: nodeClusteringEnabled ? '#8b5cf6' : '#6b7280',
              color: 'white',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500'
            }}
          >
            🔗 {nodeClusteringEnabled ? 'Clustered' : 'Cluster'} View
          </button>
          
          {/* Minimap Toggle */}
          <button
            onClick={() => setShowMinimap(!showMinimap)}
            style={{
              background: showMinimap ? '#3b82f6' : '#6b7280',
              color: 'white',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500'
            }}
          >
            🗺️ {showMinimap ? 'Hide' : 'Show'} Map
          </button>
          <button
            onClick={zoomOut}
            style={{
              background: '#6b7280',
              color: 'white',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '6px 0 0 6px',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '500',
              borderRight: '1px solid #4b5563'
            }}
          >
            −
          </button>
          <button
            onClick={zoomIn}
            style={{
              background: '#6b7280',
              color: 'white',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '0 6px 6px 0',
              cursor: 'pointer',
              fontSize: '16px',
              fontWeight: '500',
              marginRight: '8px'
            }}
          >
            +
          </button>
          <button
            onClick={resetView}
            style={{
              background: '#3b82f6',
              color: 'white',
              border: 'none',
              padding: '8px 12px',
              borderRadius: '6px',
              cursor: 'pointer',
              fontSize: '13px',
              fontWeight: '500'
            }}
          >
            🎯 Reset View
          </button>
          <button
            onClick={saveTreeAsImage}
            style={{
              background: '#10b981',
              color: 'white',
              border: 'none',
              padding: '10px 16px',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600',
              boxShadow: '0 2px 4px rgba(16, 185, 129, 0.2)'
            }}
          >
            💾 Save Tree
          </button>
        </div>
      </div>
      
      {/* Full screen tree visualization */}
      <div style={{ 
        flex: 1,
        width: '100vw',
        height: 'calc(100vh - 60px)',
        overflow: 'auto',
        background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 50%, #e2e8f0 100%)',
        position: 'relative'
      }}>
        <svg 
          width={svgWidth} 
          height={svgHeight}
          style={{ 
            background: 'transparent',
            display: 'block',
            cursor: isDragging ? 'grabbing' : 'grab'
          }}
          onWheel={handleWheel}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          <g 
            transform={`translate(${panX}, ${panY}) scale(${zoom})`}
            style={{
              transition: isDragging ? 'none' : 'transform 0.15s ease-out',
              transformOrigin: 'center'
            }}
          >
            {/* Render optimized connection lines */}
            {connectionLines}
            
            {/* Render performance-capped nodes */}
            {performanceVisibleNodes.map((node) => (
              <TreeNode
                key={node.id}
                node={node}
                onComplete={handleCompleteChallenge}
                onNodeClick={handleNodeClick}
                isSaved={savedJobs.has(node.id)}
              />
            ))}
          </g>
        </svg>
        
        {/* Minimap (Priority 6) */}
        {showMinimap && (
          <div style={{
            position: 'absolute',
            bottom: '20px',
            right: '20px',
            width: '200px',
            height: '150px',
            background: 'rgba(255, 255, 255, 0.95)',
            border: '2px solid #e5e7eb',
            borderRadius: '8px',
            padding: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
            zIndex: 1002
          }}>
            <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '8px', color: '#374151' }}>
              Tree Overview
            </div>
            <svg width="184" height="120" style={{ border: '1px solid #e5e7eb', borderRadius: '4px' }}>
              {/* Minimap background */}
              <rect width="184" height="120" fill="#f9fafb" />
              
              {/* Minimap nodes (simplified) */}
              {(nodeClusteringEnabled ? clusteredNodes : positionedNodes).slice(0, 50).map(node => { // Limit for performance
                const mapX = ((node.x + 1600) / 3200) * 184; // Normalize to minimap bounds
                const mapY = ((node.y + 1100) / 2200) * 120;
                
                return (
                  <circle
                    key={node.id}
                    cx={Math.max(2, Math.min(182, mapX))}
                    cy={Math.max(2, Math.min(118, mapY))}
                    r={node.is_anchor ? 3 : 2}
                    fill={
                      node.is_anchor ? '#8b5cf6' :
                      node.type === 'occupation' ? '#3b82f6' :
                      node.type === 'skillgroup' ? '#10b981' : '#6b7280'
                    }
                    opacity={0.8}
                  />
                );
              })}
              
              {/* Viewport indicator */}
              <rect
                x={Math.max(0, Math.min(174, 92 - (panX / zoom) * 0.05))}
                y={Math.max(0, Math.min(110, 60 - (panY / zoom) * 0.05))}
                width={Math.min(184, 10 / zoom)}
                height={Math.min(120, 10 / zoom)}
                fill="none"
                stroke="#ef4444"
                strokeWidth="2"
                strokeDasharray="3,3"
              />
            </svg>
            
            {/* Minimap stats */}
            <div style={{ 
              fontSize: '10px', 
              color: '#6b7280', 
              marginTop: '4px',
              display: 'flex',
              justifyContent: 'space-between'
            }}>
              <span>{filteredNodes.length} visible</span>
              <span>{Math.round(zoom * 100)}% zoom</span>
            </div>
          </div>
        )}
        
        {/* Keyboard Shortcuts Help (Priority 6) */}
        <div style={{
          position: 'absolute',
          bottom: '20px',
          left: '20px',
          background: 'rgba(0, 0, 0, 0.8)',
          color: 'white',
          padding: '12px',
          borderRadius: '8px',
          fontSize: '11px',
          maxWidth: '200px',
          zIndex: 1002
        }}>
          <div style={{ fontWeight: '600', marginBottom: '8px' }}>⌨️ Keyboard Shortcuts</div>
          <div style={{ lineHeight: '1.4' }}>
            <div>Arrow keys: Pan around</div>
            <div>+/- : Zoom in/out</div>
            <div>0 : Reset view</div>
            <div>Ctrl+F : Focus search</div>
            <div>🔗 Clustering: Better organization</div>
            <div>🗺️ Minimap: Tree overview</div>
          </div>
        </div>
        
        {/* Node Detail Modal */}
        {showNodeModal && selectedNode && (
          <NodeDetailModal
            node={selectedNode}
            graphId={treeData?.graph_id}
            onClose={handleCloseModal}
            onCompleteChallenge={handleCompleteChallenge}
            onSaveJob={handleJobSaved}
          />
        )}
      </div>
    </div>
  );
};

export default CompetenceTreeView;