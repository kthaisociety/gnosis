export type UserRole = 'admin' | 'user';
export type UserStatus = 'active' | 'pending' | 'inactive';

export interface MockUser {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  status: UserStatus;
  createdAt: Date;
  inviteToken?: string;
}

export interface InviteLink {
  token: string;
  email: string;
  createdAt: Date;
  expiresAt: Date;
}
