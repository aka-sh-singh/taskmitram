import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from 'next-themes';
import { TooltipProvider } from '@/components/ui/tooltip';
import { ToastContainer } from 'react-toastify';
import { AuthProvider } from '@/contexts/AuthContext';
import { ChatProvider } from '@/contexts/ChatContext';
import { OAuthHandler } from '@/components/auth/OAuthHandler';
import Landing from '@/pages/Landing';
import Login from '@/pages/Login';
import Signup from '@/pages/Signup';
import Chat from '@/pages/Chat';
import Workflow from '@/pages/Workflow';
import NotFound from '@/pages/NotFound';
import MainLayout from '@/components/layout/MainLayout';
import 'react-toastify/dist/ReactToastify.css';

const queryClient = new QueryClient();

const App = () => (
    <QueryClientProvider client={queryClient}>
        <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
            <TooltipProvider>
                <BrowserRouter>
                    <AuthProvider>
                        <ChatProvider>
                            <OAuthHandler />
                            <Routes>
                                <Route path="/" element={<Landing />} />
                                <Route path="/login" element={<Login />} />
                                <Route path="/signup" element={<Signup />} />

                                {/* Protected Routes with persistent Sidebar */}
                                <Route path="/chat/:chatId" element={<MainLayout><Chat /></MainLayout>} />
                                <Route path="/workflow/:workflowId" element={<MainLayout><Workflow /></MainLayout>} />

                                <Route path="*" element={<NotFound />} />
                            </Routes>
                            <ToastContainer
                                position="top-right"
                                autoClose={3000}
                                hideProgressBar={false}
                                newestOnTop
                                closeOnClick
                                rtl={false}
                                pauseOnFocusLoss
                                draggable
                                pauseOnHover
                                theme="dark"
                                style={{ zIndex: 9999 }}
                            />
                        </ChatProvider>
                    </AuthProvider>
                </BrowserRouter>
            </TooltipProvider>
        </ThemeProvider>
    </QueryClientProvider>
);

export default App;
