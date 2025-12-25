import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useChat } from '@/contexts/ChatContext';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { SettingsModal } from '@/components/settings';
import ThemeToggle from '@/components/layout/ThemeToggle';
import {
    Workflow,
    Plus,
    MoreVertical,
    Edit2,
    Trash2,
    User,
    X,
    Check,
} from 'lucide-react';
import {
    DropdownMenu,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
    Tooltip,
    TooltipContent,
    TooltipProvider,
    TooltipTrigger,
} from "@/components/ui/tooltip";

const ChatSidebar = () => {
    const { chats, loadChats, renameChat, deleteChat, currentChatId, setCurrentChatId, clearMessages } = useChat();
    const { user } = useAuth();
    const navigate = useNavigate();
    const [editingId, setEditingId] = useState<string | null>(null);
    const [editTitle, setEditTitle] = useState('');
    const [showSettingsModal, setShowSettingsModal] = useState(false);

    useEffect(() => {
        loadChats();
    }, []);

    const handleRename = async (chatId: string) => {
        if (editTitle.trim()) {
            await renameChat(chatId, editTitle);
            setEditingId(null);
            setEditTitle('');
        }
    };

    const handleDelete = async (chatId: string) => {
        if (confirm('Are you sure you want to delete this chat?')) {
            await deleteChat(chatId);
            if (currentChatId === chatId) {
                navigate('/chat/new');
            }
        }
    };

    const sortedChats = [...chats].sort(
        (a, b) => new Date(b.last_activity).getTime() - new Date(a.last_activity).getTime()
    );

    return (
        <TooltipProvider>
            <div className="w-64 h-screen bg-sidebar-bg border-r border-border flex flex-col">
                <div className="p-4 border-b border-border flex items-center justify-between">
                    <Link to="/" className="flex flex-col gap-1">
                        <div className="flex items-center gap-2">
                            <Workflow className="w-6 h-6 text-primary" />
                            <span className="text-xl font-bold">TaskMitra</span>
                        </div>
                        <p className="text-xs text-muted-foreground pl-8">Workflow Orchestration</p>
                    </Link>
                    <ThemeToggle />
                </div>

                <div className="p-3">
                    <Button
                        onClick={() => {
                            clearMessages();
                            setCurrentChatId(null);
                            navigate('/chat/new');
                        }}
                        className="w-full bg-primary hover:bg-primary-hover text-primary-foreground"
                    >
                        <Plus className="w-4 h-4 mr-2" />
                        New Workflow
                    </Button>
                </div>

                <div className="flex-1 overflow-y-auto px-3 space-y-1">
                    {sortedChats.map((chat) => (
                        <div
                            key={chat.id}
                            className={`group relative flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${currentChatId === chat.id
                                ? 'bg-sidebar-hover'
                                : 'hover:bg-sidebar-hover'
                                }`}
                        >
                            {editingId === chat.id ? (
                                <div className="flex-1 flex items-center gap-2">
                                    <input
                                        value={editTitle}
                                        onChange={(e) => setEditTitle(e.target.value)}
                                        className="h-7 w-full bg-input-bg border border-input-border rounded px-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                                        autoFocus
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter') handleRename(chat.id);
                                            if (e.key === 'Escape') setEditingId(null);
                                        }}
                                    />
                                    <Button
                                        size="icon"
                                        variant="ghost"
                                        className="h-7 w-7"
                                        onClick={() => handleRename(chat.id)}
                                    >
                                        <Check className="w-3 h-3" />
                                    </Button>
                                    <Button
                                        size="icon"
                                        variant="ghost"
                                        className="h-7 w-7"
                                        onClick={() => setEditingId(null)}
                                    >
                                        <X className="w-3 h-3" />
                                    </Button>
                                </div>
                            ) : (
                                <>
                                    <Workflow className="w-4 h-4 flex-shrink-0 text-muted-foreground" />
                                    <Tooltip>
                                        <TooltipTrigger asChild>
                                            <div
                                                className="flex-1 text-sm truncate"
                                                onClick={() => navigate(`/chat/${chat.id}`)}
                                            >
                                                {chat.title}
                                            </div>
                                        </TooltipTrigger>
                                        <TooltipContent side="right" className="max-w-xs break-words">
                                            {chat.title}
                                        </TooltipContent>
                                    </Tooltip>
                                    <DropdownMenu>
                                        <DropdownMenuTrigger asChild>
                                            <Button
                                                size="icon"
                                                variant="ghost"
                                                className="h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity"
                                            >
                                                <MoreVertical className="w-3 h-3" />
                                            </Button>
                                        </DropdownMenuTrigger>
                                        <DropdownMenuContent align="end">
                                            <DropdownMenuItem
                                                onClick={() => {
                                                    setEditingId(chat.id);
                                                    setEditTitle(chat.title);
                                                }}
                                            >
                                                <Edit2 className="w-4 h-4 mr-2" />
                                                Rename
                                            </DropdownMenuItem>
                                            <DropdownMenuItem
                                                onClick={() => handleDelete(chat.id)}
                                                className="text-destructive"
                                            >
                                                <Trash2 className="w-4 h-4 mr-2" />
                                                Delete
                                            </DropdownMenuItem>
                                        </DropdownMenuContent>
                                    </DropdownMenu>
                                </>
                            )}
                        </div>
                    ))}
                </div>

                <div className="p-3 border-t border-border">
                    <Button
                        variant="ghost"
                        className="w-full justify-start hover:bg-sidebar-hover"
                        onClick={() => setShowSettingsModal(true)}
                    >
                        <User className="w-4 h-4 mr-2" />
                        <span className="truncate">{user?.username || 'Guest'}</span>
                    </Button>
                </div>
            </div>

            <SettingsModal open={showSettingsModal} onOpenChange={setShowSettingsModal} />
        </TooltipProvider>
    );
};

export default ChatSidebar;
