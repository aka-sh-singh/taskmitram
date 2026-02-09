import { useEffect, useState, useRef } from "react";
import { oauthProviders } from "@/lib/oauth-providers";
import { useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import { Loader2 } from "lucide-react";

/**
 * OAuthHandler - A modular component that handles OAuth callbacks
 */
export function OAuthHandler() {
    const [isProcessing, setIsProcessing] = useState(false);
    const [providerName, setProviderName] = useState<string | null>(null);
    const navigate = useNavigate();
    const isExchangeRef = useRef(false);

    useEffect(() => {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get("code");
        const state = urlParams.get("state");
        const error = urlParams.get("error");

        if (state && (code || error) && !isExchangeRef.current) {
            const provider = oauthProviders[state];

            if (!provider) {
                console.warn(`Unknown OAuth provider: ${state}`);
                window.history.replaceState({}, document.title, window.location.pathname);
                return;
            }

            isExchangeRef.current = true;

            // Handle Error/Cancel case
            if (error) {
                console.info(`OAuth connection for ${provider.name} was cancelled or failed: ${error}`);

                if (error === "access_denied") {
                    toast.info(`Connection to ${provider.name} was cancelled`);
                } else {
                    toast.error(`Failed to connect ${provider.name}: ${error}`);
                }

                // Immediately clean URL
                window.history.replaceState({}, document.title, window.location.pathname);

                const returnUrl = localStorage.getItem("oauth_return_url");
                if (returnUrl) {
                    localStorage.removeItem("oauth_return_url");
                    navigate(returnUrl, { replace: true });
                } else {
                    navigate("/chat/new", { replace: true });
                }
                return;
            }

            // Handle Success case
            if (code) {
                setIsProcessing(true);
                setProviderName(provider.name);

                // Immediately clean URL so a fast refresh or other effect doesn't see code again
                window.history.replaceState({}, document.title, window.location.pathname);

                const exchangeCode = async () => {
                    try {
                        await provider.exchange(code);
                        toast.success(`${provider.name} connected successfully`);

                        const returnUrl = localStorage.getItem("oauth_return_url");
                        if (returnUrl) {
                            localStorage.removeItem("oauth_return_url");
                            navigate(returnUrl, { replace: true });
                        } else {
                            navigate("/chat/new", { replace: true });
                        }
                    } catch (error: any) {
                        console.error(`Failed to exchange OAuth code for ${provider.name}:`, error);
                        toast.error(`Failed to connect ${provider.name}`);
                    } finally {
                        setIsProcessing(false);
                        setProviderName(null);
                    }
                };

                exchangeCode();
            }
        }
    }, [navigate]);

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
