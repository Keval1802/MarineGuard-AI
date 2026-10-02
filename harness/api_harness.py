from fastapi.testclient import TestClient
from typing import Dict
from app.database import init_db

class APIEndpointHarness:
    """Verifies FastAPI endpoints, fallback incident resolution, and email alerts."""

    def __init__(self, app):
        init_db()
        self.client = TestClient(app)
        self.headers = {"Authorization": "Bearer dev-admin-token"}

    def verify_all_endpoints(self) -> Dict[str, bool]:
        results = {}
        
        # 1. GET Incidents List
        res1 = self.client.get("/api/v1/incidents", headers=self.headers)
        results["get_incidents"] = (res1.status_code == 200)

        # 2. Reanalyze with Test Incident ID
        res2 = self.client.post("/api/v1/incidents/test-reanalyze-inc-001/reanalyze", headers=self.headers)
        results["reanalyze_incident"] = (res2.status_code == 200)

        # 3. Send Incident Email Alert
        res3 = self.client.post("/api/v1/incidents/test-reanalyze-inc-001/email", headers=self.headers)
        results["send_email_alert"] = (res3.status_code == 200)

        return results
