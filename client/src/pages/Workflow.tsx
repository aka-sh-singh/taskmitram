import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Workflow as WorkflowIcon, ArrowLeft, LayoutDashboard, Settings, Activity } from 'lucide-react';

const Workflow = () => {
    const { workflowId } = useParams<{ workflowId: string }>();
    const navigate = useNavigate();

    return (
        <div className="flex-1 flex flex-col overflow-hidden bg-background text-foreground">
            {/* Header */}
            <div className="h-14 border-b border-border flex items-center justify-between px-6 bg-sidebar-bg">
                <div className="flex items-center gap-4">
                    <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => navigate(-1)}
                        className="hover:bg-sidebar-hover transition-colors h-8 w-8 group-data-[sidebar=closed]/sidebar:hidden"
                    >
                        <ArrowLeft className="h-4 w-4" />
                    </Button>
                </div>

                <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" className="gap-2">
                        <Activity className="h-4 w-4" />
                        Status: Draft
                    </Button>
                    <Button variant="outline" size="sm" className="gap-2">
                        <Settings className="h-4 w-4" />
                        Configure
                    </Button>
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-auto p-8">
                <div className="max-w-5xl mx-auto space-y-8">
                    <div className="flex flex-col items-center justify-center py-20 text-center space-y-6">
                        <div className="relative">
                            <div className="absolute -inset-4 bg-gradient-to-r from-primary/20 to-purple-600/20 rounded-full blur-xl animate-pulse"></div>
                            <div className="relative bg-card p-8 rounded-full border border-border shadow-2xl">
                                <WorkflowIcon className="h-16 w-16 text-primary" />
                            </div>
                        </div>
                        <div className="space-y-4">
                            <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
                                Workflow Orchestration
                            </h1>
                            <p className="text-muted-foreground text-lg max-w-xl mx-auto leading-relaxed">
                                You're viewing the workflow for chat <span className="text-foreground font-mono bg-muted px-2 py-0.5 rounded text-sm italic">{workflowId}</span>.
                                The visual workflow builder and advanced orchestration monitoring tools are currently in development.
                            </p>
                        </div>
                    </div>

                    {/* Grid of cards for features */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {[
                            { title: 'Node Graph', description: 'Visualize and edit the flow of tasks using a drag-and-drop interface.', icon: <LayoutDashboard className="h-6 w-6 text-primary" />, comingSoon: true },
                            { title: 'Agent Selection', description: 'Assign specialized AI agents to specific nodes in your workflow.', icon: <Settings className="h-6 w-6 text-blue-500" />, comingSoon: true },
                            { title: 'Live Execution', description: 'Monitor the status of each node as the workflow executes in real-time.', icon: <Activity className="h-6 w-6 text-green-500" />, comingSoon: true }
                        ].map((card, idx) => (
                            <div key={idx} className="group relative">
                                <div className="absolute -inset-0.5 bg-gradient-to-r from-primary to-blue-600 rounded-2xl blur opacity-0 group-hover:opacity-10 transition duration-500"></div>
                                <div className="relative p-6 rounded-2xl border border-border bg-card/40 backdrop-blur-sm hover:border-primary/50 hover:translate-y-[-4px] transition-all duration-300 flex flex-col h-full">
                                    <div className="mb-4 p-3 bg-muted/50 rounded-xl w-fit group-hover:bg-primary/10 transition-colors">
                                        {card.icon}
                                    </div>
                                    <h3 className="text-lg font-semibold mb-2 group-hover:text-primary transition-colors">{card.title}</h3>
                                    <p className="text-sm text-muted-foreground mb-6 flex-1">{card.description}</p>
                                    <div className="mt-auto">
                                        {card.comingSoon && (
                                            <span className="text-[10px] uppercase tracking-wider font-extrabold text-primary bg-primary/10 px-3 py-1 rounded-full border border-primary/20">
                                                Coming Soon
                                            </span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Workflow;
