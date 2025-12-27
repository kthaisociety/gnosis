import { authClient } from "@/lib/auth";

const ADMIN_EMAILS = [
  "giulio@kthais.com",
  "niklavs@kthais.com",
  "michael@kthais.com",
  "georg@kthais.com",
  "sebastian@kthais.com",
  "elindstenz@outlook.com"
];

export function useAdmin() {
  const session = authClient.useSession();
  
  const isAdmin = 
    session.data?.user?.email && 
    ADMIN_EMAILS.includes(session.data.user.email);

  return {
    isAdmin: !!isAdmin,
    isLoading: session.isPending,
    user: session.data?.user
  };
}
