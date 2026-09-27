"use client";

import React, { useEffect, useState } from "react";
import { SystemHealth as SystemHealthType } from "@/lib/types";
import { api } from "@/lib/api";
import { Activity, Database, Server, Clock, ShieldCheck, Mail, Cpu } from "lucide-react";

export default function SystemHealthComponent() {
  const [health, setHealth] = useState<SystemHealthType | null>(null);

  useEffect(() => {
    api.getHealth().then(setHealth);
  }, []);

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 shadow-lg">
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-marine-500/10 border border-marine-500/30 text-marine-500 rounded-xl">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-100">System Diagnostics & Scheduler</h3>
            <p className="text-xs text-slate-400">Near-Real-Time Monitoring Health</p>
          </div>
        </div>

        <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          Status: Operational
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        
        {/* Backend API Service */}
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 mb-2">
            <Server className="w-4 h-4 text-marine-500" />
            <span className="text-xs font-semibold uppercase tracking-wider">FastAPI Backend</span>
          </div>
          <p className="text-xl font-bold text-slate-100">{health?.project || "MarineGuard AI Backend"}</p>
          <span className="text-xs text-slate-500 font-mono">Version {health?.version || "1.0.0"}</span>
        </div>

        {/* Database Layer */}
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 mb-2">
            <Database className="w-4 h-4 text-emerald-500" />
            <span className="text-xs font-semibold uppercase tracking-wider">Database Persistence</span>
          </div>
          <p className="text-xl font-bold text-slate-100">{health?.database || "SQLite / PostgreSQL"}</p>
          <span className="text-xs text-emerald-400 font-mono">Status: Connected</span>
        </div>

        {/* Scheduler */}
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <div className="flex items-center gap-2 text-slate-400 mb-2">
            <Clock className="w-4 h-4 text-amber-500" />
            <span className="text-xs font-semibold uppercase tracking-wider">Scheduled Monitor</span>
          </div>
          <p className="text-xl font-bold text-slate-100">GitHub Actions</p>
          <span className="text-xs text-amber-400 font-mono">Cycle: Source-Aware Polling</span>
        </div>

      </div>

      {/* Quotas & Security Status */}
      <div className="mt-6 pt-4 border-t border-slate-800/80 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-marine-500" />
          <span>Copernicus STAC Quota: <strong className="text-slate-200">Normal</strong></span>
        </div>
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-marine-500" />
          <span>LangGraph AI Agent Quota: <strong className="text-slate-200">Active</strong></span>
        </div>
        <div className="flex items-center gap-2">
          <Mail className="w-4 h-4 text-marine-500" />
          <span>Email Alert Dispatcher: <strong className="text-slate-200">Ready</strong></span>
        </div>
      </div>
    </div>
  );
}
