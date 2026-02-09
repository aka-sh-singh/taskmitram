import React, { createContext, useContext, useState, useEffect } from 'react';
import { axiosInstance, setOnTokenRefreshedCallback, refreshTokens } from '@/lib/axios';
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

    // Optimized Auth Initialization
    useEffect(() => {
        const initAuth = async () => {
            const token = localStorage.getItem('access_token');
            if (token) {
                try {
                    await fetchUserProfile();
                } catch (error) {
                    console.error("Initial profile fetch failed:", error);
                }
            }

            // Only stop "loading" if we succeeded in getting a user OR if we truly have no token
            // This prevents a "flash" of the login page during token rotation
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
                const data = await refreshTokens(refresh);
                const { access_token, refresh_token: newRefreshToken } = data;

                localStorage.setItem("access_token", access_token);
                localStorage.setItem("refresh_token", newRefreshToken);

                setAccessToken(access_token);
                setRefreshToken(newRefreshToken);

                return true;
            } catch (error) {
                // If it's a 401, clear everything. If it's a 500/network error, don't logout!
                const status = (error as any).response?.status;
                if (status === 401 || status === 403) {
                    localStorage.removeItem("access_token");
                    localStorage.removeItem("refresh_token");
                    setAccessToken(null);
                    setRefreshToken(null);
                    setUser(null);
                }
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
                isAuthenticated: (!!accessToken || !!localStorage.getItem('access_token')) && !!user,
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
