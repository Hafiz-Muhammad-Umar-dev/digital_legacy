import React from "react";

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-[#E2E8E6] bg-white/50 p-12 text-center">
      {icon && <div className="mb-4 text-[#5A6A72]">{icon}</div>}
      <h3 className="font-serif text-xl text-[#141B1F]">{title}</h3>
      <p className="mt-1.5 max-w-sm text-sm text-[#5A6A72]">{description}</p>
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}
