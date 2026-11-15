import React from "react";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "pending" | "approved" | "rejected" | "neutral" | "success" | "warning";
}

export function Badge({ children, variant = "neutral" }: BadgeProps) {
  const variants = {
    pending: "bg-amber-50 text-amber-700 border-amber-200",
    approved: "bg-emerald-50 text-emerald-700 border-emerald-200",
    rejected: "bg-red-50 text-red-700 border-red-200",
    neutral: "bg-[#F6F5F2] text-[#5A6A72] border-[#E2E8E6]",
    success: "bg-emerald-50 text-emerald-700 border-emerald-200",
    warning: "bg-amber-50 text-amber-700 border-amber-200",
  };

  return (
    <span className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium uppercase tracking-wider ${variants[variant]}`}>
      {children}
    </span>
  );
}
