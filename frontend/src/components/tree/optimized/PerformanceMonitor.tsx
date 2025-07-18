import React, { useState, useEffect, useCallback, useRef } from 'react';

interface PerformanceMetrics {
  fps: number;
  renderTime: number;
  memoryUsage: number;
  nodeCount: number;
  edgeCount: number;
  visibleNodes: number;
  culledNodes: number;
  averageFrameTime: number;
}

interface PerformanceMonitorProps {
  nodeCount: number;
  edgeCount: number;
  visibleNodes: number;
  onMetricsUpdate?: (metrics: PerformanceMetrics) => void;
  showStats?: boolean;
}

const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  nodeCount,
  edgeCount,
  visibleNodes,
  onMetricsUpdate,
  showStats = false
}) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    fps: 0,
    renderTime: 0,
    memoryUsage: 0,
    nodeCount: 0,
    edgeCount: 0,
    visibleNodes: 0,
    culledNodes: 0,
    averageFrameTime: 0
  });

  const frameTimesRef = useRef<number[]>([]);
  const lastFrameTimeRef = useRef<number>(performance.now());
  const animationFrameRef = useRef<number>();

  // Calculate FPS and frame times
  const measurePerformance = useCallback(() => {
    const now = performance.now();
    const frameTime = now - lastFrameTimeRef.current;
    lastFrameTimeRef.current = now;

    // Keep last 60 frame times for average
    frameTimesRef.current.push(frameTime);
    if (frameTimesRef.current.length > 60) {
      frameTimesRef.current.shift();
    }

    const averageFrameTime = frameTimesRef.current.reduce((a, b) => a + b, 0) / frameTimesRef.current.length;
    const fps = Math.round(1000 / averageFrameTime);

    // Get memory usage if available
    let memoryUsage = 0;
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      memoryUsage = Math.round(memory.usedJSHeapSize / 1024 / 1024); // MB
    }

    const newMetrics: PerformanceMetrics = {
      fps,
      renderTime: frameTime,
      memoryUsage,
      nodeCount,
      edgeCount,
      visibleNodes,
      culledNodes: nodeCount - visibleNodes,
      averageFrameTime
    };

    setMetrics(newMetrics);
    onMetricsUpdate?.(newMetrics);

    animationFrameRef.current = requestAnimationFrame(measurePerformance);
  }, [nodeCount, edgeCount, visibleNodes, onMetricsUpdate]);

  useEffect(() => {
    animationFrameRef.current = requestAnimationFrame(measurePerformance);
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [measurePerformance]);

  // Performance warnings
  const getPerformanceStatus = useCallback(() => {
    if (metrics.fps < 30) return { status: 'poor', color: '#ef4444' };
    if (metrics.fps < 45) return { status: 'fair', color: '#f59e0b' };
    return { status: 'good', color: '#10b981' };
  }, [metrics.fps]);

  const performanceStatus = getPerformanceStatus();

  if (!showStats) return null;

  return (
    <div style={{
      position: 'absolute',
      top: '10px',
      right: '10px',
      background: 'rgba(0, 0, 0, 0.9)',
      color: 'white',
      padding: '12px',
      borderRadius: '8px',
      fontSize: '11px',
      fontFamily: 'monospace',
      minWidth: '200px',
      zIndex: 1000
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        marginBottom: '8px',
        fontSize: '12px',
        fontWeight: '600'
      }}>
        <div style={{
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: performanceStatus.color,
          marginRight: '8px'
        }} />
        Performance Monitor
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px' }}>
        <div>FPS:</div>
        <div style={{ color: performanceStatus.color, fontWeight: '600' }}>
          {metrics.fps}
        </div>
        
        <div>Frame Time:</div>
        <div>{metrics.averageFrameTime.toFixed(1)}ms</div>
        
        <div>Memory:</div>
        <div>{metrics.memoryUsage}MB</div>
        
        <div>Total Nodes:</div>
        <div>{metrics.nodeCount}</div>
        
        <div>Visible:</div>
        <div style={{ color: '#10b981' }}>{metrics.visibleNodes}</div>
        
        <div>Culled:</div>
        <div style={{ color: '#6b7280' }}>{metrics.culledNodes}</div>
        
        <div>Edges:</div>
        <div>{metrics.edgeCount}</div>
      </div>

      {/* Performance tips */}
      {metrics.fps < 30 && (
        <div style={{
          marginTop: '8px',
          padding: '8px',
          background: 'rgba(239, 68, 68, 0.1)',
          borderRadius: '4px',
          fontSize: '10px',
          color: '#fca5a5'
        }}>
          ⚠️ Low FPS detected
          <br />
          Try zooming out or reducing visible nodes
        </div>
      )}

      {metrics.memoryUsage > 100 && (
        <div style={{
          marginTop: '8px',
          padding: '8px',
          background: 'rgba(245, 158, 11, 0.1)',
          borderRadius: '4px',
          fontSize: '10px',
          color: '#fbbf24'
        }}>
          🔥 High memory usage
          <br />
          Consider refreshing the page
        </div>
      )}

      {/* Performance score */}
      <div style={{
        marginTop: '8px',
        padding: '6px',
        background: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '4px',
        textAlign: 'center'
      }}>
        <div style={{ fontSize: '10px', color: '#9ca3af' }}>Performance Score</div>
        <div style={{ 
          fontSize: '14px', 
          fontWeight: '600',
          color: performanceStatus.color
        }}>
          {performanceStatus.status.toUpperCase()}
        </div>
      </div>
    </div>
  );
};

export default React.memo(PerformanceMonitor);