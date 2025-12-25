import { User, Link2 } from "lucide-react";
import { cn } from "@/lib/utils";

type SettingsTab = "account" | "app-connections";

interface SettingsSidebarProps {
    activeTab: SettingsTab;
    onTabChange: (tab: SettingsTab) => void;
}

const navItems = [
    { id: "account" as const, label: "Account", icon: User },
    { id: "app-connections" as const, label: "App Connections", icon: Link2 },
];

export function SettingsSidebar({ activeTab, onTabChange }: SettingsSidebarProps) {
    return (
        <nav className="w-56 border-r border-border p-4 space-y-1">
            {navItems.map((item) => (
                <button
                    key={item.id}
                    onClick={() => onTabChange(item.id)}
                    className={cn(
                        "w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors",
                        activeTab === item.id
                            ? "bg-primary/10 text-primary"
                            : "text-muted-foreground hover:bg-muted hover:text-foreground"
                    )}
                >
                    <item.icon className="h-5 w-5" />
                    {item.label}
                </button>
            ))}
        </nav>
    );
}
