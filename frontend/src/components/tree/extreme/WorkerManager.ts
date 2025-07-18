import { PositionedNode } from '../types';

interface WorkerMessage {
  id: string;
  type: string;
  data?: any;
}

interface WorkerResponse {
  id: string;
  type: 'success' | 'error';
  result?: any;
  error?: string;
}

/**
 * Ultra-fast Web Worker manager for offloading heavy computations
 */
export class WorkerManager {
  private worker: Worker | null = null;
  private messageId = 0;
  private pendingMessages = new Map<string, {
    resolve: (value: any) => void;
    reject: (error: Error) => void;
    timestamp: number;
  }>();

  constructor() {
    this.initializeWorker();
  }

  private initializeWorker(): void {
    try {
      this.worker = new Worker('/workers/treeWorker.js');
      
      this.worker.onmessage = (event: MessageEvent<WorkerResponse>) => {
        const { id, type, result, error } = event.data;
        const pending = this.pendingMessages.get(id);
        
        if (pending) {
          this.pendingMessages.delete(id);
          
          if (type === 'success') {
            pending.resolve(result);
          } else {
            pending.reject(new Error(error || 'Worker error'));
          }
        }
      };

      this.worker.onerror = (error) => {
        console.error('Worker error:', error);
        // Reject all pending messages
        const pendingEntries = Array.from(this.pendingMessages.entries());
        for (const [id, pending] of pendingEntries) {
          pending.reject(new Error('Worker crashed'));
        }
        this.pendingMessages.clear();
      };

      console.log('🚀 WorkerManager initialized');
    } catch (error) {
      console.error('Failed to initialize worker:', error);
    }
  }

  private postMessage(type: string, data?: any): Promise<any> {
    return new Promise((resolve, reject) => {
      if (!this.worker) {
        reject(new Error('Worker not available'));
        return;
      }

      const id = `msg_${++this.messageId}`;
      const message: WorkerMessage = { id, type, data };
      
      this.pendingMessages.set(id, {
        resolve,
        reject,
        timestamp: Date.now()
      });

      this.worker.postMessage(message);

      // Timeout after 10 seconds
      setTimeout(() => {
        const pending = this.pendingMessages.get(id);
        if (pending) {
          this.pendingMessages.delete(id);
          reject(new Error('Worker timeout'));
        }
      }, 10000);
    });
  }

  /**
   * Build spatial index for ultra-fast viewport culling
   */
  async buildSpatialIndex(nodes: PositionedNode[], gridSize: number = 500): Promise<{
    success: boolean;
    indexSize: number;
    buildTime: number;
  }> {
    return this.postMessage('buildSpatialIndex', { nodes, gridSize });
  }

  /**
   * Cull viewport using spatial index
   */
  async cullViewport(bounds: {
    left: number;
    right: number;
    top: number;
    bottom: number;
  }, gridSize: number = 500): Promise<{
    visibleNodes: PositionedNode[];
    totalNodes: number;
    cullTime: number;
  }> {
    return this.postMessage('cullViewport', { bounds, gridSize });
  }

  /**
   * Calculate optimized layout
   */
  async calculateLayout(
    nodes: PositionedNode[],
    edges: { source: string; target: string }[],
    centerX: number,
    centerY: number
  ): Promise<{
    nodes: PositionedNode[];
    cached: boolean;
    calculateTime: number;
  }> {
    return this.postMessage('calculateLayout', { nodes, edges, centerX, centerY });
  }

  /**
   * Batch process multiple operations for maximum efficiency
   */
  async batchProcess(operations: Array<{
    type: string;
    [key: string]: any;
  }>): Promise<{
    results: any[];
    totalTime: number;
  }> {
    return this.postMessage('batchProcess', { operations });
  }

  /**
   * Clear all worker caches
   */
  async clearCaches(): Promise<{ success: boolean }> {
    return this.postMessage('clearCaches');
  }

  /**
   * Get worker performance statistics
   */
  async getStats(): Promise<{
    spatialIndexSize: number;
    nodeCacheSize: number;
    edgeCacheSize: number;
    layoutCacheSize: number;
    memoryUsage: any;
  }> {
    return this.postMessage('getStats');
  }

  /**
   * Cleanup worker resources
   */
  destroy(): void {
    if (this.worker) {
      this.worker.terminate();
      this.worker = null;
    }
    
    // Reject all pending messages
    const pendingEntries = Array.from(this.pendingMessages.entries());
    for (const [id, pending] of pendingEntries) {
      pending.reject(new Error('Worker destroyed'));
    }
    this.pendingMessages.clear();
  }

  /**
   * Check if worker is available
   */
  isAvailable(): boolean {
    return this.worker !== null;
  }
}

// Singleton instance
let workerManager: WorkerManager | null = null;

/**
 * Get the singleton WorkerManager instance
 */
export function getWorkerManager(): WorkerManager {
  if (!workerManager) {
    workerManager = new WorkerManager();
  }
  return workerManager;
}

/**
 * Cleanup worker resources
 */
export function destroyWorkerManager(): void {
  if (workerManager) {
    workerManager.destroy();
    workerManager = null;
  }
}