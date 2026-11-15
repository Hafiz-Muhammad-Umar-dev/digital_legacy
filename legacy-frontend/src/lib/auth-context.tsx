"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { auth, tokens } from "./api";
import type { RegisterPayload, User } from "./types";

interface AuthState {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (p: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
}

const Ctx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!tokens.access) { setLoading(false); return; }
    auth.me().then(setUser).catch(() => tokens.clear()).finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    tokens.set(await auth.login(email, password));
    setUser(await auth.me());
  }, []);

  const register = useCallback(async (p: RegisterPayload) => {
    await auth.register(p);
    await login(p.email, p.password);
  }, [login]);

  const logout = useCallback(async () => {
    try { await auth.logout(); } catch { /* token may already be invalid */ }
    tokens.clear();
    setUser(null);
  }, []);

  return <Ctx.Provider value={{ user, loading, login, register, logout }}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const c = useContext(Ctx);
  if (!c) throw new Error("useAuth must be used inside <AuthProvider>");
  return c;
}
