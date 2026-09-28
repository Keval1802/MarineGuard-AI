import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import List, Tuple

class Settings(BaseSettings):
    PROJECT_NAME: str = "MarineGuard AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Core Study Area (Gujarat - Surat / Hazira Coastal Region)
    # Bounding Box: [min_lon, min_lat, max_lon, max_lat]
    SURAT_HAZIRA_BBOX: Tuple[float, float, float, float] = (72.50, 21.00, 72.85, 21.30)
    DEFAULT_AOI_CENTER: Tuple[float, float] = (21.145, 72.620)
    
    # Database
    # Local fallback SQLite, Supabase PostgreSQL for production
    DATABASE_URL: str = Field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "sqlite:///" + os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "marineguard.db")).replace("\\", "/")
        )
    )
    
    # Authentication & Security
    SECRET_KEY: str = Field(default="")
    SUPABASE_URL: str = Field(default="https://lnlbjvfnwigxkwubxxsg.supabase.co")
    SUPABASE_ANON_KEY: str = Field(
        default_factory=lambda: os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    )
    SUPABASE_SERVICE_ROLE_KEY: str = Field(
        default_factory=lambda: os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SECRET_KEY", "")
    )
    SUPABASE_JWKS_URL: str = Field(
        default_factory=lambda: f"{os.getenv('SUPABASE_URL', 'https://lnlbjvfnwigxkwubxxsg.supabase.co')}/auth/v1/.well-known/jwks.json"
    )
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://marineguard.vercel.app"
    ]
    
    # Satellite Data Sources (Copernicus Ecosystem)
    COPERNICUS_CDSE_URL: str = "https://catalogue.dataspace.copernicus.eu/resto/api/collections"
    COPERNICUS_STAC_URL: str = "https://catalogue.dataspace.copernicus.eu/stac"
    COPERNICUS_USERNAME: str = Field(default="")
    COPERNICUS_PASSWORD: str = Field(default="")
    CDSE_CLIENT_ID: str = Field(default_factory=lambda: os.getenv("CDSE_CLIENT_ID", ""))
    CDSE_CLIENT_SECRET: str = Field(default_factory=lambda: os.getenv("CDSE_CLIENT_SECRET", ""))
    
    # Environmental APIs
    OPEN_METEO_WEATHER_URL: str = "https://api.open-meteo.com/v1/forecast"
    OPEN_METEO_MARINE_URL: str = "https://marine-api.open-meteo.com/v1/marine"
    
    # LLM & Agent Config (Gemini Primary / Groq Fallback)
    GEMINI_API_KEY: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    GROQ_API_KEY: str = Field(default_factory=lambda: os.getenv("GROQ_API_KEY", ""))
    PRIMARY_LLM_MODEL: str = Field(default="gemini-2.5-flash-lite") # Fallback to gemini-2.5-flash-lite / gemini-flash-latest
    FALLBACK_LLM_MODEL: str = Field(default="openai/gpt-oss-120b") # Groq model fallback
    
    # Object Storage (Cloudflare R2 or Local fallback)
    STORAGE_TYPE: str = Field(default="local")  # 'local' or 'r2'
    LOCAL_STORAGE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "storage", "evidence"))
    R2_ACCOUNT_ID: str = Field(default="")
    R2_ACCESS_KEY_ID: str = Field(default="")
    R2_SECRET_ACCESS_KEY: str = Field(default="")
    R2_BUCKET_NAME: str = Field(default="marineguard-evidence")
    
    # Email / Notification
    SMTP_HOST: str = Field(default="smtp.gmail.com")
    SMTP_PORT: int = 587
    SMTP_USER: str = Field(default="")
    SMTP_PASSWORD: str = Field(default="")
    ALERT_EMAIL_RECIPIENT: str = Field(default="alerts@marineguard.ai")

    @field_validator("SMTP_PORT", mode="before")
    @classmethod
    def parse_smtp_port(cls, v):
        if v == "" or v is None:
            return 587
        if isinstance(v, str):
            v_str = v.strip()
            if not v_str:
                return 587
            return int(v_str)
        return v

    @field_validator("SMTP_HOST", mode="before")
    @classmethod
    def parse_smtp_host(cls, v):
        if not v or (isinstance(v, str) and not v.strip()):
            return "smtp.gmail.com"
        return v

    @field_validator("ALERT_EMAIL_RECIPIENT", mode="before")
    @classmethod
    def parse_alert_email_recipient(cls, v):
        if not v or (isinstance(v, str) and not v.strip()):
            return "alerts@marineguard.ai"
        return v
    
    # Incident Merge Rule Parameters (Section 21)
    INCIDENT_MERGE_MAX_DISTANCE_KM: float = 5.0
    INCIDENT_MERGE_MAX_TIME_HOURS: float = 48.0
    
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

settings = Settings()
