import React from 'react';
import ChatSidebar from '@/components/chat/ChatSidebar';
import { User, Workflow, PanelLeftOpen, SquarePen, ArrowLeft } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from '@/components/ui/tooltip';
import { SettingsModal } from '@/components/settings';

interface MainLayoutProps {
    children: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
    const [isSidebarOpen, setIsSidebarOpen] = React.useState(true);
    const [showSettingsModal, setShowSettingsModal] = React.useState(false);
    const navigate = useNavigate();
    const { user } = useAuth();
    const location = useLocation();
    const isWorkflowPage = location.pathname.startsWith('/workflow');

    return (
        <TooltipProvider delayDuration={0}>
            <div className={`flex h-screen overflow-hidden bg-background text-foreground group/sidebar`} data-sidebar={isSidebarOpen ? 'open' : 'closed'}>
                {/* Sidebar Container */}
                <div className={`transition-all duration-300 ease-in-out border-r border-border bg-sidebar-bg flex flex-col ${isSidebarOpen ? 'w-64' : 'w-[68px]'}`}>
                    {isSidebarOpen ? (
                        <ChatSidebar isOpen={isSidebarOpen} onToggle={() => setIsSidebarOpen(!isSidebarOpen)} />
                    ) : (
                        <div className="h-full flex flex-col items-center py-4 px-3 gap-6">
                            {/* Top Actions */}
                            <div className="space-y-4 flex flex-col items-center w-full">
                                <button
                                    onClick={() => setIsSidebarOpen(true)}
                                    className="p-2.5 rounded-xl hover:bg-sidebar-hover text-muted-foreground hover:text-primary transition-all duration-200"
                                    title="Open Sidebar"
                                >
                                    <PanelLeftOpen className="h-5 w-5" />
                                </button>

                                <Tooltip>
                                    <TooltipTrigger asChild>
                                        <button
                                            onClick={() => navigate('/chat/new')}
                                            className="p-2.5 rounded-xl bg-primary/10 text-primary hover:bg-primary/20 transition-all duration-200 border border-primary/20"
                                        >
                                            <SquarePen className="h-5 w-5" />
                                        </button>
                                    </TooltipTrigger>
                                    <TooltipContent side="right">New Workflow</TooltipContent>
                                </Tooltip>
                            </div>

                            {/* Center Space Filler */}
                            <div className="flex-1" />

                            {/* Bottom Profile */}
                            <div className="mt-auto pt-4 border-t border-border/50 w-full flex flex-col items-center gap-4">
                                <Tooltip>
                                    <TooltipTrigger asChild>
                                        <div
                                            onClick={() => setShowSettingsModal(true)}
                                            className="w-9 h-9 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary text-xs font-bold cursor-pointer hover:bg-primary/20 transition-all font-sans"
                                        >
                                            {user?.username?.charAt(0).toUpperCase() || <User className="h-4 w-4" />}
                                        </div>
                                    </TooltipTrigger>
                                    <TooltipContent side="right">Account: {user?.username || 'User'}</TooltipContent>
                                </Tooltip>
                            </div>
                        </div>
                    )}
                </div>

                <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
                    {!isSidebarOpen && (
                        <div className="absolute top-0 left-0 right-0 h-14 flex items-center px-4 shrink-0 z-30 pointer-events-none">
                            <div className="flex items-center gap-2 pointer-events-auto ml-2">
                                {isWorkflowPage && (
                                    <button
                                        onClick={() => navigate(-1)}
                                        className="p-2 rounded-lg hover:bg-sidebar-hover text-muted-foreground transition-colors mr-1"
                                        title="Back"
                                    >
                                        <ArrowLeft className="h-5 w-5" />
                                    </button>
                                )}
                                <div className="flex items-center gap-2 cursor-pointer group" onClick={() => navigate('/')}>
                                    <Workflow className="w-5 h-5 text-primary group-hover:scale-110 transition-transform" />
                                    <span className="font-bold tracking-tight text-lg">TaskMitra</span>
                                </div>
                            </div>
                        </div>
                    )}
                    <div className="flex-1 flex flex-col min-h-0">
                        {children}
                    </div>
                </main>

                <SettingsModal open={showSettingsModal} onOpenChange={setShowSettingsModal} />
            </div>
        </TooltipProvider>
    );
};

export default MainLayout;
