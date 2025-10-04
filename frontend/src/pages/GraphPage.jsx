import { useState, useCallback, useEffect } from 'react';
import {
    ReactFlow,
    Background,
    Controls,
    MiniMap,
    useNodesState,
    useEdgesState,
    Panel,
} from 'reactflow';
import 'reactflow/dist/style.css';
import '../styles/Graph.css';

// Modern color palette for outer nodes (each outer node gets its own distinct color)
const OUTER_NODE_COLORS = [
    '#667eea', // Purple-blue
    '#f093fb', // Pink
    '#4facfe', // Blue
    '#43e97b', // Green
    '#fa709a', // Rose
    '#feca57', // Yellow
    '#ff6b6b', // Red
    '#4ecdc4', // Teal
    '#a29bfe', // Lavender
    '#fd79a8', // Hot pink
];

// Lighter tints for inner nodes (matching their parent's color)
const getInnerNodeColor = (outerColor) => {
    // Convert hex to RGB and lighten
    const r = parseInt(outerColor.slice(1, 3), 16);
    const g = parseInt(outerColor.slice(3, 5), 16);
    const b = parseInt(outerColor.slice(5, 7), 16);
    
    // Lighten by 40%
    const lighten = (color) => Math.min(255, Math.round(color + (255 - color) * 0.6));
    
    return `rgb(${lighten(r)}, ${lighten(g)}, ${lighten(b)})`;
};

export default function GraphPage() {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [stats, setStats] = useState({ outer: 0, inner: 0, edges: 0 });
    const [selectedNode, setSelectedNode] = useState(null);
    const [expandedNodes, setExpandedNodes] = useState(new Set());
    const [hasData, setHasData] = useState(false);

    // Load graph data
    useEffect(() => {
        loadGraphData();
    }, []);

    const loadGraphData = () => {
        // Try to load from sessionStorage
        const storedGraph = sessionStorage.getItem('latestGraph');
        if (storedGraph) {
            try {
                const graphData = JSON.parse(storedGraph);
                processGraphData(graphData);
            } catch (error) {
                console.error('Error loading graph data:', error);
            }
        }
    };

    const loadDummyData = async () => {
        try {
            const response = await fetch('/dummy-graph.json');
            const graphData = await response.json();
            processGraphData(graphData);
        } catch (error) {
            console.error('Error loading dummy data:', error);
            alert('Failed to load demo data');
        }
    };

    // Helper function to count connections for each inner node
    const countConnections = (nodeId, edges, nodes) => {
        return edges.filter(e => 
            (e.source === nodeId || e.target === nodeId) &&
            nodes.find(n => n.id === (e.source === nodeId ? e.target : e.source))?.type === 'inner'
        ).length;
    };

    const processGraphData = (graphData) => {
        if (!graphData || !graphData.nodes || !graphData.edges) {
            console.error('Invalid graph data format');
            return;
        }

        // Normalize node types (handle both formats)
        graphData.nodes.forEach(node => {
            // Convert 'central' to 'outer'
            if (node.type === 'central') {
                node.type = 'outer';
            }
            // Convert 'subnode' to 'inner'
            if (node.type === 'subnode') {
                node.type = 'inner';
            }
        });

        // Normalize edge format (convert 'from/to' to 'source/target')
        graphData.edges.forEach(edge => {
            if (edge.from && !edge.source) {
                edge.source = edge.from;
            }
            if (edge.to && !edge.target) {
                edge.target = edge.to;
            }
            // Also handle 'label' vs 'title'
            if (edge.label && !edge.title) {
                edge.title = edge.label;
            }
        });

        const outerNodes = graphData.nodes.filter(n => n.type === 'outer');
        const innerNodes = graphData.nodes.filter(n => n.type === 'inner');

        // Auto-assign parents based on edge connections if missing
        innerNodes.forEach(innerNode => {
            if (!innerNode.parent) {
                // Find the first outer node connected to this inner node
                const parentEdge = graphData.edges.find(e => 
                    (e.source === innerNode.id && outerNodes.find(o => o.id === e.target)) ||
                    (e.target === innerNode.id && outerNodes.find(o => o.id === e.source))
                );
                
                if (parentEdge) {
                    const parentId = outerNodes.find(o => o.id === parentEdge.source || o.id === parentEdge.target)?.id;
                    if (parentId) {
                        innerNode.parent = parentId;
                    }
                } else {
                    // If no connection found, assign to first outer node
                    if (outerNodes.length > 0) {
                        innerNode.parent = outerNodes[0].id;
                    }
                }
            }
        });

        // Initialize all nodes as expanded
        const allExpanded = new Set(outerNodes.map(n => n.id));
        setExpandedNodes(allExpanded);

        // Position outer nodes in a HORIZONTAL LINE
        const totalWidth = 1600;
        const startX = 200;
        const spacing = totalWidth / (outerNodes.length + 1);
        const outerY = 100; // Fixed Y position for all outer nodes

        outerNodes.forEach((node, i) => {
            node.position = {
                x: startX + (i + 1) * spacing,
                y: outerY
            };
        });

        // Position inner nodes with each parent's group at a DIFFERENT horizontal level
        outerNodes.forEach((parent, parentIndex) => {
            const siblings = innerNodes.filter(n => n.parent === parent.id);
            
            if (siblings.length === 0) return;
            
            // Sort siblings by connection count (most connected in center)
            const siblingsWithConnections = siblings.map(node => ({
                node,
                connections: countConnections(node.id, graphData.edges, graphData.nodes)
            }));
            siblingsWithConnections.sort((a, b) => b.connections - a.connections);
            
            const totalSiblings = siblings.length;
            const horizontalSpread = Math.min(600, totalSiblings * 160); // Wider spread for horizontal layout
            
            // Each parent gets its own Y level (tier)
            const tierHeight = 180; // Vertical spacing between tiers
            const baseY = parent.position.y + 250 + (parentIndex * tierHeight);
            
            if (totalSiblings === 1) {
                // Single node centered horizontally on its tier
                siblings[0].position = {
                    x: parent.position.x,
                    y: baseY
                };
            } else if (totalSiblings === 2) {
                // Two nodes side by side on the same tier
                siblings[0].position = {
                    x: parent.position.x - 120,
                    y: baseY
                };
                siblings[1].position = {
                    x: parent.position.x + 120,
                    y: baseY
                };
            } else {
                // Multiple nodes: spread horizontally across the full tier
                siblingsWithConnections.forEach((item, idx) => {
                    // Distribute evenly across the horizontal space
                    const xPosition = parent.position.x - horizontalSpread / 2 + 
                                    (idx / (totalSiblings - 1)) * horizontalSpread;
                    
                    // Small vertical variation for organic look (within the tier)
                    const verticalJitter = (idx % 3) * 12 - 12; // -12, 0, or 12
                    
                    item.node.position = {
                        x: xPosition,
                        y: baseY + verticalJitter
                    };
                });
            }
        });

        // Assign colors to outer nodes
        const parentColorMap = {};
        outerNodes.forEach((node, index) => {
            const color = OUTER_NODE_COLORS[index % OUTER_NODE_COLORS.length];
            node.color = color;
            parentColorMap[node.id] = color;
        });

        // Create React Flow nodes
        const reactFlowNodes = [...outerNodes, ...innerNodes].map(node => {
            const isOuter = node.type === 'outer';
            const outerColor = isOuter ? node.color : parentColorMap[node.parent];
            const color = isOuter ? outerColor : getInnerNodeColor(outerColor);

            return {
                id: node.id,
                position: node.position,
                data: { 
                    label: node.title,
                    type: node.type,
                    parent: node.parent,
                    color: color,
                    outerColor: outerColor
                },
                style: {
                    background: color,
                    color: '#1a1a1a',
                    border: isOuter ? `3px solid ${outerColor}` : `2px solid ${outerColor}`,
                    borderRadius: isOuter ? '12px' : '8px',
                    padding: isOuter ? '14px 24px' : '10px 16px',
                    fontSize: isOuter ? '15px' : '12px',
                    fontWeight: isOuter ? '700' : '600',
                    minWidth: isOuter ? '140px' : '100px',
                    cursor: 'pointer',
                    boxShadow: isOuter 
                        ? '0 4px 12px rgba(0,0,0,0.15)' 
                        : '0 2px 6px rgba(0,0,0,0.1)',
                },
                type: 'default',
                hidden: false, // Show all initially
            };
        });

        // Create edges - including parent-child edges
        const allEdges = [];
        
        // 1. Add parent-child edges (outer to inner)
        innerNodes.forEach(innerNode => {
            if (innerNode.parent) {
                const parentColor = parentColorMap[innerNode.parent];
                allEdges.push({
                    id: `parent-${innerNode.parent}-${innerNode.id}`,
                    source: innerNode.parent,
                    target: innerNode.id,
                    type: 'straight',
                    animated: false,
                    style: {
                        stroke: parentColor,
                        strokeWidth: 2,
                        strokeOpacity: 0.4,
                    },
                    hidden: false,
                });
            }
        });

        // 2. Add regular edges from the data with smarter routing
        graphData.edges.forEach(edge => {
            const sourceNode = graphData.nodes.find(n => n.id === edge.source);
            const targetNode = graphData.nodes.find(n => n.id === edge.target);
            
            const isCrossParent = sourceNode?.parent !== targetNode?.parent && 
                                sourceNode?.type === 'inner' && targetNode?.type === 'inner';

            const sourceColor = sourceNode?.type === 'outer' 
                ? parentColorMap[sourceNode.id]
                : parentColorMap[sourceNode?.parent];

            // Use different edge types based on connection type
            let edgeType = 'smoothstep';
            if (isCrossParent) {
                edgeType = 'default'; // Straight lines for cross-parent (clearer)
            }

            allEdges.push({
                id: `${edge.source}-${edge.target}`,
                source: edge.source,
                target: edge.target,
                label: edge.title || '',
                type: edgeType,
                animated: false,
                style: {
                    stroke: isCrossParent ? '#888' : (sourceColor || '#555'),
                    strokeWidth: isCrossParent ? 2.5 : 3,
                    strokeDasharray: isCrossParent ? '8,4' : 'none',
                    strokeOpacity: isCrossParent ? 0.6 : 0.8,
                },
                labelStyle: {
                    fontSize: '11px',
                    fill: '#1a1a1a',
                    fontWeight: 600,
                    background: 'rgba(255, 255, 255, 0.95)',
                    padding: '3px 8px',
                    borderRadius: '6px',
                    border: '1px solid #e5e5e5',
                },
                labelBgPadding: [8, 4],
                labelBgBorderRadius: 6,
                labelBgStyle: {
                    fill: 'rgba(255, 255, 255, 0.95)',
                    stroke: '#e5e5e5',
                    strokeWidth: 1,
                },
                hidden: false,
            });
        });

        setNodes(reactFlowNodes);
        setEdges(allEdges);
        setStats({
            outer: outerNodes.length,
            inner: innerNodes.length,
            edges: allEdges.length
        });
        setHasData(true);
    };

    const handleNodeClick = useCallback((event, node) => {
        if (node.data.type === 'outer') {
            // Toggle expansion
            setExpandedNodes(prev => {
                const newExpanded = new Set(prev);
                if (newExpanded.has(node.id)) {
                    newExpanded.delete(node.id);
                } else {
                    newExpanded.add(node.id);
                }

                // Update node visibility
                setNodes(nds => 
                    nds.map(n => {
                        if (n.data.type === 'inner' && n.data.parent === node.id) {
                            return { ...n, hidden: !newExpanded.has(node.id) };
                        }
                        return n;
                    })
                );

                // Update edge visibility
                setEdges(eds =>
                    eds.map(e => {
                        const sourceNode = nodes.find(n => n.id === e.source);
                        const targetNode = nodes.find(n => n.id === e.target);
                        
                        const sourceVisible = sourceNode?.data.type === 'outer' || 
                                            newExpanded.has(sourceNode?.data.parent);
                        const targetVisible = targetNode?.data.type === 'outer' || 
                                            newExpanded.has(targetNode?.data.parent);
                        
                        return { ...e, hidden: !(sourceVisible && targetVisible) };
                    })
                );

                return newExpanded;
            });
        }
        
        setSelectedNode(node);
    }, [nodes, setNodes, setEdges]);

    return (
        <div className="graph-page">
            <div className="page-header">
                <h2>Knowledge Graph Visualization</h2>
                <p className="subtitle">Interactive mindmap - click outer nodes to collapse/expand their sub-topics</p>
            </div>

            <div className="graph-container">
                {hasData ? (
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        onNodeClick={handleNodeClick}
                        fitView
                        fitViewOptions={{ padding: 0.2 }}
                        minZoom={0.1}
                        maxZoom={2}
                    >
                        <Background color="#e5e5e5" gap={20} />
                        <Controls />
                        <MiniMap 
                            nodeColor={(node) => node.data.color}
                            nodeStrokeWidth={3}
                            zoomable
                            pannable
                        />
                        <Panel position="top-right" className="stats-panel">
                            <div className="stats-header">
                                <h3>Graph Statistics</h3>
                            </div>
                            <div className="stats-grid">
                                <div className="stat-item">
                                    <span className="stat-label">Main Topics:</span>
                                    <span className="stat-value">{stats.outer}</span>
                                </div>
                                <div className="stat-item">
                                    <span className="stat-label">Sub-topics:</span>
                                    <span className="stat-value">{stats.inner}</span>
                                </div>
                                <div className="stat-item">
                                    <span className="stat-label">Connections:</span>
                                    <span className="stat-value">{stats.edges}</span>
                                </div>
                            </div>
                            {selectedNode && (
                                <div className="selected-node-info">
                                    <h4>Selected Node</h4>
                                    <p><strong>{selectedNode.data.label}</strong></p>
                                    <p className="node-type">
                                        {selectedNode.data.type === 'outer' ? 'Main Topic' : 'Sub-topic'}
                                    </p>
                                </div>
                            )}
                        </Panel>
                        <Panel position="top-left" className="controls-panel">
                            <button 
                                className="btn btn-control"
                                onClick={loadDummyData}
                                title="Load Demo Data"
                            >
                                📊 Load Demo
                            </button>
                            <button 
                                className="btn btn-control"
                                onClick={() => {
                                    const allOuter = nodes.filter(n => n.data.type === 'outer').map(n => n.id);
                                    setExpandedNodes(new Set(allOuter));
                                    setNodes(nds => nds.map(n => ({ ...n, hidden: false })));
                                    setEdges(eds => eds.map(e => ({ ...e, hidden: false })));
                                }}
                                title="Expand All"
                            >
                                ➕ Expand All
                            </button>
                            <button 
                                className="btn btn-control"
                                onClick={() => {
                                    setExpandedNodes(new Set());
                                    setNodes(nds => nds.map(n => 
                                        n.data.type === 'inner' ? { ...n, hidden: true } : n
                                    ));
                                    setEdges(eds => eds.map(e => {
                                        const sourceNode = nodes.find(n => n.id === e.source);
                                        const targetNode = nodes.find(n => n.id === e.target);
                                        const hide = sourceNode?.data.type === 'inner' || targetNode?.data.type === 'inner';
                                        return { ...e, hidden: hide };
                                    }));
                                }}
                                title="Collapse All"
                            >
                                ➖ Collapse All
                            </button>
                        </Panel>
                    </ReactFlow>
                ) : (
                    <div className="graph-message">
                        <div className="message-icon">📊</div>
                        <h3>No Graph Data</h3>
                        <p>Upload a PDF to generate a hierarchical knowledge graph, or load demo data to explore.</p>
                        <button 
                            className="btn btn-primary"
                            onClick={loadDummyData}
                        >
                            Load Demo Data
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}
