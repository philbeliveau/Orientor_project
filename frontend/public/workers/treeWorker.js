// Ultra-fast Web Worker for heavy tree calculations
// Runs in background thread to prevent UI blocking

class TreeWorker {
  constructor() {
    this.spatialIndex = new Map();
    this.nodeCache = new Map();
    this.edgeCache = new Map();
    this.layoutCache = new Map();
    
    console.log('🚀 TreeWorker initialized');
  }

  // Spatial indexing for ultra-fast viewport culling
  buildSpatialIndex(nodes, gridSize = 500) {
    const startTime = performance.now();
    
    this.spatialIndex.clear();
    
    for (const node of nodes) {
      const cellX = Math.floor(node.x / gridSize);
      const cellY = Math.floor(node.y / gridSize);
      const cellKey = `${cellX},${cellY}`;
      
      if (!this.spatialIndex.has(cellKey)) {
        this.spatialIndex.set(cellKey, []);
      }
      
      this.spatialIndex.get(cellKey).push(node);
    }
    
    const endTime = performance.now();
    console.log(`🔥 Spatial index built in ${endTime - startTime}ms for ${nodes.length} nodes`);
    
    return {
      success: true,
      indexSize: this.spatialIndex.size,
      buildTime: endTime - startTime
    };
  }

  // Ultra-fast viewport culling using spatial index
  cullViewport(bounds, gridSize = 500) {
    const startTime = performance.now();
    
    const visibleNodes = [];
    
    const startX = Math.floor(bounds.left / gridSize);
    const endX = Math.ceil(bounds.right / gridSize);
    const startY = Math.floor(bounds.top / gridSize);
    const endY = Math.ceil(bounds.bottom / gridSize);

    for (let x = startX; x <= endX; x++) {
      for (let y = startY; y <= endY; y++) {
        const cellKey = `${x},${y}`;
        const cell = this.spatialIndex.get(cellKey);
        
        if (cell) {
          for (const node of cell) {
            if (this.isNodeInBounds(node, bounds)) {
              visibleNodes.push(node);
            }
          }
        }
      }
    }

    const endTime = performance.now();
    
    return {
      visibleNodes,
      totalNodes: visibleNodes.length,
      cullTime: endTime - startTime
    };
  }

  // Fast node bounds checking
  isNodeInBounds(node, bounds) {
    const nodeWidth = node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200);
    const nodeHeight = node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100);
    
    return node.x + nodeWidth/2 >= bounds.left &&
           node.x - nodeWidth/2 <= bounds.right &&
           node.y + nodeHeight/2 >= bounds.top &&
           node.y - nodeHeight/2 <= bounds.bottom;
  }

  // Optimized layout calculation
  calculateOptimizedLayout(nodes, edges, centerX, centerY) {
    const startTime = performance.now();
    
    // Check cache first
    const cacheKey = `${nodes.length}-${edges.length}-${centerX}-${centerY}`;
    if (this.layoutCache.has(cacheKey)) {
      return {
        nodes: this.layoutCache.get(cacheKey),
        cached: true,
        calculateTime: 0
      };
    }

    const positioned = [];
    const visibleNodes = nodes.filter(n => n.visible !== false);
    const anchors = visibleNodes.filter(n => n.is_anchor);
    
    // Build adjacency map
    const adjacencyMap = new Map();
    const parentMap = new Map();
    
    for (const edge of edges) {
      const sourceVisible = visibleNodes.find(n => n.id === edge.source);
      const targetVisible = visibleNodes.find(n => n.id === edge.target);
      
      if (sourceVisible && targetVisible) {
        if (!adjacencyMap.has(edge.source)) {
          adjacencyMap.set(edge.source, []);
        }
        adjacencyMap.get(edge.source).push(edge.target);
        parentMap.set(edge.target, edge.source);
      }
    }

    // Position anchors in center
    if (anchors.length > 0) {
      if (anchors.length === 1) {
        positioned.push({
          ...anchors[0],
          x: centerX,
          y: centerY
        });
      } else {
        const anchorRadius = 250; // Smaller radius for better performance
        for (let i = 0; i < anchors.length; i++) {
          const angle = (2 * Math.PI * i) / anchors.length;
          positioned.push({
            ...anchors[i],
            x: centerX + anchorRadius * Math.cos(angle),
            y: centerY + anchorRadius * Math.sin(angle)
          });
        }
      }
    }

    // Position other nodes in concentric circles
    const processedNodes = new Set(anchors.map(a => a.id));
    let currentLevel = 0;
    const maxLevels = 3; // Reduced levels for performance

    while (currentLevel < maxLevels && processedNodes.size < visibleNodes.length) {
      const parentNodes = positioned.filter(p => !processedNodes.has(p.id) === false);
      const childNodes = [];

      for (const parent of parentNodes) {
        const children = (adjacencyMap.get(parent.id) || [])
          .map(id => visibleNodes.find(n => n.id === id))
          .filter(node => node && !processedNodes.has(node.id));
        
        childNodes.push(...children);
        for (const child of children) {
          if (child) processedNodes.add(child.id);
        }
      }

      if (childNodes.length === 0) break;

      // Position children in ring
      const radius = 400 + currentLevel * 300; // Smaller spacing
      for (let i = 0; i < childNodes.length; i++) {
        const angle = (2 * Math.PI * i) / childNodes.length;
        positioned.push({
          ...childNodes[i],
          x: centerX + radius * Math.cos(angle),
          y: centerY + radius * Math.sin(angle)
        });
      }

      currentLevel++;
    }

    // Position remaining nodes
    const remainingNodes = visibleNodes.filter(node => !positioned.find(p => p.id === node.id));
    if (remainingNodes.length > 0) {
      const outerRadius = 400 + currentLevel * 300;
      for (let i = 0; i < remainingNodes.length; i++) {
        const angle = (2 * Math.PI * i) / remainingNodes.length;
        positioned.push({
          ...remainingNodes[i],
          x: centerX + outerRadius * Math.cos(angle),
          y: centerY + outerRadius * Math.sin(angle)
        });
      }
    }

    const endTime = performance.now();
    
    // Cache result
    this.layoutCache.set(cacheKey, positioned);
    
    return {
      nodes: positioned,
      cached: false,
      calculateTime: endTime - startTime
    };
  }

  // Batch process multiple operations
  batchProcess(operations) {
    const startTime = performance.now();
    const results = [];
    
    for (const operation of operations) {
      switch (operation.type) {
        case 'buildSpatialIndex':
          results.push(this.buildSpatialIndex(operation.nodes, operation.gridSize));
          break;
        case 'cullViewport':
          results.push(this.cullViewport(operation.bounds, operation.gridSize));
          break;
        case 'calculateLayout':
          results.push(this.calculateOptimizedLayout(
            operation.nodes, 
            operation.edges, 
            operation.centerX, 
            operation.centerY
          ));
          break;
      }
    }
    
    const endTime = performance.now();
    
    return {
      results,
      totalTime: endTime - startTime
    };
  }

  // Clear all caches
  clearCaches() {
    this.nodeCache.clear();
    this.edgeCache.clear();
    this.layoutCache.clear();
    this.spatialIndex.clear();
    
    return { success: true };
  }

  // Get performance stats
  getStats() {
    return {
      spatialIndexSize: this.spatialIndex.size,
      nodeCacheSize: this.nodeCache.size,
      edgeCacheSize: this.edgeCache.size,
      layoutCacheSize: this.layoutCache.size,
      memoryUsage: performance.memory ? {
        used: performance.memory.usedJSHeapSize,
        total: performance.memory.totalJSHeapSize,
        limit: performance.memory.jsHeapSizeLimit
      } : null
    };
  }
}

// Initialize worker
const worker = new TreeWorker();

// Message handler
self.addEventListener('message', (event) => {
  const { id, type, data } = event.data;
  
  try {
    let result;
    
    switch (type) {
      case 'buildSpatialIndex':
        result = worker.buildSpatialIndex(data.nodes, data.gridSize);
        break;
      case 'cullViewport':
        result = worker.cullViewport(data.bounds, data.gridSize);
        break;
      case 'calculateLayout':
        result = worker.calculateOptimizedLayout(data.nodes, data.edges, data.centerX, data.centerY);
        break;
      case 'batchProcess':
        result = worker.batchProcess(data.operations);
        break;
      case 'clearCaches':
        result = worker.clearCaches();
        break;
      case 'getStats':
        result = worker.getStats();
        break;
      default:
        throw new Error(`Unknown operation: ${type}`);
    }
    
    self.postMessage({
      id,
      type: 'success',
      result
    });
    
  } catch (error) {
    self.postMessage({
      id,
      type: 'error',
      error: error.message
    });
  }
});

console.log('🚀 TreeWorker ready for operations');