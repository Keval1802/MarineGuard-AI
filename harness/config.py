import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class HarnessSettings:
    USE_REAL_SATELLITE_ASSETS: bool = os.getenv("HARNESS_USE_REAL_ASSETS", "True").lower() == "true"
    MOCK_LLM_RESPONSES: bool = os.getenv("HARNESS_MOCK_LLM", "True").lower() == "true"
    STRICT_MATH_VALIDATION: bool = True
    
    ASSET_DIR: Path = BASE_DIR / "harness" / "assets"
    S1_SAR_PATH: Path = ASSET_DIR / "real_sentinel1_sar_hazira.png"
    S2_OPTICAL_PATH: Path = ASSET_DIR / "real_sentinel2_optical_hazira.png"
    
    FIXTURES_DIR: Path = BASE_DIR / "harness" / "fixtures"

harness_settings = HarnessSettings()
