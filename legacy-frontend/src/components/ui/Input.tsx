import React from "react";

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(({
  className = "",
  label,
  error,
  helperText,
  id,
  ...props
}, ref) => {
  const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, "-") : undefined);

  return (
    <div className="w-full">
      {label && (
        <label htmlFor={inputId} className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-[#5A6A72]">
          {label}
        </label>
      )}
      <input
        ref={ref}
        id={inputId}
        className={`w-full rounded-lg border bg-white px-4 py-2.5 text-sm text-[#141B1F] placeholder:text-[#5A6A72]/50 transition-all focus:outline-none focus:ring-1 ${
          error
            ? "border-[#A8422B] focus:border-[#A8422B] focus:ring-[#A8422B]"
            : "border-[#E2E8E6] focus:border-[#2B454E] focus:ring-[#2B454E]"
        } ${className}`}
        {...props}
      />
      {error && <p className="mt-1 text-xs text-[#A8422B]">{error}</p>}
      {helperText && !error && <p className="mt-1 text-xs text-[#5A6A72]">{helperText}</p>}
    </div>
  );
});

Input.displayName = "Input";
