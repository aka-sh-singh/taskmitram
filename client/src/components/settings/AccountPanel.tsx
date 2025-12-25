import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useAuth } from "@/contexts/AuthContext";
import { LogOut, User, Mail, Trash2 } from "lucide-react";
import { useChat } from "@/contexts/ChatContext";

export function AccountPanel() {
    const { user, logout } = useAuth();
    const { deleteAllChats } = useChat();

    const handleLogout = () => {
        logout();
    };

    const handleDeleteAllChats = async () => {
        if (confirm("Are you sure you want to delete all chats? This action cannot be undone.")) {
            await deleteAllChats();
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-xl font-semibold text-foreground">Account</h2>
                <p className="text-sm text-muted-foreground mt-1">
                    Your account information
                </p>
            </div>

            {/* User Information (Read-only) */}
            <div className="p-4 rounded-xl bg-card border border-border space-y-4">
                <h3 className="font-semibold text-foreground">Profile Information</h3>

                <div className="space-y-3">
                    <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                        <User className="h-4 w-4 text-muted-foreground" />
                        <div>
                            <p className="text-xs text-muted-foreground">Username</p>
                            <p className="text-sm font-medium text-foreground">
                                {user?.username || "Guest"}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                        <Mail className="h-4 w-4 text-muted-foreground" />
                        <div>
                            <p className="text-xs text-muted-foreground">Email</p>
                            <p className="text-sm font-medium text-foreground">
                                {user?.email || "Not available"}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Data Management Section */}
            <div className="p-4 rounded-xl bg-card border border-border">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="font-semibold text-foreground">Data Management</h3>
                        <p className="text-sm text-muted-foreground">
                            Delete all your conversation history
                        </p>
                    </div>
                    <Button
                        variant="destructive"
                        size="sm"
                        onClick={handleDeleteAllChats}
                        className="gap-2"
                    >
                        <Trash2 className="h-4 w-4" />
                        Delete All Chats
                    </Button>
                </div>
            </div>

            <Separator />

            {/* Logout Section */}
            <div className="p-4 rounded-xl bg-card border border-border">
                <div className="flex items-center justify-between">
                    <div>
                        <h3 className="font-semibold text-foreground">Sign Out</h3>
                        <p className="text-sm text-muted-foreground">
                            Sign out of your account
                        </p>
                    </div>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleLogout}
                        className="gap-2"
                    >
                        <LogOut className="h-4 w-4" />
                        Logout
                    </Button>
                </div>
            </div>
        </div>
    );
}
