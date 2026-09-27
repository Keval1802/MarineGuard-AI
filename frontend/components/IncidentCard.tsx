import React from "react";
import Link from "next/link";
import { Incident } from "@/lib/api";
import RiskBadge from "./RiskBadge";
import { AlertCircle, Calendar, MapPin, ArrowRight, ShieldCheck, Compass } from "lucide-react";

interface IncidentCardProps {
  incident: Incident;
}

export default function IncidentCard({ incident }: IncidentCardProps) {
  const getRiskLevel = (score: number) => {
    if (score >= 0.75) return "CRITICAL";
    if (score >= 0.50) return "HIGH";
    if (score >= 0.30) return "MODERATE";
    return "LOW";
  };

  const riskLevel = getRiskLevel(incident.priority_score);

  const getLocationName = (lat: number, lon: number, code: string, dbLocName?: string) => {
    if (dbLocName && dbLocName !== "Unknown Marine Region") return dbLocName;
    if (lat >= 29.8 && lat <= 31.0 && lon >= 32.1 && lon <= 32.6) {
      return "Great Bitter Lake, Suez Canal, Egypt";
    }
    if ((lat >= 13.0 && lat <= 13.5 && lon >= 80.0 && lon <= 80.5) || code.includes("ENNORE")) {
      return "Ennore Port Sector, Chennai";
    }
    if (lat >= 20.5 && lat <= 22.0 && lon >= 72.0 && lon <= 73.0) {
      return "Surat & Hazira Sector, Gujarat";
    }
    if (lat >= 22.5 && lat <= 23.5 && lon >= 69.5 && lon <= 70.8) {
      return "Kandla & Gulf of Kutch Sector, Gujarat";
    }
    if (lat >= 12.0 && lat <= 13.5 && lon >= 100.5 && lon <= 101.5) {
      return "Sattahip & Pattaya Sector, Thailand";
    }
    return `Coastal Sector (${lat.toFixed(3)}°N, ${lon.toFixed(3)}°E)`;
  };

  const locationName = getLocationName(incident.latitude, incident.longitude, incident.incident_code, incident.location_name);

  return (
    <div className="bg-slate-900 border border-slate-800 hover:border-slate-700 rounded-xl p-5 transition-all shadow-md hover:shadow-xl group">
      
      {/* Header */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div>
          <span className="text-xs font-mono text-marine-500 font-semibold uppercase">{incident.incident_code}</span>
          <h3 className="text-lg font-bold text-slate-100 mt-0.5 group-hover:text-marine-500 transition-colors">
            {incident.anomaly_type.replace(/_/g, " ")}
          </h3>
        </div>
        <RiskBadge level={riskLevel} score={incident.priority_score} />
      </div>

      {/* Location & Metadata */}
      <div className="space-y-2 text-sm text-slate-400 mb-4">
        <div className="flex items-center gap-2">
          <MapPin className="w-4 h-4 text-marine-400 shrink-0" />
          <span className="font-semibold text-slate-200">{locationName}</span>
          <span className="text-xs text-slate-500 font-mono">({incident.latitude.toFixed(3)}°N, {incident.longitude.toFixed(3)}°E)</span>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-slate-500 shrink-0" />
          <span>First Observed: {new Date(incident.first_detected).toLocaleDateString()}</span>
        </div>
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-slate-500 shrink-0" />
          <span>Evidence Confidence: <strong className="text-slate-200">{incident.confidence_score.toFixed(1)}%</strong></span>
        </div>
      </div>

      {/* Report Snippet */}
      {incident.report && (
        <p className="text-xs text-slate-400 line-clamp-2 bg-slate-950/60 p-2.5 rounded-lg border border-slate-800/80 mb-4 italic">
          "{incident.report.replace(/#|\*/g, "").slice(0, 140)}..."
        </p>
      )}

      {/* Action Footer */}
      <div className="flex items-center justify-between pt-3 border-t border-slate-800/60 text-xs">
        <span className="text-slate-500 font-mono uppercase">Status: <strong className="text-slate-300">{incident.status}</strong></span>
        
        <Link
          href={`/incidents/${incident.id || incident.incident_code}`}
          className="inline-flex items-center gap-1 font-semibold text-marine-500 hover:text-marine-400 transition-colors"
        >
          View Investigation <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>

    </div>
  );
}
