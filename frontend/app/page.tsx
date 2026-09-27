import Link from "next/link";
import { Waves, ArrowRight, ShieldCheck, Compass, MapPin, Database, Cpu, Layers } from "lucide-react";

export default function Home() {
  return (
    <div className="space-y-12 py-6">
      
      {/* Hero Banner */}
      <div className="bg-gradient-to-br from-slate-900 via-slate-900 to-marine-950 border border-slate-800 rounded-3xl p-8 sm:p-12 shadow-2xl relative overflow-hidden">
        <div className="absolute -right-12 -bottom-12 opacity-10 text-marine-500">
          <Waves className="w-96 h-96" />
        </div>

        <div className="relative z-10 max-w-3xl space-y-6">
          <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-marine-500/15 text-marine-400 border border-marine-500/30">
            <span className="w-2 h-2 rounded-full bg-marine-500 animate-pulse" />
            Agentic AI + Geospatial Remote Sensing Platform
          </span>

          <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-100 tracking-tight leading-tight">
            Multi-Source Marine Pollution <span className="text-transparent bg-clip-text bg-gradient-to-r from-marine-400 to-cyan-300">Early-Warning & Investigation</span>
          </h1>

          <p className="text-lg text-slate-300 leading-relaxed">
            MarineGuard AI continuously analyzes satellite remote sensing, meteorological wind vectors, oceanographic currents, coastal GIS features, and historical reports to detect, track, investigate, and assess potential marine pollution events along the Gujarat coast.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-4">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-xl font-bold bg-marine-500 hover:bg-marine-400 text-white shadow-lg shadow-marine-500/20 transition-all transform hover:-translate-y-0.5"
            >
              Launch Operational Dashboard <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Feature Architecture Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-3">
          <div className="w-12 h-12 rounded-xl bg-marine-500/15 border border-marine-500/30 flex items-center justify-center text-marine-400">
            <Layers className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-100">Per-Class Anomaly Detection</h3>
          <p className="text-sm text-slate-400">
            Unsupervised baseline anomaly detection incorporating Sentinel-1 SAR wind-gates (2–10 m/s) and Sentinel-2 optical spectral ratios.
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-3">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Cpu className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-100">LangGraph Agentic Reasoning</h3>
          <p className="text-sm text-slate-400">
            Stateful multi-agent investigation workflow combining Router, Evidence, Source, Impact, and Report agents.
          </p>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl space-y-3">
          <div className="w-12 h-12 rounded-xl bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400">
            <Compass className="w-6 h-6" />
          </div>
          <h3 className="text-lg font-bold text-slate-100">Pollutant Drift & GIS Impact</h3>
          <p className="text-sm text-slate-400">
            Pollutant-specific drift vectors intersecting with Hazira mangrove belts, Suvali/Dumas beaches, and coastal fishing zones.
          </p>
        </div>
      </div>

    </div>
  );
}
