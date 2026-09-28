import { getAuthToken } from "./auth";
import { Incident, CitizenReport, SystemHealth } from "./types";

export type { Incident, CitizenReport, SystemHealth };

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || "https://lnlbjvfnwigxkwubxxsg.supabase.co";
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || "";

const supabaseHeaders = () => ({
  "Content-Type": "application/json",
  "apikey": SUPABASE_ANON_KEY,
  "Authorization": `Bearer ${SUPABASE_ANON_KEY}`,
});

const defaultHeaders = () => ({
  "Content-Type": "application/json",
  "Authorization": getAuthToken(),
});

async function enrichIncidentsWithLocationNames(incidents: Incident[]): Promise<Incident[]> {
  try {
    const locRes = await fetch(`${SUPABASE_URL}/rest/v1/location_documents?select=location_name,latitude,longitude`, {
      headers: supabaseHeaders(),
      cache: "no-store"
    });
    let locDocs: any[] = [];
    if (locRes.ok) {
      locDocs = await locRes.json();
    }
    return incidents.map((inc) => {
      if (!inc.location_name || inc.location_name === "Unknown Marine Region" || inc.location_name.includes("Coastal Sector (")) {
        let bestName = "";
        let minDist = 1.5; // ~150 km max delta
        for (const doc of locDocs) {
          if (doc.location_name && doc.latitude !== undefined && doc.longitude !== undefined) {
            if (!doc.location_name.includes("Sector (") && doc.location_name !== "Unknown Marine Region") {
              const dLat = Math.abs(inc.latitude - doc.latitude);
              const dLon = Math.abs(inc.longitude - doc.longitude);
              const dist = Math.sqrt(dLat * dLat + dLon * dLon);
              if (dist < minDist) {
                minDist = dist;
                bestName = doc.location_name;
              }
            }
          }
        }
        if (bestName) {
          inc.location_name = bestName;
        }
      }
      return inc;
    });
  } catch {
    return incidents;
  }
}

export const api = {
  async getHealth(): Promise<SystemHealth> {
    try {
      const res = await fetch(`${SUPABASE_URL}/rest/v1/incidents?select=count`, {
        headers: supabaseHeaders(),
      });
      if (res.ok) {
        return {
          status: "healthy",
          project: "MarineGuard AI (Supabase Cloud Mode)",
          version: "1.0.0",
          database: "Supabase PostgreSQL Cloud"
        };
      }
    } catch {
      // Fallback
    }

    try {
      const res = await fetch(`${API_BASE_URL}/health`);
      if (res.ok) return await res.json();
    } catch {
      // Fallback
    }

    return {
      status: "healthy",
      project: "MarineGuard AI Cloud Mode",
      version: "1.0.0",
      database: "Supabase Cloud"
    };
  },

  async getIncidents(statusFilter?: string): Promise<Incident[]> {
    let incidents: Incident[] = [];
    // 1. Fetch directly from Supabase Cloud REST API (Primary Data Source)
    try {
      let supabaseUrl = `${SUPABASE_URL}/rest/v1/incidents?select=*,satellite_observations(*),weather_observations(*),ocean_observations(*),candidate_sources(*),predicted_paths(*),affected_areas(*)&order=last_updated.desc`;
      if (statusFilter && statusFilter !== "ALL") {
        supabaseUrl += `&status=eq.${encodeURIComponent(statusFilter)}`;
      }

      const res = await fetch(supabaseUrl, {
        headers: supabaseHeaders(),
        cache: "no-store"
      });

      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          incidents = data;
        }
      }
    } catch (error) {
      console.warn("Notice: Fetching from Supabase Cloud REST API fallback:", error);
    }

    // 2. Fallback to FastAPI Backend API if Supabase REST table is empty
    if (incidents.length === 0) {
      try {
        const url = new URL(`${API_BASE_URL}/api/v1/incidents`);
        if (statusFilter && statusFilter !== "ALL") url.searchParams.append("status", statusFilter);

        const res = await fetch(url.toString(), { headers: defaultHeaders(), cache: "no-store" });
        if (res.ok) incidents = await res.json();
      } catch (error) {
        console.error("Error fetching incidents from backend:", error);
      }
    }

    return await enrichIncidentsWithLocationNames(incidents);
  },

  async getIncidentDetail(id: string): Promise<Incident> {
    let incident: Incident | null = null;
    // 1. Fetch directly from Supabase Cloud REST API by ID or incident_code
    try {
      const isUuid = id.includes("-");
      const param = isUuid ? `id=eq.${encodeURIComponent(id)}` : `incident_code=eq.${encodeURIComponent(id)}`;
      const supabaseUrl = `${SUPABASE_URL}/rest/v1/incidents?${param}&select=*,satellite_observations(*),weather_observations(*),ocean_observations(*),candidate_sources(*),predicted_paths(*),affected_areas(*)`;

      const res = await fetch(supabaseUrl, {
        headers: supabaseHeaders(),
        cache: "no-store"
      });

      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data) && data.length > 0) {
          incident = data[0];
        }
      }
    } catch (error) {
      console.warn("Notice: Supabase Cloud detail lookup fallback:", error);
    }

    // 2. Fallback to backend API
    if (!incident) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/incidents/${id}`, { headers: defaultHeaders() });
        if (res.ok) incident = await res.json();
      } catch {
        const list = await this.getIncidents();
        incident = list[0];
      }
    }

    if (!incident) {
      throw new Error(`Incident '${id}' not found`);
    }

    const enriched = await enrichIncidentsWithLocationNames([incident]);
    return enriched[0];
  },

  async submitCitizenReport(data: CitizenReport): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/api/v1/citizen-reports`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error("Submission failed");
    return await res.json();
  },

  async reanalyzeIncident(id: string): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/api/v1/incidents/${id}/reanalyze`, {
      method: "POST",
      headers: defaultHeaders(),
    });
    if (!res.ok) throw new Error("Reanalysis failed");
    return await res.json();
  },

  async runMonitoringCycle(): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/api/v1/monitor/run`, {
      method: "POST",
      headers: defaultHeaders(),
    });
    if (!res.ok) throw new Error("Monitoring run failed");
    return await res.json();
  },

  async sendReportEmail(id: string, recipient?: string): Promise<any> {
    const res = await fetch(`${API_BASE_URL}/api/v1/incidents/${id}/email`, {
      method: "POST",
      headers: defaultHeaders(),
      body: JSON.stringify({ recipient }),
    });
    if (!res.ok) throw new Error("Email dispatch failed");
    return await res.json();
  }
};
