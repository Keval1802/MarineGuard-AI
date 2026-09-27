import sys
import os
import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.config import settings

def test_cdse():
    client_id = settings.CDSE_CLIENT_ID
    client_secret = settings.CDSE_CLIENT_SECRET
    print(f"Client ID: {client_id[:12]}...")

    token_resp = httpx.post(
        "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        },
        timeout=10.0
    )
    print("OAuth Token status:", token_resp.status_code)
    if token_resp.status_code != 200:
        print("Token Error:", token_resp.text)
        return

    token = token_resp.json().get("access_token")

    lat, lon = 19.1075, 72.8263
    bbox = [lon - 0.08, lat - 0.08, lon + 0.08, lat + 0.08]

    evalscript_s1 = """//VERSION=3
function setup() {
  return {
    input: ["VV"],
    output: { bands: 3 }
  };
}
function evaluatePixel(sample) {
  var v = sample.VV * 2.5;
  return [v, v, v];
}"""

    p_body = {
        "input": {
            "bounds": {"bbox": bbox},
            "data": [{"type": "sentinel-1-grd"}]
        },
        "output": {
            "width": 512,
            "height": 512,
            "responses": [{"identifier": "default", "format": {"type": "image/png"}}]
        },
        "evalscript": evalscript_s1
    }

    headers = {"Authorization": f"Bearer {token}"}
    print("Sending Process API request to Copernicus Data Space for Sentinel-1 SAR...")
    try:
        p_resp = httpx.post(
            "https://sh.dataspace.copernicus.eu/api/v1/process",
            json=p_body,
            headers=headers,
            timeout=45.0
        )
        print("Sentinel-1 Process API HTTP Status:", p_resp.status_code)
        print("Response Content Length:", len(p_resp.content), "bytes")
        if p_resp.status_code != 200:
            print("Response Body Error Details:\n", p_resp.text[:800])
    except Exception as e:
        print("HTTP Exception:", e)

if __name__ == "__main__":
    test_cdse()
