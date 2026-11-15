import React from "react";

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "bronze" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(({
  className = "",
  variant = "primary",
  size = "md",
  isLoading = false,
  children,
  disabled,
  ...props
}, ref) => {
  const variantStyles = {
    primary: "bg-[#2B454E] text-white hover:bg-[#3D5F6B] shadow-sm",
    secondary: "bg-white text-[#141B1F] border border-[#E2E8E6] hover:bg-[#F6F5F2] hover:border-[#CBD5D1]",
    bronze: "bg-[#9E7B4F] text-white hover:bg-[#B58D5D] shadow-sm",
    danger: "bg-white text-[#A8422B] border border-[#A8422B]/30 hover:bg-[#A8422B]/10",
    ghost: "bg-transparent text-[#141B1F] hover:bg-[#E2E8E6]/50 shadow-none",
  };

  const sizeStyles = {
    sm: "px-3 py-1.5 text-xs rounded-md",
    md: "px-4 py-2.5 text-sm rounded-lg",
    lg: "px-6 py-3 text-base rounded-xl",
  };

  return (
    <button
      ref={ref}
      disabled={disabled || isLoading}
      className={`inline-flex items-center justify-center font-medium transition-all duration-200 active:scale-[0.98] disabled:opacity-50 disabled:pointer-events-none ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {isLoading ? (
        <span className="flex items-center gap-2">
          <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          Loading...
        </span>
      ) : children}
    </button>
  );
});

Button.displayName = "Button";
