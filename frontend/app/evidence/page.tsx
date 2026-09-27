"use client";

import React, { useEffect, useState } from "react";
import { Incident, api } from "@/lib/api";
import EvidenceViewer from "@/components/EvidenceViewer";
import { Image as ImageIcon } from "lucide-react";

export default function EvidencePage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);

  useEffect(() => {
    api.getIncidents().then(setIncidents);
  }, []);

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="pb-4 border-b border-slate-800">
        <h1 className="text-2xl font-extrabold text-slate-100 flex items-center gap-2">
          <ImageIcon className="w-6 h-6 text-marine-500" /> Satellite Evidence Gallery
        </h1>
        <p className="text-sm text-slate-400">Inspect raw satellite crops and annotated anomaly masks.</p>
      </div>

      {/* Gallery Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {incidents.map((inc) => {
          const obs = inc.satellite_observations?.[0];
          const missionName = obs?.mission || (inc.incident_code.includes("S1") ? "Sentinel-1D SAR" : "Sentinel-2A Optical");

          return (
            <div key={inc.id || inc.incident_code} className="space-y-3">
              <div className="flex items-center justify-between text-sm bg-slate-900 px-3 py-2 rounded-lg border border-slate-800">
                <div className="flex items-center gap-2">
                  <span className="font-mono font-bold text-marine-400">{inc.incident_code}</span>
                  <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-medium">
                    {missionName}
                  </span>
                </div>
                <span className="text-xs text-amber-400 font-semibold">{inc.anomaly_type.replace(/_/g, " ")}</span>
              </div>
              <EvidenceViewer observation={obs} incidentCode={inc.incident_code} />
            </div>
          );
        })}
      </div>

    </div>
  );
}
