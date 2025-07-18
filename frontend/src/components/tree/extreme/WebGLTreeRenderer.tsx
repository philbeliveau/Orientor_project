import React, { useRef, useEffect, useCallback, useMemo } from 'react';
import { PositionedNode } from '../types';

interface WebGLTreeRendererProps {
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

// WebGL shaders for maximum performance
const vertexShaderSource = `
  attribute vec2 a_position;
  attribute vec2 a_texCoord;
  attribute vec4 a_color;
  
  uniform vec2 u_resolution;
  uniform vec2 u_translation;
  uniform float u_scale;
  
  varying vec2 v_texCoord;
  varying vec4 v_color;
  
  void main() {
    vec2 scaledPosition = a_position * u_scale;
    vec2 translatedPosition = scaledPosition + u_translation;
    
    vec2 clipSpace = ((translatedPosition / u_resolution) * 2.0) - 1.0;
    gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);
    
    v_texCoord = a_texCoord;
    v_color = a_color;
  }
`;

const fragmentShaderSource = `
  precision mediump float;
  
  uniform sampler2D u_texture;
  
  varying vec2 v_texCoord;
  varying vec4 v_color;
  
  void main() {
    vec4 texColor = texture2D(u_texture, v_texCoord);
    gl_FragColor = texColor * v_color;
  }
`;

// Ultra-optimized WebGL renderer
const WebGLTreeRenderer: React.FC<WebGLTreeRendererProps> = ({
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
  const glRef = useRef<WebGLRenderingContext | null>(null);
  const programRef = useRef<WebGLProgram | null>(null);
  const buffersRef = useRef<{
    position: WebGLBuffer | null;
    texCoord: WebGLBuffer | null;
    color: WebGLBuffer | null;
    indices: WebGLBuffer | null;
  }>({
    position: null,
    texCoord: null,
    color: null,
    indices: null
  });
  const textureRef = useRef<WebGLTexture | null>(null);
  const animationFrameRef = useRef<number>();

  // Aggressive viewport culling with spatial indexing
  const visibleNodes = useMemo(() => {
    const bounds = {
      left: (-panX / zoom) - 500,
      right: (-panX + width) / zoom + 500,
      top: (-panY / zoom) - 500,
      bottom: (-panY + height) / zoom + 500
    };

    // Spatial indexing for O(log n) lookup instead of O(n)
    const spatialIndex = new Map<string, PositionedNode[]>();
    const gridSize = 1000;

    nodes.forEach(node => {
      const gridX = Math.floor(node.x / gridSize);
      const gridY = Math.floor(node.y / gridSize);
      const key = `${gridX},${gridY}`;
      
      if (!spatialIndex.has(key)) {
        spatialIndex.set(key, []);
      }
      spatialIndex.get(key)!.push(node);
    });

    const visibleGrids = [];
    for (let x = Math.floor(bounds.left / gridSize); x <= Math.floor(bounds.right / gridSize); x++) {
      for (let y = Math.floor(bounds.top / gridSize); y <= Math.floor(bounds.bottom / gridSize); y++) {
        const key = `${x},${y}`;
        if (spatialIndex.has(key)) {
          visibleGrids.push(...spatialIndex.get(key)!);
        }
      }
    }

    return visibleGrids.filter(node => {
      const nodeWidth = node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200);
      const nodeHeight = node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100);
      
      return node.x + nodeWidth/2 >= bounds.left &&
             node.x - nodeWidth/2 <= bounds.right &&
             node.y + nodeHeight/2 >= bounds.top &&
             node.y - nodeHeight/2 <= bounds.bottom;
    }).slice(0, 25); // Hard limit for extreme performance
  }, [nodes, panX, panY, zoom, width, height]);

  // Create WebGL shader
  const createShader = useCallback((gl: WebGLRenderingContext, type: number, source: string) => {
    const shader = gl.createShader(type);
    if (!shader) return null;
    
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
      console.error('Shader compilation error:', gl.getShaderInfoLog(shader));
      gl.deleteShader(shader);
      return null;
    }
    
    return shader;
  }, []);

  // Create WebGL program
  const createProgram = useCallback((gl: WebGLRenderingContext) => {
    const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);
    
    if (!vertexShader || !fragmentShader) return null;
    
    const program = gl.createProgram();
    if (!program) return null;
    
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error('Program linking error:', gl.getProgramInfoLog(program));
      gl.deleteProgram(program);
      return null;
    }
    
    return program;
  }, [createShader]);

  // Initialize WebGL
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext('webgl', {
      antialias: false,
      depth: false,
      stencil: false,
      alpha: false,
      premultipliedAlpha: false,
      preserveDrawingBuffer: false
    });

    if (!gl) {
      console.error('WebGL not supported');
      return;
    }

    glRef.current = gl;
    const program = createProgram(gl);
    if (!program) return;

    programRef.current = program;

    // Create buffers
    buffersRef.current = {
      position: gl.createBuffer(),
      texCoord: gl.createBuffer(),
      color: gl.createBuffer(),
      indices: gl.createBuffer()
    };

    // Create texture for node rendering
    const texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);
    
    // Create a simple white texture for now
    const pixel = new Uint8Array([255, 255, 255, 255]);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, pixel);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    
    textureRef.current = texture;

    // Set up WebGL state
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.clearColor(0.97, 0.98, 0.99, 1.0);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);

  }, [createProgram]);

  // Ultra-fast render function
  const render = useCallback(() => {
    const gl = glRef.current;
    const program = programRef.current;
    const buffers = buffersRef.current;
    
    if (!gl || !program || !buffers.position) return;

    // Clear canvas
    gl.clear(gl.COLOR_BUFFER_BIT);

    if (visibleNodes.length === 0) return;

    // Use program
    gl.useProgram(program);

    // Set uniforms
    const resolutionLocation = gl.getUniformLocation(program, 'u_resolution');
    const translationLocation = gl.getUniformLocation(program, 'u_translation');
    const scaleLocation = gl.getUniformLocation(program, 'u_scale');
    
    gl.uniform2f(resolutionLocation, width, height);
    gl.uniform2f(translationLocation, panX, panY);
    gl.uniform1f(scaleLocation, zoom);

    // Create vertex data for visible nodes
    const positions: number[] = [];
    const texCoords: number[] = [];
    const colors: number[] = [];
    const indices: number[] = [];

    visibleNodes.forEach((node, index) => {
      const cardWidth = node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200);
      const cardHeight = node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100);
      
      const x = node.x - cardWidth/2;
      const y = node.y - cardHeight/2;
      
      // Get node color
      let r = 0.42, g = 0.51, b = 0.73; // Default blue
      if (node.type === "skillgroup") {
        r = 0.06; g = 0.72; b = 0.51; // Green
      } else if (node.is_anchor) {
        r = 0.55; g = 0.36; b = 0.95; // Purple
      } else if (savedJobs.has(node.id)) {
        r = 0.96; g = 0.62; b = 0.07; // Orange
      }

      // Create quad vertices
      const vertexIndex = index * 4;
      
      // Positions (quad)
      positions.push(x, y);                    // Bottom-left
      positions.push(x + cardWidth, y);        // Bottom-right
      positions.push(x + cardWidth, y + cardHeight); // Top-right
      positions.push(x, y + cardHeight);       // Top-left
      
      // Texture coordinates
      texCoords.push(0, 0);  // Bottom-left
      texCoords.push(1, 0);  // Bottom-right
      texCoords.push(1, 1);  // Top-right
      texCoords.push(0, 1);  // Top-left
      
      // Colors (same for all vertices)
      for (let i = 0; i < 4; i++) {
        colors.push(r, g, b, 1.0);
      }
      
      // Indices for two triangles per quad
      indices.push(
        vertexIndex, vertexIndex + 1, vertexIndex + 2,
        vertexIndex, vertexIndex + 2, vertexIndex + 3
      );
    });

    // Upload vertex data
    gl.bindBuffer(gl.ARRAY_BUFFER, buffers.position);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.DYNAMIC_DRAW);
    
    gl.bindBuffer(gl.ARRAY_BUFFER, buffers.texCoord);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(texCoords), gl.DYNAMIC_DRAW);
    
    gl.bindBuffer(gl.ARRAY_BUFFER, buffers.color);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(colors), gl.DYNAMIC_DRAW);
    
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, buffers.indices);
    gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, new Uint16Array(indices), gl.DYNAMIC_DRAW);

    // Set up attributes
    const positionLocation = gl.getAttribLocation(program, 'a_position');
    const texCoordLocation = gl.getAttribLocation(program, 'a_texCoord');
    const colorLocation = gl.getAttribLocation(program, 'a_color');

    // Position attribute
    gl.bindBuffer(gl.ARRAY_BUFFER, buffers.position);
    gl.enableVertexAttribArray(positionLocation);
    gl.vertexAttribPointer(positionLocation, 2, gl.FLOAT, false, 0, 0);

    // Texture coordinate attribute
    gl.bindBuffer(gl.ARRAY_BUFFER, buffers.texCoord);
    gl.enableVertexAttribArray(texCoordLocation);
    gl.vertexAttribPointer(texCoordLocation, 2, gl.FLOAT, false, 0, 0);

    // Color attribute
    gl.bindBuffer(gl.ARRAY_BUFFER, buffers.color);
    gl.enableVertexAttribArray(colorLocation);
    gl.vertexAttribPointer(colorLocation, 4, gl.FLOAT, false, 0, 0);

    // Bind texture
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, textureRef.current);
    gl.uniform1i(gl.getUniformLocation(program, 'u_texture'), 0);

    // Draw
    gl.drawElements(gl.TRIANGLES, indices.length, gl.UNSIGNED_SHORT, 0);

  }, [visibleNodes, width, height, panX, panY, zoom, savedJobs]);

  // Render loop with frame rate limiting
  useEffect(() => {
    let lastTime = 0;
    const targetFPS = 60;
    const frameTime = 1000 / targetFPS;

    const renderLoop = (currentTime: number) => {
      if (currentTime - lastTime >= frameTime) {
        render();
        lastTime = currentTime;
      }
      animationFrameRef.current = requestAnimationFrame(renderLoop);
    };

    animationFrameRef.current = requestAnimationFrame(renderLoop);

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

    const dpr = Math.min(window.devicePixelRatio || 1, 2); // Limit DPR for performance
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    const gl = glRef.current;
    if (gl) {
      gl.viewport(0, 0, canvas.width, canvas.height);
    }
  }, [width, height]);

  // Optimized mouse handling
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left - panX) / zoom;
    const y = (e.clientY - rect.top - panY) / zoom;

    // Very fast collision detection
    const hoveredNode = visibleNodes.find(node => {
      const cardWidth = node.is_anchor ? 280 : (node.type === "occupation" ? 240 : 200);
      const cardHeight = node.is_anchor ? 140 : (node.type === "occupation" ? 120 : 100);
      
      return x >= node.x - cardWidth/2 &&
             x <= node.x + cardWidth/2 &&
             y >= node.y - cardHeight/2 &&
             y <= node.y + cardHeight/2;
    });

    onNodeHover?.(hoveredNode || null);
    canvas.style.cursor = hoveredNode ? 'pointer' : 'grab';
  }, [visibleNodes, panX, panY, zoom, onNodeHover]);

  const handleMouseClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX - rect.left - panX) / zoom;
    const y = (e.clientY - rect.top - panY) / zoom;

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
  }, [visibleNodes, panX, panY, zoom, onNodeClick]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      style={{ 
        display: 'block', 
        cursor: 'inherit', // Inherit cursor from parent container
        background: 'transparent',
        pointerEvents: 'auto'
      }}
      onMouseMove={handleMouseMove}
      onClick={handleMouseClick}
    />
  );
};

export default React.memo(WebGLTreeRenderer);