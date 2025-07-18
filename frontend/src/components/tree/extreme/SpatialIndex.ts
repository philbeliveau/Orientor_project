import { PositionedNode } from '../types';

export interface SpatialBounds {
  left: number;
  right: number;
  top: number;
  bottom: number;
}

export interface SpatialCell {
  x: number;
  y: number;
  nodes: PositionedNode[];
}

/**
 * Ultra-fast spatial indexing for O(1) viewport culling
 * Using a grid-based approach for maximum performance
 */
export class SpatialIndex {
  private gridSize: number;
  private grid: Map<string, PositionedNode[]>;
  private nodeToCell: Map<string, string>;

  constructor(gridSize: number = 500) {
    this.gridSize = gridSize;
    this.grid = new Map();
    this.nodeToCell = new Map();
  }

  /**
   * Add a node to the spatial index
   */
  addNode(node: PositionedNode): void {
    const cellKey = this.getCellKey(node.x, node.y);
    
    // Remove from old cell if exists
    this.removeNode(node.id);
    
    // Add to new cell
    if (!this.grid.has(cellKey)) {
      this.grid.set(cellKey, []);
    }
    
    this.grid.get(cellKey)!.push(node);
    this.nodeToCell.set(node.id, cellKey);
  }

  /**
   * Remove a node from the spatial index
   */
  removeNode(nodeId: string): void {
    const cellKey = this.nodeToCell.get(nodeId);
    if (cellKey) {
      const cell = this.grid.get(cellKey);
      if (cell) {
        const index = cell.findIndex(n => n.id === nodeId);
        if (index !== -1) {
          cell.splice(index, 1);
          if (cell.length === 0) {
            this.grid.delete(cellKey);
          }
        }
      }
      this.nodeToCell.delete(nodeId);
    }
  }

  /**
   * Get all nodes within viewport bounds - O(1) performance
   */
  getNodesInBounds(bounds: SpatialBounds): PositionedNode[] {
    const result: PositionedNode[] = [];
    
    const startX = Math.floor(bounds.left / this.gridSize);
    const endX = Math.ceil(bounds.right / this.gridSize);
    const startY = Math.floor(bounds.top / this.gridSize);
    const endY = Math.ceil(bounds.bottom / this.gridSize);

    for (let x = startX; x <= endX; x++) {
      for (let y = startY; y <= endY; y++) {
        const cellKey = `${x},${y}`;
        const cell = this.grid.get(cellKey);
        
        if (cell) {
          // Further filter nodes within exact bounds
          for (const node of cell) {
            if (this.isNodeInBounds(node, bounds)) {
              result.push(node);
            }
          }
        }
      }
    }

    return result;
  }

  /**
   * Update the entire index with new nodes
   */
  updateIndex(nodes: PositionedNode[]): void {
    // Clear existing index
    this.grid.clear();
    this.nodeToCell.clear();

    // Add all nodes
    for (const node of nodes) {
      this.addNode(node);
    }
  }

  /**
   * Get nearest nodes to a point - for mouse interactions
   */
  getNearestNodes(x: number, y: number, maxDistance: number = 100): PositionedNode[] {
    const bounds: SpatialBounds = {
      left: x - maxDistance,
      right: x + maxDistance,
      top: y - maxDistance,
      bottom: y + maxDistance
    };

    const candidates = this.getNodesInBounds(bounds);
    
    return candidates
      .map(node => ({
        node,
        distance: Math.sqrt(Math.pow(node.x - x, 2) + Math.pow(node.y - y, 2))
      }))
      .filter(item => item.distance <= maxDistance)
      .sort((a, b) => a.distance - b.distance)
      .map(item => item.node);
  }

  /**
   * Get statistics about the spatial index
   */
  getStats(): {
    totalCells: number;
    totalNodes: number;
    averageNodesPerCell: number;
    maxNodesPerCell: number;
  } {
    const totalCells = this.grid.size;
    const totalNodes = this.nodeToCell.size;
    
    let maxNodesPerCell = 0;
    const cells = Array.from(this.grid.values());
    for (const cell of cells) {
      maxNodesPerCell = Math.max(maxNodesPerCell, cell.length);
    }

    return {
      totalCells,
      totalNodes,
      averageNodesPerCell: totalCells > 0 ? totalNodes / totalCells : 0,
      maxNodesPerCell
    };
  }

  private getCellKey(x: number, y: number): string {
    const cellX = Math.floor(x / this.gridSize);
    const cellY = Math.floor(y / this.gridSize);
    return `${cellX},${cellY}`;
  }

  private isNodeInBounds(node: PositionedNode, bounds: SpatialBounds): boolean {
    const nodeWidth = node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200);
    const nodeHeight = node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100);
    
    return node.x + nodeWidth/2 >= bounds.left &&
           node.x - nodeWidth/2 <= bounds.right &&
           node.y + nodeHeight/2 >= bounds.top &&
           node.y - nodeHeight/2 <= bounds.bottom;
  }
}

/**
 * Memory pool for frequently created objects
 */
export class ObjectPool<T> {
  private pool: T[] = [];
  private createFn: () => T;
  private resetFn: (obj: T) => void;

  constructor(createFn: () => T, resetFn: (obj: T) => void, initialSize: number = 100) {
    this.createFn = createFn;
    this.resetFn = resetFn;
    
    // Pre-populate pool
    for (let i = 0; i < initialSize; i++) {
      this.pool.push(createFn());
    }
  }

  acquire(): T {
    const obj = this.pool.pop();
    if (obj) {
      this.resetFn(obj);
      return obj;
    }
    return this.createFn();
  }

  release(obj: T): void {
    this.pool.push(obj);
  }

  clear(): void {
    this.pool = [];
  }
}

/**
 * Throttled event handler for performance
 */
export class ThrottledEventHandler {
  private lastTime: number = 0;
  private throttleMs: number;
  private callback: (...args: any[]) => void;

  constructor(callback: (...args: any[]) => void, throttleMs: number = 16) {
    this.callback = callback;
    this.throttleMs = throttleMs;
  }

  handle(...args: any[]): void {
    const now = performance.now();
    if (now - this.lastTime >= this.throttleMs) {
      this.callback(...args);
      this.lastTime = now;
    }
  }
}

/**
 * Performance monitor for real-time optimization
 */
export class PerformanceTracker {
  private frameTimes: number[] = [];
  private maxSamples: number = 60;
  private lastFrameTime: number = 0;

  startFrame(): void {
    this.lastFrameTime = performance.now();
  }

  endFrame(): void {
    const frameTime = performance.now() - this.lastFrameTime;
    this.frameTimes.push(frameTime);
    
    if (this.frameTimes.length > this.maxSamples) {
      this.frameTimes.shift();
    }
  }

  getAverageFPS(): number {
    if (this.frameTimes.length === 0) return 0;
    
    const avgFrameTime = this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length;
    return Math.round(1000 / avgFrameTime);
  }

  getAverageFrameTime(): number {
    if (this.frameTimes.length === 0) return 0;
    return this.frameTimes.reduce((a, b) => a + b, 0) / this.frameTimes.length;
  }

  isPerformanceGood(): boolean {
    return this.getAverageFPS() >= 45;
  }

  shouldReduceQuality(): boolean {
    return this.getAverageFPS() < 30;
  }
}