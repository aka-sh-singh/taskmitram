import { axiosInstance } from "./axios";

// Types matching backend schemas
export interface IntegrationStatus {
    provider: string;
    connected: boolean;
}

export interface IntegrationStatusResponse {
    status: Record<string, IntegrationStatus>;
}

export interface ConnectURLResponse {
    auth_url: string;
}

export interface DisconnectResponse {
    provider: string;
    status: string;
}

// Provider constants (must match backend)
export const PROVIDERS = {
    GOOGLE_GMAIL: "google_gmail",
} as const;

// API calls
export const integrationsApi = {
    // Get status of all integrations
    getStatus: async (): Promise<IntegrationStatusResponse> => {
        const response = await axiosInstance.get<IntegrationStatusResponse>("/integrations/status");
        return response.data;
    },

    // Google integration
    google: {
        // Get OAuth URL to connect
        connect: async (): Promise<ConnectURLResponse> => {
            const response = await axiosInstance.get<ConnectURLResponse>("/integrations/google/connect");
            return response.data;
        },

        // Exchange OAuth code for tokens
        exchange: async (code: string): Promise<{ provider: string; status: string }> => {
            const response = await axiosInstance.post<{ provider: string; status: string }>(
                "/integrations/google/exchange",
                { code }
            );
            return response.data;
        },

        // Disconnect Google integration
        disconnect: async (): Promise<DisconnectResponse> => {
            const response = await axiosInstance.delete<DisconnectResponse>("/integrations/google/disconnect");
            return response.data;
        },
    },
};
