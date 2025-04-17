import React, { useCallback } from 'react';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  NodeMouseHandler,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion } from 'framer-motion';

interface SkillNodeData {
  label: string;
  level: number;
  description: string;
}

interface CustomNode extends Node {
  type: 'skill';
  data: SkillNodeData;
}

interface SkillTreeCanvasProps {
  onNodeClick?: (node: CustomNode) => void;
}

const SkillTreeCanvas: React.FC<SkillTreeCanvasProps> = ({ onNodeClick }) => {
  const initialNodes: CustomNode[] = [
    {
      id: '1',
      type: 'skill',
      data: { label: 'Problem Solving', level: 3, description: 'Core analytical skills' },
      position: { x: 250, y: 0 },
    },
    {
      id: '2',
      type: 'skill',
      data: { label: 'Data Analysis', level: 2, description: 'Data interpretation and visualization' },
      position: { x: 100, y: 100 },
    },
    {
      id: '3',
      type: 'skill',
      data: { label: 'Communication', level: 4, description: 'Effective verbal and written skills' },
      position: { x: 400, y: 100 },
    },
  ];

  const initialEdges: Edge[] = [
    { id: 'e1-2', source: '1', target: '2' },
    { id: 'e1-3', source: '1', target: '3' },
  ];

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => setEdges((eds: Edge[]) => addEdge(params, eds)),
    [setEdges]
  );

  const handleNodeClick: NodeMouseHandler = useCallback(
    (event: React.MouseEvent, node: Node) => {
      if (onNodeClick && node.type === 'skill') {
        onNodeClick(node as CustomNode);
      }
    },
    [onNodeClick]
  );

  const CustomNode = ({ data }: { data: SkillNodeData }) => (
    <motion.div
      whileHover={{ scale: 1.05 }}
      className="px-4 py-2 shadow-md rounded-full bg-white border-2 border-blue-200"
    >
      <div className="text-sm font-medium text-gray-700">{data.label}</div>
      <div className="text-xs text-gray-500">Level: {data.level}</div>
    </motion.div>
  );

  const nodeTypes = {
    skill: CustomNode,
  };

  return (
    <div className="w-full h-[calc(100vh-4rem)] bg-gradient-to-br from-white to-blue-50">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background color="#aaa" gap={16} />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default SkillTreeCanvas; 