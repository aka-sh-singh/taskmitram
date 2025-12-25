import { useState } from "react";
import {
    Dialog,
    DialogContent,
    DialogTitle,
} from "@/components/ui/dialog";
import { SettingsSidebar } from "./SettingsSidebar";
import { AccountPanel } from "./AccountPanel";
import { AppConnectionsPanel } from "./AppConnectionsPanel";

type SettingsTab = "account" | "app-connections";

interface SettingsModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}

export function SettingsModal({ open, onOpenChange }: SettingsModalProps) {
    const [activeTab, setActiveTab] = useState<SettingsTab>("account");

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent className="max-w-4xl h-[80vh] p-0 gap-0 overflow-hidden">
                <DialogTitle className="sr-only">Settings</DialogTitle>

                <div className="flex h-full">
                    {/* Left Sidebar Navigation */}
                    <SettingsSidebar activeTab={activeTab} onTabChange={setActiveTab} />

                    {/* Right Content Panel */}
                    <div className="flex-1 p-6 overflow-y-auto">
                        {activeTab === "account" && <AccountPanel />}
                        {activeTab === "app-connections" && <AppConnectionsPanel />}
                    </div>
                </div>
            </DialogContent>
        </Dialog>
    );
}
