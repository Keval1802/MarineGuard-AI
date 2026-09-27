import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

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

# Mount Static Evidence Assets Folder
os.makedirs(settings.LOCAL_STORAGE_DIR, exist_ok=True)
app.mount("/storage/evidence", StaticFiles(directory=settings.LOCAL_STORAGE_DIR), name="evidence")

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
