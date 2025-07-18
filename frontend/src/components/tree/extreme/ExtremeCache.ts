import { PositionedNode, CompetenceTreeData } from '../types';

/**
 * Ultra-aggressive caching system using IndexedDB and memory
 * Provides near-instantaneous load times for previously viewed trees
 */
export class ExtremeCache {
  private memoryCache = new Map<string, any>();
  private dbName = 'CompetenceTreeCache';
  private dbVersion = 1;
  private db: IDBDatabase | null = null;
  private maxMemoryCacheSize = 50; // Limit memory cache size
  private cacheHitCount = 0;
  private cacheMissCount = 0;

  constructor() {
    this.initializeDB();
  }

  private async initializeDB(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);
      
      request.onerror = () => {
        console.error('Failed to initialize IndexedDB');
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        console.log('🚀 ExtremeCache IndexedDB initialized');
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;
        
        // Create stores for different data types
        if (!db.objectStoreNames.contains('treeData')) {
          db.createObjectStore('treeData', { keyPath: 'id' });
        }
        
        if (!db.objectStoreNames.contains('nodePositions')) {
          db.createObjectStore('nodePositions', { keyPath: 'id' });
        }
        
        if (!db.objectStoreNames.contains('spatialIndex')) {
          db.createObjectStore('spatialIndex', { keyPath: 'id' });
        }
        
        if (!db.objectStoreNames.contains('userPreferences')) {
          db.createObjectStore('userPreferences', { keyPath: 'id' });
        }
      };
    });
  }

  /**
   * Cache tree data with aggressive compression
   */
  async cacheTreeData(graphId: string, data: CompetenceTreeData): Promise<void> {
    const cacheKey = `tree_${graphId}`;
    
    // Compress data for storage
    const compressedData = this.compressTreeData(data);
    
    // Store in memory cache
    this.setMemoryCache(cacheKey, compressedData);
    
    // Store in IndexedDB
    if (this.db) {
      try {
        const transaction = this.db.transaction(['treeData'], 'readwrite');
        const store = transaction.objectStore('treeData');
        
        await new Promise<void>((resolve, reject) => {
          const request = store.put({
            id: cacheKey,
            data: compressedData,
            timestamp: Date.now(),
            version: this.dbVersion
          });
          
          request.onsuccess = () => resolve();
          request.onerror = () => reject(request.error);
        });
        
        console.log(`📦 Cached tree data for ${graphId}`);
      } catch (error) {
        console.error('Failed to cache tree data:', error);
      }
    }
  }

  /**
   * Retrieve cached tree data
   */
  async getCachedTreeData(graphId: string): Promise<CompetenceTreeData | null> {
    const cacheKey = `tree_${graphId}`;
    
    // Check memory cache first
    const memoryData = this.getMemoryCache(cacheKey);
    if (memoryData) {
      this.cacheHitCount++;
      return this.decompressTreeData(memoryData);
    }
    
    // Check IndexedDB
    if (this.db) {
      try {
        const transaction = this.db.transaction(['treeData'], 'readonly');
        const store = transaction.objectStore('treeData');
        
        const data = await new Promise<any>((resolve, reject) => {
          const request = store.get(cacheKey);
          request.onsuccess = () => resolve(request.result);
          request.onerror = () => reject(request.error);
        });
        
        if (data && this.isValidCacheEntry(data)) {
          this.cacheHitCount++;
          // Move to memory cache for faster access
          this.setMemoryCache(cacheKey, data.data);
          return this.decompressTreeData(data.data);
        }
      } catch (error) {
        console.error('Failed to retrieve cached tree data:', error);
      }
    }
    
    this.cacheMissCount++;
    return null;
  }

  /**
   * Cache node positions
   */
  async cacheNodePositions(graphId: string, positions: PositionedNode[]): Promise<void> {
    const cacheKey = `positions_${graphId}`;
    
    // Compress positions data
    const compressedPositions = this.compressPositions(positions);
    
    // Store in memory cache
    this.setMemoryCache(cacheKey, compressedPositions);
    
    // Store in IndexedDB
    if (this.db) {
      try {
        const transaction = this.db.transaction(['nodePositions'], 'readwrite');
        const store = transaction.objectStore('nodePositions');
        
        await new Promise<void>((resolve, reject) => {
          const request = store.put({
            id: cacheKey,
            positions: compressedPositions,
            timestamp: Date.now()
          });
          
          request.onsuccess = () => resolve();
          request.onerror = () => reject(request.error);
        });
        
        console.log(`📍 Cached node positions for ${graphId}`);
      } catch (error) {
        console.error('Failed to cache node positions:', error);
      }
    }
  }

  /**
   * Retrieve cached node positions
   */
  async getCachedNodePositions(graphId: string): Promise<PositionedNode[] | null> {
    const cacheKey = `positions_${graphId}`;
    
    // Check memory cache first
    const memoryData = this.getMemoryCache(cacheKey);
    if (memoryData) {
      this.cacheHitCount++;
      return this.decompressPositions(memoryData);
    }
    
    // Check IndexedDB
    if (this.db) {
      try {
        const transaction = this.db.transaction(['nodePositions'], 'readonly');
        const store = transaction.objectStore('nodePositions');
        
        const data = await new Promise<any>((resolve, reject) => {
          const request = store.get(cacheKey);
          request.onsuccess = () => resolve(request.result);
          request.onerror = () => reject(request.error);
        });
        
        if (data && this.isValidCacheEntry(data)) {
          this.cacheHitCount++;
          // Move to memory cache
          this.setMemoryCache(cacheKey, data.positions);
          return this.decompressPositions(data.positions);
        }
      } catch (error) {
        console.error('Failed to retrieve cached positions:', error);
      }
    }
    
    this.cacheMissCount++;
    return null;
  }

  /**
   * Cache spatial index
   */
  async cacheSpatialIndex(graphId: string, index: Map<string, PositionedNode[]>): Promise<void> {
    const cacheKey = `spatial_${graphId}`;
    
    // Convert Map to serializable format
    const serializedIndex = Object.fromEntries(index);
    
    // Store in memory cache
    this.setMemoryCache(cacheKey, serializedIndex);
    
    // Store in IndexedDB
    if (this.db) {
      try {
        const transaction = this.db.transaction(['spatialIndex'], 'readwrite');
        const store = transaction.objectStore('spatialIndex');
        
        await new Promise<void>((resolve, reject) => {
          const request = store.put({
            id: cacheKey,
            index: serializedIndex,
            timestamp: Date.now()
          });
          
          request.onsuccess = () => resolve();
          request.onerror = () => reject(request.error);
        });
        
        console.log(`🗺️ Cached spatial index for ${graphId}`);
      } catch (error) {
        console.error('Failed to cache spatial index:', error);
      }
    }
  }

  /**
   * Retrieve cached spatial index
   */
  async getCachedSpatialIndex(graphId: string): Promise<Map<string, PositionedNode[]> | null> {
    const cacheKey = `spatial_${graphId}`;
    
    // Check memory cache first
    const memoryData = this.getMemoryCache(cacheKey);
    if (memoryData) {
      this.cacheHitCount++;
      return new Map(Object.entries(memoryData));
    }
    
    // Check IndexedDB
    if (this.db) {
      try {
        const transaction = this.db.transaction(['spatialIndex'], 'readonly');
        const store = transaction.objectStore('spatialIndex');
        
        const data = await new Promise<any>((resolve, reject) => {
          const request = store.get(cacheKey);
          request.onsuccess = () => resolve(request.result);
          request.onerror = () => reject(request.error);
        });
        
        if (data && this.isValidCacheEntry(data)) {
          this.cacheHitCount++;
          // Move to memory cache
          this.setMemoryCache(cacheKey, data.index);
          return new Map(Object.entries(data.index));
        }
      } catch (error) {
        console.error('Failed to retrieve cached spatial index:', error);
      }
    }
    
    this.cacheMissCount++;
    return null;
  }

  /**
   * Cache user preferences
   */
  async cacheUserPreferences(userId: string, preferences: any): Promise<void> {
    const cacheKey = `prefs_${userId}`;
    
    // Store in memory cache
    this.setMemoryCache(cacheKey, preferences);
    
    // Store in IndexedDB
    if (this.db) {
      try {
        const transaction = this.db.transaction(['userPreferences'], 'readwrite');
        const store = transaction.objectStore('userPreferences');
        
        await new Promise<void>((resolve, reject) => {
          const request = store.put({
            id: cacheKey,
            preferences,
            timestamp: Date.now()
          });
          
          request.onsuccess = () => resolve();
          request.onerror = () => reject(request.error);
        });
        
        console.log(`⚙️ Cached user preferences for ${userId}`);
      } catch (error) {
        console.error('Failed to cache user preferences:', error);
      }
    }
  }

  /**
   * Get cache statistics
   */
  getStats(): {
    memoryCacheSize: number;
    cacheHitRate: number;
    totalRequests: number;
    hitCount: number;
    missCount: number;
  } {
    const totalRequests = this.cacheHitCount + this.cacheMissCount;
    const hitRate = totalRequests > 0 ? (this.cacheHitCount / totalRequests) * 100 : 0;
    
    return {
      memoryCacheSize: this.memoryCache.size,
      cacheHitRate: hitRate,
      totalRequests,
      hitCount: this.cacheHitCount,
      missCount: this.cacheMissCount
    };
  }

  /**
   * Clear all caches
   */
  async clearAll(): Promise<void> {
    // Clear memory cache
    this.memoryCache.clear();
    
    // Clear IndexedDB
    if (this.db) {
      try {
        const stores = ['treeData', 'nodePositions', 'spatialIndex', 'userPreferences'];
        
        for (const storeName of stores) {
          const transaction = this.db.transaction([storeName], 'readwrite');
          const store = transaction.objectStore(storeName);
          await new Promise<void>((resolve, reject) => {
            const request = store.clear();
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
          });
        }
        
        console.log('🧹 Cleared all caches');
      } catch (error) {
        console.error('Failed to clear caches:', error);
      }
    }
    
    // Reset counters
    this.cacheHitCount = 0;
    this.cacheMissCount = 0;
  }

  private setMemoryCache(key: string, value: any): void {
    // Implement LRU eviction
    if (this.memoryCache.size >= this.maxMemoryCacheSize) {
      const firstKey = this.memoryCache.keys().next().value;
      this.memoryCache.delete(firstKey);
    }
    
    this.memoryCache.set(key, value);
  }

  private getMemoryCache(key: string): any {
    return this.memoryCache.get(key);
  }

  private compressTreeData(data: CompetenceTreeData): any {
    // Simple compression - remove unnecessary fields
    return {
      nodes: data.nodes.map(node => ({
        id: node.id,
        label: node.label || node.skill_label,
        type: node.type,
        is_anchor: node.is_anchor,
        visible: node.visible,
        state: node.state,
        xp_reward: node.xp_reward
      })),
      edges: data.edges.map(edge => ({
        source: edge.source,
        target: edge.target
      })),
      graph_id: data.graph_id
    };
  }

  private decompressTreeData(compressed: any): CompetenceTreeData {
    return {
      nodes: compressed.nodes.map((node: any) => ({
        ...node,
        skill_label: node.label
      })),
      edges: compressed.edges,
      graph_id: compressed.graph_id
    };
  }

  private compressPositions(positions: PositionedNode[]): any {
    // Store only essential position data
    return positions.map(pos => ({
      id: pos.id,
      x: Math.round(pos.x),
      y: Math.round(pos.y),
      type: pos.type,
      is_anchor: pos.is_anchor
    }));
  }

  private decompressPositions(compressed: any): PositionedNode[] {
    return compressed.map((pos: any) => ({
      ...pos,
      label: pos.label || pos.skill_label || 'Unknown'
    }));
  }

  private isValidCacheEntry(entry: any): boolean {
    // Check if cache entry is not too old (24 hours)
    const maxAge = 24 * 60 * 60 * 1000; // 24 hours
    return entry.timestamp && (Date.now() - entry.timestamp) < maxAge;
  }
}

// Singleton instance
let extremeCache: ExtremeCache | null = null;

/**
 * Get the singleton ExtremeCache instance
 */
export function getExtremeCache(): ExtremeCache {
  if (!extremeCache) {
    extremeCache = new ExtremeCache();
  }
  return extremeCache;
}