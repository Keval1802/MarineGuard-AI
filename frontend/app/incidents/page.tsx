"use client";

import React, { useEffect, useState } from "react";
import { Incident, api } from "@/lib/api";
import IncidentCard from "@/components/IncidentCard";
import { Filter, Search, AlertTriangle } from "lucide-react";

export default function IncidentsPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [anomalyFilter, setAnomalyFilter] = useState("ALL");
  const [statusFilter, setStatusFilter] = useState("ALL");

  useEffect(() => {
    api.getIncidents().then(setIncidents);
  }, []);

  const filteredIncidents = incidents.filter((inc) => {
    const matchesSearch =
      inc.incident_code.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inc.anomaly_type.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesAnomaly = anomalyFilter === "ALL" || inc.anomaly_type === anomalyFilter;
    const matchesStatus = statusFilter === "ALL" || inc.status === statusFilter;
    return matchesSearch && matchesAnomaly && matchesStatus;
  });

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="pb-4 border-b border-slate-800">
        <h1 className="text-2xl font-extrabold text-slate-100">Incident Explorer</h1>
        <p className="text-sm text-slate-400">Search, filter, and inspect active and historical marine pollution incidents.</p>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-slate-900 border border-slate-800 p-4 rounded-xl flex flex-wrap items-center justify-between gap-4">
        
        {/* Search Input */}
        <div className="relative flex-1 min-w-[240px]">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
          <input
            type="text"
            placeholder="Search by incident code or pollutant type..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-marine-500"
          />
        </div>

        {/* Anomaly Type Filter */}
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-500" />
          <select
            value={anomalyFilter}
            onChange={(e) => setAnomalyFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-marine-500"
          >
            <option value="ALL">All Anomaly Classes</option>
            <option value="OIL_LIKE_ANOMALY">Oil-Like Anomaly</option>
            <option value="FLOATING_MATERIAL_CANDIDATE">Floating Material Candidate</option>
            <option value="HIGH_TURBIDITY_EVENT">High Turbidity Event</option>
            <option value="SURFACE_ANOMALY">Surface Anomaly</option>
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-950 border border-slate-800 text-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-marine-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="DETECTED">Detected</option>
            <option value="UNDER_INVESTIGATION">Under Investigation</option>
            <option value="MONITORING">Monitoring</option>
            <option value="RESOLVED">Resolved</option>
          </select>
        </div>

      </div>

      {/* Incident Cards Grid */}
      {filteredIncidents.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 p-12 rounded-xl text-center text-slate-500 space-y-2">
          <AlertTriangle className="w-8 h-8 mx-auto text-slate-600" />
          <p>No matching marine incidents found for the selected filters.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filteredIncidents.map((inc) => (
            <IncidentCard key={inc.id || inc.incident_code} incident={inc} />
          ))}
        </div>
      )}

    </div>
  );
}
