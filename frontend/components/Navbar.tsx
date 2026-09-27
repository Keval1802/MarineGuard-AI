"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Waves, LayoutDashboard, AlertTriangle, Image as ImageIcon, Activity, UserCheck, PlusCircle } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export default function Navbar() {
  const pathname = usePathname();
  const [isHealthy, setIsHealthy] = useState<boolean>(true);

  useEffect(() => {
    api.getHealth().then((h) => setIsHealthy(h.status === "healthy"));
  }, []);

  const navLinks = [
    { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    { href: "/incidents", label: "Incidents", icon: AlertTriangle },
    { href: "/evidence", label: "Evidence Gallery", icon: ImageIcon },
    { href: "/citizen-report", label: "Report Pollution", icon: PlusCircle },
  ];

  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <Link href="/dashboard" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-marine-500/20 border border-marine-500/40 flex items-center justify-center text-marine-500">
              <Waves className="w-6 h-6" />
            </div>
            <div>
              <span className="font-bold text-xl text-slate-100 tracking-tight">MarineGuard <span className="text-marine-500">AI</span></span>
              <span className="block text-xs text-slate-400">Indian Coastal Intelligence</span>
            </div>
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href || pathname?.startsWith(link.href + "/");
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-marine-500/20 text-marine-500 border border-marine-500/30"
                      : "text-slate-300 hover:bg-slate-800 hover:text-white"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {link.label}
                </Link>
              );
            })}
          </nav>

          {/* System Health Status Indicator */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-xs px-2.5 py-1.5 rounded-full bg-slate-800/80 border border-slate-700 text-slate-300">
              <span className={`w-2 h-2 rounded-full ${isHealthy ? "bg-emerald-500 animate-pulse" : "bg-amber-500"}`} />
              {isHealthy ? "Backend Online" : "Local Demo Mode"}
            </div>

            <Link
              href="/login"
              className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              title="Authentication Session"
            >
              <UserCheck className="w-5 h-5" />
            </Link>
          </div>

        </div>
      </div>
    </header>
  );
}
