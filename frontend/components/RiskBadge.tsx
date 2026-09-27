import React from "react";

interface RiskBadgeProps {
  level: "LOW" | "MODERATE" | "HIGH" | "CRITICAL" | string;
  type?: "risk" | "confidence";
  score?: number;
}

export default function RiskBadge({ level, type = "risk", score }: RiskBadgeProps) {
  const getColors = () => {
    switch (level.toUpperCase()) {
      case "CRITICAL":
      case "VERY HIGH":
        return "bg-rose-500/15 text-rose-400 border-rose-500/30";
      case "HIGH":
        return "bg-orange-500/15 text-orange-400 border-orange-500/30";
      case "MODERATE":
        return "bg-amber-500/15 text-amber-400 border-amber-500/30";
      case "LOW":
      default:
        return "bg-emerald-500/15 text-emerald-400 border-emerald-500/30";
    }
  };

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold border ${getColors()}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {type === "confidence" ? `Conf: ${level}` : `Risk: ${level}`}
      {score !== undefined && <span className="opacity-80 font-normal">({score.toFixed(1)})</span>}
    </span>
  );
}
