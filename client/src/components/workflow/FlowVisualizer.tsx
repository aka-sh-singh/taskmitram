import React, { useEffect, useMemo } from 'react';
import {
    ReactFlow,
    Background,
    Controls,
    Panel,
    useNodesState,
    useEdgesState,
    MarkerType,
    Node,
    Edge,
    BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import ToolNode from './ToolNode';

interface FlowVisualizerProps {
    workflowData?: {
        nodes: any[];
        edges: any[];
    };
    isLoading?: boolean;
}

const FlowVisualizer: React.FC<FlowVisualizerProps> = ({ workflowData, isLoading }) => {
    const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

    // Register custom node types
    const nodeTypes = useMemo(() => ({
        tool_node: ToolNode,
        tool: ToolNode,
        condition: ToolNode,
        delay: ToolNode,
        approval: ToolNode,
        gmail_node: ToolNode,
        drive_node: ToolNode,
        sheet_node: ToolNode,
        github_node: ToolNode,
        summarizer_node: ToolNode,
        schedule_workflow: ToolNode,
        // Fallback for direct tool names
        send_gmail: ToolNode,
        fetch_recent_gmail: ToolNode,
        read_gmail_message: ToolNode,
        list_drive_files: ToolNode,
        create_drive_file: ToolNode,
        update_spreadsheet_values: ToolNode,
        append_spreadsheet_values: ToolNode,
        create_spreadsheet: ToolNode,
        summarize_text: ToolNode,
    }), []);

    useEffect(() => {
        if (workflowData && workflowData.nodes) {
            const formattedNodes = workflowData.nodes.map((node, index) => {
                // Handle both backend pre-formatted and raw node patterns
                const position = node.position || {
                    x: node.position_x ?? (index * 220),
                    y: node.position_y ?? 100
                };

                return {
                    id: String(node.id),
                    // Use node.type from backend, fallback to tool_node for custom styling if needed
                    type: node.type || 'tool_node',
                    position,
                    data: {
                        ...node.data, // Backend puts tool/args in data
                        node_type: node.node_type || node.type,
                        tool: node.tool || node.data?.tool,
                        arguments: node.arguments || node.data?.arguments,
                    },
                };
            });

            // 2. Map Edges
            const formattedEdges = workflowData.edges.map(edge => ({
                id: String(edge.id),
                // Backend returns source/target, fallback to source_node/target_node
                source: String(edge.source || edge.source_node),
                target: String(edge.target || edge.target_node),
                label: edge.label,
                animated: true,
                style: { stroke: '#6366f1', strokeWidth: 2 },
                markerEnd: {
                    type: MarkerType.ArrowClosed,
                    color: '#6366f1',
                },
            }));

            setNodes(formattedNodes);
            setEdges(formattedEdges);
        }
    }, [workflowData, setNodes, setEdges, nodeTypes]);

    if (isLoading) {
        return (
            <div className="w-full h-full min-h-[500px] flex items-center justify-center border border-border rounded-xl bg-card/10 backdrop-blur-sm">
                <div className="flex flex-col items-center gap-4">
                    <div className="h-10 w-10 border-4 border-primary border-t-transparent rounded-full animate-spin"></div>
                    <span className="text-sm text-muted-foreground font-medium animate-pulse">Designing Agentic Workflow...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full h-full border border-border/50 rounded-lg bg-background overflow-hidden relative shadow-sm">
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                nodeTypes={nodeTypes}
                fitView
                colorMode="light"
                minZoom={0.2}
                maxZoom={2}
            >
                <Background color="#e2e8f0" gap={15} variant={BackgroundVariant.Dots} />
                <Controls className="bg-background border-border" />
                <Panel position="top-right" className="bg-background/60 p-3 rounded-xl border border-border/50 backdrop-blur-xl shadow-2xl m-4">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        <div className="text-[10px] font-mono text-foreground/70 uppercase tracking-widest font-black">
                            Live Graph Orchestration
                        </div>
                    </div>
                </Panel>
            </ReactFlow>
        </div>
    );
};

export default FlowVisualizer;
