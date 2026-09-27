export type AnomalyType = 
  | "NORMAL"
  | "SURFACE_ANOMALY"
  | "OIL_LIKE_ANOMALY"
  | "FLOATING_MATERIAL_CANDIDATE"
  | "HIGH_TURBIDITY_EVENT"
  | "UNKNOWN";

export type IncidentStatus = 
  | "DETECTED"
  | "UNDER_INVESTIGATION"
  | "POSSIBLE"
  | "LIKELY"
  | "HIGH_CONFIDENCE"
  | "MONITORING"
  | "RESOLVED"
  | "CLOSED"
  | "FALSE_POSITIVE";

export interface SatelliteObservation {
  id: string;
  mission: string;
  product_id: string;
  acquisition_time: string;
  cloud_cover?: number;
  image_path?: string;
  annotated_image_path?: string;
  before_after_image_path?: string;
  model_result?: string;
  detection_method: string;
  wind_speed_ms?: number;
  confidence: number;
}

export interface WeatherObservation {
  id: string;
  timestamp: string;
  wind_speed: number;
  wind_direction: number;
  rainfall: number;
  source: string;
}

export interface OceanObservation {
  id: string;
  timestamp: string;
  current_speed: number;
  current_direction: number;
  tide: string;
  sea_surface_temperature?: number;
  source: string;
}

export interface PredictedPath {
  id?: string;
  forecast_time: string;
  latitude: number;
  longitude: number;
  uncertainty: number;
}

export interface AffectedArea {
  id?: string;
  area_name: string;
  area_type: string;
  distance_km: number;
  risk_level: "LOW" | "MODERATE" | "HIGH" | "CRITICAL";
}

export interface CandidateSource {
  id?: string;
  source_type: string;
  reference: string;
  confidence: string;
  evidence_json?: Record<string, any>;
}

export interface Incident {
  id: string;
  incident_code: string;
  anomaly_type: AnomalyType;
  latitude: number;
  longitude: number;
  location_name?: string;
  first_detected: string;
  last_updated: string;
  confidence_score: number;
  severity_score: number;
  priority_score: number;
  status: IncidentStatus;
  report?: string;
  satellite_observations?: SatelliteObservation[];
  weather_observations?: WeatherObservation[];
  ocean_observations?: OceanObservation[];
  candidate_sources?: CandidateSource[];
  predicted_paths?: PredictedPath[];
  affected_areas?: AffectedArea[];
}

export interface CitizenReport {
  id?: string;
  description: string;
  latitude: number;
  longitude: number;
  image_path?: string;
  submitted_at?: string;
  verification_status?: string;
}

export interface SystemHealth {
  status: string;
  project: string;
  version: string;
  database: string;
}
