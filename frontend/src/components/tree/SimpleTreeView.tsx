import React, { useState, useEffect } from 'react';
import { useCompetenceTree } from './useCompetenceTree';

interface SimpleTreeViewProps {
  graphId: string;
}

const SimpleTreeView: React.FC<SimpleTreeViewProps> = ({ graphId }) => {
  console.log('🚀 SimpleTreeView mounted with graphId:', graphId);
  
  const {
    treeData,
    nodes,
    edges,
    loading,
    error,
    getProgress
  } = useCompetenceTree(graphId);

  useEffect(() => {
    console.log('📊 SimpleTreeView render state:', {
      loading,
      error,
      hasTreeData: !!treeData,
      nodesCount: nodes.length,
      edgesCount: edges.length
    });
  }, [loading, error, treeData, nodes.length, edges.length]);

  if (loading) {
    console.log('⏳ SimpleTreeView: Still loading...');
    return (
      <div style={{ 
        height: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: '#f8fafc'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ 
            width: '60px', 
            height: '60px', 
            border: '4px solid #e2e8f0',
            borderTop: '4px solid #3b82f6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 20px'
          }} />
          <p style={{ color: '#6b7280', fontSize: '16px' }}>Loading tree data...</p>
          <p style={{ color: '#9ca3af', fontSize: '14px' }}>Graph ID: {graphId}</p>
        </div>
      </div>
    );
  }

  if (error) {
    console.log('❌ SimpleTreeView: Error state:', error);
    return (
      <div style={{ 
        height: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: '#fef2f2'
      }}>
        <div style={{ textAlign: 'center', color: '#dc2626' }}>
          <h2>Error Loading Tree</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!treeData || nodes.length === 0) {
    console.log('🚫 SimpleTreeView: No data available');
    return (
      <div style={{ 
        height: '100vh', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        background: '#fffbeb'
      }}>
        <div style={{ textAlign: 'center', color: '#d97706' }}>
          <h2>No Tree Data</h2>
          <p>Tree data loaded but no nodes found.</p>
          <p>Nodes: {nodes.length}, Edges: {edges.length}</p>
        </div>
      </div>
    );
  }

  console.log('✅ SimpleTreeView: Rendering tree with', nodes.length, 'nodes');
  
  const progress = getProgress();
  
  return (
    <div style={{ height: '100vh', background: '#f8fafc', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ 
        padding: '20px', 
        background: 'white', 
        borderBottom: '1px solid #e5e7eb',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ margin: '0 0 10px 0', color: '#1f2937' }}>Competence Tree</h1>
        <div style={{ display: 'flex', gap: '20px', fontSize: '14px', color: '#6b7280' }}>
          <span>📊 {nodes.length} nodes</span>
          <span>🔗 {edges.length} edges</span>
          <span>✅ {progress.completed}/{progress.total} completed ({progress.percentage}%)</span>
          <span>🆔 {graphId}</span>
        </div>
      </div>

      {/* Simple tree visualization */}
      <div style={{ 
        height: 'calc(100vh - 120px)', 
        padding: '20px',
        overflow: 'auto'
      }}>
        <div style={{ 
          position: 'relative',
          width: '2000px', // Make it much bigger
          height: '2000px', // Make it much bigger
          margin: '0 auto'
        }}>
          {/* Render nodes as simple circles */}
          {nodes.map((node, index) => {
            const x = (node.x || (index % 10) * 200) + 1000; // Center in bigger space
            const y = (node.y || Math.floor(index / 10) * 150) + 1000; // Center in bigger space
            
            const nodeColor = node.is_anchor ? '#8b5cf6' : 
                            node.type === 'occupation' ? '#3b82f6' :
                            node.type === 'skillgroup' ? '#10b981' : '#6b7280';
            
            return (
              <div
                key={node.id}
                style={{
                  position: 'absolute',
                  left: x,
                  top: y,
                  width: node.is_anchor ? '40px' : '24px',
                  height: node.is_anchor ? '40px' : '24px',
                  backgroundColor: nodeColor,
                  borderRadius: '50%',
                  border: '2px solid white',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  cursor: 'pointer',
                  fontSize: '10px',
                  color: 'white',
                  fontWeight: 'bold',
                  zIndex: 10,
                  transform: 'translate(-50%, -50%)'
                }}
                title={`${node.skill_label || node.id}\nType: ${node.type}`}
                onClick={() => console.log('Node clicked:', node)}
              >
                {node.is_anchor ? '⭐' : '●'}
              </div>
            );
          })}

          {/* Render edges as simple lines */}
          {edges.map((edge, index) => {
            const sourceNode = nodes.find(n => n.id === edge.source);
            const targetNode = nodes.find(n => n.id === edge.target);
            
            if (!sourceNode || !targetNode) return null;
            
            const sourceX = (sourceNode.x || ((nodes.indexOf(sourceNode)) % 10) * 200) + 1000;
            const sourceY = (sourceNode.y || Math.floor((nodes.indexOf(sourceNode)) / 10) * 150) + 1000;
            const targetX = (targetNode.x || ((nodes.indexOf(targetNode)) % 10) * 200) + 1000;
            const targetY = (targetNode.y || Math.floor((nodes.indexOf(targetNode)) / 10) * 150) + 1000;
            
            const length = Math.sqrt(Math.pow(targetX - sourceX, 2) + Math.pow(targetY - sourceY, 2));
            const angle = Math.atan2(targetY - sourceY, targetX - sourceX) * 180 / Math.PI;
            
            return (
              <div
                key={`edge-${index}`}
                style={{
                  position: 'absolute',
                  left: sourceX,
                  top: sourceY,
                  width: length,
                  height: '2px',
                  backgroundColor: '#d1d5db',
                  transformOrigin: '0 50%',
                  transform: `rotate(${angle}deg)`,
                  zIndex: 1
                }}
              />
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default SimpleTreeView;