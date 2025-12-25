import { integrationsApi } from "./integrations";

// OAuth Provider configuration
export interface OAuthProvider {
    id: string;
    name: string;
    exchange: (code: string) => Promise<{ provider: string; status: string }>;
}

// Registry of all OAuth providers
// To add a new provider, just add an entry here
export const oauthProviders: Record<string, OAuthProvider> = {
    google_gmail: {
        id: "google_gmail",
        name: "Gmail",
        exchange: (code) => integrationsApi.google.exchange(code),
    },
    // Future providers - just add entries here:
    // twitter: {
    //   id: "twitter",
    //   name: "Twitter",
    //   exchange: (code) => integrationsApi.twitter.exchange(code),
    // },
    // google_drive: {
    //   id: "google_drive",
    //   name: "Google Drive",
    //   exchange: (code) => integrationsApi.googleDrive.exchange(code),
    // },
};

// Helper to get provider by ID
export function getOAuthProvider(providerId: string): OAuthProvider | undefined {
    return oauthProviders[providerId];
}
