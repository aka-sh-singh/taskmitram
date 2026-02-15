import { Handle, Position } from '@xyflow/react';
import { Mail, HardDrive, FileSpreadsheet, Github, Cpu, Calendar } from 'lucide-react';

const getIcon = (tool?: string, nodeType?: string) => {
    if (nodeType === 'approval') return <Cpu className="w-4 h-4 text-yellow-400" />;
    if (nodeType === 'condition') return <Cpu className="w-4 h-4 text-purple-400" />;
    if (nodeType === 'delay') return <Calendar className="w-4 h-4 text-orange-400" />;

    const t = tool?.toLowerCase() || '';
    if (t.includes('gmail')) return <Mail className="w-4 h-4 text-red-400" />;
    if (t.includes('drive')) return <HardDrive className="w-4 h-4 text-blue-400" />;
    if (t.includes('spreadsheet') || t.includes('sheet')) return <FileSpreadsheet className="w-4 h-4 text-green-400" />;
    if (t.includes('github')) return <Github className="w-4 h-4 text-slate-700" />;

    return <Cpu className="w-4 h-4 text-primary" />;
};

const getLabel = (tool?: string, nodeType?: string) => {
    if (nodeType && nodeType !== 'tool') return nodeType.toUpperCase();
    if (!tool) return 'ACTION';
    return tool.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const ToolNode = ({ data, selected }: any) => {
    const { tool, node_type, arguments: args } = data;

    return (
        <div className={`px-3 py-2 rounded-lg border transition-all duration-300 shadow-sm ${selected
            ? 'border-primary bg-primary/5 scale-102 ring-1 ring-primary/20'
            : 'border-border bg-card hover:border-primary/30'
            } min-w-[170px]`}>
            <Handle type="target" position={Position.Left} className="w-3 h-3 bg-primary border-2 border-background" />

            <div className="flex items-center gap-3">
                <div className="p-1.5 rounded-md bg-accent/40 border border-border shadow-sm">
                    {getIcon(tool, node_type)}
                </div>
                <div className="flex flex-col">
                    <span className="text-[9px] font-bold text-muted-foreground uppercase tracking-widest leading-none mb-0.5">
                        {node_type || 'Node'}
                    </span>
                    <span className="text-xs font-semibold text-foreground tracking-tight">
                        {getLabel(tool, node_type)}
                    </span>
                </div>
            </div>

            {args && Object.keys(args).length > 0 && (
                <div className="mt-3 pt-3 border-t border-border/50">
                    <div className="grid grid-cols-1 gap-1.5">
                        {Object.entries(args).map(([key, value]: [string, any]) => (
                            <div key={key} className="flex flex-col gap-0.5 px-2 py-1 rounded bg-accent/30 border border-border/20 text-[9px]">
                                <span className="text-primary/70 font-bold uppercase tracking-tighter">{key}</span>
                                <span className="text-muted-foreground truncate font-mono">
                                    {typeof value === 'object' ? JSON.stringify(value) : String(value)}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <Handle type="source" position={Position.Right} className="w-3 h-3 bg-primary border-2 border-background" />
        </div>
    );
};

export default ToolNode;
