import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Zap, Workflow, ArrowRight, Link as LinkIcon, Brain } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';

const Landing = () => {
    const { isAuthenticated, isLoading, silentRefresh } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        const initAuth = async () => {
            if (localStorage.getItem('access_token')) {
                await silentRefresh();
            }
        };
        initAuth();
    }, []);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center">
                <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background">
            <Navbar />

            <main className="container mx-auto px-4 pt-32 pb-20">
                {/* Hero Section */}
                <div className="max-w-4xl mx-auto text-center space-y-8 mb-32">
                    <div className="flex justify-center mb-8">
                        <div className="relative">
                            <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full"></div>
                            <Workflow className="w-24 h-24 text-primary relative" />
                        </div>
                    </div>

                    <h1 className="text-6xl font-bold tracking-tight">
                        Manage, Automate, and Elevate Your Workflows
                    </h1>

                    <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                        TaskMitra is your intelligent platform for automating workflows, orchestrating AI tasks, and managing everything with precision.
                    </p>

                    <div className="flex gap-4 justify-center pt-4">
                        <Button
                            size="lg"
                            onClick={() => navigate(isAuthenticated ? '/chat/new' : '/signup')}
                            className="bg-primary hover:bg-primary-hover text-primary-foreground text-lg px-8 py-6 h-auto group"
                        >
                            Get Started
                            <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </Button>
                    </div>
                </div>

                {/* Why Choose TaskMitra Section */}
                <div className="max-w-6xl mx-auto mb-32">
                    <h2 className="text-4xl font-bold text-center mb-16">Why Choose TaskMitra?</h2>
                    <div className="grid md:grid-cols-3 gap-8">
                        <div className="p-8 rounded-2xl bg-card border border-border hover:border-primary/50 transition-colors">
                            <Brain className="w-12 h-12 text-primary mb-4" />
                            <h3 className="text-2xl font-semibold mb-3">Smart Automation</h3>
                            <p className="text-muted-foreground">
                                Automate complex workflows with AI-driven agents that plan, execute, and optimize tasks intelligently.
                            </p>
                        </div>

                        <div className="p-8 rounded-2xl bg-card border border-border hover:border-primary/50 transition-colors">
                            <Zap className="w-12 h-12 text-primary mb-4" />
                            <h3 className="text-2xl font-semibold mb-3">Seamless Orchestration</h3>
                            <p className="text-muted-foreground">
                                Orchestrate and monitor tasks in real time with precision.
                            </p>
                        </div>

                        <div className="p-8 rounded-2xl bg-card border border-border hover:border-primary/50 transition-colors">
                            <LinkIcon className="w-12 h-12 text-primary mb-4" />
                            <h3 className="text-2xl font-semibold mb-3">Powerful Integrations</h3>
                            <p className="text-muted-foreground">
                                Connect to Gmail, Notion, Sheets, and more — securely through TaskMitra.
                            </p>
                        </div>
                    </div>
                </div>

                {/* How TaskMitra Works Section */}
                <div className="max-w-4xl mx-auto mb-32">
                    <h2 className="text-4xl font-bold text-center mb-16">How TaskMitra Works</h2>
                    <div className="space-y-6">
                        <div className="flex gap-6 items-start p-6 rounded-xl bg-card border border-border">
                            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-xl">
                                1
                            </div>
                            <div>
                                <p className="text-lg text-foreground">
                                    <span className="font-semibold">Describe your task</span> in plain English.
                                </p>
                            </div>
                        </div>

                        <div className="flex gap-6 items-start p-6 rounded-xl bg-card border border-border">
                            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-xl">
                                2
                            </div>
                            <div>
                                <p className="text-lg text-foreground">
                                    <span className="font-semibold">The Planner Agent</span> breaks it into steps.
                                </p>
                            </div>
                        </div>

                        <div className="flex gap-6 items-start p-6 rounded-xl bg-card border border-border">
                            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-xl">
                                3
                            </div>
                            <div>
                                <p className="text-lg text-foreground">
                                    <span className="font-semibold">The Executor Agent</span> performs each step.
                                </p>
                            </div>
                        </div>

                        <div className="flex gap-6 items-start p-6 rounded-xl bg-card border border-border">
                            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold text-xl">
                                4
                            </div>
                            <div>
                                <p className="text-lg text-foreground">
                                    <span className="font-semibold">The Memory Agent</span> stores context.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* About Section */}
                <div className="max-w-4xl mx-auto mb-20">
                    <div className="p-10 rounded-2xl bg-card border border-border text-center">
                        <h2 className="text-3xl font-bold mb-6">About the TaskMitra Research Project</h2>
                        <p className="text-lg text-muted-foreground mb-4">
                            TaskMitra is a master's research initiative exploring AI-driven workflow orchestration with human-in-the-loop safety.
                        </p>
                        <p className="text-lg text-muted-foreground mb-4">
                            Built using <span className="text-primary font-semibold">LangChain</span>, <span className="text-primary font-semibold">LangGraph</span>, <span className="text-primary font-semibold">FastAPI</span>, and <span className="text-primary font-semibold">PostgreSQL</span>.
                        </p>
                        <p className="text-lg text-muted-foreground">
                            Conducted as part of a research study at <span className="font-semibold">PES University, Bangalore</span>.
                        </p>
                    </div>
                </div>
            </main>

            {/* Footer */}
            <footer className="border-t border-border py-8">
                <div className="container mx-auto px-4 text-center text-muted-foreground">
                    <p>© 2025 TaskMitra — All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
};

export default Landing;
