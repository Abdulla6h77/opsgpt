"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, AlertTriangle, Upload, Activity } from "lucide-react";
import { cn } from "@/lib/utils";

const menu = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/incidents", label: "Incidents", icon: AlertTriangle },
  { href: "/upload", label: "Upload Logs", icon: Upload }
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden w-64 shrink-0 border-r border-border bg-card/80 backdrop-blur md:block">
      <div className="flex h-16 items-center gap-2 border-b border-border px-5">
        <Activity className="h-5 w-5 text-primary" />
        <span className="text-lg font-bold tracking-tight">OpsGPT</span>
      </div>
      <nav className="p-3">
        <ul className="space-y-1">
          {menu.map((item) => {
            const Icon = item.icon;
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                    active ? "bg-primary/20 text-primary" : "text-muted-foreground hover:bg-accent hover:text-foreground"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
}

