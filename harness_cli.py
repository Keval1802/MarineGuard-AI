import sys
import os
import argparse

sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from app.database import init_db
from harness.api_harness import APIEndpointHarness
from harness.agent_harness import AgentWorkflowHarness
from app.main import app

def main():
    init_db()
    parser = argparse.ArgumentParser(description="MarineGuard AI System Harness Runner")
    parser.add_argument("--mode", choices=["all", "api", "agents", "satellite", "pollutants"], default="all")
    args = parser.parse_args()

    print("MARINEGUARD AI SYSTEM HARNESS RUNNER")
    print("Mode: " + args.mode)

    if args.mode in ["all", "api"]:
        print("\nTesting API & Email Alert Harness...")
        api_harness = APIEndpointHarness(app)
        res = api_harness.verify_all_endpoints()
        for k, v in res.items():
            status = "PASSED" if v else "FAILED"
            print(f"  {k}: {status}")

    if args.mode in ["all", "agents"]:
        print("\nTesting Agentic AI Workflow Harness...")
        import asyncio
        payload = {
            "incident_id": "test-harness-001",
            "incident_code": "MG-HARNESS-01",
            "latitude": 21.145,
            "longitude": 72.620,
            "anomaly_type": "FLOATING_MATERIAL_CANDIDATE",
            "first_detected": "2026-10-02T00:00:00Z",
            "last_updated": "2026-10-02T00:00:00Z",
            "confidence_score": 85.0,
            "severity_score": 75.0,
            "priority_score": 0.82,
            "status": "DETECTED"
        }
        out = asyncio.run(AgentWorkflowHarness.run_workflow_test(payload))
        print(f"  Workflow Result: {out}")

    if args.mode in ["all", "pollutants"]:
        print("\nTesting Multi-Pollutant Spectrum Analysis Harness...")
        import asyncio
        p_res = asyncio.run(AgentWorkflowHarness.run_all_pollutants_harness_test())
        for ptype, info in p_res.items():
            print(f"  Pollutant Type: {ptype:<30} -> Priority: {info['priority_score']:.3f} [{info['risk_level']}] (Severity: {info['base_severity']:.2f})")

    print("\nSystem Harness Execution Completed Successfully")

if __name__ == "__main__":
    main()
