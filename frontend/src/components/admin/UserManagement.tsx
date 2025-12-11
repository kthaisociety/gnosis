import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  UserPlus, 
  Trash2, 
  Copy, 
  Check, 
  Mail,
  Clock,
  UserCheck,
  X
} from "lucide-react";
import { userStore } from "@/stores/userStore";
import { MockUser } from "@/types/user";
import { toast } from "sonner";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

const UserManagement = () => {
  const [users, setUsers] = useState<MockUser[]>([]);
  const [inviteEmail, setInviteEmail] = useState("");
  const [isInviting, setIsInviting] = useState(false);
  const [copiedToken, setCopiedToken] = useState<string | null>(null);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [userToDelete, setUserToDelete] = useState<MockUser | null>(null);

  useEffect(() => {
    setUsers(userStore.getUsers());
  }, []);

  const refreshUsers = () => {
    setUsers(userStore.getUsers());
  };

  const handleInviteUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsInviting(true);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 800));

    if (userStore.getUserByEmail(inviteEmail)) {
      toast.error("User with this email already exists");
      setIsInviting(false);
      return;
    }

    const invite = userStore.createInvite(inviteEmail);
    refreshUsers();
    
    toast.success("Invite created successfully", {
      description: `Invite link generated for ${inviteEmail}`,
    });
    
    setInviteEmail("");
    setShowInviteForm(false);
    setIsInviting(false);
  };

  const confirmDeleteUser = () => {
    if (!userToDelete) return;
    
    userStore.deleteUser(userToDelete.id);
    refreshUsers();
    toast.success("User removed", {
      description: `${userToDelete.email} has been removed`,
    });
    setUserToDelete(null);
  };

  const handleDeleteUser = (user: MockUser) => {
    if (user.role === "admin") {
      toast.error("Cannot delete admin users");
      return;
    }
    setUserToDelete(user);
  };

  const copyInviteLink = (token: string) => {
    const inviteUrl = `${window.location.origin}/invite/${token}`;
    navigator.clipboard.writeText(inviteUrl);
    setCopiedToken(token);
    toast.success("Invite link copied to clipboard");
    setTimeout(() => setCopiedToken(null), 2000);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return (
          <span className="flex items-center gap-1.5 px-2 py-1 rounded-full text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <UserCheck className="w-3 h-3" />
            Active
          </span>
        );
      case "pending":
        return (
          <span className="flex items-center gap-1.5 px-2 py-1 rounded-full text-xs bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">
            <Clock className="w-3 h-3" />
            Pending
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1.5 px-2 py-1 rounded-full text-xs bg-muted text-muted-foreground border border-border">
            Inactive
          </span>
        );
    }
  };

  return (
    <div className="glass-card rounded-xl p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-medium">User Management</h3>
          <p className="text-sm text-muted-foreground">
            {users.length} total users
          </p>
        </div>
        <Button
          onClick={() => setShowInviteForm(!showInviteForm)}
          size="sm"
          className="gap-2"
        >
          {showInviteForm ? (
            <>
              <X className="w-4 h-4" />
              Cancel
            </>
          ) : (
            <>
              <UserPlus className="w-4 h-4" />
              Invite User
            </>
          )}
        </Button>
      </div>

      {/* Invite Form */}
      {showInviteForm && (
        <form onSubmit={handleInviteUser} className="mb-6 p-4 rounded-lg bg-muted/30 border border-border">
          <label className="text-sm font-medium mb-2 block">
            Send Invite Link
          </label>
          <div className="flex gap-2">
            <Input
              type="email"
              placeholder="user@example.com"
              value={inviteEmail}
              onChange={(e) => setInviteEmail(e.target.value)}
              required
              className="flex-1"
            />
            <Button type="submit" disabled={isInviting} className="gap-2">
              {isInviting ? (
                <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
              ) : (
                <>
                  <Mail className="w-4 h-4" />
                  Send Invite
                </>
              )}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            User will receive a link to set their password and activate their account.
          </p>
        </form>
      )}

      {/* Users List */}
      <div className="space-y-3">
        {users.map((user) => (
          <div
            key={user.id}
            className="flex items-center justify-between p-4 rounded-lg bg-muted/20 border border-border hover:bg-muted/30 transition-colors"
          >
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center">
                <span className="text-sm font-medium text-primary">
                  {user.name.charAt(0).toUpperCase()}
                </span>
              </div>
              <div>
                <p className="font-medium text-sm">{user.name}</p>
                <p className="text-xs text-muted-foreground">{user.email}</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {getStatusBadge(user.status)}
              
              {user.status === "pending" && user.inviteToken && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyInviteLink(user.inviteToken!)}
                  className="gap-1.5 text-xs"
                >
                  {copiedToken === user.inviteToken ? (
                    <>
                      <Check className="w-3 h-3" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="w-3 h-3" />
                      Copy Link
                    </>
                  )}
                </Button>
              )}

              {user.role !== "admin" && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleDeleteUser(user)}
                  className="text-destructive hover:text-destructive hover:bg-destructive/10"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              )}

              {user.role === "admin" && (
                <span className="text-xs text-muted-foreground px-2 py-1 rounded bg-muted">
                  Admin
                </span>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={!!userToDelete} onOpenChange={(open) => !open && setUserToDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete User</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <span className="font-medium text-foreground">{userToDelete?.email}</span>? 
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction 
              onClick={confirmDeleteUser}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default UserManagement;
