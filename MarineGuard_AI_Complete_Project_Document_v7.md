# MarineGuard AI
## Multi-Source Agentic Marine Pollution Early-Warning, Investigation and Response Intelligence System

**Project Type:** Full-Stack Web + Agentic AI + Generative AI + MCP + RAG + Geospatial Intelligence Project  
**Primary Domain:** Marine Pollution Monitoring  
**Initial Study Area:** Gujarat Coast / Surat–Hazira Coastal Region  
**Hardware Requirement:** None  
**Primary Goal:** Near-real-time marine pollution early warning, investigation, impact assessment, and evidence-grounded reporting

---

# Table of Contents

1. Executive Summary
2. Project Introduction
3. Problem Statement
4. Motivation
5. Project Vision
6. Project Objectives
7. Scope
8. What the System Will and Will Not Do
9. Key Innovation
10. High-Level System Concept
11. System Architecture
12. Data Sources
13. Satellite Data Strategy
14. Near-Real-Time Monitoring Strategy
15. Marine Incident Lifecycle
16. Detection Layer
17. Agentic AI Layer
18. Agent Responsibilities
19. MCP Server Design
20. RAG Knowledge Layer
21. Incident State Management
22. Evidence and Confidence Model
23. Source Investigation
24. Trajectory and Drift Analysis
25. Environmental Impact Analysis
26. Risk and Priority Scoring
27. Alerting and Reporting
28. Database Design
29. API Design
30. Dashboard Design
31. Functional Requirements
32. Non-Functional Requirements
33. Technology Stack
34. Suggested Project Structure
35. End-to-End Workflow
36. Example Incident Scenario
37. Development Roadmap
38. Testing Strategy
39. Evaluation Metrics
40. Security and Safety
41. Limitations
42. Ethical and Legal Considerations
43. Cost Strategy
44. Deployment Strategy
45. Future Enhancements
46. Expected Project Outcomes
47. Final Project Definition
48. References

---

# 1. Executive Summary

MarineGuard AI is a software-based marine pollution intelligence platform designed to detect, investigate, track, and assess possible marine pollution events.

The system combines multiple sources of environmental and geospatial information, including satellite imagery, weather information, wind data, ocean-current data, tide information, vessel movement data, geographic information, citizen reports, historical pollution incidents, and environmental documents.

The project is not intended to behave like a simple image classifier. Instead of only answering **“Is pollution visible in this image?”**, MarineGuard AI aims to answer a complete operational set of questions:

- What unusual event has been detected?
- Where is it located?
- What type of pollution might it represent?
- How confident is the system?
- What evidence supports the conclusion?
- Where could the pollution have originated?
- Are ships, ports, rivers, or other coastal sources nearby?
- Where could the pollution move next?
- Which coastlines or environmentally sensitive regions could be affected?
- How severe is the incident?
- Is the event important enough to generate an alert?

MarineGuard AI uses traditional remote-sensing, machine-learning, geospatial, and mathematical methods for factual processing and calculations. Agentic AI is then used to coordinate the investigation, request additional evidence, compare information from several tools, retrieve relevant historical knowledge, and create an understandable evidence-grounded incident report.

The system is designed to operate without dedicated physical hardware.

---

# 2. Project Introduction

Marine pollution is a complex environmental problem involving many possible pollutant types and many possible sources.

Examples include:

- Oil spills
- Floating plastic and waste
- Industrial discharge
- Coastal dumping
- River-borne waste
- Sediment and turbidity events
- Harmful water-surface anomalies
- Pollution related to shipping activity
- Pollution following extreme rainfall or flooding

Traditional monitoring systems are often specialized. One system may analyze satellite imagery, another may track vessels, another may collect public complaints, and another may provide weather information.

MarineGuard AI attempts to combine these separate information sources into one intelligent investigation workflow.

The project therefore focuses on:

**Detection + Evidence + Investigation + Prediction + Impact + Alerting**

rather than detection alone.

---

# 3. Problem Statement

Marine pollution events are difficult to monitor because:

1. The ocean is large.
2. Pollution may appear only temporarily.
3. Satellite coverage is not continuous.
4. Cloud cover affects optical satellite imagery.
5. Pollution can move after it is released.
6. Different types of pollution require different detection methods.
7. A visible anomaly does not automatically prove pollution.
8. Determining the possible source requires multiple data sources.
9. Environmental impact depends on where the pollution moves.
10. Monitoring systems often operate independently rather than together.

The central problem addressed by MarineGuard AI is:

> How can a software-only Agentic AI system combine satellite observations, environmental data, vessel movement, geographic context, citizen evidence, and historical knowledge to identify and investigate possible marine pollution incidents and provide evidence-grounded early warnings?

---

# 4. Motivation

A basic pollution detector can identify an unusual pattern, but real decision-making requires more information.

```text
Possible marine surface anomaly detected
                    ↓
Where is it?
                    ↓
What evidence supports it?
                    ↓
Is there vessel activity nearby?
                    ↓
What is the wind direction?
                    ↓
What is the ocean-current direction?
                    ↓
Could it move toward the coastline?
                    ↓
Are mangroves, fishing areas, or beaches at risk?
                    ↓
Should an alert be generated?
```

This is a multi-step reasoning problem and naturally fits an Agentic AI architecture because different agents can specialize in different tasks and call different tools.

---

# 5. Project Vision

The long-term vision is to create an intelligent digital assistant for marine pollution monitoring.

The system should continuously observe available environmental data and maintain an evolving understanding of active marine incidents.

```text
Observe
   ↓
Detect
   ↓
Investigate
   ↓
Verify
   ↓
Predict
   ↓
Assess impact
   ↓
Prioritize
   ↓
Explain
   ↓
Alert
   ↓
Continue monitoring
```

The system should update an incident when new evidence becomes available rather than treating every observation as an unrelated event.

---

# 6. Project Objectives

## Primary Objectives

1. Automatically discover new satellite observations for a selected coastal region.
2. Process satellite imagery to identify unusual marine-surface or coastal-water patterns.
3. Create structured marine incident records.
4. Combine evidence from multiple data sources.
5. Use Agentic AI to investigate incidents.
6. Estimate possible pollution origin zones.
7. Estimate possible movement direction.
8. Identify potentially affected coastal areas.
9. Calculate confidence, severity, and priority.
10. Generate evidence-grounded alerts and reports.
11. Capture and return satellite evidence images for detected incidents.
12. Generate annotated incident images and before/after comparisons.
13. Maintain incident history.
14. Continue updating incidents as new evidence arrives.

## Secondary Objectives

- Build a production-style full-stack web interface using Next.js and FastAPI.
- Deploy frontend, backend, database, object storage, and scheduled jobs on purpose-built platforms.
- Demonstrate authentication, maps, API integration, geospatial queries, and deployment workflows.


- Support citizen-submitted observations.
- Support historical incident comparison.
- Provide a visual map-based dashboard.
- Provide an MCP server for marine intelligence tools.
- Use RAG for environmental reports and response procedures.
- Support email notifications.
- Provide explainable results.

---

# 7. Scope

## Initial Geographic Scope

The first implementation should focus on a limited study area:

```text
Gujarat Coast
        ↓
Surat / Hazira coastal region
```

Starting with one region simplifies satellite search, data storage, geographic analysis, model testing, visualization, and evaluation.

## Initial Pollution Classes

Version 1 should avoid trying to classify every marine pollutant.

A practical starting set is:

```text
NORMAL
SURFACE_ANOMALY
OIL_LIKE_ANOMALY
FLOATING_MATERIAL_CANDIDATE
HIGH_TURBIDITY_EVENT
UNKNOWN
```

The word **candidate** is important because the system must separate detection from confirmation.

---

# 8. What the System Will and Will Not Do

## The System Will

- Monitor selected marine/coastal areas.
- Retrieve new environmental data.
- Detect suspicious changes.
- Maintain incident state.
- Combine multiple evidence sources.
- Calculate risk indicators.
- Estimate possible movement.
- Produce evidence-based investigation reports.
- Generate alerts.
- Visualize incidents geographically.
- Return satellite evidence images for incidents.
- Generate annotated images showing detected anomaly regions.
- Generate before/after image comparisons where available.

## The System Will Not

- Guarantee that every detected anomaly is pollution.
- Accuse a ship, company, port, or person of causing pollution.
- Replace environmental authorities.
- Provide legally conclusive source attribution.
- Claim second-by-second satellite monitoring.
- Treat an LLM response as scientific evidence.
- Use AI-generated numbers when deterministic data are available.

---

# 9. Key Innovation

The innovation of MarineGuard AI is not any single detection algorithm. Satellite-based pollution detection, weather systems, vessel tracking, and marine datasets already exist.

The value of the project is the integration and reasoning layer:

```text
Remote Sensing
       +
Geospatial Analysis
       +
Environmental Data
       +
Vessel Activity
       +
Incident Memory
       +
RAG
       +
MCP
       +
Agentic AI
       ↓
Marine Pollution Intelligence
```

Core design principle:

> Scientific and deterministic systems generate evidence. Agentic AI coordinates, investigates, retrieves, and explains that evidence.

---

# 10. High-Level System Concept

```text
                   MARINE ENVIRONMENT
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
 Satellite Imagery     Weather           Vessel Data
       │                  │                  │
       ├──────────────────┼──────────────────┤
       ▼                  ▼                  ▼
 Ocean Currents        GIS Data       Citizen Reports
       │                  │                  │
       └──────────────────┼──────────────────┘
                          ▼
                   Data Ingestion
                          ↓
                   Preprocessing
                          ↓
                  Detection Engine
                          ↓
                    Incident Store
                          ↓
                    Agentic Layer
                          ↓
               Evidence Investigation
                          ↓
                Source / Path Analysis
                          ↓
                  Impact Assessment
                          ↓
                    Risk Scoring
                          ↓
                    Alert Engine
                          ↓
              Dashboard / Email / API
```

---

# 11. System Architecture

MarineGuard AI is designed as a full-stack, multi-service system.

The system separates responsibilities so that each technology is used for a clear engineering purpose.

```text
                      Internet / User
                            │
                            ▼
                    ┌───────────────┐
                    │    Vercel     │
                    │    Next.js    │
                    │  TypeScript   │
                    └───────┬───────┘
                            │ HTTPS / REST
                            ▼
                    ┌───────────────┐
                    │    Render     │
                    │    FastAPI    │
                    │    Python     │
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
          LangGraph        MCP            RAG
            Agents        Server        Retriever
              │             │             │
              └─────────────┼─────────────┘
                            │
                 ┌──────────┴──────────┐
                 ▼                     ▼
             Supabase              Cloudflare R2
          PostgreSQL/PostGIS       Evidence Assets
          Auth + Metadata          Images / Masks
                 ▲
                 │
          GitHub Actions
       Scheduled Monitoring Jobs
                 │
      ┌──────────┼───────────┐
      ▼          ▼           ▼
 Copernicus   Weather       Ocean
 Satellite      Data         Data
```

## Layer 1 — Frontend

Technology:

```text
Next.js
React
TypeScript
Tailwind CSS
```

Responsibilities:

- Dashboard UI
- Incident pages
- Interactive maps
- Authentication flow
- Evidence image display
- Before/after comparison view
- System-health view
- Filters and search
- API consumption
- Responsive web interface

Deployment:

```text
Vercel
```

## Layer 2 — Backend API

Technology:

```text
FastAPI
Python
Pydantic
SQLAlchemy
```

Responsibilities:

- Incident APIs
- Agent execution endpoints
- Risk and confidence calculations
- RAG integration
- MCP integration
- Satellite-processing orchestration
- Database operations
- Evidence metadata
- Alert services

Deployment:

```text
Render
```

Important:

Render is used for request/response backend services.

It is **not** the primary scheduler for the automated monitoring pipeline.

## Layer 3 — Database and Authentication

Technology:

```text
Supabase
PostgreSQL
PostGIS
Supabase Auth
```

Responsibilities:

- Incident persistence
- User accounts
- Alert queue
- System-health state
- Geospatial queries
- Evidence metadata
- Processing history
- Authentication

## Layer 4 — Evidence / Object Storage

Recommended:

```text
Cloudflare R2
```

Responsibilities:

- Cropped satellite images
- Annotated evidence images
- Before/after comparisons
- Masks
- Small GeoTIFF patches
- Other incident-linked assets

## Layer 5 — Scheduled Monitoring

Technology:

```text
GitHub Actions
```

Responsibilities:

- Scheduled source polling
- New-data detection
- Satellite processing
- Environmental-data retrieval
- Deterministic event detection
- Incident creation/update
- Agent retry execution
- Health logging

## Layer 6 — Agentic AI

Technology:

```text
LangGraph
```

Responsibilities:

- Evidence coordination
- Source investigation
- Impact analysis
- Tool selection
- Stateful incident reasoning
- Report generation

## Layer 7 — MCP Tool Layer

Responsibilities:

- Controlled tool access
- Satellite tools
- Weather tools
- Ocean tools
- GIS tools
- Incident tools
- Evidence-image tools

## Layer 8 — RAG Knowledge Layer

Responsibilities:

- Historical reports
- Marine guidelines
- Research papers
- Incident references
- Response procedures

## Layer 9 — Scientific / Geospatial Processing

Responsibilities:

- Raster processing
- Anomaly detection
- Image comparison
- Coordinate calculations
- Risk scoring
- Drift estimation
- Spatial intersections

Core principle:

```text
Frontend presents
Backend orchestrates
Database persists
Object storage stores evidence
GitHub Actions schedules
Scientific code detects
Agents investigate
MCP connects tools
RAG provides knowledge
```


# 12. Data Sources

MarineGuard AI should use a multi-source design. No single source should be treated as sufficient proof.

## Satellite Data
- Copernicus Sentinel-1
- Copernicus Sentinel-2
- Copernicus Sentinel-3
- NASA ocean-observation datasets

## Environmental Data
- Wind direction
- Wind speed
- Rainfall
- Atmospheric conditions
- Tide
- Ocean currents
- Sea-surface information

## Geographic Data
- Coastlines
- Ports
- Rivers
- Drainage outlets
- Industrial coastal areas
- Beaches
- Mangroves
- Protected areas
- Fishing zones
- Settlements

## Vessel Data

Vessel/AIS data are useful but must be treated as **optional in Version 1**.

Commercial AIS APIs are often paid, and some community AIS services require receiver contribution or other access conditions. Because MarineGuard AI is intended to remain software-only and cloud-native, the V1 system must not depend on live AIS access.

When legally and technically available, supported vessel fields may include:
- AIS position
- Vessel identifier
- Vessel type
- Direction
- Speed
- Historical track

Fallback behavior:

```text
If vessel data are available:
    use them as supporting evidence

If vessel data are unavailable:
    continue the investigation without them
    mark vessel evidence as unavailable
```

Recommended V1 alternatives:
- Public shipping-lane geography
- Port locations
- Historical/public vessel datasets
- Generic maritime traffic context

Future versions may integrate commercial or institutional AIS feeds.

## Human Reports
- Citizen report
- Location
- Text description
- Image
- Timestamp

## Historical Data
- Past incidents
- Satellite observations
- Official marine reports
- Environmental studies

---

# 13. Satellite Data Strategy

## Sentinel-1

Sentinel-1 uses Synthetic Aperture Radar (SAR).

Important properties:
- Works during day and night.
- Works through cloud cover.
- Useful for sea-surface analysis.
- Can support detection of oil-like surface anomalies.
- Imaging modes can provide resolution down to approximately 5 m.
- The current Sentinel-1C/1D constellation is configured around a nominal 6-day revisit pattern.

Primary role:

```text
Oil-like anomaly detection
Surface roughness analysis
Cloud-independent verification
```

## Sentinel-2

Sentinel-2 is an optical multispectral mission.

Important properties:
- 13 spectral bands.
- Four bands at 10 m spatial resolution.
- Six bands at 20 m.
- Three bands at 60 m.
- Designed for approximately a 5-day revisit at the equator with the two operational satellites.
- Data are openly available via Copernicus Data Space.

Primary role:

```text
Coastal observation
Water-colour analysis
Floating-material candidates
Turbidity
Multi-date change detection
```

A 10 m pixel does not mean the satellite can detect an individual bottle. Sentinel-2 should be used for sufficiently large patches, accumulations, or spectral anomalies.

## Sentinel-3

Sentinel-3 OLCI is lower resolution but useful for broad ocean monitoring.

Important properties:
- Approximately 300 m full-resolution sampling.
- Near Real Time products can be available in less than three hours after acquisition.

Primary role:

```text
Wide-area ocean monitoring
Early environmental context
Ocean-colour anomalies
Large-scale events
```

---



## Satellite Evidence Image Capture Strategy

A core product feature of MarineGuard AI is the ability to return a visual satellite image in response to a detected incident.

This feature should not be described as taking a new live photo on demand.

Instead, the system should retrieve the latest available relevant satellite observation for the selected area and create an incident-focused evidence image.

The image workflow can include:

```text
Incident coordinates
        ↓
Select latest relevant satellite scene
        ↓
Crop area of interest
        ↓
Render selected bands / SAR view
        ↓
Apply anomaly mask or polygon
        ↓
Add annotations
        ↓
Return final evidence image
```

MarineGuard AI should support three main image outputs:

1. **Raw Satellite Evidence Image**  
   The original or minimally processed image of the area of interest.

2. **Annotated Incident Image**  
   The satellite image with bounding boxes, segmentation masks, or polygons showing the detected anomaly, plus metadata such as confidence and area.

3. **Before / After Comparison Image**  
   A side-by-side comparison between an earlier observation and the latest one for the same location.

Important metadata that must always be displayed with returned images:

- Satellite mission
- Acquisition date/time
- Bounding box or coordinates
- Processing type
- Whether the image is raw, annotated, or comparative

This feature makes the platform visual and evidence-grounded rather than text-only.


# 14. Near-Real-Time Monitoring Strategy

The project should not claim true continuous satellite monitoring.

MarineGuard AI should instead use **scheduled, near-real-time, multi-source monitoring**.

Different sources update at different speeds:

```text
Citizen report        → immediate when submitted
Weather               → minutes / hourly
Vessel data           → optional / source dependent
Ocean information     → source dependent
Sentinel-3            → hours after acquisition
Sentinel-1            → orbital acquisition
Sentinel-2            → orbital acquisition
```

## Serverless Scheduling Model

For the deployed platform, the primary monitoring mechanism should be **GitHub Actions scheduled workflows** rather than an always-on background worker.

```text
GitHub Actions
      ↓
Scheduled run
      ↓
Check for new source data
      ↓
Process only unprocessed observations
      ↓
Update persistent database
      ↓
Save incident-linked evidence assets
      ↓
Trigger agent analysis if required
      ↓
Exit
```

This design is lightweight and scalable because it does not require a permanently running server.

Recommended source-aware polling:

```text
Weather       → every 30–60 minutes
Ocean data    → according to provider update frequency
Satellite     → every few hours or around expected acquisitions
Citizen data  → processed when submitted / next scheduled cycle
RAG           → only during an active investigation
LLM agents    → only after a meaningful event is detected
```

The system should avoid polling satellite sources every few minutes because the upstream satellites themselves do not generate new scenes that frequently.

## Persistent State Requirement

GitHub Actions runners are temporary. Therefore, a local SQLite database created inside the runner must not be treated as deployed persistent storage.

Use:

```text
Local development:
SQLite + local files

Deployed prototype:
Persistent external database
+
Persistent evidence/object storage
```

The dashboard/API may be hosted separately and may sleep between user visits without interrupting the monitoring workflow.

## New Evidence Workflow

```text
Scheduled job starts
      ↓
New Evidence?
   /       \
 NO         YES
 ↓           ↓
Exit      Process
             ↓
       Existing incident?
          /        \
        YES         NO
        ↓            ↓
      Update       Create
        \            /
         \          /
          ↓        ↓
         Re-evaluate
              ↓
          Alert if needed
              ↓
             Exit
```

This keeps the system event-driven without requiring an always-on worker.

---

# 15. Marine Incident Lifecycle

Each marine event should pass through states such as:

```text
DETECTED
   ↓
UNDER_INVESTIGATION
   ↓
POSSIBLE
   ↓
LIKELY
   ↓
HIGH_CONFIDENCE
   ↓
MONITORING
   ↓
RESOLVED / CLOSED
```

A different path may end in:

```text
FALSE_POSITIVE
```

The complete event history should be retained.

---

# 16. Detection Layer

The detection layer should not primarily rely on an LLM.

## V1 Approach: Unsupervised, Not Trained/Fine-Tuned

A labeled, ground-truth marine-pollution dataset for the Gujarat coast does not exist publicly, and pollution events are too rare and too rarely documented to assemble one within a student project's time and $0 budget. **V1 should therefore not attempt to train or fine-tune a supervised segmentation model.**

Instead, V1 uses deterministic and statistical methods that require no labeled training data:

```text
Build a "normal water appearance" baseline
      ↓
   from the AOI's own historical clean scenes
      ↓
Compare each new scene against the baseline
      ↓
Statistical / band-ratio outlier = anomaly candidate
```

Supervised segmentation (fine-tuning a CV model on labeled pollution imagery) moves to Future Enhancements, for if/when a labeled dataset becomes available.

## Per-Pollutant-Class Detection Methods

Because the project targets multiple pollutant types rather than oil spills alone, each class needs its own detection logic — a single generic "spectral analysis" step cannot reliably distinguish an oil sheen from a turbidity plume from a floating-debris patch. The signal each pollutant leaves in satellite data is physically different.

### OIL_LIKE_ANOMALY
```text
Primary:   Sentinel-1 SAR dark-patch detection
           (damped surface roughness under a thin oil film)
Support:   Sentinel-2 sunglint-band response, when the scene
           geometry produces glint over the AOI
Gate:      Only treat a SAR dark patch as an oil-candidate when
           local wind speed is roughly 2-10 m/s at acquisition time.
           Below ~2 m/s, natural slicks/biogenic films look identical
           to oil ("look-alikes"). Above ~10-12 m/s, wave action
           disperses oil enough that it stops being visible in SAR.
           Outside this window, flag as a lower-confidence
           look-alike candidate rather than a standard anomaly.
```

### FLOATING_MATERIAL_CANDIDATE
```text
Primary:   Sentinel-2 optical, NIR/SWIR band-ratio floating-material
           index (floating solids reflect differently from open
           water in the NIR/SWIR range)
Note:      SAR is not useful for this class — floating debris does
           not reliably change surface roughness the way oil does.
```

### HIGH_TURBIDITY_EVENT
```text
Primary:   Sentinel-2 red/NIR band-ratio turbidity index
Note:      SAR is not needed for this class. Turbidity plumes are
           driven by suspended sediment concentration, not surface
           roughness, so they are an optical-only signal.
```

### SURFACE_ANOMALY / UNKNOWN
```text
Primary:   Generic statistical outlier detection against the AOI's
           normal-water baseline (the catch-all for patterns that
           don't cleanly match the three specific classes above)
```

## Multi-Date Change Detection

Compare a satellite image at T1 with an image at T2 and identify changed water regions. This applies across all classes as a secondary confirmation step. Two conditions must hold before a T1/T2 comparison is trusted:

```text
Both scenes must be geometrically co-registered to the same AOI grid.
Both scenes must have acceptable cloud coverage over the AOI itself
(a clear T2 compared against a cloud-obscured T1 is not a valid
comparison and should be skipped, not silently processed).
```

Example structured output:

```json
{
  "incident_id": "MG-2026-0001",
  "observation_type": "satellite",
  "anomaly_type": "oil_like_anomaly",
  "detection_method": "sar_dark_patch",
  "wind_speed_ms": 5.2,
  "latitude": 21.145,
  "longitude": 72.620,
  "estimated_area_km2": 1.8,
  "model_confidence": 0.71,
  "timestamp": "2026-09-25T08:00:00+05:30"
}
```

---

# 17. Agentic AI Layer

The Agentic AI layer receives structured evidence.

Recommended flow:

```text
Raw satellite/environment data
             ↓
Scientific preprocessing
             ↓
Structured detection
             ↓
Agentic investigation
             ↓
Evidence-grounded report
```

LangGraph is suitable because the incident is stateful and may evolve over time.

---

# 18. Agent Responsibilities

The first practical version should use a limited number of agents.

## 18.1 Router / Incident Agent
- Receives a new event.
- Determines which investigation is required.
- Selects appropriate tools.
- Maintains workflow state.

## 18.2 Evidence Agent
- Gathers available evidence.
- Requests weather information.
- Requests ocean conditions.
- Requests vessel information.
- Retrieves related observations.
- Tracks missing information.

## 18.3 Source Investigation Agent
- Estimates possible origin region.
- Investigates nearby vessels.
- Identifies river outlets.
- Identifies ports and industrial zones.
- Compares incident history.

Outputs should use terms such as **candidate source** or **possible source**, not **confirmed polluter**.

## 18.4 Impact and Trajectory Agent
- Uses location, wind, currents, tide, and time.
- Estimates likely movement.
- Intersects movement with coastal GIS information.
- Identifies potentially exposed regions.

## 18.5 Risk and Report Agent
- Interprets deterministic risk results.
- Summarizes evidence.
- Explains why an alert was created.
- Shows uncertainty clearly.
- Generates a human-readable incident report.

---

# 19. MCP Server Design

MarineGuard AI can include a custom MCP server that acts as the controlled interface between agents and tools.

Possible MCP tools:

```text
search_satellite_observations()
get_latest_sentinel1_scene()
get_latest_sentinel2_scene()
get_sentinel3_ocean_product()
get_weather()
get_wind()
get_ocean_current()
get_tide()
get_nearby_ports()
get_nearby_rivers()
get_sensitive_areas()
get_vessel_tracks()
get_previous_incidents()
calculate_distance()
calculate_drift()
get_incident()
update_incident()
create_alert()
generate_incident_report()

get_satellite_evidence_image()

get_annotated_incident_image()

get_before_after_comparison_image()
```

## MCP Reliability and Graceful Degradation

MCP tools should expose structured failure states such as:

```text
source unavailable
quota exhausted
authentication failed
temporary timeout
data not available
```

An unavailable tool must never cause the LLM to invent missing evidence.

If a required tool fails:

```text
store the incident
mark the missing evidence source
continue with available deterministic evidence
retry on the next scheduled cycle
```

## MCP Security

Suggested capability scopes:

```text
satellite.read
weather.read
ocean.read
vessel.read
incident.read
incident.write
alert.write
```

Tools should not receive unrestricted file, shell, or database permissions.

---

# 20. RAG Knowledge Layer

RAG should be used for document knowledge rather than live sensor calculations.

Documents may include:
- Historical oil-spill reports
- Marine pollution research papers
- Coastal-management documents
- Government response guidelines
- Environmental impact studies
- Previous incident reports
- Port pollution procedures
- Marine ecosystem documents

RAG flow:

```text
Documents
   ↓
Text extraction
   ↓
Cleaning
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector Database
   ↓
Retriever
   ↓
Relevant evidence
   ↓
Agent
```

Possible questions:

```text
Have similar incidents occurred near this region?
Which sensitive ecosystems are documented nearby?
What response procedure is recommended for this type of event?
What historical pollution sources are known in this region?
```

---

# 21. Incident State Management

A core concept of MarineGuard AI is persistent incident state.

```python
from typing import TypedDict, List, Dict, Optional

class MarineIncidentState(TypedDict):
    incident_id: str
    latitude: float
    longitude: float
    first_detected: str
    last_updated: str
    anomaly_type: str
    satellite_evidence: List[Dict]
    weather_evidence: List[Dict]
    ocean_evidence: List[Dict]
    vessel_evidence: List[Dict]
    citizen_reports: List[Dict]
    possible_sources: List[Dict]
    predicted_path: List[Dict]
    affected_areas: List[Dict]
    confidence_score: float
    severity_score: float
    priority_score: float
    status: str
    report: Optional[str]
```

Example evolution:

```text
08:00 Satellite anomaly      Confidence = 0.42
09:00 Weather evidence       Confidence = 0.48
10:15 Citizen report         Confidence = 0.62
12:30 Additional imagery     Confidence = 0.79
```

The same incident is updated rather than recreated.

## Incident Merge Rule

"Same incident" must be decided by an explicit rule, not left implicit — this rule is what the Section 39 "correct event merging" and "duplicate incident rate" metrics are measured against.

```text
A new detection merges into an existing open incident when ALL of:

  same anomaly_type (or SURFACE_ANOMALY/UNKNOWN matching any class)
  within 5 km of the existing incident's current known location
  within 48 hours of the existing incident's last_updated time
  existing incident status is not RESOLVED/CLOSED/FALSE_POSITIVE

Otherwise: create a new incident.
```

The 5 km / 48-hour values are initial project defaults and should be tuned once real observations are available — but a default must exist from the start, or merge behavior is undefined and untestable.

### "Current known location" must be kept up to date

A pollutant can legitimately drift several km over 48 hours (Section 24), so the incident's `latitude`/`longitude` in Section 28 must be **updated every time new evidence arrives**, not left frozen at the first-detection point. The merge check above always compares against the incident's most recently known position (its latest observation, or its latest Section 24 predicted position if more recent evidence hasn't arrived yet) — never against the original detection point. Matching against a stale, original position would let a real ongoing incident drift outside the 5 km radius and incorrectly split into a duplicate, which is precisely what this rule exists to prevent.

---

# 22. Evidence and Confidence Model

Confidence should not be generated only from an LLM.

An initial deterministic evidence model could use:

```text
Satellite evidence      0–30 points
Second-source evidence  0–20 points
Citizen evidence        0–10 points
Vessel/context match    0–15 points
Environmental match     0–15 points
Historical consistency  0–10 points
```

Total: 0–100.

Initial project thresholds:

```text
0–29   → LOW
30–49  → MODERATE
50–74  → HIGH
75–100 → VERY HIGH
```

These thresholds must later be calibrated with validation data.

---

# 23. Source Investigation

Source investigation should produce candidate origins, not accusations.

```text
Current anomaly location
        ↓
Reverse drift estimation
        ↓
Probable previous region
        ↓
Search nearby:
   • vessel tracks
   • river outlets
   • ports
   • industrial coastline
   • previous incidents
        ↓
Candidate source list
```

Example:

```json
{
  "candidate_sources": [
    {
      "type": "vessel_activity",
      "distance_km": 2.3,
      "confidence": "moderate"
    },
    {
      "type": "river_outlet",
      "distance_km": 8.7,
      "confidence": "low"
    }
  ]
}
```

---

# 24. Trajectory and Drift Analysis

An initial student version does not need a complex oceanographic simulator.

A simplified model can use:
- Current direction
- Current speed
- Wind direction
- Wind speed
- Time interval

Conceptually:

```text
Current component
        +
Wind influence (scaled by a pollutant-specific windage factor)
        ↓
Estimated movement vector
```

## Windage Factor Is Pollutant-Specific

A single wind-drift coefficient across all pollutant types will misestimate at least some of them, because how much an object is pushed by wind versus current depends on how much of it sits above versus below the water surface.

```text
OIL_LIKE_ANOMALY
    Thin surface film, mostly in-water.
    Approx. movement ≈ 100% of current + ~3% of wind speed,
    deflected roughly 10-20° from wind direction.

FLOATING_MATERIAL_CANDIDATE
    Solid debris, partially emergent above the surface.
    Windage factor is higher and more variable than oil
    (commonly cited in a wider ~2-6%+ range depending on
    object size/buoyancy) — treat predicted paths for this
    class as lower-confidence than for OIL_LIKE_ANOMALY.

HIGH_TURBIDITY_EVENT
    Suspended sediment plume, dominated by current and
    dispersion rather than wind. Wind term should be
    weighted near zero for this class.
```

These are initial project approximations, not validated coefficients — they should be clearly labeled as such in any report shown to a user (see Section 27's "candidate/possible" language convention), and calibrated later if real drift observations become available.

Example path:

```json
[
  {"time": "+3h", "latitude": 21.160, "longitude": 72.640},
  {"time": "+6h", "latitude": 21.175, "longitude": 72.660}
]
```

Later versions can use scientific particle-tracking models.

---

# 25. Environmental Impact Analysis

The predicted path should be compared with GIS layers.

Potentially affected assets:
- Coastline
- Mangroves
- Wetlands
- Beaches
- Fishing areas
- Ports
- Coastal villages
- Protected marine areas

Example:

```text
Predicted pollution path
          ↓
Spatial intersection
          ↓
Mangrove region within 4 km
          ↓
Impact risk increases
```

---

# 26. Risk and Priority Scoring

A deterministic risk score can combine:
- Detection confidence
- Pollution severity
- Estimated area
- Distance to coastline
- Environmental sensitivity
- Trajectory direction
- Human/economic exposure

## Normalization Rule

Every component below must be normalized to the same **0-1** scale before combination. `confidence_score` from Section 22 is produced on a 0-100 scale, so it must be divided by 100 first. Mixing a 0-100 term with 0-1 terms in the same weighted sum would let that one term dominate the score regardless of the others — the formula below assumes all five inputs are already 0-1.

## Component Definitions

These four inputs must be computed, not left implicit, or the formula below cannot actually run:

```text
confidence_score_norm   = confidence_score (Section 22) / 100

severity_score           = normalized 0-1 estimate of pollutant
                            severity, derived from anomaly_type and
                            estimated_area_km2 (e.g., a simple
                            starting rule: OIL_LIKE_ANOMALY and
                            HIGH_TURBIDITY_EVENT start from a higher
                            base severity than FLOATING_MATERIAL_
                            CANDIDATE at the same area; scale up with
                            estimated_area_km2 toward a project-
                            defined maximum)

coastal_impact_score     = 1 - (distance_to_coast_km / max_relevant_
                            distance_km), clipped to [0, 1]
                            (closer to coast = higher score)

ecosystem_score          = 1 if predicted path intersects a
                            protected/sensitive GIS layer (Section 25)
                            within the projection window, scaled down
                            toward 0 with distance from the nearest
                            sensitive area otherwise

human_exposure_score     = normalized 0-1 estimate based on
                            proximity to ports, fishing zones, and
                            coastal settlements from GIS data
```

These are initial project-defined rules, explicitly meant to be replaced with better-calibrated versions once real incidents are available — but a first version must exist for the formula to be implementable at all.

## Formula

```python
priority_score = (
    confidence_score_norm * 0.25
    + severity_score * 0.25
    + coastal_impact_score * 0.20
    + ecosystem_score * 0.20
    + human_exposure_score * 0.10
)
# priority_score is 0-1
```

This is only an initial project formula and should later be validated.

Possible levels (on the normalized 0-1 scale):

```text
0.00-0.29  → LOW
0.30-0.49  → MODERATE
0.50-0.74  → HIGH
0.75-1.00  → CRITICAL
```

---

# 27. Alerting and Reporting

The system should avoid alert fatigue.

Example (using the 0-1 `priority_score` scale from Section 26):

```text
< 0.30            → Store only
0.30 - 0.59       → Dashboard notification
0.60 - 0.79       → Email alert
0.80+             → High-priority alert
```

Example report:

```text
MARINEGUARD AI — INCIDENT ALERT

Incident: MG-2026-0001
Location: Hazira coastal region
Status: Under Investigation
Detected: 25 September 2026, 08:00 IST
Event: Oil-like marine surface anomaly candidate
Confidence: High
Estimated affected area: 1.8 km²
Current movement: Toward northeast
Potential coastal exposure: Moderate

Evidence:
• Sentinel observation
• Wind data
• Ocean-current data
• Nearby vessel activity

Important:
Identified vessels and locations are candidates for investigation only.
The system does not establish responsibility.

Recommended next step:
Additional observation and official verification.
```

---

# 28. Database Design

Local-development database:

```text
SQLite
```

Deployed-prototype / production database:

```text
PostgreSQL + PostGIS
```

Important: GitHub Actions runners are temporary. SQLite should therefore be used only for local development and testing. A deployed monitoring job must write incident state to persistent external storage.

Recommended tables:

## incidents
```text
id
incident_code
anomaly_type
latitude
longitude
first_detected
last_updated
confidence_score
severity_score
priority_score
status
created_at
updated_at
```

## satellite_observations
```text
id
incident_id
mission
product_id
acquisition_time
cloud_cover
image_path
model_result
detection_method
wind_speed_ms
confidence
created_at
```

`detection_method` records which Section 16 technique produced this observation (e.g. `sar_dark_patch`, `floating_debris_index`, `turbidity_index`, `statistical_outlier`). `wind_speed_ms` is nullable and only populated for `OIL_LIKE_ANOMALY` detections, where it records the wind speed used to evaluate the SAR wind-gate. Storing both is required to audit why a detection was classified as it was, and to break the Section 39 evaluation metrics out per class rather than as one blended number.

## processed_source_items
```text
id
source_name
source_item_id
acquisition_time
processed
processed_at
checksum
```

Purpose: prevent the same satellite product or external source item from being downloaded and processed repeatedly.

Example rule:

```text
if source_item_id already exists and processed = true:
    skip
```

## weather_observations
```text
id
incident_id
timestamp
wind_speed
wind_direction
rainfall
source
```

## ocean_observations
```text
id
incident_id
timestamp
current_speed
current_direction
tide
sea_surface_temperature
source
```

## vessel_events
```text
id
incident_id
vessel_identifier
timestamp
latitude
longitude
speed
direction
distance_from_incident
```

## citizen_reports
```text
id
incident_id
description
latitude
longitude
image_path
submitted_at
verification_status
```

## candidate_sources
```text
id
incident_id
source_type
reference
confidence
evidence_json
created_at
```

## predicted_paths
```text
id
incident_id
forecast_time
latitude
longitude
uncertainty
```

## affected_areas
```text
id
incident_id
area_type
area_name
distance_km
risk_level
```

## alerts
```text
id
incident_id
alert_type
recipient
status
sent_at
```

---

# 29. API Design

FastAPI can expose the backend. Every route is labeled with its required access level so the security model is explicit rather than implied, and maps directly onto FastAPI dependency functions during implementation.

```text
PUBLIC
GET  /health
POST /citizen-reports

AUTHENTICATED
GET  /incidents
GET  /incidents/{incident_id}
GET  /incidents/{incident_id}/evidence
GET  /incidents/{incident_id}/trajectory
GET  /incidents/{incident_id}/sources
GET  /incidents/{incident_id}/impact

ADMIN
POST /incidents/{incident_id}/reanalyze
GET  /admin/jobs
GET  /admin/errors
POST /admin/test-alert

SYSTEM / ADMIN
POST /monitor/run
```

`PUBLIC` routes require no token. `AUTHENTICATED` routes require a valid Supabase-issued access token. `ADMIN` and `SYSTEM / ADMIN` routes require a valid token *and* an admin role/claim, and should additionally be rate-limited — see Section 40 (Web / API Security) for how each level is enforced.

---

# 30. Frontend and Dashboard Design

The final frontend should use:

```text
Next.js
React
TypeScript
Tailwind CSS
```

Deployment:

```text
Vercel
```

Streamlit may still be used during early prototyping, but the final portfolio version should use Next.js to demonstrate full-stack web-development skills.

## Suggested Routes

```text
/
 /dashboard
 /incidents
 /incidents/[incidentId]
 /map
 /evidence
 /system-health
 /login
```

## Dashboard

Display:

- Active incidents
- High-priority incidents
- Latest satellite update
- Monitored region
- System health
- Latest alerts
- Evidence availability

## Interactive Map

Display:

```text
Detected anomaly
Predicted path
Candidate source region
Affected coastline
Sensitive ecosystem
```

Possible map technologies:

```text
Leaflet
React Leaflet
Mapbox-compatible library
```

## Incident Detail Page

Show:

```text
Incident summary
Risk level
Confidence
Evidence timeline
Satellite image
Annotated evidence image
Before/after comparison
Interactive map
Predicted movement
Candidate sources
Potential impacts
Agent report
Source availability
```

## Example Page Layout

```text
┌──────────────────────────────────────────────┐
│ MarineGuard AI                              │
├──────────────────────────────────────────────┤
│ Incident MG-2026-001                        │
│                                              │
│ Risk: HIGH                                  │
│ Confidence: 78%                             │
│                                              │
│ ┌────────────────────────────────────────┐  │
│ │            Interactive Map             │  │
│ │                                        │  │
│ │        Detected Anomaly                │  │
│ │                  ↗ predicted path      │  │
│ └────────────────────────────────────────┘  │
│                                              │
│ Satellite Evidence                          │
│ [Before]              [Current]              │
│                                              │
│ Agent Investigation                         │
│ Evidence-grounded incident analysis         │
│                                              │
│ Evidence                                    │
│ ✓ Satellite                                 │
│ ✓ Weather                                   │
│ ✓ Ocean current                             │
│ ⚠ Vessel data unavailable                   │
└──────────────────────────────────────────────┘
```

## Web Development Skills Demonstrated

The frontend should demonstrate:

- React components
- TypeScript
- Routing
- REST API integration
- Authentication
- Maps
- Image rendering
- Loading states
- Error states
- Filtering
- Pagination
- Responsive design
- Environment variables
- Deployment workflows
- API caching where appropriate


# 31. Functional Requirements

The system shall:

1. Define one or more monitored geographic regions.
2. Search for new satellite observations.
3. Download or process selected scenes.
4. Run anomaly-detection logic.
5. Create structured incidents.
6. Store incident history.
7. Retrieve weather information.
8. Retrieve ocean information where available.
9. Query optional vessel information where available.
10. Query geographic features.
11. Run Agentic AI investigation.
12. Calculate confidence.
13. Calculate risk.
14. Estimate movement.
15. Identify potentially affected areas.
16. Generate reports.
17. Capture and store satellite evidence images.
18. Generate annotated incident images.
19. Generate before/after comparison images where possible.
20. Send alerts.
21. Provide authenticated web access.
22. Display incidents through a Next.js dashboard.
23. Display interactive maps.
24. Display evidence images.
25. Display system-health information.
26. Support REST API communication between frontend and backend.
27. Re-evaluate incidents when new evidence arrives.
28. Store logs and errors.
29. Maintain alert retry state.
30. Track scheduler health.


# 32. Non-Functional Requirements

## Reliability
Continue operating if one external source is temporarily unavailable.

## Explainability
Every important conclusion should show supporting evidence.

## Traceability
Every incident update should be timestamped.

## Modularity
Satellite, weather, vessel, and AI services should be replaceable.

## Security
Secrets should never be hard-coded.

## Cost Efficiency
LLMs should run only after deterministic filtering identifies a meaningful event.

## Scalability
The architecture should allow the monitored region to expand later.

## Maintainability
Agents and tools should have clearly separated responsibilities.

---

# 33. Technology Stack

## Frontend

```text
Next.js
React
TypeScript
Tailwind CSS
React Leaflet / equivalent map library
```

Deployment:

```text
Vercel
```

## Backend

```text
Python
FastAPI
Pydantic
SQLAlchemy
HTTPX / Requests
```

Deployment:

```text
Render
```

## Agentic AI

```text
LangGraph
LangChain
Gemini-compatible LLM
Groq-compatible fallback if required
```

## MCP

```text
Model Context Protocol Python SDK
Custom Marine Intelligence MCP Server
```

## RAG

```text
Document loaders
Chunking pipeline
Embedding model
FAISS / Chroma for local development
Versioned prebuilt vector index for deployed prototype
```

For a static marine-reference corpus, the vector index should be built offline and reused rather than regenerated during every scheduled job.

Recommended deployed-prototype strategy:

```text
Marine documents
      ↓
Build embeddings locally
      ↓
Create FAISS index
      ↓
Version index
      ↓
Store as GitHub Release asset
      ↓
Scheduled job downloads/reuses it
```

Rebuild only when:

- documents change
- embedding model changes
- chunking strategy changes

## Database

```text
Supabase PostgreSQL
PostGIS
Supabase Auth
```

Local development:

```text
SQLite
```

## Object Storage

Recommended:

```text
Cloudflare R2
```

Purpose:

- Satellite evidence images
- Annotated images
- Before/after comparisons
- Masks
- Small GeoTIFF patches

## Satellite / Geospatial

```text
Rasterio
GeoPandas
Shapely
PyProj
Pystac Client
NumPy
OpenCV
Pillow
```

## Machine Learning

Initial:

```text
scikit-learn
OpenCV
```

Advanced:

```text
PyTorch
```

## Scheduling

Primary deployed-prototype scheduler:

```text
GitHub Actions
```

Local alternatives:

```text
APScheduler
Cron
```

## Email

Initial:

```text
Gmail SMTP / Gmail API
```

Later alternatives:

```text
Resend
SendGrid
AWS SES
```

## Version Control / CI

```text
GitHub
GitHub Actions
```


# 34. Suggested Project Structure

```text
marineguard-ai/
│
├── README.md
├── .gitignore
│
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tsconfig.json
│   ├── app/
│   │   ├── page.tsx
│   │   ├── dashboard/
│   │   ├── incidents/
│   │   │   └── [incidentId]/
│   │   ├── map/
│   │   ├── evidence/
│   │   ├── system-health/
│   │   └── login/
│   ├── components/
│   │   ├── IncidentCard.tsx
│   │   ├── IncidentMap.tsx
│   │   ├── EvidenceViewer.tsx
│   │   ├── RiskBadge.tsx
│   │   └── SystemHealth.tsx
│   ├── lib/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── types.ts
│   └── public/
│
├── backend/
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── api/
│   │   │   ├── incidents.py
│   │   │   ├── citizen_reports.py
│   │   │   ├── monitoring.py
│   │   │   └── health.py
│   │   ├── models/
│   │   │   ├── incident.py
│   │   │   ├── evidence.py
│   │   │   ├── satellite.py
│   │   │   └── alert.py
│   │   ├── satellite/
│   │   │   ├── catalog.py
│   │   │   ├── sentinel1.py
│   │   │   ├── sentinel2.py
│   │   │   ├── sentinel3.py
│   │   │   ├── preprocessing.py
│   │   │   ├── anomaly_detector.py
│   │   │   ├── image_capture.py
│   │   │   └── image_annotation.py
│   │   ├── environmental/
│   │   │   ├── weather.py
│   │   │   ├── ocean.py
│   │   │   ├── tide.py
│   │   │   └── gis.py
│   │   ├── agents/
│   │   │   ├── state.py
│   │   │   ├── graph.py
│   │   │   ├── router_agent.py
│   │   │   ├── evidence_agent.py
│   │   │   ├── source_agent.py
│   │   │   ├── impact_agent.py
│   │   │   └── report_agent.py
│   │   ├── mcp/
│   │   │   ├── server.py
│   │   │   └── tools/
│   │   ├── rag/
│   │   │   ├── ingest.py
│   │   │   ├── retriever.py
│   │   │   └── vector_store.py
│   │   ├── services/
│   │   │   ├── confidence.py
│   │   │   ├── risk.py
│   │   │   ├── trajectory.py
│   │   │   ├── storage_service.py
│   │   │   ├── email_service.py
│   │   │   └── report_service.py
│   │   └── prompts/
│   │       ├── evidence_prompt.py
│   │       ├── source_prompt.py
│   │       └── report_prompt.py
│   │
│   └── tests/
│
├── workflows/
│   └── monitor.yml
│
├── rag-assets/
│   ├── manifest.json
│   └── README.md
│
├── scripts/
│   ├── build_rag_index.py
│   ├── download_sample_scene.py
│   ├── process_scene.py
│   └── seed_demo_incident.py
│
└── docs/
    └── architecture/
```

Deployment mapping:

```text
frontend/   → Vercel
backend/    → Render
database    → Supabase
evidence    → Cloudflare R2
workflows   → GitHub Actions
RAG index   → GitHub Release asset
```


# 35. End-to-End Workflow

```text
START
  ↓
Scheduler checks external sources
  ↓
New satellite/environment data?
  ↓
Preprocess data
  ↓
Run anomaly detection
  ↓
Candidate anomaly?
 ┌────────────┐
 │            │
NO           YES
 │            │
END           ↓
        Create / update incident
               ↓
         Evidence Agent
               ↓
      Collect supporting data
               ↓
        Source Agent
               ↓
       Candidate origins
               ↓
      Impact/Trajectory Agent
               ↓
       Calculate affected areas
               ↓
     Deterministic confidence/risk
               ↓
          Report Agent
               ↓
          Priority high?
          /           \
        NO             YES
        ↓               ↓
      Store          Send alert
        ↓               ↓
       END             END
```

---

# 36. Example Incident Scenario

## Stage 1 — Initial Observation

A new satellite observation contains a suspicious sea-surface pattern near the Hazira coast.

```text
Anomaly type: Surface anomaly
Area: 1.8 km²
Initial confidence: 42%
```

Incident created: `MG-2026-0001`.

## Stage 2 — Environmental Context

The Evidence Agent requests wind, ocean current, nearby vessel activity, and sensitive areas.

The system finds the current is moving toward the northeast and the coastline is within the projected path.

Confidence becomes 51%.

## Stage 3 — Additional Evidence

A later observation supports the anomaly.

Confidence becomes 73%.

## Stage 4 — Source Investigation

Backward movement estimation identifies a possible previous location. Vessel data show two vessels passed near that region.

The system stores them as **candidate vessel tracks** and does not claim responsibility.

## Stage 5 — Impact

The predicted movement approaches a sensitive coastal region, so risk rises.

## Stage 6 — Alert

MarineGuard AI sends an incident report because both confidence and impact exceed the configured thresholds.

---

# 37. Development Roadmap

## Phase 1 — Study Area and Satellite Access
- Create Copernicus Data Space account.
- Select Gujarat study area.
- Search Sentinel-2 scenes.
- Download/sample scenes.
- Read GeoTIFF data.
- Display bands.
- Understand coordinates.

**Deliverable:** Satellite exploration notebook.

## Phase 2 — Historical Change Detection
- Select two observations.
- Crop the same geographic region.
- Normalize.
- Mask land/cloud where required.
- Identify changed regions.

**Deliverable:** Change detection pipeline.

## Phase 3 — Candidate Anomaly Detector
- Define anomaly classes.
- Implement baseline CV/ML detector.
- Produce location, area, confidence.
- Save results.

**Deliverable:** `anomaly_detector.py`.

## Phase 4 — Incident Database
- Create database schema.
- Save observations.
- Create incidents.
- Update incidents.
- Store event timeline.
- Track processed source/product IDs to prevent duplicate processing.

**Deliverable:** Persistent incident and processing-state layer.

## Phase 5 — Satellite Evidence Image Capture
- Retrieve the latest usable satellite observation.
- Crop the incident area of interest.
- Render true-colour or selected-band output.
- Save raw evidence image.
- Overlay anomaly mask / polygon.
- Generate annotated evidence image.
- Generate before/after comparison image where available.
- Save image metadata.
- Expose image endpoints to the API/dashboard.

**Deliverable:** Image capture and annotation pipeline.

## Phase 6 — Environmental Context
- Weather integration.
- Wind integration.
- Ocean/current integration.
- GIS coastline data.
- Define provider-specific update schedules.

## Phase 7 — Basic Trajectory
- Vector calculation.
- Multi-hour projected path.
- Map visualization.

## Phase 8 — MCP Server
Expose tools such as:

```text
get_weather
get_ocean_current
get_incident
get_satellite_observation
get_satellite_evidence_image
get_sensitive_areas
calculate_drift
```

Also implement structured tool errors, missing-data states, quota states, and retry-safe behavior.

## Phase 9 — LangGraph Agents
Add:

```text
Evidence Agent
Source Agent
Impact Agent
Report Agent
```

Agents must consume structured evidence and never invent unavailable data.

## Phase 10 — RAG
- Gather marine documents.
- Ingest.
- Chunk.
- Embed.
- Retrieve.
- Integrate with agents.

## Phase 11 — Dashboard
- Map.
- Incident list.
- Evidence images.
- Timeline.
- Risk.
- Trajectory.
- Source availability status.

## Phase 12 — Alerts
- Email.
- Priority threshold.
- Duplicate-alert prevention.
- Alert retry state.

## Phase 13 — Scheduled Near-Real-Time Automation
- GitHub Actions scheduled workflows.
- Source-aware schedules.
- New-data detection.
- Persistent external database updates.
- Quota-aware retries.
- Exponential backoff.
- Health logging.
- Agent retry on later cycles.

The dashboard/API may be hosted separately and may sleep between user visits without interrupting monitoring.

---

# 38. Testing Strategy

## Unit Tests
- Coordinate calculations
- Risk calculations
- Confidence calculations
- Distance
- Trajectory
- Data parsers
- API adapters

## Satellite Tests
- Scene retrieval
- Missing bands
- Cloudy images
- Corrupt images
- Coordinate alignment
- Same-region cropping

## Agent Tests
- Missing weather data
- Missing vessel data
- Conflicting evidence
- Low-confidence detection
- High-confidence detection
- Unknown anomaly
- False positive

## Incident Logic Tests
- Merge rule: same class, within 5 km / 48 hr → merges into existing incident
- Merge rule: same class, outside 5 km or 48 hr → creates a new incident
- Merge rule: candidate incident is RESOLVED/CLOSED/FALSE_POSITIVE → creates a new incident, does not merge
- Incident `latitude`/`longitude` updates to the current known location when new evidence arrives
- SAR wind-gate: wind speed inside 2-10 m/s → standard-confidence oil candidate
- SAR wind-gate: wind speed outside 2-10 m/s → lower-confidence look-alike candidate, not a standard anomaly
- Class routing: a turbidity-index signal is not passed through SAR oil-detection logic, and vice versa

## Integration Tests

```text
Satellite
→ detection
→ incident
→ agent
→ alert
```

## Failure Tests

Simulate:
- API timeout
- Satellite source unavailable
- Copernicus quota/rate-limit response
- LLM unavailable
- LLM daily/rate quota exhausted
- Vessel data unavailable
- Database unavailable
- Persistent evidence storage unavailable
- Email failure
- Email quota exceeded
- Frontend API unavailable
- Backend cold start
- Supabase unavailable
- Object storage unavailable
- RAG index unavailable

The system should degrade safely rather than invent information.

Quota-exhaustion rule:

```text
If LLM quota is exhausted:
    keep incident status = UNDER_INVESTIGATION
    store all deterministic evidence
    retry the AI investigation on the next scheduled cycle
```

No incident should be dropped because an LLM provider is temporarily unavailable.

---

# 39. Evaluation Metrics

## Ground-Truth Strategy (V1)

No labeled marine-pollution dataset exists for the Gujarat coast, so formal precision/recall against real labeled incidents is not achievable in V1. Detection metrics below should instead be measured with:

```text
Synthetic injection:
    Artificially alter pixel values in a known-clean scene to
    simulate each pollutant class's expected signature (e.g., a
    darkened patch for oil-like SAR, an altered band ratio for
    turbidity), then check whether the detector flags it.

Manual visual review:
    A human reviews flagged incidents against the source imagery
    and marks each as a reasonable candidate or a clear miss.
```

This is an honest, achievable V1 evaluation approach, not a substitute for real validation once genuine incidents accumulate over time.

## Detection Metrics

Measured **per pollutant class** (Section 16), not as one combined number — an oil-like detector's realistic precision/recall looks very different from a turbidity detector's, and averaging them together would hide which class actually needs work.

```text
Per class (OIL_LIKE_ANOMALY, FLOATING_MATERIAL_CANDIDATE,
           HIGH_TURBIDITY_EVENT, SURFACE_ANOMALY/UNKNOWN):
    Precision (on synthetic/reviewed cases)
    Recall (on synthetic/reviewed cases)
    F1 score
    False-positive rate
```

IoU for segmentation is deferred to whichever future version introduces supervised segmentation (Section 16).

## Incident Metrics
- Correct event merging (evaluated against the Section 21 merge rule)
- Duplicate incident rate
- Time to incident creation

## Agent Metrics
- Tool-call success rate
- Unsupported claim rate
- Source completeness
- Structured-output validity

## Alert Metrics
- Useful-alert rate
- False alert rate
- Duplicate alert rate
- Alert latency

## System Metrics
- API success rate
- Job success rate
- Average processing time
- LLM calls per incident
- Cost per incident

---

# 40. Security and Safety

## Secret Management
Use environment variables. Never commit API keys, database passwords, email credentials, or OAuth tokens.

## Web / API Security

Adding a Next.js frontend and a separately hosted FastAPI backend introduces a browser-facing attack surface that the original software-only design did not have. This must be handled explicitly.

### Cross-Origin Requests (CORS)

Vercel (frontend) and Render (backend) are different origins. FastAPI must run `CORSMiddleware` restricted to the known, explicit Vercel deployment URL(s) — not a wildcard `*` — so only the intended frontend can call the API from a browser.

### Token Verification (Backend, Independent of the Frontend)

Supabase Auth issuing a session to the Next.js frontend is **not** sufficient on its own. Login state in the browser proves nothing to the backend by itself; the backend must independently verify every incoming request.

```text
Request arrives with Authorization: Bearer <token>
        ↓
Backend fetches Supabase project's JWKS (cached, refreshed periodically)
        ↓
Backend verifies token signature + expiry against the JWKS
        ↓
Valid  → extract user id / role claim, proceed
Invalid / expired / missing → reject with 401
```

The backend must not trust a decoded token's contents without verifying its signature against Supabase's JWKS endpoint first — a token cannot be treated as valid simply because it decodes into a plausible-looking payload.

### Endpoint Access Levels

Every route in Section 29 is labeled `PUBLIC`, `AUTHENTICATED`, `ADMIN`, or `SYSTEM / ADMIN`. This is enforced with layered FastAPI dependencies, not left to convention:

```text
PUBLIC            → no dependency
AUTHENTICATED     → require_user  (valid JWT)
ADMIN             → require_user + require_admin_role
SYSTEM / ADMIN     → require_user + require_admin_role + rate limit
```

This matters beyond access control: `POST /monitor/run` and `POST /incidents/{incident_id}/reanalyze` trigger LLM calls and satellite processing. If left open, repeated anonymous calls would burn through LLM and Copernicus API quotas specified in Section 43. Locking these routes down protects system resources, not just the data.

### Rate Limiting

`SYSTEM / ADMIN` and `ADMIN` routes should be rate-limited per user/IP even when authenticated, so a single compromised or misbehaving client cannot exhaust shared API quotas on its own.

## Tool Authorization
Agents should access only required MCP tools.

## Data Validation
All external API responses must be validated.

## Output Guardrails
The report agent should follow rules such as:

```text
Use only provided evidence.
Do not invent measurements.
Do not identify a party as responsible without verified evidence.
Clearly distinguish observation, inference, and uncertainty.
State when data are unavailable.
```

---

# 41. Limitations

## Satellite Revisit
Sentinel satellites do not provide continuous video.

## Cloud Cover
Optical imagery can be obscured by clouds.

## Spatial Resolution
Small pollution objects may not be visible.

## False Positives
Natural phenomena may resemble pollution, including low-wind areas, biological films, sediment, algal events, sun glint, and natural water-colour differences.

## Source Attribution
Finding nearby ships or industrial locations does not prove responsibility.

## Trajectory Accuracy
A simplified drift model is an estimate.

## Open Data Availability
Some useful vessel or high-resolution commercial data may not be freely available.

## AIS / Vessel Data Availability
Live and historical AIS data may require paid services or contribution-based access. MarineGuard AI V1 must therefore treat vessel data as optional and continue functioning when it is unavailable.

## API and LLM Quotas
Satellite-processing APIs and LLM services have usage limits. The system must use caching, deduplication, backoff, and delayed retries rather than assuming unlimited access.

---

# 42. Ethical and Legal Considerations

The system should distinguish:

```text
Observed fact
vs
Calculated estimate
vs
AI inference
```

Example:

```text
Observed:
A radar anomaly exists.

Calculated:
Backward drift points southwest.

Context:
A vessel passed through the candidate area.

Correct conclusion:
The vessel is a candidate for further investigation.

Incorrect conclusion:
The vessel caused the spill.
```

The system supports decision-making; it does not replace authorized investigations.

---

# 43. Resource & Cost Optimization Strategy

MarineGuard AI is designed as an **optimized, cloud-efficient platform**, utilizing open-access satellite data streams and scalable serverless compute.

## Hardware

Required:

```text
None
```

## Recommended Production Cloud Stack

```text
Frontend:
Vercel

Backend:
Render

Database/Auth:
Supabase

Evidence Storage:
Cloudflare R2

Scheduler:
GitHub Actions

RAG Index:
GitHub Release asset

LLM:
Gemini / Groq LLM Services
```

## Cost-Control Principles

1. Do not use an always-on worker for monitoring.
2. Run scheduled jobs through GitHub Actions.
3. Do not invoke LLMs for every polling cycle.
4. Do not store full satellite scenes unless required.
5. Keep only incident-linked evidence assets.
6. Reuse a prebuilt RAG index.
7. Cache source metadata.
8. Never reprocess the same source product unnecessarily.
9. Treat paid AIS as optional.
10. Keep the dashboard/API independent from monitoring.

## Monitoring Cost Control

```text
Raw source data
      ↓
Deterministic filter
      ↓
Meaningful anomaly?
     /        \
   NO          YES
   ↓            ↓
 Exit       Agentic AI
```

## Persistent State

Local development:

```text
SQLite
Local files
```

Deployed prototype:

```text
Supabase PostgreSQL
Cloudflare R2
```

## RAG Persistence

Do not rebuild FAISS/Chroma inside every temporary GitHub Actions runner.

Preferred strategy:

```text
Build index offline once
      ↓
Version it
      ↓
Upload as GitHub Release asset
      ↓
Reuse during deployment
```

## LLM Quota Rule

If LLM quota is exhausted:

```text
store incident
status = UNDER_INVESTIGATION
retry next scheduled cycle
```

Never fabricate a replacement analysis.

## Satellite Storage Retention

```text
Temporary raw scene:
Delete after processing

Cropped AOI patch:
Keep only when linked to incident

Annotated image:
Keep

Before/after comparison:
Keep

Routine no-anomaly imagery:
Delete
```

## External API Quota Strategy

The system must:

- Cache already retrieved metadata.
- Track source product IDs.
- Avoid duplicate processing.
- Use reasonable polling intervals.
- Respect provider rate limits.
- Use exponential backoff.
- Retry later rather than dropping work.

## Email Quota Rule

Email delivery must be treated as a queued operation.

If the provider quota is exhausted:

```text
alert status = QUOTA_EXHAUSTED
      ↓
store alert
      ↓
retry later
```

Do not drop a high-priority incident alert because email delivery temporarily failed.


# 44. Deployment Strategy

MarineGuard AI intentionally uses multiple deployment platforms, but every platform has a specific responsibility.

The goal is not to maximize the number of services.

The goal is to learn realistic separation of concerns.

## Frontend — Vercel

Deploy:

```text
Next.js
TypeScript
Tailwind CSS
```

Responsibilities:

- User interface
- Authentication flow
- Dashboard
- Interactive maps
- Evidence viewing
- Client-side API integration

Benefits:

- Native Next.js workflow
- Preview deployments
- Environment variables
- CI/CD from GitHub
- Frontend logs
- Production build experience

## Backend — Render

Deploy:

```text
FastAPI
Python
LangGraph
MCP integration
RAG APIs
```

Responsibilities:

- REST API
- Agent execution
- Database services
- Risk calculations
- Trajectory services
- Evidence metadata APIs
- Report generation

Important:

Render is **not** responsible for the scheduled monitoring loop in the free prototype.

If the Render service sleeps, scheduled monitoring should still continue.

## Database — Supabase

Use:

```text
PostgreSQL
PostGIS
Supabase Auth
```

Responsibilities:

- Incident persistence
- Authentication
- User records
- Alert queue
- Processing history
- Scheduler-health state
- Geospatial queries
- Evidence metadata

Example geospatial queries:

```text
Find incidents within 10 km

Find protected areas intersecting a predicted path

Find nearest coastline

Find incidents inside a selected polygon
```

## Evidence Storage — Cloudflare R2

Use for:

```text
Satellite evidence images
Annotated PNG/JPEG images
Before/after comparisons
Masks
Small GeoTIFF patches
```

Do not store unnecessary full satellite scenes.

## Scheduled Monitoring — GitHub Actions

Use:

```text
Scheduled workflows
```

Responsibilities:

- Poll satellite/environmental sources
- Process new source items
- Run deterministic anomaly detection
- Create/update incidents
- Trigger Agentic AI only when required
- Retry pending investigations
- Retry pending alerts
- Update system-health state

The scheduler is **best effort**, not an SLA-backed real-time service.

### Platform Constraints (documented, not worked around)

GitHub Actions scheduling has known limits that should be stated as accepted constraints of the free prototype rather than engineered around:

```text
Public repositories:
Standard runners are free; scheduled workflows run.

Private repositories:
Scheduled workflows consume the account's included free Actions minutes.

Either visibility:
A scheduled workflow is automatically disabled after 60 days
with no repository activity.

Either visibility:
schedule-triggered runs are best-effort and may be delayed
or occasionally dropped under GitHub-side load.
```

The repository should therefore stay active through normal development commits during the build phase. No artificial "keep-alive" job should be added purely to defeat the 60-day rule — that treats a platform constraint as something to game rather than a limitation to design around and disclose. If the project reaches a stage of genuine idle time longer than 60 days, re-enabling the workflow manually is the honest fix.

## RAG Index — GitHub Release Asset

Recommended deployed-prototype strategy:

```text
Build FAISS index offline
      ↓
Version the index
      ↓
Upload to GitHub Release
      ↓
Backend / job downloads when required
```

Rebuild only when documents, embeddings, or chunking change.

## Logical Deployment Architecture

```text
                      User
                       │
                       ▼
                Vercel / Next.js
                       │
                       ▼
                Render / FastAPI
                       │
        ┌──────────────┼───────────────┐
        ▼              ▼               ▼
    LangGraph          MCP             RAG
        │              │               │
        └──────────────┼───────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
          Supabase          Cloudflare R2
        PostgreSQL/PostGIS    Evidence
              ▲
              │
         GitHub Actions
        Scheduled Monitor
              │
     ┌────────┼─────────┐
     ▼        ▼         ▼
 Sentinel  Weather    Ocean
```

## Local Development

```text
Next.js local dev server
FastAPI local server
SQLite
Local evidence directory
Local FAISS index
```

## Future Production Upgrade

A production version may add:

```text
Dedicated worker
Job queue
Managed scheduler
Paid object storage
Managed observability
Autoscaling API
Dedicated geospatial database
```


# 45. Future Enhancements

## Multi-Pollutant Classification
Extend to oil, floating waste, turbidity, algal anomaly, and other marine anomalies.

## Land-to-Sea Pollution Pathway
Connect rainfall, river flow, known waste hotspots, and coastal currents to estimate possible marine waste movement.

## Advanced Drift Simulation
Add particle-tracking or oceanographic models.

## Cross-Satellite Fusion
Fuse Sentinel-1, Sentinel-2, Sentinel-3, and NASA products.

## Citizen Mobile Reporting
Allow users to upload a photo, location, and description.

## Response Planning
Suggest monitoring zones, inspection regions, priority coastline, and areas requiring human verification.

## Historical Pattern Analysis
Find recurring pollution hotspots.

## Advanced MCP Ecosystem
Expose MarineGuard tools to other MCP-compatible AI clients.

---

# Full-Stack Engineering Value

MarineGuard AI intentionally demonstrates multiple engineering domains in one coherent product.

## Web Development

```text
Next.js
React
TypeScript
Tailwind CSS
Routing
REST API integration
Authentication
Maps
Responsive design
```

## Backend Engineering

```text
FastAPI
Pydantic
SQLAlchemy
API design
Structured errors
Service separation
```

## Database Engineering

```text
PostgreSQL
PostGIS
Supabase
SQL
Geospatial queries
Authentication
```

## Generative AI

```text
LLM integration
Structured outputs
Prompt engineering
Tool calling
Evidence-grounded reporting
```

## Agentic AI

```text
LangGraph
Stateful workflows
Conditional routing
Multi-step investigation
Tool orchestration
```

## MCP

```text
Custom MCP server
Tool definitions
Agent-to-tool integration
Permission boundaries
```

## RAG

```text
Document ingestion
Chunking
Embeddings
FAISS
Retrieval
Grounded responses
```

## Computer Vision / Remote Sensing

```text
OpenCV
Rasterio
Satellite imagery
Anomaly detection
Image annotation
```

## Geospatial Engineering

```text
GeoPandas
PostGIS
Coordinates
Spatial intersections
Trajectory mapping
```

## DevOps / Deployment

```text
GitHub
GitHub Actions
Vercel
Render
Supabase
Cloudflare R2
Environment variables
Logs
CI/CD
```

The project should not use these technologies merely to increase the technology count.

Every component must support the central problem:

> Detect, investigate, explain, and monitor marine pollution incidents.

---

# 46. Expected Project Outcomes

At the end of the project, the prototype should demonstrate:

1. Automated satellite-data discovery.
2. Geospatial satellite-image processing.
3. Marine anomaly detection.
4. Persistent incident state.
5. Multi-source evidence aggregation.
6. LangGraph Agentic AI.
7. MCP tool calling.
8. RAG over marine documents.
9. Simplified trajectory prediction.
10. Environmental impact analysis.
11. Risk scoring.
12. Satellite evidence image capture.
13. Annotated image generation.
14. Before/after visual comparison.
15. Map-based dashboard.
16. Automated alerts.
17. Evidence-grounded GenAI reports.

---

# 47. Final Project Definition

## Project Name

**MarineGuard AI**

## Full Title

**MarineGuard AI: A Multi-Source Agentic Marine Pollution Early-Warning, Investigation and Response Intelligence System**

## Technical Definition

MarineGuard AI is a full-stack, multi-source, scheduled/event-driven Agentic AI platform that combines satellite remote sensing, environmental observations, optional vessel activity, geospatial analytics, structured risk models, MCP-based tools, RAG, and stateful LangGraph workflows to detect, investigate, track, and assess potential marine pollution incidents and generate evidence-grounded alerts.

## Simple Definition

MarineGuard AI is a software system that watches marine and coastal data, detects suspicious environmental changes, investigates what may be happening, estimates where the event may move, identifies what could be affected, captures satellite evidence images for those incidents, and alerts users only when the available evidence indicates that the event is important.

## Core Principle

```text
Scientific processing
        ↓
Structured evidence
        ↓
Agentic investigation
        ↓
Explainable decision support
```

---

# 48. References

## Copernicus Sentinel-1
Copernicus Data Space Ecosystem  
https://dataspace.copernicus.eu/data-collections/copernicus-sentinel-missions/sentinel-1

Sentinel-1 Documentation  
https://documentation.dataspace.copernicus.eu/Data/Sentinel1.html

## Copernicus Sentinel-2
Copernicus Data Space Ecosystem  
https://dataspace.copernicus.eu/data-collections/copernicus-sentinel-missions/sentinel-2

Sentinel-2 Documentation  
https://documentation.dataspace.copernicus.eu/Data/SentinelMissions/Sentinel2.html

## Copernicus Sentinel-3
Sentinel-3 OLCI Product Documentation  
https://sentiwiki.copernicus.eu/web/olci-products

## Copernicus APIs
https://documentation.dataspace.copernicus.eu/APIs.html

## NASA Ocean Data
NASA Earthdata / Ocean Biology Distributed Active Archive Center  
https://www.earthdata.nasa.gov/

---

# Recommended First Milestone

Do not begin with the entire Agentic AI system.

Start with:

```text
Select one Gujarat coastal area
          ↓
Get two Sentinel-2 images
          ↓
Read them with Python
          ↓
Crop the same region
          ↓
Compare the two dates
          ↓
Display detected changes on a map
```

Only after this works should the project add:

```text
Incident database
        ↓
Environmental data
        ↓
MCP
        ↓
LangGraph
        ↓
RAG
        ↓
Automated alerts
```

This keeps the project achievable while allowing it to grow into a substantial Agentic AI system.
