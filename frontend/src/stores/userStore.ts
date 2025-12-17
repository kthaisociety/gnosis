import { MockUser, InviteLink } from "@/types/user";

// Mock data store (simulates database)
let mockUsers: MockUser[] = [
  {
    id: "1",
    email: "admin@ocrbench.com",
    name: "Admin User",
    role: "admin",
    status: "active",
    createdAt: new Date("2024-01-01"),
  },
  {
    id: "2",
    email: "john@example.com",
    name: "John Doe",
    role: "user",
    status: "active",
    createdAt: new Date("2024-02-15"),
  },
  {
    id: "3",
    email: "jane@example.com",
    name: "Jane Smith",
    role: "user",
    status: "pending",
    createdAt: new Date("2024-03-01"),
    inviteToken: "invite-abc123",
  },
];

let inviteLinks: InviteLink[] = [
  {
    token: "invite-abc123",
    email: "jane@example.com",
    createdAt: new Date("2024-03-01"),
    expiresAt: new Date("2024-03-08"),
  },
];

export const userStore = {
  getUsers: (): MockUser[] => [...mockUsers],

  getUserById: (id: string): MockUser | undefined =>
    mockUsers.find(u => u.id === id),

  getUserByEmail: (email: string): MockUser | undefined =>
    mockUsers.find(u => u.email === email),

  getUserByInviteToken: (token: string): MockUser | undefined =>
    mockUsers.find(u => u.inviteToken === token),

  addUser: (user: Omit<MockUser, "id" | "createdAt">): MockUser => {
    const newUser: MockUser = {
      ...user,
      id: crypto.randomUUID(),
      createdAt: new Date(),
    };
    mockUsers = [...mockUsers, newUser];
    return newUser;
  },
  updateUser: (id: string, updates: Partial<MockUser>): MockUser | undefined => {
    const index = mockUsers.findIndex(u => u.id === id);
    if (index === -1) return undefined;
    mockUsers[index] = { ...mockUsers[index], ...updates };
    return mockUsers[index];
  },
  deleteUser: (id: string): boolean => {
    const initialLength = mockUsers.length;
    mockUsers = mockUsers.filter(u => u.id !== id);
    return mockUsers.length < initialLength;
  },
  createInvite: (email: string): InviteLink => {
    const token = `invite-${crypto.randomUUID().slice(0, 8)}`;
    const invite: InviteLink = {
      token,
      email,
      createdAt: new Date(),
      expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000), // 7 days
    };
    inviteLinks = [...inviteLinks, invite];
    // Create pending user
    userStore.addUser({
      email,
      name: email.split("@")[0],
      role: "user",
      status: "pending",
      inviteToken: token,
    });

    return invite;
  },

  getInviteByToken: (token: string): InviteLink | undefined =>
    inviteLinks.find(i => i.token === token),

  activateUser: (token: string, name: string): MockUser | undefined => {
    const user = mockUsers.find(u => u.inviteToken === token);
    if (!user) return undefined;

    user.status = "active";
    user.name = name;
    delete user.inviteToken;

    // Remove used invite
    inviteLinks = inviteLinks.filter(i => i.token !== token);

    return user;
  },
};
