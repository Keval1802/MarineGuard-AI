-- =====================================================================
-- MARINEGUARD AI — SUPABASE POSTGRESQL / POSTGIS SCHEMA MIGRATION DDL
-- Project: MarineGuard AI (Gulf of Khambhat / Hazira Coastal Protection)
-- Target: Supabase Dashboard -> SQL Editor
-- =====================================================================

-- 1. Enable PostGIS Extension for Geospatial Operations
CREATE EXTENSION IF NOT EXISTS postgis;

-- 2. Incidents Table (Section 21)
CREATE TABLE IF NOT EXISTS public.incidents (
    id VARCHAR(36) PRIMARY KEY,
    incident_code VARCHAR(32) UNIQUE NOT NULL,
    anomaly_type VARCHAR(50) NOT NULL DEFAULT 'UNKNOWN',
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    location_name VARCHAR(255) DEFAULT 'Unknown Marine Region',
    first_detected TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    confidence_score DOUBLE PRECISION DEFAULT 0.0,
    severity_score DOUBLE PRECISION DEFAULT 0.0,
    priority_score DOUBLE PRECISION DEFAULT 0.0,
    status VARCHAR(50) NOT NULL DEFAULT 'DETECTED',
    report TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

ALTER TABLE public.incidents ADD COLUMN IF NOT EXISTS location_name VARCHAR(255) DEFAULT 'Unknown Marine Region';

CREATE INDEX IF NOT EXISTS idx_incidents_code ON public.incidents(incident_code);
CREATE INDEX IF NOT EXISTS idx_incidents_coords ON public.incidents(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_incidents_status ON public.incidents(status);

-- 3. Satellite Observations Table (Section 13)
CREATE TABLE IF NOT EXISTS public.satellite_observations (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) REFERENCES public.incidents(id) ON DELETE CASCADE,
    mission VARCHAR(50) NOT NULL,
    product_id VARCHAR(128) NOT NULL,
    acquisition_time TIMESTAMP WITH TIME ZONE NOT NULL,
    cloud_cover DOUBLE PRECISION,
    image_path VARCHAR(255),
    annotated_image_path VARCHAR(255),
    before_after_image_path VARCHAR(255),
    model_result VARCHAR(50),
    detection_method VARCHAR(50) NOT NULL,
    wind_speed_ms DOUBLE PRECISION,
    confidence DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

-- 4. Weather Observations Table (Section 17)
CREATE TABLE IF NOT EXISTS public.weather_observations (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) REFERENCES public.incidents(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    wind_speed DOUBLE PRECISION NOT NULL,
    wind_direction DOUBLE PRECISION NOT NULL,
    rainfall DOUBLE PRECISION DEFAULT 0.0,
    source VARCHAR(50) DEFAULT 'Open-Meteo'
);

-- 5. Ocean Observations Table (Section 18)
CREATE TABLE IF NOT EXISTS public.ocean_observations (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) REFERENCES public.incidents(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    current_speed DOUBLE PRECISION NOT NULL,
    current_direction DOUBLE PRECISION NOT NULL,
    tide VARCHAR(20) DEFAULT 'UNKNOWN',
    sea_surface_temperature DOUBLE PRECISION,
    source VARCHAR(50) DEFAULT 'Open-Meteo Marine'
);

-- 6. Vessel Events Table (Section 19 / Section 42 Candidate Sources)
CREATE TABLE IF NOT EXISTS public.vessel_events (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) REFERENCES public.incidents(id) ON DELETE CASCADE,
    vessel_id VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    speed_knots DOUBLE PRECISION,
    heading_deg DOUBLE PRECISION,
    risk_level VARCHAR(20) DEFAULT 'UNKNOWN'
);

-- 7. Candidate Sources Table (Section 23)
CREATE TABLE IF NOT EXISTS public.candidate_sources (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) REFERENCES public.incidents(id) ON DELETE CASCADE,
    source_type VARCHAR(50) NOT NULL,
    reference VARCHAR(128) NOT NULL,
    confidence VARCHAR(20) DEFAULT 'moderate',
    evidence_json JSONB
);

-- 8. Predicted Trajectory Paths Table (Section 24)
CREATE TABLE IF NOT EXISTS public.predicted_paths (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) REFERENCES public.incidents(id) ON DELETE CASCADE,
    forecast_time TIMESTAMP WITH TIME ZONE NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    uncertainty DOUBLE PRECISION NOT NULL DEFAULT 1.0
);

-- 9. Affected Coastal Areas Table (Section 25)
CREATE TABLE IF NOT EXISTS public.affected_areas (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) REFERENCES public.incidents(id) ON DELETE CASCADE,
    area_type VARCHAR(50) NOT NULL,
    area_name VARCHAR(128) NOT NULL,
    distance_km DOUBLE PRECISION NOT NULL,
    risk_level VARCHAR(20) NOT NULL
);

-- 10. Citizen Reports Table (Section 20)
CREATE TABLE IF NOT EXISTS public.citizen_reports (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) REFERENCES public.incidents(id),
    description TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    image_path VARCHAR(255),
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    verification_status VARCHAR(50) DEFAULT 'PENDING'
);

-- 11. Alerts Log Table (Section 27)
CREATE TABLE IF NOT EXISTS public.alerts (
    id VARCHAR(36) PRIMARY KEY,
    incident_id VARCHAR(36) REFERENCES public.incidents(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,
    recipient VARCHAR(128) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'QUEUED',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()),
    sent_at TIMESTAMP WITH TIME ZONE
);

-- 12. Location Scraped Documents Table for RAG Knowledge Base
CREATE TABLE IF NOT EXISTS public.location_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_name VARCHAR(255) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    topic VARCHAR(128) NOT NULL,
    content TEXT NOT NULL,
    source VARCHAR(255) DEFAULT 'Web Search & GIS Database',
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now())
);

CREATE INDEX IF NOT EXISTS idx_location_docs_name ON public.location_documents(location_name);
CREATE INDEX IF NOT EXISTS idx_location_docs_coords ON public.location_documents(latitude, longitude);

-- 13. Enable Row Level Security (RLS) & Idempotent Policies
ALTER TABLE public.incidents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.location_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.satellite_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.weather_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.ocean_observations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vessel_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.candidate_sources ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.predicted_paths ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.affected_areas ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;

-- Drop Existing Policies (Prevents 42710 Duplicate Errors)
DROP POLICY IF EXISTS "Allow public read access to incidents" ON public.incidents;
DROP POLICY IF EXISTS "Allow public read incidents" ON public.incidents;
DROP POLICY IF EXISTS "Allow anon insert incidents" ON public.incidents;
DROP POLICY IF EXISTS "Allow anon update incidents" ON public.incidents;
DROP POLICY IF EXISTS "Allow anon delete incidents" ON public.incidents;

DROP POLICY IF EXISTS "Allow public read access to satellite_observations" ON public.satellite_observations;
DROP POLICY IF EXISTS "Allow public read satellite_observations" ON public.satellite_observations;
DROP POLICY IF EXISTS "Allow anon insert satellite_observations" ON public.satellite_observations;
DROP POLICY IF EXISTS "Allow anon update satellite_observations" ON public.satellite_observations;
DROP POLICY IF EXISTS "Allow anon delete satellite_observations" ON public.satellite_observations;

DROP POLICY IF EXISTS "Allow public read weather_observations" ON public.weather_observations;
DROP POLICY IF EXISTS "Allow anon insert weather_observations" ON public.weather_observations;
DROP POLICY IF EXISTS "Allow public read ocean_observations" ON public.ocean_observations;
DROP POLICY IF EXISTS "Allow anon insert ocean_observations" ON public.ocean_observations;

DROP POLICY IF EXISTS "Allow public read vessel_events" ON public.vessel_events;
DROP POLICY IF EXISTS "Allow anon insert vessel_events" ON public.vessel_events;
DROP POLICY IF EXISTS "Allow anon update vessel_events" ON public.vessel_events;
DROP POLICY IF EXISTS "Allow anon delete vessel_events" ON public.vessel_events;

DROP POLICY IF EXISTS "Allow public read candidate_sources" ON public.candidate_sources;
DROP POLICY IF EXISTS "Allow anon insert candidate_sources" ON public.candidate_sources;
DROP POLICY IF EXISTS "Allow public read predicted_paths" ON public.predicted_paths;
DROP POLICY IF EXISTS "Allow anon insert predicted_paths" ON public.predicted_paths;
DROP POLICY IF EXISTS "Allow public read affected_areas" ON public.affected_areas;
DROP POLICY IF EXISTS "Allow anon insert affected_areas" ON public.affected_areas;
DROP POLICY IF EXISTS "Allow public read alerts" ON public.alerts;
DROP POLICY IF EXISTS "Allow anon insert alerts" ON public.alerts;

DROP POLICY IF EXISTS "Allow public select storage" ON storage.objects;
DROP POLICY IF EXISTS "Allow anon insert storage" ON storage.objects;
DROP POLICY IF EXISTS "Allow anon update storage" ON storage.objects;
DROP POLICY IF EXISTS "Allow anon delete storage" ON storage.objects;

-- Incidents Policies
CREATE POLICY "Allow public read incidents" ON public.incidents FOR SELECT USING (true);
CREATE POLICY "Allow anon insert incidents" ON public.incidents FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anon update incidents" ON public.incidents FOR UPDATE USING (true);
CREATE POLICY "Allow anon delete incidents" ON public.incidents FOR DELETE USING (true);

-- Satellite Observations Policies
CREATE POLICY "Allow public read satellite_observations" ON public.satellite_observations FOR SELECT USING (true);
CREATE POLICY "Allow anon insert satellite_observations" ON public.satellite_observations FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anon update satellite_observations" ON public.satellite_observations FOR UPDATE USING (true);
CREATE POLICY "Allow anon delete satellite_observations" ON public.satellite_observations FOR DELETE USING (true);

-- Telemetry Policies
CREATE POLICY "Allow public read weather_observations" ON public.weather_observations FOR SELECT USING (true);
CREATE POLICY "Allow anon insert weather_observations" ON public.weather_observations FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public read ocean_observations" ON public.ocean_observations FOR SELECT USING (true);
CREATE POLICY "Allow anon insert ocean_observations" ON public.ocean_observations FOR INSERT WITH CHECK (true);

-- Vessel Events Policies
CREATE POLICY "Allow public read vessel_events" ON public.vessel_events FOR SELECT USING (true);
CREATE POLICY "Allow anon insert vessel_events" ON public.vessel_events FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anon update vessel_events" ON public.vessel_events FOR UPDATE USING (true);
CREATE POLICY "Allow anon delete vessel_events" ON public.vessel_events FOR DELETE USING (true);

-- Evidence & Risk Tables Policies
CREATE POLICY "Allow public read candidate_sources" ON public.candidate_sources FOR SELECT USING (true);
CREATE POLICY "Allow anon insert candidate_sources" ON public.candidate_sources FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public read predicted_paths" ON public.predicted_paths FOR SELECT USING (true);
CREATE POLICY "Allow anon insert predicted_paths" ON public.predicted_paths FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public read affected_areas" ON public.affected_areas FOR SELECT USING (true);
CREATE POLICY "Allow anon insert affected_areas" ON public.affected_areas FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow public read alerts" ON public.alerts FOR SELECT USING (true);
-- Location Documents RLS Policies
DROP POLICY IF EXISTS "Allow public read location_documents" ON public.location_documents;
DROP POLICY IF EXISTS "Allow anon insert location_documents" ON public.location_documents;
DROP POLICY IF EXISTS "Allow anon update location_documents" ON public.location_documents;

CREATE POLICY "Allow public read location_documents" ON public.location_documents FOR SELECT USING (true);
CREATE POLICY "Allow anon insert location_documents" ON public.location_documents FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow anon update location_documents" ON public.location_documents FOR UPDATE USING (true);

-- Storage Objects Policies for marineguard-evidence bucket
CREATE POLICY "Allow public select storage" ON storage.objects FOR SELECT USING (bucket_id = 'marineguard-evidence');
CREATE POLICY "Allow anon insert storage" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'marineguard-evidence');
CREATE POLICY "Allow anon update storage" ON storage.objects FOR UPDATE USING (bucket_id = 'marineguard-evidence');
CREATE POLICY "Allow anon delete storage" ON storage.objects FOR DELETE USING (bucket_id = 'marineguard-evidence');

