import axios from 'axios';
import { toast } from 'react-toastify';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const axiosInstance = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];
let onTokenRefreshedCallback: ((accessToken: string, refreshToken: string) => void) | null = null;

export const setOnTokenRefreshedCallback = (cb: (accessToken: string, refreshToken: string) => void) => {
    onTokenRefreshedCallback = cb;
};

function subscribeTokenRefresh(cb: (token: string) => void) {
    refreshSubscribers.push(cb);
}

function onRefreshed(token: string) {
    refreshSubscribers.forEach((cb) => cb(token));
    refreshSubscribers = [];
}

function addAuthorizationHeader(config: any, token: string) {
    config.headers.Authorization = `Bearer ${token}`;
    return config;
}

// Request interceptor to attach access token
axiosInstance.interceptors.request.use(
    (config) => {
        const accessToken = localStorage.getItem('access_token');
        if (accessToken) {
            config.headers.Authorization = `Bearer ${accessToken}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor to handle token refresh
axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            originalRequest._retry = true;

            if (isRefreshing) {
                return new Promise((resolve) => {
                    subscribeTokenRefresh((newToken: string) => {
                        resolve(
                            axiosInstance(addAuthorizationHeader(originalRequest, newToken))
                        );
                    });
                });
            }

            isRefreshing = true;

            try {
                const refreshToken = localStorage.getItem('refresh_token');
                if (!refreshToken) {
                    throw new Error('No refresh token');
                }

                const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
                    refresh_token: refreshToken,
                });

                const { access_token, refresh_token: newRefreshToken } = response.data;

                localStorage.setItem('access_token', access_token);
                localStorage.setItem('refresh_token', newRefreshToken);

                if (onTokenRefreshedCallback) {
                    onTokenRefreshedCallback(access_token, newRefreshToken);
                }

                onRefreshed(access_token);
                isRefreshing = false;

                return axiosInstance(
                    addAuthorizationHeader(originalRequest, access_token)
                );
            } catch (refreshError) {
                isRefreshing = false;
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                window.location.href = '/login';
                toast.error('Session expired. Please login again.');
                return Promise.reject(refreshError);
            }
        }

        const errorMessage = error.response?.data?.detail || error.message || 'An error occurred';
        toast.error(errorMessage);
        return Promise.reject(error);
    }
);
