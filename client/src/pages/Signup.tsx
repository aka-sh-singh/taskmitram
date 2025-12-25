import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Workflow } from 'lucide-react';
import ThemeToggle from '@/components/layout/ThemeToggle';

const Signup = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { signup } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!username || !email || !password) {
            return;
        }

        setIsLoading(true);
        try {
            await signup(username, email, password);
            navigate('/chat/new');
        } catch (error) {
            // Error handled in AuthContext
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4 bg-background relative">
            <div className="absolute top-4 right-4">
                <ThemeToggle />
            </div>
            <div className="w-full max-w-md">
                <div className="glass-card rounded-2xl p-8 space-y-6">
                    <div className="text-center space-y-2">
                        <Link to="/" className="flex items-center justify-center gap-2 text-2xl font-bold">
                            <Workflow className="w-8 h-8 text-primary" />
                            <span>TaskMitra</span>
                        </Link>
                        <h1 className="text-2xl font-semibold">Create Account</h1>
                        <p className="text-muted-foreground">Start your journey with TaskMitra</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="username">Username</Label>
                            <Input
                                id="username"
                                type="text"
                                placeholder="Enter unique username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="bg-input-bg border-input-border"
                                required
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="Enter your email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="bg-input-bg border-input-border"
                                required
                            />
                        </div>

                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="bg-input-bg border-input-border"
                                required
                                minLength={6}
                            />
                        </div>

                        <Button
                            type="submit"
                            className="w-full bg-primary hover:bg-primary-hover text-primary-foreground"
                            disabled={isLoading}
                        >
                            {isLoading ? 'Creating account...' : 'Sign Up'}
                        </Button>
                    </form>

                    <div className="text-center text-sm text-muted-foreground">
                        Already have an account?{' '}
                        <Link to="/login" className="text-primary hover:underline">
                            Sign in
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Signup;
