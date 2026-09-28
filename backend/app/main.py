import os
import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse

from app.config import settings
from app.database import init_db
from app.api import incidents, citizen_reports, monitoring, health, rag, mcp

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.LOCAL_STORAGE_DIR, exist_ok=True)
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="MarineGuard AI Multi-Source Agentic Pollution Early-Warning System API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Section 40: CORS Middleware restricted to explicit Vercel and local origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

os.makedirs(settings.LOCAL_STORAGE_DIR, exist_ok=True)

@app.get("/storage/evidence/{filename:path}")
async def serve_evidence_file(filename: str):
    """
    Serves satellite evidence image files with multi-tier fallback:
    1. Returns local file if present on disk.
    2. Redirects to Supabase Cloud Storage bucket if present online.
    3. Dynamically generates synthetic evidence on-demand if missing.
    """
    local_path = os.path.join(settings.LOCAL_STORAGE_DIR, filename)
    if os.path.exists(local_path):
        return FileResponse(local_path)

    # 2. Check Supabase Cloud Storage bucket public URL
    supabase_url = f"{settings.SUPABASE_URL}/storage/v1/object/public/marineguard-evidence/{filename}"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.head(supabase_url)
            if res.status_code == 200:
                return RedirectResponse(url=supabase_url)
    except Exception:
        pass

    # 3. Dynamic On-Demand Synthetic Fallback Generation
    try:
        from app.satellite.image_capture import SatelliteImageCaptureService
        svc = SatelliteImageCaptureService()
        
        # Parse safe incident_code from filename
        if "_raw" in filename:
            incident_code = filename.split("_raw")[0]
        elif "_annotated" in filename:
            incident_code = filename.split("_annotated")[0]
        elif "_comparison" in filename:
            incident_code = filename.split("_comparison")[0]
        else:
            incident_code = filename.rsplit("_", 1)[0]

        mission = "Sentinel-1" if "sentinel-1" in filename.lower() else "Sentinel-2"
        svc.capture_evidence_images(
            incident_code=incident_code,
            anomaly_type="FLOATING_MATERIAL_CANDIDATE",
            confidence=85.0,
            area_km2=0.005,
            mission=mission
        )
        if os.path.exists(local_path):
            return FileResponse(local_path)
    except Exception:
        pass

    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"status": "error", "message": f"Evidence file {filename} not found"}
    )

# Include API Routers
app.include_router(incidents.router, prefix=settings.API_V1_STR)
app.include_router(citizen_reports.router, prefix=settings.API_V1_STR)
app.include_router(monitoring.router, prefix=settings.API_V1_STR)
app.include_router(rag.router, prefix=settings.API_V1_STR)
app.include_router(mcp.router, prefix=settings.API_V1_STR)
app.include_router(health.router)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An internal server error occurred.",
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
