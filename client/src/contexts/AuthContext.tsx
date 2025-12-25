import React, { createContext, useContext, useState, useEffect } from 'react';
import { axiosInstance, setOnTokenRefreshedCallback } from '@/lib/axios';
import { toast } from 'react-toastify';

interface User {
    id: string;
    username: string;
    email: string;
}

interface AuthContextType {
    user: User | null;
    accessToken: string | null;
    refreshToken: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    login: (email: string, password: string) => Promise<void>;
    signup: (username: string, email: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
    silentRefresh: () => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

let isRefreshing = false;
let refreshPromise: Promise<boolean> | null = null;

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [user, setUser] = useState<User | null>(null);
    const [accessToken, setAccessToken] = useState<string | null>(
        localStorage.getItem('access_token')
    );
    const [refreshToken, setRefreshToken] = useState<string | null>(
        localStorage.getItem('refresh_token')
    );
    const [isLoading, setIsLoading] = useState(true);

    // Sync React state when the axios interceptor rotates tokens
    useEffect(() => {
        setOnTokenRefreshedCallback((newAccess, newRefresh) => {
            setAccessToken(newAccess);
            setRefreshToken(newRefresh);
        });
    }, []);

    // Silent refresh on mount
    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem('access_token');
            if (token) {
                const success = await silentRefresh();
                if (success) {
                    await fetchUserProfile();
                }
            }
            setIsLoading(false);
        };

        initAuth();
    }, []);

    const fetchUserProfile = async () => {
        try {
            const response = await axiosInstance.get('/users/me');
            setUser(response.data);
        } catch (error) {
            console.error('Failed to fetch user profile:', error);
        }
    };

    const silentRefresh = async (): Promise<boolean> => {
        const refresh = localStorage.getItem("refresh_token");
        if (!refresh) return false;

        if (isRefreshing) return refreshPromise!;

        isRefreshing = true;

        refreshPromise = (async () => {
            try {
                // Use a standard axios call here to avoid interceptor recursion if it somehow fails
                const response = await axiosInstance.post("/auth/refresh", {
                    refresh_token: refresh,
                });

                const { access_token, refresh_token: newRefreshToken } = response.data;

                localStorage.setItem("access_token", access_token);
                localStorage.setItem("refresh_token", newRefreshToken);

                setAccessToken(access_token);
                setRefreshToken(newRefreshToken);

                return true;
            } catch (error) {
                localStorage.removeItem("access_token");
                localStorage.removeItem("refresh_token");
                setAccessToken(null);
                setRefreshToken(null);
                return false;
            } finally {
                isRefreshing = false;
                refreshPromise = null;
            }
        })();

        return refreshPromise;
    };

    const login = async (email: string, password: string) => {
        try {
            const response = await axiosInstance.post('/auth/login', {
                email,
                password,
            });

            const { access_token, refresh_token } = response.data;
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            setAccessToken(access_token);
            setRefreshToken(refresh_token);

            await fetchUserProfile();
            toast.success('Login successful!');
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Login failed';
            toast.error(message);
            throw error;
        }
    };

    const signup = async (username: string, email: string, password: string) => {
        try {
            const response = await axiosInstance.post('/auth/signup', {
                username,
                email,
                password,
            });

            const { access_token, refresh_token } = response.data;
            localStorage.setItem('access_token', access_token);
            localStorage.setItem('refresh_token', refresh_token);
            setAccessToken(access_token);
            setRefreshToken(refresh_token);

            await fetchUserProfile();
            toast.success('Account created successfully!');
        } catch (error: any) {
            const message = error.response?.data?.detail || 'Signup failed';
            toast.error(message);
            throw error;
        }
    };

    const logout = async () => {
        try {
            const refresh = localStorage.getItem('refresh_token');
            if (refresh) {
                await axiosInstance.post('/auth/logout', {
                    refresh_token: refresh,
                });
            }
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            setAccessToken(null);
            setRefreshToken(null);
            setUser(null);
            toast.info('Logged out successfully');
        }
    };

    return (
        <AuthContext.Provider
            value={{
                user,
                accessToken,
                refreshToken,
                isAuthenticated: !!accessToken && !!user,
                isLoading,
                login,
                signup,
                logout,
                silentRefresh,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};
