import React, { useEffect, useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { integrationsApi, PROVIDERS, IntegrationStatus } from "@/lib/integrations";
import { Mail, Loader2, Check, X, HardDrive, FileSpreadsheet, Github } from "lucide-react";
import { toast } from "react-toastify";

interface AppInfo {
    id: string;
    provider: string;
    name: string;
    icon: React.ReactNode;
    connected: boolean;
}

export function AppConnectionsPanel() {
    const [apps, setApps] = useState<AppInfo[]>([
        {
            id: "gmail",
            provider: PROVIDERS.GOOGLE_GMAIL,
            name: "Gmail",
            icon: <Mail className="h-5 w-5" />,
            connected: false,
        },
        {
            id: "drive",
            provider: PROVIDERS.GOOGLE_DRIVE,
            name: "Google Drive",
            icon: <HardDrive className="h-5 w-5" />,
            connected: false,
        },
        {
            id: "sheets",
            provider: PROVIDERS.GOOGLE_SHEETS,
            name: "Google Sheets",
            icon: <FileSpreadsheet className="h-5 w-5" />,
            connected: false,
        },
        {
            id: "github",
            provider: PROVIDERS.GITHUB,
            name: "GitHub",
            icon: <Github className="h-5 w-5" />,
            connected: false,
        },
    ]);
    const [isLoading, setIsLoading] = useState(true);
    const [processingProvider, setProcessingProvider] = useState<string | null>(null);
    const isFetchingStatus = useRef(false);

    const fetchIntegrationStatus = async () => {
        if (isFetchingStatus.current) return;

        try {
            isFetchingStatus.current = true;
            setIsLoading(true);
            const response = await integrationsApi.getStatus();

            setApps((prevApps) =>
                prevApps.map((app) => {
                    const integrationStatus: IntegrationStatus | undefined = response.status[app.provider];
                    return {
                        ...app,
                        connected: integrationStatus?.connected ?? false,
                    };
                })
            );
        } catch (error) {
            console.error("Failed to fetch integration status:", error);
            toast.error("Failed to load integration status");
        } finally {
            setIsLoading(false);
            isFetchingStatus.current = false;
        }
    };

    useEffect(() => {
        fetchIntegrationStatus();
    }, []);

    const handleConnect = async (provider: string) => {
        try {
            setProcessingProvider(provider);
            let response;

            if (provider === PROVIDERS.GOOGLE_GMAIL) {
                response = await integrationsApi.google.connect();
            } else if (provider === PROVIDERS.GOOGLE_DRIVE) {
                response = await integrationsApi.drive.connect();
            } else if (provider === PROVIDERS.GOOGLE_SHEETS) {
                response = await integrationsApi.sheets.connect();
            } else if (provider === PROVIDERS.GITHUB) {
                response = await integrationsApi.github.connect();
            } else {
                return;
            }

            if (response.auth_url) {
                localStorage.setItem("oauth_return_url", window.location.pathname);
                window.location.href = response.auth_url;
            }
        } catch (error) {
            console.error("Failed to connect:", error);
            toast.error("Failed to initiate connection");
            setProcessingProvider(null);
        }
    };

    const handleDisconnect = async (provider: string) => {
        try {
            setProcessingProvider(provider);
            let response;

            if (provider === PROVIDERS.GOOGLE_GMAIL) {
                response = await integrationsApi.google.disconnect();
            } else if (provider === PROVIDERS.GOOGLE_DRIVE) {
                response = await integrationsApi.drive.disconnect();
            } else if (provider === PROVIDERS.GOOGLE_SHEETS) {
                response = await integrationsApi.sheets.disconnect();
            } else if (provider === PROVIDERS.GITHUB) {
                response = await integrationsApi.github.disconnect();
            } else {
                return;
            }

            if (response.status === "disconnected") {
                await fetchIntegrationStatus();
                const providerName = provider.includes('_') ? provider.split('_')[1] : provider;
                toast.success(`${providerName.toUpperCase()} disconnected successfully`);
            }
        } catch (error) {
            console.error("Failed to disconnect:", error);
            toast.error("Failed to disconnect");
        } finally {
            setProcessingProvider(null);
        }
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center py-12">
                <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-xl font-semibold text-foreground">App Connections</h2>
                <p className="text-sm text-muted-foreground mt-1">
                    Connect your apps to enable integrations
                </p>
            </div>

            <div className="space-y-3">
                {apps.map((app) => {
                    const isProcessing = processingProvider === app.provider;

                    return (
                        <div
                            key={app.id}
                            className="flex items-center justify-between p-4 rounded-xl bg-card border border-border"
                        >
                            <div className="flex items-center gap-3">
                                <div className="flex items-center justify-center h-10 w-10 rounded-lg bg-muted">
                                    {app.icon}
                                </div>
                                <div>
                                    <p className="font-medium text-foreground">{app.name}</p>
                                    <div className="flex items-center gap-1.5 mt-0.5">
                                        {app.connected ? (
                                            <>
                                                <Check className="h-3 w-3 text-green-500" />
                                                <span className="text-xs text-green-500">Connected</span>
                                            </>
                                        ) : (
                                            <>
                                                <X className="h-3 w-3 text-muted-foreground" />
                                                <span className="text-xs text-muted-foreground">Not Connected</span>
                                            </>
                                        )}
                                    </div>
                                </div>
                            </div>

                            <Button
                                variant={app.connected ? "outline" : "default"}
                                size="sm"
                                onClick={() =>
                                    app.connected
                                        ? handleDisconnect(app.provider)
                                        : handleConnect(app.provider)
                                }
                                disabled={isProcessing}
                            >
                                {isProcessing ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                ) : app.connected ? (
                                    "Disconnect"
                                ) : (
                                    "Connect"
                                )}
                            </Button>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
