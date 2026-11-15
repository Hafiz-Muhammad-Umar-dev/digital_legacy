"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/lib/auth-context";

export default function AuthForm({ mode }: { mode: "login" | "register" }) {
  const { login, register } = useAuth();
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const isLogin = mode === "login";

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (isLogin) await login(email, password);
      else await register({ email, password, full_name: fullName || undefined });
      router.replace("/personas");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-md flex-col justify-center px-6">
      <h1 className="text-4xl leading-tight">
        {isLogin ? "Welcome back" : "Start preserving a story"}
      </h1>
      <p className="mt-2 text-ink/70">
        {isLogin ? "Sign in to continue with your personas." : "Create an account to add your first persona."}
      </p>

      <form onSubmit={onSubmit} className="mt-8 space-y-4">
        {!isLogin && (
          <div>
            <label className="label" htmlFor="name">Full name</label>
            <input id="name" className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </div>
        )}
        <div>
          <label className="label" htmlFor="email">Email</label>
          <input id="email" type="email" required className="input" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div>
          <label className="label" htmlFor="password">Password</label>
          <input id="password" type="password" required minLength={8} className="input" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        {error && <p className="error" role="alert">{error}</p>}
        <button className="btn w-full" disabled={busy}>
          {busy ? "Please wait…" : isLogin ? "Sign in" : "Create account"}
        </button>
      </form>

      <p className="mt-6 text-sm text-ink/70">
        {isLogin ? "New here? " : "Already have an account? "}
        <Link className="text-dusk underline" href={isLogin ? "/register" : "/login"}>
          {isLogin ? "Create an account" : "Sign in"}
        </Link>
      </p>
    </main>
  );
}
