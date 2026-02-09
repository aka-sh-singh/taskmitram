import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useChat } from '@/contexts/ChatContext';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, Loader2, LayoutDashboard, Workflow, CheckCircle2, Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { axiosInstance } from '@/lib/axios';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from '@/components/ui/dialog';

const ChatWindow = () => {
    const { chatId } = useParams<{ chatId: string }>();
    const { messages, loadChat, sendMessage, isStreaming, currentChatId, clearMessages, setCurrentChatId } =
        useChat();
    const { isAuthenticated, isLoading } = useAuth();
    const navigate = useNavigate();
    const [input, setInput] = useState('');
    const [processedActions, setProcessedActions] = useState<Set<string>>(new Set());
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        if (isLoading) return;

        if (!isAuthenticated) {
            navigate('/login');
            return;
        }

        if (chatId && chatId !== 'new') {
            // Only load if it's a different chat or if we're not currently streaming
            if (currentChatId !== chatId && !isStreaming) {
                loadChat(chatId);
            }
            setCurrentChatId(chatId);
        } else if (chatId === 'new') {
            clearMessages();
            setCurrentChatId(null);
        }
    }, [chatId, isAuthenticated, isStreaming, isLoading]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: isStreaming ? 'auto' : 'smooth' });
    };

    if (isLoading) {
        return (
            <div className="flex-1 flex items-center justify-center bg-background">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
        );
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isStreaming) return;

        const message = input.trim();
        setInput('');

        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
        }

        const targetChatId = currentChatId ?? chatId ?? 'new';

        await sendMessage(targetChatId, message);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInput(e.target.value);
        e.target.style.height = 'auto';
        e.target.style.height = Math.min(e.target.scrollHeight, 200) + 'px';
    };

    return (
        <div className="flex-1 flex flex-col h-screen bg-background">
            {/* Header with Dashboard and Workflow Buttons */}
            <div className="h-14 border-b border-border flex items-center justify-between px-6 bg-sidebar-bg">
                <h2 className="text-lg font-semibold text-foreground">
                    {chatId === 'new' ? 'New Workflow' : 'Workflow Orchestration'}
                </h2>

                <div className="flex items-center gap-2">
                    {currentChatId && (
                        <Dialog>
                            <DialogTrigger asChild>
                                <Button variant="outline" size="sm" className="gap-2">
                                    <LayoutDashboard className="h-4 w-4" />
                                    Dashboard
                                </Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Workflow Dashboard</DialogTitle>
                                    <DialogDescription>
                                        This feature is coming soon. Here you'll be able to view all the workflow from this chat window.
                                    </DialogDescription>
                                </DialogHeader>
                                <div className="py-8 text-center text-muted-foreground">
                                    <Workflow className="h-16 w-16 mx-auto mb-4 opacity-50" />
                                    <p className="text-sm">Future use - Workflow monitoring and orchestration dashboard</p>
                                </div>
                            </DialogContent>
                        </Dialog>
                    )}
                </div>
            </div>

            <div className="flex-1 overflow-y-auto px-4 py-6">
                {messages.length === 0 ? (
                    <div className="h-full flex items-center justify-center">
                        <div className="text-center space-y-4 max-w-md">
                            <h2 className="text-2xl font-semibold">Create a Workflow</h2>
                            <p className="text-muted-foreground">
                                Describe your workflow and let TaskMitra orchestrate it for you
                            </p>
                        </div>
                    </div>
                ) : (
                    <div className="max-w-3xl mx-auto space-y-6">
                        {messages.map((message) => {
                            // Don't render empty agent messages while streaming (to avoid empty pills)
                            if (message.sender === 'agent' && !message.content && isStreaming) {
                                return null;
                            }

                            return (
                                <div
                                    key={message.id}
                                    className={`chat-message flex gap-3 px-2 ${message.sender === 'user' ? 'flex-row-reverse' : 'flex-row'
                                        }`}
                                >
                                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center border shadow-sm ${message.sender === 'user'
                                        ? 'bg-primary/10 border-primary/20 text-primary'
                                        : 'bg-muted border-border text-muted-foreground'
                                        }`}>
                                        {message.sender === 'user' ? (
                                            <User className="w-5 h-5" />
                                        ) : (
                                            <Bot className="w-5 h-5 text-primary" />
                                        )}
                                    </div>

                                    <div
                                        className={`flex-1 min-w-0 ${message.sender === 'user' ? 'flex justify-end' : ''}`}
                                    >
                                        <div
                                            className={`transition-all duration-200 ${message.sender === 'user'
                                                ? 'max-w-[85%] bg-bubble-user text-primary-foreground rounded-2xl px-4 py-2.5 shadow-sm'
                                                : 'w-full py-1'
                                                }`}
                                        >
                                            {message.sender === 'user' ? (
                                                <div className="whitespace-pre-wrap break-words text-sm leading-relaxed">{message.content}</div>
                                            ) : (
                                                <div className="space-y-4">
                                                    <div className={`prose prose-sm dark:prose-invert max-w-none break-words font-sans text-foreground/90 leading-relaxed content-transition ${isStreaming && message.id === messages[messages.length - 1]?.id ? 'streaming-content' : ''
                                                        }`}>
                                                        <ReactMarkdown>
                                                            {message.content.replace(/\[ACTION_ID:[^\]]+\]/g, '')}
                                                        </ReactMarkdown>
                                                    </div>

                                                    {/* Parsing Action Tag */}
                                                    {message.content.match(/\[ACTION_ID:([^:]+):([^\]]+)\]/) && (() => {
                                                        const match = message.content.match(/\[ACTION_ID:([^:]+):([^\]]+)\]/);
                                                        if (!match) return null;
                                                        const actionId = match[1];
                                                        const actionName = match[2];
                                                        const isProcessed = processedActions.has(actionId);

                                                        return (
                                                            <div className="mt-4 p-4 border border-primary/20 rounded-xl bg-primary/5 space-y-3 animate-in fade-in slide-in-from-bottom-2 max-w-xl">
                                                                <div className="flex items-center gap-2 text-sm font-medium text-primary">
                                                                    <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
                                                                        <Workflow className="w-4 h-4" />
                                                                    </div>
                                                                    <div className="flex flex-col">
                                                                        <span className="text-xs opacity-70 uppercase tracking-wider">Security Check</span>
                                                                        <span>Authorize {actionName.replace('_', ' ')}?</span>
                                                                    </div>
                                                                </div>

                                                                {isProcessed ? (
                                                                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                                                        <CheckCircle2 className="w-4 h-4 text-green-500" />
                                                                        <span>Action processed.</span>
                                                                    </div>
                                                                ) : (
                                                                    <div className="flex gap-2">
                                                                        <Button
                                                                            size="sm"
                                                                            className="flex-1 bg-primary hover:bg-primary/90 shadow-sm"
                                                                            onClick={async (e) => {
                                                                                const target = e.currentTarget;
                                                                                target.disabled = true;
                                                                                if (match) {
                                                                                    try {
                                                                                        await axiosInstance.post(`/approvals/${actionId}/approve`, {});
                                                                                        setProcessedActions(prev => new Set(prev).add(actionId)); // Mark as processed
                                                                                        sendMessage(chatId || 'new', "Approved. Please proceed.");
                                                                                    } catch (err) {
                                                                                        console.error("Approval failed", err);
                                                                                        target.disabled = false;
                                                                                    }
                                                                                }
                                                                            }}
                                                                        >
                                                                            Confirm Action
                                                                        </Button>
                                                                        <Button
                                                                            size="sm"
                                                                            variant="outline"
                                                                            className="flex-1 border-primary/20 hover:bg-destructive/5 hover:text-destructive hover:border-destructive/20"
                                                                            onClick={async (e) => {
                                                                                const target = e.currentTarget;
                                                                                target.disabled = true;
                                                                                if (match) {
                                                                                    try {
                                                                                        await axiosInstance.post(`/approvals/${actionId}/reject`, {});
                                                                                        setProcessedActions(prev => new Set(prev).add(actionId)); // Mark as processed
                                                                                        // Send a message to the agent so it knows it was cancelled
                                                                                        sendMessage(chatId || 'new', "Rejected. Do not proceed with this action.");
                                                                                    } catch (err) {
                                                                                        console.error("Rejection failed", err);
                                                                                        target.disabled = false;
                                                                                    }
                                                                                }
                                                                            }}
                                                                        >
                                                                            Cancel
                                                                        </Button>
                                                                    </div>
                                                                )}
                                                            </div>
                                                        );
                                                    })()}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            );
                        })}

                        {/* Show typing indicator only if the last agent message is empty */}
                        {isStreaming && (!messages[messages.length - 1]?.content) && (
                            <div className="flex items-start gap-3 px-2">
                                <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center border shadow-sm bg-muted border-border text-muted-foreground">
                                    <Bot className="w-5 h-5 text-primary" />
                                </div>
                                <div className="py-2">
                                    <div className="typing-indicator">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            <div className="border-t border-border bg-input-bg p-4">
                <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
                    <div className="flex gap-3 items-end">
                        <Textarea
                            ref={textareaRef}
                            value={input}
                            onChange={handleTextareaChange}
                            onKeyDown={handleKeyDown}
                            placeholder="Describe your workflow..."
                            className="flex-1 min-h-[56px] max-h-[200px] resize-none bg-background border-input-border focus-visible:ring-primary"
                            rows={1}
                            disabled={isStreaming}
                        />
                        <Button
                            type="submit"
                            size="icon"
                            className="h-14 w-14 flex-shrink-0 bg-primary hover:bg-primary-hover text-primary-foreground"
                            disabled={!input.trim() || isStreaming}
                        >
                            {isStreaming ? (
                                <Loader2 className="w-5 h-5 animate-spin" />
                            ) : (
                                <Send className="w-5 h-5" />
                            )}
                        </Button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default ChatWindow;
