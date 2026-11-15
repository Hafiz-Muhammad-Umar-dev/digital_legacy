"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { ToastProvider } from "@/components/ui/Toast";
import { ErrorBoundary } from "@/components/ui/ErrorBoundary";
import { Button } from "@/components/ui/Button";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-[#F6F5F2]">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-[#2B454E] border-t-transparent" />
          <p className="mt-4 text-sm text-[#5A6A72]">Loading your workspace...</p>
        </div>
      </div>
    );
  }

  const navItems = [
    {
      name: "Personas",
      href: "/personas",
      icon: (
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>
      ),
    },
  ];

  return (
    <ToastProvider>
      <ErrorBoundary>
        <div className="min-h-screen flex bg-[#F6F5F2]">
          {/* Desktop Sidebar */}
          <aside className="hidden md:flex md:w-64 md:flex-col border-r border-[#E2E8E6] bg-white">
            <div className="flex h-16 items-center px-6 border-b border-[#E2E8E6]">
              <Link href="/personas" className="font-serif text-xl tracking-tight text-[#141B1F] flex items-center gap-2">
                <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#2B454E] text-white font-sans text-sm font-bold">DL</span>
                Digital Legacy
              </Link>
            </div>

            <div className="flex flex-1 flex-col justify-between px-4 py-6">
              <nav className="space-y-1">
                {navItems.map((item) => {
                  const isActive = pathname.startsWith(item.href);
                  return (
                    <Link
                      key={item.name}
                      href={item.href}
                      className={`flex items-center gap-3 rounded-lg px-3.5 py-2.5 text-sm font-medium transition-colors ${
                        isActive
                          ? "bg-[#2B454E] text-white"
                          : "text-[#5A6A72] hover:bg-[#F6F5F2] hover:text-[#141B1F]"
                      }`}
                    >
                      {item.icon}
                      {item.name}
                    </Link>
                  );
                })}
              </nav>

              <div className="border-t border-[#E2E8E6] pt-4">
                <div className="flex items-center gap-3 px-3 py-2">
                  <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#2B454E]/10 font-serif text-sm font-bold text-[#2B454E]">
                    {(user.full_name || user.email).charAt(0).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-[#141B1F] truncate">{user.full_name || "Account"}</p>
                    <p className="text-xs text-[#5A6A72] truncate">{user.email}</p>
                  </div>
                </div>
                <div className="mt-3">
                  <Button
                    variant="secondary"
                    size="sm"
                    className="w-full justify-center"
                    onClick={async () => {
                      await logout();
                      router.replace("/login");
                    }}
                  >
                    Sign out
                  </Button>
                </div>
              </div>
            </div>
          </aside>

          {/* Main Content Area */}
          <div className="flex flex-1 flex-col min-w-0">
            {/* Mobile Header */}
            <header className="flex h-16 items-center justify-between border-b border-[#E2E8E6] bg-white px-6 md:hidden">
              <Link href="/personas" className="font-serif text-xl tracking-tight text-[#141B1F]">
                Digital Legacy
              </Link>
              <button
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                className="rounded-lg p-2 text-[#5A6A72] hover:bg-[#F6F5F2] hover:text-[#141B1F]"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  {mobileMenuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </header>

            {/* Mobile Menu Dropdown */}
            {mobileMenuOpen && (
              <div className="border-b border-[#E2E8E6] bg-white px-6 py-4 md:hidden shadow-lg">
                <nav className="space-y-2">
                  <Link
                    href="/personas"
                    onClick={() => setMobileMenuOpen(false)}
                    className="block rounded-lg px-3 py-2 text-base font-medium text-[#2B454E] bg-[#F6F5F2]"
                  >
                    Personas
                  </Link>
                </nav>
                <div className="mt-6 border-t border-[#E2E8E6] pt-4">
                  <p className="text-sm font-medium text-[#141B1F]">{user.full_name || user.email}</p>
                  <Button
                    variant="secondary"
                    size="sm"
                    className="mt-3 w-full justify-center"
                    onClick={async () => {
                      await logout();
                      router.replace("/login");
                    }}
                  >
                    Sign out
                  </Button>
                </div>
              </div>
            )}

            <main className="flex-1 p-6 md:p-10 max-w-7xl mx-auto w-full">{children}</main>
          </div>
        </div>
      </ErrorBoundary>
    </ToastProvider>
  );
}
