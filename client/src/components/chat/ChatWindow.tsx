import React, { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useChat } from '@/contexts/ChatContext';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, Loader2, Workflow, CheckCircle2, Bot, User } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { axiosInstance } from '@/lib/axios';

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

    React.useLayoutEffect(() => {
        if (isLoading) return;

        if (!isAuthenticated) {
            navigate('/login');
            return;
        }

        if (chatId && chatId !== 'new') {
            if (currentChatId !== chatId && !isStreaming) {
                loadChat(chatId);
            }
            setCurrentChatId(chatId);
        } else if (chatId === 'new' && !isStreaming) {
            if (currentChatId !== null || messages.length > 0) {
                clearMessages();
                setCurrentChatId(null);
            }
        }
    }, [chatId, isAuthenticated, isStreaming, isLoading, currentChatId]);

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
        <div className="flex-1 flex flex-col h-full bg-background relative">
            {/* Header (Standardized Navigation Bar) */}
            <div className="h-14 border-b border-border flex items-center justify-between px-6 bg-sidebar-bg z-10">
                <div className="flex items-center gap-2">
                </div>

                <div className="flex items-center gap-2">
                    {currentChatId && (
                        <Button
                            variant="ghost"
                            size="sm"
                            className="gap-2 text-muted-foreground hover:text-primary transition-all duration-300 rounded-full border border-border/50 hover:border-primary/30"
                            onClick={() => navigate(`/workflow/${currentChatId}`)}
                        >
                            <Workflow className="h-4 w-4" />
                            Workflow
                        </Button>
                    )}
                </div>
            </div>

            <div className="flex-1 overflow-y-auto no-scrollbar scroll-smooth">
                {(chatId === 'new' && messages.length === 0) ? (
                    <div className="h-full flex flex-col items-center justify-center -mt-14 px-4">
                        <div className="text-center space-y-6 max-w-2xl w-full">
                            <div className="relative inline-block mb-4">
                                <div className="absolute -inset-4 bg-primary/10 rounded-full blur-2xl animate-pulse"></div>
                                <Workflow className="h-12 w-12 text-primary relative" />
                            </div>
                            <h2 className="text-3xl font-bold tracking-tight">What would you like to automate?</h2>

                            {/* Centered Input Area for New Chat */}
                            <div className="w-full max-w-2xl mt-8">
                                <form onSubmit={handleSubmit} className="relative group">
                                    <div className="absolute -inset-0.5 bg-gradient-to-r from-primary/30 to-blue-500/30 rounded-2xl blur opacity-30 group-hover:opacity-100 transition duration-500"></div>
                                    <div className="relative bg-card border border-border rounded-2xl p-4 shadow-xl shadow-primary/5">
                                        <Textarea
                                            ref={textareaRef}
                                            value={input}
                                            onChange={handleTextareaChange}
                                            onKeyDown={handleKeyDown}
                                            placeholder="Describe your workflow..."
                                            className="w-full min-h-[100px] max-h-[400px] resize-none bg-transparent border-0 focus-visible:ring-0 p-2 text-lg leading-relaxed placeholder:text-muted-foreground/50"
                                            rows={2}
                                            disabled={isStreaming}
                                        />
                                        <div className="flex items-center justify-between mt-2 pt-2 border-t border-border/50">
                                            <div className="flex gap-1">
                                                <button type="button" className="p-2 rounded-lg hover:bg-muted text-muted-foreground transition-colors">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l8.57-8.57A4 4 0 1 1 18 8.84l-8.59 8.51a2 2 0 0 1-2.83-2.83l8.49-8.48" /></svg>
                                                </button>
                                            </div>
                                            <Button
                                                type="submit"
                                                size="icon"
                                                className={`h-10 w-10 rounded-xl transition-all duration-300 ${input.trim() ? 'bg-primary text-primary-foreground scale-100' : 'bg-muted text-muted-foreground scale-95 opacity-50'}`}
                                                disabled={!input.trim() || isStreaming}
                                            >
                                                {isStreaming ? (
                                                    <Loader2 className="w-5 h-5 animate-spin" />
                                                ) : (
                                                    <Send className="w-5 h-5" />
                                                )}
                                            </Button>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>
                ) : (
                    <div className="max-w-3xl mx-auto space-y-8 py-10 px-4">
                        {messages.map((message) => {
                            if (message.sender === 'agent' && !message.content && isStreaming) {
                                return null;
                            }

                            return (
                                <div
                                    key={message.id}
                                    className={`flex gap-4 group animate-in fade-in duration-500`}
                                >
                                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center border shadow-sm ${message.sender === 'user'
                                        ? 'bg-muted/50 border-border text-foreground order-last'
                                        : 'bg-primary/10 border-primary/20 text-primary'
                                        }`}>
                                        {message.sender === 'user' ? (
                                            <User className="w-4 h-4" />
                                        ) : (
                                            <Bot className="w-4 h-4" />
                                        )}
                                    </div>

                                    <div className={`flex-1 min-w-0 ${message.sender === 'user' ? 'text-right' : ''}`}>
                                        <div className={`inline-block text-left max-w-full ${message.sender === 'user'
                                            ? 'bg-muted/30 px-4 py-2.5 rounded-2xl border border-border/50'
                                            : 'w-full'
                                            }`}>
                                            {message.sender === 'user' ? (
                                                <div className="whitespace-pre-wrap break-words text-sm leading-relaxed text-foreground/90">{message.content}</div>
                                            ) : (
                                                <div className="space-y-4">
                                                    <div className={`prose prose-sm dark:prose-invert max-w-none break-words font-sans text-foreground/90 leading-relaxed content-transition ${isStreaming && message.id === messages[messages.length - 1]?.id ? 'streaming-content' : ''}`}>
                                                        <ReactMarkdown>
                                                            {message.content.replace(/\[ACTION_ID:[^\]]+\]/g, '')}
                                                        </ReactMarkdown>
                                                    </div>

                                                    {/* Action Cards (Redesigned) */}
                                                    {message.content.match(/\[ACTION_ID:([^:]+):([^\]]+)\]/) && (() => {
                                                        const match = message.content.match(/\[ACTION_ID:([^:]+):([^\]]+)\]/);
                                                        if (!match) return null;
                                                        const actionId = match[1];
                                                        const actionName = match[2];
                                                        const isProcessed = processedActions.has(actionId);

                                                        return (
                                                            <div className="mt-4 p-5 border border-primary/20 rounded-2xl bg-primary/5 space-y-4 animate-in fade-in slide-in-from-bottom-3 max-w-xl">
                                                                <div className="flex items-center gap-3 text-sm font-medium text-primary">
                                                                    <div className="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center shadow-inner">
                                                                        <Workflow className="w-5 h-5" />
                                                                    </div>
                                                                    <div className="flex flex-col">
                                                                        <span className="text-[10px] opacity-70 uppercase tracking-widest font-bold">Safe Guard</span>
                                                                        <span className="text-base">Authorize {actionName.replace('_', ' ')}?</span>
                                                                    </div>
                                                                </div>

                                                                {isProcessed ? (
                                                                    <div className="flex items-center gap-2 text-sm text-green-600 bg-green-500/10 w-fit px-3 py-1.5 rounded-lg border border-green-500/20">
                                                                        <CheckCircle2 className="w-4 h-4" />
                                                                        <span>Successfully processed</span>
                                                                    </div>
                                                                ) : (
                                                                    <div className="flex gap-2">
                                                                        <Button
                                                                            size="sm"
                                                                            className="flex-1 bg-primary hover:bg-primary-hover shadow-lg shadow-primary/20 rounded-xl py-5 h-auto"
                                                                            onClick={async (e) => {
                                                                                const target = e.currentTarget;
                                                                                target.disabled = true;
                                                                                if (match) {
                                                                                    try {
                                                                                        await axiosInstance.post(`/approvals/${actionId}/approve`, {});
                                                                                        setProcessedActions(prev => new Set(prev).add(actionId));
                                                                                        sendMessage(chatId || 'new', "Approved. Please proceed.");
                                                                                    } catch (err) {
                                                                                        console.error("Approval failed", err);
                                                                                        target.disabled = false;
                                                                                    }
                                                                                }
                                                                            }}
                                                                        >
                                                                            Confirm Execution
                                                                        </Button>
                                                                        <Button
                                                                            size="sm"
                                                                            variant="outline"
                                                                            className="flex-1 border-primary/20 hover:bg-destructive/5 hover:text-destructive hover:border-destructive/20 rounded-xl py-5 h-auto text-muted-foreground"
                                                                            onClick={async (e) => {
                                                                                const target = e.currentTarget;
                                                                                target.disabled = true;
                                                                                if (match) {
                                                                                    try {
                                                                                        await axiosInstance.post(`/approvals/${actionId}/reject`, {});
                                                                                        setProcessedActions(prev => new Set(prev).add(actionId));
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

                        {isStreaming && (!messages[messages.length - 1]?.content) && (
                            <div className="flex items-start gap-4">
                                <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center border shadow-sm bg-primary/10 border-primary/20 text-primary">
                                    <Bot className="w-4 h-4" />
                                </div>
                                <div className="py-2">
                                    <div className="typing-indicator scale-75">
                                        <span></span>
                                        <span></span>
                                        <span></span>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div ref={messagesEndRef} className="h-40" />
                    </div>
                )}
            </div>

            {/* Sticky Bottom Input Area (Only visible when chat has messages and not a new chat) */}
            {(messages.length > 0 && chatId !== 'new') && (
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-background via-background/95 to-transparent pb-8 pt-10 px-4 pointer-events-none">
                    <div className="max-w-3xl mx-auto pointer-events-auto">
                        <form onSubmit={handleSubmit} className="relative group">
                            <div className="absolute -inset-0.5 bg-border rounded-xl opacity-20 group-focus-within:opacity-100 transition duration-300 ring-1 ring-primary/20"></div>
                            <div className="relative bg-card border border-border rounded-xl flex items-end p-2 px-3 shadow-lg">
                                <Textarea
                                    ref={textareaRef}
                                    value={input}
                                    onChange={handleTextareaChange}
                                    onKeyDown={handleKeyDown}
                                    placeholder="Message TaskMitra..."
                                    className="flex-1 min-h-[44px] max-h-[200px] resize-none border-0 focus-visible:ring-0 bg-transparent py-3 text-base leading-snug"
                                    rows={1}
                                    disabled={isStreaming}
                                />
                                <Button
                                    type="submit"
                                    size="icon"
                                    className={`mb-1 h-9 w-9 rounded-lg transition-all ${input.trim() ? 'bg-primary text-primary-foreground opacity-100' : 'bg-muted text-muted-foreground opacity-40'}`}
                                    disabled={!input.trim() || isStreaming}
                                >
                                    {isStreaming ? (
                                        <Loader2 className="w-4 h-4 animate-spin" />
                                    ) : (
                                        <Send className="w-4 h-4" />
                                    )}
                                </Button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ChatWindow;
