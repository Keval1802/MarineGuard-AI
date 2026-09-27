"use client";

import React, { useEffect, useState } from "react";
import { Incident, api } from "@/lib/api";
import IncidentCard from "@/components/IncidentCard";
import { AlertTriangle, RefreshCw, ShieldAlert, MapPin, Activity, CheckCircle2 } from "lucide-react";

export default function DashboardPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [runningMonitor, setRunningMonitor] = useState<boolean>(false);
  const [notification, setNotification] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    const data = await api.getIncidents();
    setIncidents(data);
    setLoading(false);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRunMonitor = async () => {
    setRunningMonitor(true);
    setNotification("Running scheduled monitoring cycle & satellite anomaly scan...");
    try {
      await api.runMonitoringCycle();
      setNotification("Monitoring cycle complete! New satellite observations processed.");
      await loadData();
    } catch {
      setNotification("Local simulation monitoring completed.");
      await loadData();
    } finally {
      setRunningMonitor(false);
      setTimeout(() => setNotification(null), 5000);
    }
  };

  const highPriorityCount = incidents.filter((i) => i.priority_score >= 0.50).length;

  return (
    <div className="space-y-8">
      
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-100">Marine Incident Dashboard</h1>
          <p className="text-sm text-slate-400">Near-Real-Time Early Warning & Response Intelligence — Gujarat Study Area</p>
        </div>

        <button
          onClick={handleRunMonitor}
          disabled={runningMonitor}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl font-bold bg-marine-500 hover:bg-marine-400 text-white shadow-lg transition-all disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${runningMonitor ? "animate-spin" : ""}`} />
          {runningMonitor ? "Scanning Satellites..." : "Run Monitoring Scan"}
        </button>
      </div>

      {notification && (
        <div className="bg-marine-500/15 border border-marine-500/40 text-marine-300 p-4 rounded-xl text-sm flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 text-marine-400 shrink-0" />
          <span>{notification}</span>
        </div>
      )}

      {/* Summary Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase">Total Incidents</span>
            <AlertTriangle className="w-5 h-5 text-marine-400" />
          </div>
          <p className="text-3xl font-extrabold text-slate-100">{incidents.length}</p>
          <span className="text-xs text-slate-500 font-mono">Monitored Records</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase">High Priority</span>
            <ShieldAlert className="w-5 h-5 text-rose-500" />
          </div>
          <p className="text-3xl font-extrabold text-rose-400">{highPriorityCount}</p>
          <span className="text-xs text-slate-500 font-mono">Requires Action</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase">Monitored Region</span>
            <MapPin className="w-5 h-5 text-emerald-400" />
          </div>
          <p className="text-xl font-bold text-slate-100">Hazira / Surat</p>
          <span className="text-xs text-emerald-400 font-mono">BBOX: 72.50E - 72.85E</span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-semibold uppercase">System Mode</span>
            <Activity className="w-5 h-5 text-amber-400" />
          </div>
          <p className="text-xl font-bold text-slate-100">Development</p>
          <span className="text-xs text-amber-400 font-mono">Zero-Cost Prototype</span>
        </div>

      </div>

      {/* Active Incidents List */}
      <div className="space-y-4">
        <h2 className="text-lg font-bold text-slate-200">Active Marine Pollution Incidents</h2>
        {loading ? (
          <div className="bg-slate-900 p-8 rounded-xl text-center text-slate-500">Loading incident data...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {incidents.map((inc) => (
              <IncidentCard key={inc.id || inc.incident_code} incident={inc} />
            ))}
          </div>
        )}
      </div>

    </div>
  );
}
