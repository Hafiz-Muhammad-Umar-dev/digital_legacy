"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { Button } from "./Button";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-[400px] flex-col items-center justify-center p-8 text-center">
          <div className="max-w-md rounded-2xl border border-red-200 bg-red-50 p-8">
            <h2 className="font-serif text-2xl text-red-900">Something went wrong</h2>
            <p className="mt-2 text-sm text-red-700">
              {this.state.error?.message || "An unexpected error occurred in this section."}
            </p>
            <div className="mt-6">
              <Button variant="primary" onClick={() => window.location.reload()}>
                Reload application
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
