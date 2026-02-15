import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Zap, Workflow, ArrowRight, Link as LinkIcon, Brain } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';
import { motion, useScroll, useTransform, useSpring } from 'framer-motion';
import { useRef } from 'react';


// --- Main Page ---

const Landing = () => {
    const { isAuthenticated, isLoading } = useAuth();
    const navigate = useNavigate();

    // Global Scroll Progress
    const { scrollYProgress } = useScroll();
    const scaleX = useSpring(scrollYProgress, {
        stiffness: 100,
        damping: 30,
        restDelta: 0.001
    });

    const heroRef = useRef(null);
    const { scrollY } = useScroll();

    // Enhanced Hero Parallax - Optimized (Removed blur)
    const heroY = useTransform(scrollY, [0, 500], [0, 200]);
    const heroOpacity = useTransform(scrollY, [0, 400], [1, 0]);

    // How It Works - Progressive Line
    const stepsRef = useRef(null);
    const { scrollYProgress: stepsProgress } = useScroll({
        target: stepsRef,
        offset: ["start center", "end center"]
    });
    const lineHeight = useTransform(stepsProgress, [0, 1], ["0%", "100%"]);

    if (isLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-background">
                <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-background overflow-x-hidden selection:bg-primary/20">
            <Navbar />

            {/* Scroll Progress Bar */}
            <motion.div
                className="fixed top-0 left-0 right-0 h-1 bg-primary origin-left z-50"
                style={{ scaleX }}
            />

            <main className="relative perspective-1000">
                {/* Hero Section */}
                <section ref={heroRef} className="relative min-h-[95vh] flex items-center justify-center pt-20 overflow-hidden">
                    {/* Dynamic Background Grid */}
                    <div className="absolute inset-0 -z-10 h-full w-full bg-background bg-[linear-gradient(to_right,#8080800a_1px,transparent_1px),linear-gradient(to_bottom,#8080800a_1px,transparent_1px)] bg-[size:14px_24px]">
                        <div className="absolute left-0 right-0 top-0 -z-10 m-auto h-[310px] w-[310px] rounded-full bg-primary/20 opacity-20 blur-[100px]"></div>
                    </div>

                    <motion.div
                        style={{ y: heroY, opacity: heroOpacity }}
                        className="container relative z-10 px-4 text-center max-w-5xl mx-auto"
                    >
                        <motion.div
                            initial={{ scale: 0.5, rotate: -180, opacity: 0 }}
                            animate={{ scale: 1, rotate: 0, opacity: 1 }}
                            transition={{ duration: 1, type: "spring", bounce: 0.5 }}
                            className="flex justify-center mb-8"
                        >
                            <div className="relative p-6 rounded-3xl bg-background/50 border border-white/10 shadow-2xl shadow-primary/30 ring-1 ring-white/20 backdrop-blur-sm">
                                <Workflow className="w-20 h-20 text-primary drop-shadow-lg" />
                            </div>
                        </motion.div>

                        <div className="overflow-hidden">
                            <motion.h1
                                initial={{ y: "100%" }}
                                animate={{ y: 0 }}
                                transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                                className="text-5xl md:text-7xl font-bold tracking-tight mb-8 bg-clip-text text-transparent bg-gradient-to-b from-foreground via-foreground/90 to-foreground/70"
                            >
                                <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary to-purple-500">
                                    TaskMitra
                                </span> <br />
                            </motion.h1>
                        </div>

                        <motion.p
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.5, duration: 0.8 }}
                            className="text-xl md:text-2xl text-muted-foreground max-w-3xl mx-auto mb-12 leading-relaxed"
                        >
                            TaskMitra is your personal Agentic AI assistant for automating your tasks and workflows, and managing everything with safety.
                        </motion.p>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.7, duration: 0.8 }}
                            className="flex flex-col sm:flex-row gap-6 justify-center items-center"
                        >
                            <Button
                                size="lg"
                                onClick={() => navigate(isAuthenticated ? '/chat/new' : '/signup')}
                                className="bg-primary hover:bg-primary/90 text-primary-foreground text-xl px-10 py-8 h-auto rounded-full shadow-lg shadow-primary/25 transition-all hover:scale-110 active:scale-95 group"
                            >
                                <span className="flex items-center gap-2">
                                    Get Started
                                    <ArrowRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                                </span>
                            </Button>
                        </motion.div>
                    </motion.div>
                </section>

                {/* Why Choose TaskMitra Section - Optimized Cards */}
                <section className="py-32 relative">
                    <div className="container mx-auto px-4 max-w-7xl">
                        <motion.h2
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            className="text-4xl md:text-6xl font-bold text-center mb-24"
                        >
                            Why Choose TaskMitra?
                        </motion.h2>

                        <div className="grid md:grid-cols-3 gap-8">
                            {[
                                {
                                    icon: Brain,
                                    title: "Smart Automation",
                                    desc: "Automate complex workflows with AI-driven agents that plan, execute, and optimize tasks intelligently.",
                                    color: "bg-blue-500/10 text-blue-500"
                                },
                                {
                                    icon: Zap,
                                    title: "Seamless Orchestration",
                                    desc: "Orchestrate and monitor tasks in real time with precision, tracking every step of the process.",
                                    color: "bg-yellow-500/10 text-yellow-500"
                                },
                                {
                                    icon: LinkIcon,
                                    title: "Powerful Integrations",
                                    desc: "Connect to Gmail, Notion, Sheets, and more — securely through TaskMitra's robust API ecosystem.",
                                    color: "bg-green-500/10 text-green-500"
                                }
                            ].map((feature, index) => (
                                <motion.div
                                    key={index}
                                    whileHover={{ y: -10 }}
                                    transition={{ type: "spring", stiffness: 300 }}
                                    className="p-8 rounded-3xl bg-card border border-border/50 hover:border-primary/50 transition-colors shadow-sm hover:shadow-2xl hover:shadow-primary/5 flex flex-col items-center text-center cursor-default"
                                >
                                    <div className={`p-4 rounded-2xl mb-6 ${feature.color}`}>
                                        <feature.icon className="w-10 h-10" />
                                    </div>
                                    <h3 className="text-2xl font-bold mb-4">{feature.title}</h3>
                                    <p className="text-muted-foreground leading-relaxed text-lg">
                                        {feature.desc}
                                    </p>
                                </motion.div>
                            ))}
                        </div>
                    </div>
                </section>

                {/* How TaskMitra Works Section - Connected Timeline */}
                <section id="how-it-works" ref={stepsRef} className="py-32 bg-muted/20 relative overflow-hidden">
                    <div className="container mx-auto px-4 max-w-5xl relative">
                        <motion.div
                            initial={{ opacity: 0 }}
                            whileInView={{ opacity: 1 }}
                            className="text-center mb-24"
                        >
                            <h2 className="text-4xl md:text-6xl font-bold mb-6">How It Works</h2>
                            <p className="text-xl text-muted-foreground">From idea to execution in five simple steps</p>
                        </motion.div>

                        <div className="relative">
                            {/* Connecting Line (Path) */}
                            <div className="absolute left-[2rem] md:left-1/2 top-0 bottom-0 w-1 bg-border/50 -translate-x-1/2 rounded-full overflow-hidden">
                                <motion.div
                                    style={{ height: lineHeight }}
                                    className="w-full bg-primary origin-top"
                                />
                            </div>

                            <div className="space-y-24">
                                {[
                                    {
                                        step: 1,
                                        title: "Describe your task",
                                        desc: "Simply type your request in natural language, just like you're talking to a assistant.",
                                        align: "left"
                                    },
                                    {
                                        step: 2,
                                        title: "The Orchestrator Agent",
                                        desc: "It coordinates the Planner, Executor, and Memory agents for seamless execution.",
                                        align: "right"
                                    },
                                    {
                                        step: 3,
                                        title: "The Planner Agent",
                                        desc: "Our planner agent analyzes your request and intelligently breaks it down into actionable steps.",
                                        align: "left"
                                    },
                                    {
                                        step: 4,
                                        title: "The Executor Agent",
                                        desc: "Specialized agents perform each step, interacting with tools and APIs as needed.",
                                        align: "right"
                                    },
                                    {
                                        step: 5,
                                        title: "The Memory Agent",
                                        desc: "Context is preserved across steps, ensuring a coherent and smart workflow execution.",
                                        align: "left"
                                    }
                                ].map((item, index) => (
                                    <motion.div
                                        key={index}
                                        initial={{ opacity: 0, y: 50 }}
                                        whileInView={{ opacity: 1, y: 0 }}
                                        viewport={{ margin: "-100px" }}
                                        transition={{ duration: 0.8, delay: 0.1 }}
                                        className={`flex flex-col md:flex-row items-center gap-12 relative ${item.align === 'right' ? 'md:flex-row-reverse' : ''}`}
                                    >
                                        {/* Timeline Node */}
                                        <div className="absolute left-[2rem] md:left-1/2 w-8 h-8 rounded-full bg-background border-[4px] border-primary -translate-x-1/2 z-10 shadow-[0_0_0_8px_rgba(var(--background),1)] flex items-center justify-center">
                                            <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                                        </div>

                                        {/* Step Number Big */}
                                        <div className={`hidden md:block flex-1 text-9xl font-black text-foreground/5 select-none ${item.align === 'right' ? 'text-left' : 'text-right'}`}>
                                            0{item.step}
                                        </div>

                                        {/* Content Card */}
                                        <div className={`flex-1 pl-16 md:pl-0 ${item.align === 'right' ? 'md:text-left' : 'md:text-right'}`}>
                                            <div className="p-8 rounded-3xl bg-card border border-border/50 hover:border-primary/30 transition-all shadow-sm hover:shadow-2xl hover:-translate-y-2 group">
                                                <h3 className="text-2xl md:text-3xl font-bold mb-4 group-hover:text-primary transition-colors">{item.title}</h3>
                                                <p className="text-lg text-muted-foreground leading-relaxed">{item.desc}</p>
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    </div>
                </section>

                {/* About Section */}
                <section className="py-32 relative overflow-hidden bg-foreground/5">
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ margin: "-100px" }}
                        transition={{ duration: 0.8 }}
                        className="container mx-auto px-4 max-w-5xl will-change-transform"
                    >
                        <div className="relative p-8 md:p-12 rounded-[2.5rem] bg-gradient-to-br from-background via-background/90 to-muted/50 border border-white/10 shadow-2xl backdrop-blur-sm overflow-hidden">
                            {/* Decorative Background */}
                            <div className="absolute top-0 right-0 w-[300px] h-[300px] bg-primary/10 rounded-full blur-[60px] -translate-y-1/2 translate-x-1/2" />
                            <div className="absolute bottom-0 left-0 w-[200px] h-[200px] bg-purple-500/10 rounded-full blur-[40px] translate-y-1/2 -translate-x-1/2" />

                            <div className="relative z-10 text-center space-y-8">
                                <h2 className="text-3xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-foreground to-foreground/70">
                                    About the Research Project
                                </h2>

                                <p className="text-xl text-muted-foreground max-w-3xl mx-auto leading-relaxed">
                                    TaskMitra is a research initiative exploring <span className="font-semibold text-foreground">Agentic AI-driven workflow orchestration</span> with human-in-the-loop safety.
                                </p>

                                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6 py-8">
                                    {['LangChain', 'LangGraph', 'FastAPI', 'PostgreSQL'].map((tech) => (
                                        <motion.div
                                            key={tech}
                                            whileHover={{ scale: 1.05, y: -5 }}
                                            className="p-4 rounded-xl bg-card border border-border/50 shadow-sm hover:shadow-lg hover:border-primary/20 transition-all font-semibold text-lg flex items-center justify-center cursor-default"
                                        >
                                            {tech}
                                        </motion.div>
                                    ))}
                                </div>

                                <div className="pt-4 border-t border-border/50">
                                    <p className="text-lg text-muted-foreground flex flex-col md:flex-row items-center justify-center gap-2">
                                        <span>Conducted as part of a research study at</span>
                                        <span className="flex items-center gap-2 font-bold text-foreground bg-primary/10 px-4 py-1 rounded-full">
                                            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                                            PES University, Bangalore
                                        </span>
                                    </p>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                </section>
            </main>

            {/* Footer */}
            <footer className="border-t border-border py-12 bg-background z-10 relative">
                <div className="container mx-auto px-4 text-center text-muted-foreground">
                    <div className="flex items-center justify-center gap-2 mb-4 opacity-50 hover:opacity-100 transition-opacity">
                        <Workflow className="w-5 h-5" />
                        <span className="font-semibold">TaskMitra</span>
                    </div>
                    <p>© {new Date().getFullYear()} TaskMitra — All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
};

export default Landing;
