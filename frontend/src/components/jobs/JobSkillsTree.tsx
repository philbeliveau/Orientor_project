'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { getJobSkillsTree } from '@/services/api';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node as FlowNode,
  Edge as FlowEdge,
  useNodesState,
  useEdgesState,
  Position,
  ReactFlowProvider
} from 'reactflow';
import 'reactflow/dist/style.css';
import { Disclosure, DisclosureButton, DisclosurePanel } from '@headlessui/react';
import { ChevronDownIcon } from '@heroicons/react/24/outline';

interface Node {
  id: string;
  label: string;
  type: string;
  level?: number;
  score?: number;
  [key: string]: any;
}

interface Edge {
  source: string;
  target: string;
  type?: string;
  weight?: number;
  [key: string]: any;
}

interface SkillTreeData {
  nodes: { [key: string]: Node };
  edges: Edge[];
  visualizations?: {
    plotly?: any;
    matplotlib?: string;
    streamlit?: any;
  };
}

interface JobSkillsTreeProps {
  jobId: string | null;
  className?: string;
  height?: string;
}

const JobSkillsTree: React.FC<JobSkillsTreeProps> = ({ jobId, className = '', height = '600px' }) => {
  const [skillTreeData, setSkillTreeData] = useState<SkillTreeData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [topSkills, setTopSkills] = useState<Node[]>([]);
  
  // États pour les paramètres de l'arbre
  const [treeDepth, setTreeDepth] = useState<number>(1);
  const [nodesPerLevel, setNodesPerLevel] = useState<number>(5);
  const [isApplying, setIsApplying] = useState<boolean>(false);
  const [paramVersion, setParamVersion] = useState<number>(0); // Pour forcer le rechargement
  const [debugMode, setDebugMode] = useState<boolean>(false);
  
  // États pour ReactFlow
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  
  // Test nodes to verify ReactFlow works
  const testNodes = [
    {
      id: 'test-1',
      position: { x: 250, y: 250 },
      data: { label: 'Test Node 1' },
      style: { background: '#ff0072', color: 'white', padding: '10px', borderRadius: '5px' }
    },
    {
      id: 'test-2',
      position: { x: 100, y: 100 },
      data: { label: 'Test Node 2' },
      style: { background: '#00ff72', color: 'white', padding: '10px', borderRadius: '5px' }
    }
  ];
  
  const testEdges = [
    { id: 'e1-2', source: 'test-1', target: 'test-2' }
  ];

  // Fonction pour convertir les données de l'arbre de compétences en format ReactFlow
  const convertToReactFlowFormat = useCallback((data: SkillTreeData) => {
    console.log("convertToReactFlowFormat appelée avec:", data);
    if (!data || !data.nodes || !data.edges) {
      console.log("Données invalides pour ReactFlow:", { data, hasNodes: !!data?.nodes, hasEdges: !!data?.edges });
      return;
    }

    // Identifier le nœud d'emploi (occupation)
    const occupationNode = Object.values(data.nodes).find(node => node.type === 'occupation');
    if (!occupationNode) return;
    
    console.log("Nœud d'emploi trouvé:", occupationNode);
    console.log("Tous les nœuds:", Object.values(data.nodes));
    console.log("Toutes les arêtes:", data.edges);
    
    // Créer un layout en étoile
    const centerX = 400;
    const centerY = 250;
    
    // Convertir les nœuds
    const flowNodes: FlowNode[] = [];
    const nodeIds = new Set<string>();
    
    // Ajouter le nœud d'emploi au centre
    flowNodes.push({
      id: occupationNode.id,
      position: { x: centerX, y: centerY },
      data: { label: occupationNode.label || occupationNode.id.replace('occupation::key_', 'Position ') },
      style: { background: '#4285F4', color: 'white', padding: '10px', borderRadius: '8px', width: '200px', textAlign: 'center' },
      type: 'default'
    });
    nodeIds.add(occupationNode.id);
    
    // Trouver les nœuds directement connectés au nœud d'emploi
    const level1Nodes = Object.values(data.nodes).filter(node =>
      node.id !== occupationNode.id &&
      data.edges.some(edge =>
        (edge.source === occupationNode.id && edge.target === node.id) ||
        (edge.target === occupationNode.id && edge.source === node.id)
      )
    );
    
    console.log("Nœuds de niveau 1:", level1Nodes);
    
    // Limiter au nombre de nœuds spécifié pour le niveau 1
    const topLevel1Nodes = level1Nodes.slice(0, nodesPerLevel);
    
    // Ajouter les nœuds de niveau 1 autour du nœud d'emploi
    const radius1 = 200;
    topLevel1Nodes.forEach((node, index) => {
      const angle = (index / topLevel1Nodes.length) * 2 * Math.PI;
      const x = centerX + radius1 * Math.cos(angle);
      const y = centerY + radius1 * Math.sin(angle);
      
      // Déterminer la couleur en fonction du type de nœud
      let bgColor = '#34A853'; // Vert par défaut pour les compétences
      if (node.type === 'skillsgroup') {
        bgColor = '#FBBC05'; // Jaune pour les groupes de compétences
      } else if (node.type === 'occupation') {
        bgColor = '#4285F4'; // Bleu pour les emplois
      }
      
      flowNodes.push({
        id: node.id,
        position: { x, y },
        data: { label: node.label || node.id.replace(/^(skill|skillsgroup)::/, '').replace(/_/g, ' ') },
        style: {
          background: bgColor,
          color: 'white',
          padding: '8px',
          borderRadius: '8px',
          width: '180px',
          textAlign: 'center'
        },
        type: 'default'
      });
      nodeIds.add(node.id);
    });
    
    // Si la profondeur est supérieure à 1, ajouter les nœuds de niveau 2
    if (treeDepth > 1) {
      console.log("Recherche des nœuds de niveau 2 (profondeur > 1)");
      
      // Pour chaque nœud de niveau 1, trouver les nœuds connectés (niveau 2)
      topLevel1Nodes.forEach((level1Node, level1Index) => {
        console.log(`Recherche des nœuds connectés à ${level1Node.label} (ID: ${level1Node.id})`);
        
        // Afficher toutes les arêtes liées à ce nœud pour le débogage
        const relatedEdges = data.edges.filter(edge =>
          edge.source === level1Node.id || edge.target === level1Node.id
        );
        console.log(`Arêtes liées à ${level1Node.label}:`, relatedEdges);
        
        // Approche alternative pour trouver les nœuds de niveau 2
        const level2Nodes: Node[] = [];
        
        // Parcourir toutes les arêtes pour trouver les connexions
        data.edges.forEach(edge => {
          let connectedNodeId: string | null = null;
          
          // Si l'arête part du nœud de niveau 1
          if (edge.source === level1Node.id) {
            connectedNodeId = edge.target;
          }
          // Si l'arête arrive au nœud de niveau 1
          else if (edge.target === level1Node.id) {
            connectedNodeId = edge.source;
          }
          
          // Si on a trouvé un nœud connecté et qu'il n'est pas déjà dans notre graphe
          if (connectedNodeId && !nodeIds.has(connectedNodeId) && connectedNodeId !== occupationNode.id) {
            const connectedNode = data.nodes[connectedNodeId];
            if (connectedNode && !level2Nodes.some(n => n.id === connectedNodeId)) {
              level2Nodes.push(connectedNode);
            }
          }
        });
        
        console.log(`Nœuds de niveau 2 connectés à ${level1Node.label}:`, level2Nodes);
        
        // Limiter au nombre de nœuds spécifié pour le niveau 2
        const topLevel2Nodes = level2Nodes.slice(0, Math.max(2, Math.floor(nodesPerLevel / 2)));
        
        // Calculer la position de base pour les nœuds de niveau 2
        const baseAngle = (level1Index / topLevel1Nodes.length) * 2 * Math.PI;
        const baseX = centerX + radius1 * Math.cos(baseAngle);
        const baseY = centerY + radius1 * Math.sin(baseAngle);
        
        // Ajouter les nœuds de niveau 2 autour du nœud de niveau 1
        const radius2 = 150;
        topLevel2Nodes.forEach((node, index) => {
          // Calculer un angle relatif au nœud de niveau 1
          const angleOffset = ((index / topLevel2Nodes.length) - 0.5) * Math.PI / 2;
          const angle = baseAngle + angleOffset;
          const x = baseX + radius2 * Math.cos(angle);
          const y = baseY + radius2 * Math.sin(angle);
          
          // Déterminer la couleur en fonction du type de nœud
          let bgColor = '#34A853'; // Vert par défaut pour les compétences
          if (node.type === 'skillsgroup') {
            bgColor = '#FBBC05'; // Jaune pour les groupes de compétences
          } else if (node.type === 'occupation') {
            bgColor = '#4285F4'; // Bleu pour les emplois
          }
          
          flowNodes.push({
            id: node.id,
            position: { x, y },
            data: { label: node.label || node.id.replace(/^(skill|skillsgroup)::/, '').replace(/_/g, ' ') },
            style: {
              background: bgColor,
              color: 'white',
              padding: '8px',
              borderRadius: '8px',
              width: '150px',
              textAlign: 'center'
            },
            type: 'default'
          });
          nodeIds.add(node.id);
        });
      });
    }
    
    // Si la profondeur est supérieure à 2, ajouter les nœuds de niveau 3
    if (treeDepth > 2) {
      // Trouver tous les nœuds de niveau 2 (ceux qui ont été ajoutés après les nœuds de niveau 1)
      const level2NodeIds = Array.from(nodeIds).filter(id =>
        id !== occupationNode.id &&
        !topLevel1Nodes.some(node => node.id === id)
      );
      
      // Pour chaque nœud de niveau 2, trouver les nœuds connectés (niveau 3)
      level2NodeIds.forEach(level2Id => {
        const level2Node = flowNodes.find(node => node.id === level2Id);
        if (!level2Node) return;
        
        const level3Nodes = Object.values(data.nodes).filter(node =>
          !nodeIds.has(node.id) &&
          data.edges.some(edge =>
            (edge.source === level2Id && edge.target === node.id) ||
            (edge.target === level2Id && edge.source === node.id)
          )
        );
        
        // Limiter au nombre de nœuds spécifié pour le niveau 3
        const topLevel3Nodes = level3Nodes.slice(0, Math.max(1, Math.floor(nodesPerLevel / 3)));
        
        // Ajouter les nœuds de niveau 3 autour du nœud de niveau 2
        const radius3 = 100;
        const baseX = level2Node.position.x;
        const baseY = level2Node.position.y;
        
        topLevel3Nodes.forEach((node, index) => {
          // Calculer un angle pour positionner les nœuds de niveau 3
          const angle = (index / topLevel3Nodes.length) * 2 * Math.PI;
          const x = baseX + radius3 * Math.cos(angle);
          const y = baseY + radius3 * Math.sin(angle);
          
          // Déterminer la couleur en fonction du type de nœud
          let bgColor = '#34A853'; // Vert par défaut pour les compétences
          if (node.type === 'skillsgroup') {
            bgColor = '#FBBC05'; // Jaune pour les groupes de compétences
          } else if (node.type === 'occupation') {
            bgColor = '#4285F4'; // Bleu pour les emplois
          }
          
          flowNodes.push({
            id: node.id,
            position: { x, y },
            data: { label: node.label || node.id.replace(/^(skill|skillsgroup)::/, '').replace(/_/g, ' ') },
            style: {
              background: bgColor,
              color: 'white',
              padding: '6px',
              borderRadius: '8px',
              width: '120px',
              textAlign: 'center',
              fontSize: '0.8rem'
            },
            type: 'default'
          });
          nodeIds.add(node.id);
        });
      });
    }
    
    // Convertir les arêtes entre les nœuds ajoutés
    const flowEdges: FlowEdge[] = [];
    
    data.edges.forEach((edge, index) => {
      // Vérifier que les nœuds source et cible existent dans notre ensemble de nœuds
      if (nodeIds.has(edge.source) && nodeIds.has(edge.target)) {
        flowEdges.push({
          id: `e${index}`,
          source: edge.source,
          target: edge.target,
          animated: false,
          style: {
            stroke: '#888',
            strokeWidth: edge.weight ? Math.max(1, edge.weight * 3) : 1,
            strokeOpacity: 0.8
          },
          type: 'default'
        });
      }
    });
    
    console.log("Nœuds ReactFlow:", flowNodes);
    console.log("Arêtes ReactFlow:", flowEdges);
    console.log("Nombre de nœuds:", flowNodes.length);
    console.log("Nombre d'arêtes:", flowEdges.length);
    
    console.log("Setting ReactFlow nodes and edges...");
    console.log("About to set nodes:", flowNodes.length, flowNodes);
    console.log("About to set edges:", flowEdges.length, flowEdges);
    setNodes(flowNodes);
    setEdges(flowEdges);
    console.log("ReactFlow nodes and edges set successfully");
  }, [setNodes, setEdges, treeDepth, nodesPerLevel]);

  // Forcer un rechargement complet du composant lorsque les paramètres changent
  useEffect(() => {
    if (skillTreeData) {
      console.log(`Paramètres changés: treeDepth=${treeDepth}, nodesPerLevel=${nodesPerLevel}`);
      // Réinitialiser les nœuds et les arêtes
      setNodes([]);
      setEdges([]);
      // Reconvertir les données
      convertToReactFlowFormat(skillTreeData);
    }
  }, [treeDepth, nodesPerLevel, skillTreeData, convertToReactFlowFormat]);

  // Fonction pour charger l'arbre de compétences avec les paramètres spécifiés
  const fetchSkillsTree = useCallback(async () => {
    if (!jobId) {
      setSkillTreeData(null);
      setTopSkills([]);
      setNodes([]);
      setEdges([]);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      console.log(`Demande d'arbre avec profondeur=${treeDepth}, nodesPerLevel=${nodesPerLevel}`);
      const data = await getJobSkillsTree(jobId, treeDepth, nodesPerLevel);
      const typedData = data as SkillTreeData;
      setSkillTreeData(typedData);
      
      console.log("Données de l'arbre de compétences reçues:", typedData);
      console.log(`Nombre de nœuds reçus: ${Object.keys(typedData.nodes || {}).length}`);
      console.log(`Nombre d'arêtes reçues: ${typedData.edges?.length || 0}`);
      console.log("Structure des données:", JSON.stringify(typedData, null, 2));
      
      // Analyser la profondeur des nœuds reçus
      const nodesByLevel: { [level: number]: number } = {};
      Object.values(typedData.nodes).forEach(node => {
        const level = node.level || 0;
        nodesByLevel[level] = (nodesByLevel[level] || 0) + 1;
      });
      console.log("Répartition des nœuds par niveau:", nodesByLevel);
      
      // Extraire les principales compétences à développer
      const skillNodes = Object.values(typedData.nodes).filter(
        (node) => node.type === 'skill'
      ) as Node[];
      
      // Trier par score si disponible, sinon par ordre alphabétique
      const sortedSkills = skillNodes.sort((a, b) => {
        if (a.score !== undefined && b.score !== undefined) {
          return b.score - a.score; // Du plus haut au plus bas score
        }
        return a.label.localeCompare(b.label);
      });
      
      setTopSkills(sortedSkills.slice(0, nodesPerLevel));
      
      // Convertir les données pour ReactFlow
      convertToReactFlowFormat(typedData);
    } catch (err) {
      console.error("Erreur lors du chargement de l'arbre de compétences:", err);
      setError("Impossible de charger l'arbre de compétences");
    } finally {
      setIsLoading(false);
      setIsApplying(false);
    }
  }, [jobId, treeDepth, nodesPerLevel, convertToReactFlowFormat]);

  // Charger l'arbre de compétences lorsque jobId change ou lorsque paramVersion change
  useEffect(() => {
    console.log(`Effet déclenché: jobId=${jobId}, paramVersion=${paramVersion}`);
    fetchSkillsTree();
  }, [jobId, paramVersion, fetchSkillsTree]);

  // Afficher un état de chargement
  if (isLoading) {
    return (
      <div className={`flex justify-center items-center p-8 ${className}`}>
        <LoadingSpinner size="lg" />
        <p className="ml-3" style={{ color: 'var(--text-color)' }}>Chargement de l'arbre de compétences...</p>
      </div>
    );
  }

  // Afficher un message d'erreur
  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <p className="text-red-600">
          Erreur: {error}
        </p>
      </div>
    );
  }

  // Afficher un message si aucun emploi n'est sélectionné
  if (!jobId) {
    return (
      <div className={`rounded-lg p-6 text-center ${className}`} style={{
        backgroundColor: 'var(--primary-color)',
        borderWidth: '1px',
        borderStyle: 'solid',
        borderColor: 'var(--border-color)'
      }}>
        <p style={{ color: 'var(--text-color)' }}>
          Sélectionnez un emploi pour voir l'arbre de compétences associé.
        </p>
      </div>
    );
  }

  // Afficher un message si aucune donnée n'est disponible
  if (!skillTreeData || Object.keys(skillTreeData.nodes || {}).length === 0) {
    console.log("JobSkillsTree: Pas de données ou nœuds vides", { 
      skillTreeData, 
      hasNodes: !!skillTreeData?.nodes, 
      nodeCount: Object.keys(skillTreeData?.nodes || {}).length 
    });
    return (
      <div className={`rounded-lg p-6 text-center ${className}`} style={{
        backgroundColor: 'var(--primary-color)',
        borderWidth: '1px',
        borderStyle: 'solid',
        borderColor: 'var(--border-color)'
      }}>
        <p style={{ color: 'var(--text-color)' }}>
          Aucune donnée d'arbre de compétences disponible pour cet emploi.
        </p>
      </div>
    );
  }

  // Fonction pour appliquer les nouveaux paramètres
  const applyParameters = () => {
    setIsApplying(true);
    // Incrémenter la version des paramètres pour forcer un rechargement
    setParamVersion(prev => prev + 1);
    // Le rechargement sera déclenché par l'effet qui dépend de paramVersion
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Visualisation de l'arbre de compétences ESCO */}
      <div className="rounded-lg p-6" style={{
        backgroundColor: 'var(--primary-color)',
        borderWidth: '1px',
        borderStyle: 'solid',
        borderColor: 'var(--border-color)'
      }}>
        <h3 className="text-lg font-medium mb-4" style={{ color: 'var(--accent-color)' }}>
          Arbre de compétences ESCO
          <span className="text-sm ml-2" style={{ color: 'var(--text-color)' }}>
            (Profondeur: {treeDepth}, Nœuds par niveau: {nodesPerLevel})
          </span>
        </h3>
        
        <p className="text-sm mb-4" style={{ color: 'var(--text-color)' }}>
          Cette visualisation montre les relations entre les différentes compétences requises pour ce poste, générées à partir du graphe ESCO.
        </p>
        
        {/* Légende */}
        <div className="flex flex-wrap gap-3 mb-4">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
            <span className="text-xs" style={{ color: 'var(--text-color)' }}>Emploi</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
            <span className="text-xs" style={{ color: 'var(--text-color)' }}>Compétence</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></div>
            <span className="text-xs" style={{ color: 'var(--text-color)' }}>Groupe de compétences</span>
          </div>
        </div>
        
        {/* Debug Mode Toggle */}
        <div className="mb-4">
          <button 
            onClick={() => setDebugMode(!debugMode)}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            {debugMode ? 'Mode Normal' : 'Mode Debug'}
          </button>
        </div>

        {/* Visualisation ReactFlow */}
        <div className="w-full" style={{ height: height || '600px' }}>
          <div className="w-full h-full border rounded-lg" style={{ backgroundColor: '#f9f9f9' }}>
            <ReactFlowProvider>
              <ReactFlow
                nodes={debugMode ? testNodes : nodes}
                edges={debugMode ? testEdges : edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                fitView={true}
                fitViewOptions={{ padding: 0.2 }}
                attributionPosition="bottom-right"
                className="w-full h-full"
                minZoom={0.5}
                maxZoom={2}
              >
                <Controls />
                <MiniMap />
                <Background color="#ccc" gap={16} />
              </ReactFlow>
            </ReactFlowProvider>
          </div>
        </div>
        
        <div className="mt-4 text-center">
          <p className="text-xs italic" style={{ color: 'var(--text-color)' }}>
            Nombre total de nœuds: {Object.keys(skillTreeData.nodes).length} | 
            Nombre total de relations: {skillTreeData.edges.length}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            ReactFlow - Nœuds: {nodes.length} | Arêtes: {edges.length}
          </p>
          {nodes.length === 0 && (
            <p className="text-red-500 text-sm mt-2">⚠️ Aucun nœud ReactFlow détecté - Vérification en cours...</p>
          )}
        </div>

        {/* Debug: List nodes if ReactFlow doesn't show them */}
        {nodes.length > 0 && (
          <div className="mt-4 p-4 bg-gray-100 rounded text-sm">
            <h4 className="font-semibold mb-2">Debug - Nœuds détectés:</h4>
            <ul className="space-y-1">
              {nodes.slice(0, 6).map(node => (
                <li key={node.id} className="text-xs">
                  <span className="font-mono bg-gray-200 px-1 rounded">{node.id}</span>: {node.data.label}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Dropdown pour les compétences et paramètres */}
      <div className="mt-4">
        <Disclosure>
          {({ open }) => (
            <>
              <DisclosureButton 
                className="w-full flex justify-between items-center px-4 py-2 rounded-lg" 
                style={{ 
                  backgroundColor: 'var(--primary-color)',
                  borderWidth: '1px',
                  borderStyle: 'solid',
                  borderColor: 'var(--border-color)'
                }}
              >
                <span style={{ color: 'var(--accent-color)' }}>Options et compétences</span>
                <ChevronDownIcon
                  className={`${open ? 'transform rotate-180' : ''} w-5 h-5`}
                  style={{ color: 'var(--accent-color)' }}
                />
              </DisclosureButton>
              <DisclosurePanel className="mt-2">
                {/* Top des compétences */}
                <div className="rounded-lg p-6 mb-6" style={{
                  backgroundColor: 'var(--primary-color)',
                  borderWidth: '1px',
                  borderStyle: 'solid',
                  borderColor: 'var(--border-color)'
                }}>
                  <h3 className="text-lg font-medium mb-4" style={{ color: 'var(--accent-color)' }}>
                    Top {nodesPerLevel} des compétences à acquérir
                  </h3>
                  
                  <div className="space-y-3">
                    {topSkills.map((skill, index) => (
                      <div 
                        key={skill.id} 
                        className="flex items-center p-3 rounded-lg"
                        style={{ backgroundColor: 'var(--primary-color)' }}
                      >
                        <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center text-white rounded-full mr-3"
                             style={{ backgroundColor: 'var(--accent-color)' }}>
                          {index + 1}
                        </div>
                        <div>
                          <p className="font-medium" style={{ color: 'var(--accent-color)' }}>{skill.label}</p>
                          {skill.description && (
                            <p className="text-sm mt-1 line-clamp-2" style={{ color: 'var(--text-color)' }}>
                              {skill.description}
                            </p>
                          )}
                        </div>
                        {skill.score !== undefined && (
                          <div className="ml-auto">
                            <span className="text-white text-xs font-bold px-2 py-1 rounded-full"
                                  style={{ backgroundColor: 'var(--accent-color)' }}>
                              {Math.round(skill.score * 100)}%
                            </span>
                          </div>
                        )}
                      </div>
                    ))}
                    
                    {topSkills.length === 0 && (
                      <p className="text-center py-4" style={{ color: 'var(--text-color)' }}>
                        Aucune compétence à développer identifiée.
                      </p>
                    )}
                  </div>
                </div>

                {/* Contrôles pour les paramètres de l'arbre */}
                <div className="rounded-lg p-4 mb-4" style={{
                  backgroundColor: 'var(--primary-color)',
                  borderWidth: '1px',
                  borderStyle: 'solid',
                  borderColor: 'var(--border-color)'
                }}>
                  <h3 className="text-sm font-medium mb-2" style={{ color: 'var(--accent-color)' }}>
                    Paramètres de l'arbre
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-2">
                    <div>
                      <label htmlFor="treeDepth" className="block mb-1" style={{ color: 'var(--text-color)' }}>
                        Profondeur (1-3)
                      </label>
                      <div className="flex items-center">
                        <button
                          onClick={() => setTreeDepth(Math.max(1, treeDepth - 1))}
                          className="text-white px-2 py-1 rounded-l-md"
                          style={{ backgroundColor: 'var(--accent-color)' }}
                          disabled={treeDepth <= 1}
                        >
                          -
                        </button>
                        <input
                          id="treeDepth"
                          type="number"
                          min={1}
                          max={3}
                          value={treeDepth}
                          onChange={(e) => setTreeDepth(Math.min(3, Math.max(1, parseInt(e.target.value) || 1)))}
                          className="w-12 text-center border py-1"
                          style={{ borderColor: 'var(--border-color)' }}
                        />
                        <button
                          onClick={() => setTreeDepth(Math.min(3, treeDepth + 1))}
                          className="text-white px-2 py-1 rounded-r-md"
                          style={{ backgroundColor: 'var(--accent-color)' }}
                          disabled={treeDepth >= 3}
                        >
                          +
                        </button>
                      </div>
                    </div>
                    
                    <div>
                      <label htmlFor="nodesPerLevel" className="block mb-1" style={{ color: 'var(--text-color)' }}>
                        Nœuds (3-10)
                      </label>
                      <div className="flex items-center">
                        <button
                          onClick={() => setNodesPerLevel(Math.max(3, nodesPerLevel - 1))}
                          className="text-white px-2 py-1 rounded-l-md"
                          style={{ backgroundColor: 'var(--accent-color)' }}
                          disabled={nodesPerLevel <= 3}
                        >
                          -
                        </button>
                        <input
                          id="nodesPerLevel"
                          type="number"
                          min={3}
                          max={10}
                          value={nodesPerLevel}
                          onChange={(e) => setNodesPerLevel(Math.min(10, Math.max(3, parseInt(e.target.value) || 3)))}
                          className="w-12 text-center border py-1"
                          style={{ borderColor: 'var(--border-color)' }}
                        />
                        <button
                          onClick={() => setNodesPerLevel(Math.min(10, nodesPerLevel + 1))}
                          className="text-white px-2 py-1 rounded-r-md"
                          style={{ backgroundColor: 'var(--accent-color)' }}
                          disabled={nodesPerLevel >= 10}
                        >
                          +
                        </button>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={applyParameters}
                      disabled={isLoading || isApplying}
                      className="text-white px-3 py-1 rounded-md hover:bg-opacity-90 transition-colors"
                      style={{ backgroundColor: 'var(--accent-color)' }}
                    >
                      {isApplying ? 'En cours...' : 'Appliquer'}
                    </button>
                    
                    <button
                      onClick={() => {
                        setIsApplying(true);
                        // Réinitialiser les paramètres
                        setTreeDepth(1);
                        setNodesPerLevel(5);
                        // Forcer un rechargement
                        setParamVersion(prev => prev + 1);
                      }}
                      disabled={isLoading || isApplying}
                      className="bg-gray-500 text-white px-3 py-1 rounded-md hover:bg-opacity-90 transition-colors"
                    >
                      Réinitialiser
                    </button>
                  </div>
                </div>
              </DisclosurePanel>
            </>
          )}
        </Disclosure>
      </div>
    </div>
  );
};

export default JobSkillsTree;
