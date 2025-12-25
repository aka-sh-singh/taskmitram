import { useEffect, useState } from "react";
import { oauthProviders } from "@/lib/oauth-providers";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { Loader2 } from "lucide-react";

/**
 * OAuthHandler - A modular component that handles OAuth callbacks
 * 
 * This component should be mounted at the app root level (App.tsx) to ensure
 * OAuth callbacks are processed regardless of which page the user lands on.
 * 
 * Expected URL format after OAuth redirect:
 * /?code=AUTH_CODE&state=PROVIDER_ID
 * 
 * The `state` parameter identifies which provider initiated the OAuth flow.
 * This allows the handler to route the code to the correct exchange function.
 */
export function OAuthHandler() {
    const [isProcessing, setIsProcessing] = useState(false);
    const [providerName, setProviderName] = useState<string | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get("code");
        const state = urlParams.get("state"); // Provider ID passed via OAuth state

        // Only process if we have both code and state (provider identifier)
        if (code && state && !isProcessing) {
            const provider = oauthProviders[state];

            if (!provider) {
                console.warn(`Unknown OAuth provider: ${state}`);
                // Clean URL even for unknown provider
                window.history.replaceState({}, document.title, window.location.pathname);
                return;
            }

            setIsProcessing(true);
            setProviderName(provider.name);

            const exchangeCode = async () => {
                try {
                    await provider.exchange(code);
                    toast.success(`${provider.name} connected successfully`);

                    // Redirect back to where we started or to chat
                    const returnUrl = localStorage.getItem("oauth_return_url");
                    if (returnUrl) {
                        localStorage.removeItem("oauth_return_url");
                        navigate(returnUrl);
                    } else {
                        navigate("/chat/new");
                    }
                } catch (error) {
                    console.error(`Failed to exchange OAuth code for ${provider.name}:`, error);
                    toast.error(`Failed to connect ${provider.name}`);
                } finally {
                    // Always clean up URL
                    window.history.replaceState({}, document.title, window.location.pathname);
                    setIsProcessing(false);
                    setProviderName(null);
                }
            };

            exchangeCode();
        }
    }, [navigate]);

    // Show loading overlay while processing OAuth callback
    if (isProcessing) {
        return (
            <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
                <div className="flex flex-col items-center gap-3 p-6 rounded-xl bg-card border border-border shadow-lg">
                    <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    <p className="text-sm text-muted-foreground">
                        Connecting {providerName}...
                    </p>
                </div>
            </div>
        );
    }

    return null;
}
