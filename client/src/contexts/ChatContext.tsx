import React, { createContext, useContext, useState } from 'react';
import { axiosInstance } from '@/lib/axios';
import { toast } from 'react-toastify';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext';

interface Message {
    id: string;
    sender: 'user' | 'agent';
    content: string;
    thought?: string;
    created_at: string;
}

interface Chat {
    id: string;
    title: string;
    last_activity: string;
    messages?: Message[];
}

interface ChatContextType {
    currentChatId: string | null;
    chats: Chat[];
    messages: Message[];
    isStreaming: boolean;
    loadChats: () => Promise<void>;
    loadChat: (chatId: string) => Promise<void>;
    sendMessage: (chatId: string, content: string) => Promise<void>;
    renameChat: (chatId: string, newTitle: string) => Promise<void>;
    deleteChat: (chatId: string) => Promise<void>;
    deleteAllChats: () => Promise<void>;
    setCurrentChatId: (chatId: string | null) => void;
    clearMessages: () => void;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [currentChatId, setCurrentChatId] = useState<string | null>(null);
    const [chats, setChats] = useState<Chat[]>([]);
    const [messages, setMessages] = useState<Message[]>([]);
    const [isStreaming, setIsStreaming] = useState(false);
    const { silentRefresh } = useAuth();
    const navigate = useNavigate();

    const isFetchingChats = React.useRef(false);

    const loadChats = async () => {
        if (isFetchingChats.current) return;

        const token = localStorage.getItem('access_token');
        if (!token) {
            setChats([]);
            return;
        }

        isFetchingChats.current = true;
        try {
            const response = await axiosInstance.get('/chats/');
            setChats(response.data);
        } catch (error) {
            console.error('Failed to load chats:', error);
            setChats([]);
        } finally {
            isFetchingChats.current = false;
        }
    };

    const loadChat = async (chatId: string) => {
        try {
            const response = await axiosInstance.get(`/chats/${chatId}`);
            setMessages(response.data.messages || []);
            setCurrentChatId(chatId);
        } catch (error) {
            console.error('Failed to load chat:', error);
            toast.error('Failed to load chat');
        }
    };

    const sendMessage = async (chatId: string, content: string) => {
        setIsStreaming(true);

        try {
            const userMessage: Message = {
                id: Date.now().toString(),
                sender: 'user' as const,
                content,
                created_at: new Date().toISOString(),
            };

            // Generate agent message ID in advance
            const agentMessageId = (Date.now() + 1).toString();
            const initialAgentMessage: Message = {
                id: agentMessageId,
                sender: 'agent' as const,
                content: '',
                created_at: new Date().toISOString(),
            };

            // Add both messages to state
            setMessages((prev) => [...prev, userMessage, initialAgentMessage]);

            const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

            let response = await fetch(`${apiUrl}/chats/${chatId}/messages`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                },
                body: JSON.stringify({ sender: 'user', content }),
            });

            // Handle token rotation (401)
            if (response.status === 401) {
                const refreshed = await silentRefresh();
                if (refreshed) {
                    // Retry with new token
                    response = await fetch(`${apiUrl}/chats/${chatId}/messages`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                        },
                        body: JSON.stringify({ sender: 'user', content }),
                    });
                } else {
                    throw new Error('Session expired. Please login again.');
                }
            }

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || 'Failed to connect to stream');
            }

            // Handle potential chat ID change (for "new" chats)
            const serverChatId = response.headers.get('X-Chat-Id') || response.headers.get('x-chat-id');
            if (serverChatId && serverChatId !== chatId) {
                setCurrentChatId(serverChatId);
                navigate(`/chat/${serverChatId}`, { replace: true });
                // Load chats immediately so the sidebar updates while streaming
                await loadChats();
            }

            const reader = response.body?.getReader();
            if (!reader) throw new Error('No body reader');

            const decoder = new TextDecoder();
            let accumulatedContent = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                accumulatedContent += chunk;

                // Functional update to ensure we have the latest messages state
                setMessages((prev) =>
                    prev.map((msg) =>
                        msg.id === agentMessageId ? { ...msg, content: accumulatedContent } : msg
                    )
                );
            }

            await loadChats();
        } catch (error: any) {
            console.error('Failed to send message:', error);
            toast.error(error.message || 'Failed to send message');
            // Cleanup: remove the empty agent message on error
            setMessages(prev => prev.filter(m => m.content !== '' || m.sender === 'user'));
        } finally {
            setIsStreaming(false);
        }
    };

    const renameChat = async (chatId: string, newTitle: string) => {
        try {
            await axiosInstance.patch(`/chats/${chatId}`, { title: newTitle });
            setChats((prev) =>
                prev.map((chat) =>
                    chat.id === chatId ? { ...chat, title: newTitle } : chat
                )
            );
            toast.success('Chat renamed');
        } catch (error) {
            console.error('Failed to rename chat:', error);
            toast.error('Failed to rename chat');
        }
    };

    const deleteChat = async (chatId: string) => {
        try {
            await axiosInstance.delete(`/chats/${chatId}`);
            setChats((prev) => prev.filter((chat) => chat.id !== chatId));
            if (currentChatId === chatId) {
                setCurrentChatId(null);
                setMessages([]);
            }
            toast.success('Chat deleted');
        } catch (error) {
            console.error('Failed to delete chat:', error);
            toast.error('Failed to delete chat');
        }
    };

    const deleteAllChats = async () => {
        try {
            await axiosInstance.delete('/chats/');
            setChats([]);
            setCurrentChatId(null);
            setMessages([]);
            toast.success('All chats deleted');
            navigate('/chat/new');
        } catch (error) {
            console.error('Failed to delete all chats:', error);
            toast.error('Failed to delete all chats');
        }
    };

    const clearMessages = () => {
        setMessages([]);
    };

    return (
        <ChatContext.Provider
            value={{
                currentChatId,
                chats,
                messages,
                isStreaming,
                loadChats,
                loadChat,
                sendMessage,
                renameChat,
                deleteChat,
                deleteAllChats,
                setCurrentChatId,
                clearMessages,
            }}
        >
            {children}
        </ChatContext.Provider>
    );
};

export const useChat = () => {
    const context = useContext(ChatContext);
    if (!context) {
        throw new Error('useChat must be used within ChatProvider');
    }
    return context;
};
