"use client";

import { Bell, KeyRound } from "lucide-react";

export function Navbar() {
  return (
    <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-border bg-background/90 px-4 backdrop-blur md:px-6">
      <div>
        <h1 className="text-lg font-semibold">AI DevOps Monitoring</h1>
        <p className="text-xs text-muted-foreground">Observability and incident intelligence</p>
      </div>
      <div className="flex items-center gap-4 text-muted-foreground">
        <div className="hidden items-center gap-2 rounded-md border border-border px-2 py-1 text-xs md:flex">
          <KeyRound className="h-3.5 w-3.5" />
          API key loaded
        </div>
        <Bell className="h-4 w-4" />
      </div>
    </header>
  );
}

