from typing import Dict, Any, Callable, List, Optional
import inspect
from app.mcp.tools.satellite_tools import SatelliteMCPTools
from app.mcp.tools.environmental_tools import EnvironmentalMCPTools
from app.mcp.tools.incident_tools import IncidentMCPTools
from app.mcp.tools.web_tools import WebMCPTools

class MarineIntelligenceMCPServer:
    """
    Custom Marine Intelligence MCP Server (Section 19).
    Exposes controlled, capability-scoped tools for AI Agents.
    Provides structured failure states and graceful degradation.
    """

    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._register_default_tools()

    def register_tool(self, name: str, scope: str, description: str, func: Callable):
        """Registers a tool with name, capability scope, and docstring description."""
        self.tools[name] = {
            "name": name,
            "scope": scope,
            "description": description,
            "function": func
        }

    def _register_default_tools(self):
        # Satellite Tools (Scope: satellite.read)
        self.register_tool("search_satellite_observations", "satellite.read", "Search Copernicus catalog for satellite observations", SatelliteMCPTools.search_satellite_observations)
        self.register_tool("get_latest_sentinel1_scene", "satellite.read", "Retrieve latest Sentinel-1 SAR scene for incident", SatelliteMCPTools.get_latest_sentinel1_scene)
        self.register_tool("get_latest_sentinel2_scene", "satellite.read", "Retrieve latest Sentinel-2 optical scene for incident", SatelliteMCPTools.get_latest_sentinel2_scene)
        self.register_tool("get_satellite_evidence_image", "satellite.read", "Fetch raw satellite evidence image path", SatelliteMCPTools.get_satellite_evidence_image)
        self.register_tool("get_annotated_incident_image", "satellite.read", "Fetch annotated mask overlay evidence image path", SatelliteMCPTools.get_annotated_incident_image)
        self.register_tool("get_before_after_comparison_image", "satellite.read", "Fetch side-by-side before/after comparison image path", SatelliteMCPTools.get_before_after_comparison_image)

        # Environmental & GIS Tools (Scopes: weather.read, ocean.read, vessel.read)
        self.register_tool("get_weather", "weather.read", "Retrieve wind speed, wind direction, and rainfall", EnvironmentalMCPTools.get_weather)
        self.register_tool("get_ocean_current", "ocean.read", "Retrieve ocean current speed, direction, and SST", EnvironmentalMCPTools.get_ocean_current)
        self.register_tool("get_tide", "ocean.read", "Retrieve tide state and water level", EnvironmentalMCPTools.get_tide)
        self.register_tool("get_nearby_ports", "ocean.read", "Retrieve ports near coordinates", EnvironmentalMCPTools.get_nearby_ports)
        self.register_tool("get_nearby_rivers", "ocean.read", "Retrieve river outlets near coordinates", EnvironmentalMCPTools.get_nearby_rivers)
        self.register_tool("get_sensitive_areas", "ocean.read", "Retrieve mangroves, beaches, and sensitive areas near coordinates", EnvironmentalMCPTools.get_sensitive_areas)
        self.register_tool("calculate_distance", "ocean.read", "Calculate distance between two coordinates in km", EnvironmentalMCPTools.calculate_distance)
        self.register_tool("calculate_drift", "ocean.read", "Calculate pollutant-specific drift trajectory points", EnvironmentalMCPTools.calculate_drift)

        # Incident Tools (Scopes: incident.read, incident.write, alert.write)
        self.register_tool("get_incident", "incident.read", "Retrieve active incident record", IncidentMCPTools.get_incident)
        self.register_tool("update_incident", "incident.write", "Update incident status and confidence", IncidentMCPTools.update_incident)
        self.register_tool("get_vessel_tracks", "vessel.read", "Retrieve candidate vessel tracks near coordinates", IncidentMCPTools.get_vessel_tracks)
        self.register_tool("detect_sar_vessels", "vessel.read", "Perform CA-CFAR Sentinel-1 SAR vessel detection around coordinates", IncidentMCPTools.detect_sar_vessels)
        self.register_tool("search_gfw_vessels", "vessel.read", "Search Global Fishing Watch V3 Vessels API by MMSI/IMO", IncidentMCPTools.search_gfw_vessels)
        self.register_tool("correlate_spill_vessels", "vessel.read", "Correlate oil slick polygon with candidate vessel AIS tracks and GFW identity", IncidentMCPTools.correlate_spill_vessels)
        self.register_tool("get_previous_incidents", "incident.read", "Retrieve previous historical incidents near location", IncidentMCPTools.get_previous_incidents)
        self.register_tool("create_alert", "alert.write", "Dispatch or queue incident warning alert", IncidentMCPTools.create_alert)

        # Web Tools (Scope: web.search, web.scrape)
        self.register_tool("web_search_maritime", "web.search", "Search the web in real-time for maritime incidents and vessel news", WebMCPTools.web_search_maritime)
        self.register_tool("scrape_maritime_webpage", "web.scrape", "Extract clean text from a target maritime webpage URL", WebMCPTools.scrape_maritime_webpage)

    def list_tools(self) -> List[Dict[str, str]]:
        """Returns metadata list of registered MCP tools."""
        return [
            {"name": meta["name"], "scope": meta["scope"], "description": meta["description"]}
            for meta in self.tools.values()
        ]

    async def call_tool(self, name: str, kwargs: Dict[str, Any], allowed_scopes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Executes named MCP tool with scope checking and graceful error handling.
        """
        if name not in self.tools:
            return {"status": "error", "error_code": "tool_not_found", "message": f"MCP Tool '{name}' not found."}

        tool = self.tools[name]
        
        # Capability scope authorization check (Section 19)
        if allowed_scopes and tool["scope"] not in allowed_scopes:
            return {"status": "error", "error_code": "permission_denied", "message": f"Scope '{tool['scope']}' required for tool '{name}'."}

        try:
            func = tool["function"]
            if inspect.iscoroutinefunction(func):
                result = await func(**kwargs)
            else:
                result = func(**kwargs)
            return result
        except Exception as e:
            # Structured failure state (Section 19: source unavailable, quota exhausted, etc.)
            return {
                "status": "error",
                "error_code": "source_unavailable",
                "message": f"MCP Tool '{name}' execution failed: {str(e)}"
            }

mcp_server = MarineIntelligenceMCPServer()
