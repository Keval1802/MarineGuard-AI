"use client";

import React, { useState } from "react";
import { SatelliteObservation } from "@/lib/types";
import { Image as ImageIcon, Eye, Layers, Columns } from "lucide-react";

interface EvidenceViewerProps {
  observation?: SatelliteObservation;
  rawUrl?: string;
  annotatedUrl?: string;
  comparisonUrl?: string;
  incidentCode?: string;
}

export default function EvidenceViewer({
  observation,
  rawUrl,
  annotatedUrl,
  comparisonUrl,
  incidentCode
}: EvidenceViewerProps) {
  const [activeTab, setActiveTab] = useState<"comparison" | "annotated" | "raw">("comparison");

  const code = incidentCode || (observation?.image_path ? "" : "MG-2026-COP-2303");
  const raw = rawUrl || observation?.image_path || `/storage/evidence/${code}_raw.png`;
  const annotated = annotatedUrl || observation?.annotated_image_path || `/storage/evidence/${code}_annotated.png`;
  const comparison = comparisonUrl || observation?.before_after_image_path || `/storage/evidence/${code}_comparison.png`;

  const getActiveImageUrl = () => {
    switch (activeTab) {
      case "raw":
        return raw;
      case "annotated":
        return annotated;
      case "comparison":
      default:
        return comparison;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg space-y-0">
      
      {/* Header Controls */}
      <div className="bg-slate-950 border-b border-slate-800 p-3.5 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <ImageIcon className="w-5 h-5 text-marine-500" />
          <span className="font-semibold text-sm text-slate-200">Satellite Evidence Capture</span>
          <span className="text-xs bg-marine-500/20 text-marine-400 border border-marine-500/30 px-2 py-0.5 rounded font-mono font-bold">
            Dual-Sensing: Sentinel-1 & Sentinel-2
          </span>
        </div>

        {/* Tab Switchers */}
        <div className="flex items-center bg-slate-900 p-1 rounded-lg border border-slate-800 text-xs gap-1">
          <button
            onClick={() => setActiveTab("comparison")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-all ${
              activeTab === "comparison"
                ? "bg-marine-500 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Columns className="w-3.5 h-3.5 text-amber-400" /> Combined Dual Satellite View (Sentinel-1 vs Sentinel-2)
          </button>
          <button
            onClick={() => setActiveTab("annotated")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-all ${
              activeTab === "annotated"
                ? "bg-marine-500 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Layers className="w-3.5 h-3.5" /> Annotated Overlay
          </button>
          <button
            onClick={() => setActiveTab("raw")}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md font-medium transition-all ${
              activeTab === "raw"
                ? "bg-marine-500 text-white shadow-sm"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Eye className="w-3.5 h-3.5" /> Raw Satellite Scene
          </button>
        </div>
      </div>

      {/* Main Image Display Container */}
      <div className="relative aspect-video bg-slate-950 flex items-center justify-center overflow-hidden">
        <img
          src={getActiveImageUrl()}
          alt="Sentinel Dual Satellite Evidence Comparison"
          className="w-full h-full object-contain"
          onError={(e) => {
            // Fallback render if backend image path is loading
            (e.target as HTMLImageElement).src =
              "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='800' height='400' viewBox='0 0 800 400'><rect width='800' height='400' fill='%230f172a'/><rect x='10' y='10' width='385' height='380' fill='%231e293b' stroke='%2338bdf8' stroke-width='2'/><text x='202' y='40' fill='%2338bdf8' font-size='16' font-family='monospace' font-weight='bold' text-anchor='middle'>SENTINEL-1 SAR (RADAR)</text><text x='202' y='210' fill='%2394a3b8' font-size='14' text-anchor='middle'>Radar Surface Roughness Patch</text><rect x='405' y='10' width='385' height='380' fill='%231e293b' stroke='%23facc15' stroke-width='2'/><text x='597' y='40' fill='%23facc15' font-size='16' font-family='monospace' font-weight='bold' text-anchor='middle'>SENTINEL-2 OPTICAL (MULTISPECTRAL)</text><text x='597' y='210' fill='%2394a3b8' font-size='14' text-anchor='middle'>Multispectral Optical Debris Patch</text></svg>";
          }}
        />

        {/* Dynamic Mode Description Banner */}
        <div className="absolute bottom-3 left-3 bg-slate-900/90 backdrop-blur border border-slate-700/60 px-3 py-1.5 rounded-md text-xs font-mono text-slate-300 shadow flex items-center gap-2">
          {activeTab === "comparison" && (
            <span>
              <strong className="text-marine-400">LEFT:</strong> Sentinel-1 SAR (Radar) &nbsp;|&nbsp; <strong className="text-amber-400">RIGHT:</strong> Sentinel-2 Optical (Multispectral)
            </span>
          )}
          {activeTab === "annotated" && <span>Mode: Anomaly Bounding Box & Polygon Overlay</span>}
          {activeTab === "raw" && <span>Mode: Raw Copernicus Satellite Band Crop</span>}
        </div>
      </div>

      {/* Side-by-side explicit dual-panel layout when observation or incidentCode is present */}
      <div className="bg-slate-950 p-4 border-t border-slate-800 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="border border-slate-800 rounded-lg p-3 bg-slate-900/50 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold font-mono text-marine-400 uppercase flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-marine-500 animate-pulse"></span>
              Sentinel-1 SAR Radar Image
            </span>
            <span className="text-[11px] text-slate-500 font-mono">C-Band Synthetic Aperture Radar</span>
          </div>
          <div className="aspect-video bg-slate-950 rounded border border-slate-800 overflow-hidden relative flex items-center justify-center">
            <img
              src={raw.includes("sentinel-2") ? raw.replace("sentinel-2", "sentinel-1") : raw}
              alt="Sentinel-1 SAR Radar"
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).src =
                  "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='250' viewBox='0 0 400 250'><rect width='400' height='250' fill='%23090d16'/><text x='200' y='125' fill='%2338bdf8' font-size='14' font-family='monospace' text-anchor='middle'>SENTINEL-1 SAR RADAR PATCH</text></svg>";
              }}
            />
            <div className="absolute top-2 left-2 bg-slate-900/80 px-2 py-0.5 rounded text-[10px] font-mono text-marine-300">
              Radar VV Backscatter
            </div>
          </div>
        </div>

        <div className="border border-slate-800 rounded-lg p-3 bg-slate-900/50 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold font-mono text-amber-400 uppercase flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse"></span>
              Sentinel-2 Optical Image
            </span>
            <span className="text-[11px] text-slate-500 font-mono">MSI Multispectral Instrument</span>
          </div>
          <div className="aspect-video bg-slate-950 rounded border border-slate-800 overflow-hidden relative flex items-center justify-center">
            <img
              src={raw.includes("sentinel-1") ? raw.replace("sentinel-1", "sentinel-2") : annotated}
              alt="Sentinel-2 Optical"
              className="w-full h-full object-cover"
              onError={(e) => {
                (e.target as HTMLImageElement).src =
                  "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='400' height='250' viewBox='0 0 400 250'><rect width='400' height='250' fill='%23090d16'/><text x='200' y='125' fill='%23facc15' font-size='14' font-family='monospace' text-anchor='middle'>SENTINEL-2 OPTICAL PATCH</text></svg>";
              }}
            />
            <div className="absolute top-2 left-2 bg-slate-900/80 px-2 py-0.5 rounded text-[10px] font-mono text-amber-300">
              Multispectral Optical RGB
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
