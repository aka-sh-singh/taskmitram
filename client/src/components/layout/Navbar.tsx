import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Workflow, LogOut, User } from 'lucide-react';
import ThemeToggle from '@/components/layout/ThemeToggle';

const Navbar = () => {
    const { isAuthenticated, logout, user } = useAuth();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await logout();
        navigate('/');
    };

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/80 backdrop-blur-sm">
            <div className="container mx-auto px-4 h-16 flex items-center justify-between">
                <Link to="/" className="flex items-center gap-2 text-xl font-bold">
                    <Workflow className="w-6 h-6 text-primary" />
                    <span>TaskMitra</span>
                </Link>

                <div className="flex items-center gap-3">
                    <ThemeToggle />
                    {!isAuthenticated ? (
                        <>
                            <Button
                                variant="ghost"
                                onClick={() => navigate('/login')}
                                className="hover:bg-sidebar-hover"
                            >
                                Login
                            </Button>
                            <Button
                                onClick={() => navigate('/signup')}
                                className="bg-primary hover:bg-primary-hover text-primary-foreground"
                            >
                                Sign Up
                            </Button>
                        </>
                    ) : (
                        <>
                            <Button
                                onClick={() => navigate('/chat/new')}
                                className="bg-primary hover:bg-primary-hover text-primary-foreground"
                            >
                                Create Task
                            </Button>
                            <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-card text-sm">
                                <User className="w-4 h-4" />
                                <span>{user?.username}</span>
                            </div>
                            <Button
                                variant="ghost"
                                size="icon"
                                onClick={handleLogout}
                                className="hover:bg-sidebar-hover"
                                title="Logout"
                            >
                                <LogOut className="w-4 h-4" />
                            </Button>
                        </>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
